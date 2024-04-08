from dotenv import load_dotenv
load_dotenv(override=True)

import os
from .MsalCredential import MsalCredential
import re

class AuthBearerToken:
    def __init__(self):
        separator = ';'

        client_envs = os.getenv("EGE_CLIENT_ENVS")
        subs_keys_variable = os.getenv("EGE_SUBS_KEYS")
        api_env_variable = os.getenv('EGE_API_ENV', 'prod')

        client_envs_list = ['prod', 'test']
        resource_ids_list = ['c25018ed-b371-4b37-ba4e-4d902aee2b6c','84c8d2ec-6294-47aa-8fd4-f69c870faa3a']
        if not client_envs and ';' not in subs_keys_variable:
            client_envs_list = [api_env_variable]
        if len(client_envs_list)==1:
            if 'prod' in client_envs_list:
                resource_ids_list = ['c25018ed-b371-4b37-ba4e-4d902aee2b6c']
            else:
                resource_ids_list = ['84c8d2ec-6294-47aa-8fd4-f69c870faa3a']

        client_envs = client_envs.split(separator) if client_envs else client_envs_list

        client_ids = os.getenv("EGE_CLIENT_IDS")
        client_ids = client_ids.split(separator) if client_ids else ['c25018ed-b371-4b37-ba4e-4d902aee2b6c','84c8d2ec-6294-47aa-8fd4-f69c870faa3a']

        resource_ids_variable = os.getenv("EGE_RESOURCE_IDS")
        resource_ids = resource_ids_variable.split(separator) if resource_ids_variable else resource_ids_list

        client_secrets_variable =  os.getenv("EGE_CLIENT_SECRETS")
        client_secrets = client_secrets_variable.split(separator) if client_secrets_variable else [None] * len(client_envs)

        subs_keys = subs_keys_variable.split(separator) if subs_keys_variable else [None] * len(client_envs)

        tenant_id = '3aa4a235-b6e2-48d5-9195-7fcf05b459b0'
        authority = f"https://login.microsoftonline.com/{tenant_id}"


        self._credentials = {
            env: MsalCredential(client_id, authority, client_secret)
                .with_scopes([f"{resource_id}/.default openid"]).with_subscription_key(subs_key)
            for env, client_id, client_secret, resource_id,subs_key in zip(client_envs, client_ids, client_secrets, resource_ids, subs_keys)
        }

    def get_authorization(self, environment) -> str:
        cred = self._credentials.get(environment)
        if not cred:
            raise KeyError(f"Failed to retrieve msal client for environment {environment}")
        return cred.get_authorization()

    def authorization_headers(self, uri, headers={}):
        headers |= {"Authorization": self.get_authorization(uri)}
        subs_key = self._credentials.get(uri).get_subscription_key()
        if subs_key:
            headers |= {"Ocp-Apim-Subscription-Key": subs_key}
        return headers

