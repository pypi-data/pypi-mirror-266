
"""
This module contains a python class for getting an access token for the Geodetic Engine
"""
import os
import datetime
from os.path import expanduser
import msal
import sys
import ctypes


class MsalCredential:
    def __init__(self, client_id: str, authority: str, client_secret: str = None, token_cache: str = None):

        self._token_expire = datetime.datetime.now()

        self._client_secret = client_secret
        self._cache = msal.SerializableTokenCache()

        if token_cache:
            self._token_cache = token_cache
        else:
            self._token_cache = expanduser("~/.ege-token-cache-client-"+client_id)
        if os.path.exists(self._token_cache):
            with open(self._token_cache, "r", encoding="utf8") as cachefile:
                self._cache.deserialize(cachefile.read())

        if self._client_secret:
            self._app = msal.ConfidentialClientApplication(client_id, client_credential=client_secret, authority=authority, token_cache=self._cache)
        else:
            self._app = msal.PublicClientApplication(client_id, authority=authority, token_cache=self._cache)

        self._scopes = None
        self._subscription_key = None


    def with_scopes(self, scopes):
        self._scopes = scopes
        return self

    def with_subscription_key(self, subs_key):
        self._subscription_key = subs_key
        return self

    def _has_gui(self):
        if sys.platform == "win32":
            try:
                ctypes.windll.user32.GetSystemMetrics(0)
                return True
            except:
                return False
        else:
            try:
                os.environ["DISPLAY"]
                return True
            except:
                return False


    def renew_token(self) -> dict:
        token_now = datetime.datetime.now()

        result = None
        if self._client_secret:
            result = self._app.acquire_token_for_client(self._scopes)
        else:
            accounts = self._app.get_accounts()
            if accounts:
                result = self._app.acquire_token_silent(
                    self._scopes, account=accounts[0])
            if not result:
                if self._has_gui():
                    result = self._app.acquire_token_interactive(self._scopes)
                else:
                    flow = self._app.initiate_device_flow(self._scopes)
                    if "user_code" not in flow:
                        raise Exception("Failed to create device flow")
                    print(flow["message"])
                    result = self._app.acquire_token_by_device_flow(flow)
            self._save_cache_if_changed()

        if "access_token" in result:
            self._token_expire = token_now + datetime.timedelta(seconds=result["expires_in"])
            self._token = {
                'token_type' : result["token_type"],
                'token': result['access_token']
            }
        else:
            print(result)
            raise Exception("No access token in result")

    def get_authorization(self) -> str:
        diff = self._token_expire - datetime.datetime.now()
        if diff.total_seconds() < 5.0:
            self.renew_token()
        return f'{self._token["token_type"]} {self._token["token"]}'

    def get_subscription_key(self) -> str:
        return self._subscription_key

    def _save_cache_if_changed(self):
        if self._cache.has_state_changed:
            with open(self._token_cache, "w", encoding="utf8") as cache_file:
                cache_file.write(self._cache.serialize())