import json
import requests
import os
from .AuthBearerToken import AuthBearerToken
from dotenv import load_dotenv
load_dotenv(override=True)


class InputException(ValueError):
    pass

class AuthenticationError(ValueError):
    pass

class EndpointException(ValueError):
    pass


class EGE:
    """
    Class for communicating with the Geodetic Engine API
    """
    def __init__(self):

        self.EGE_API_ENV = os.getenv('EGE_API_ENV', 'prod') # set "prod" as default if not defined
        if self.EGE_API_ENV in ('test', 'dev'):
            self.GE_API = f"https://api-{self.EGE_API_ENV}.gateway.equinor.com/geodetic-engine/v1"
        else:
            self.GE_API = "https://api.gateway.equinor.com/geodetic-engine/v1"

        self.GE_ENDPOINT_TRANSFORMATION = f"{self.GE_API}/transform"
        self.GE_WKT_ENDPOINT = f'{self.GE_API}/crs/wkt'
        self.GE_VALIDATE_ENDPOINT = f'{self.GE_API}/validate'
        if self.EGE_API_ENV in ('test', 'dev'):
            self.GE_CRS_SEARCH_ENDPOINT = f'{self.GE_API}/crs/search'
            self.GE_CT_SEARCH_ENDPOINT = f'{self.GE_API}/ct/search'
        self.auth = AuthBearerToken()

        print(self.GE_API)

    def get_pipeline(self, crs_from, crs_to):
        """Request transformation pipeline"""
        input_params = {'crs_from': crs_from.replace(" ",""), 'crs_to': crs_to.replace(" ","")}
        response = self.call_endpoint(self.GE_ENDPOINT_TRANSFORMATION, 'post', input_params)
        return response

    def transform_crs(self, points, crs_from, crs_to):
        """Transform points"""
        input_params = {'coordinates_from': points, 'crs_from': crs_from.replace(" ",""), 'crs_to': crs_to.replace(" ","")}
        response = self.call_endpoint(self.GE_ENDPOINT_TRANSFORMATION, 'post', input_params)
        return response

    def crs_search(self, types, polygon_coords, target_crs):
        """Search CRSs"""
        input_params = {'types': types, 'polygon_coords': polygon_coords, 'target_crs': target_crs.replace(" ","")}
        response = self.call_endpoint(self.GE_CRS_SEARCH_ENDPOINT, 'post', input_params)
        return response

    def ct_search(self, types, polygon_coords, source_crs, target_crs):
        """Query CTs"""
        input_params = {'types': types, 'polygon_coords': polygon_coords, 'source_crs': source_crs.replace(" ",""), 'target_crs': target_crs.replace(" ","")}
        response = self.call_endpoint(self.GE_CT_SEARCH_ENDPOINT, 'post', input_params)
        return response

    def validate_input(self, user_input):
        """
        Validate user input using
        the API validate endpoint
        """
        endpoint = f"{self.GE_VALIDATE_ENDPOINT}?input={user_input}"
        response = self.call_endpoint(endpoint, 'get')
        return response

    def request_wkt_for_crs(self, crs, wkt_version):
        """Request WKT for a CRS"""
        crs = crs.replace(" ","") # remove any whitespace
        url = f"{self.GE_WKT_ENDPOINT}?input={crs}&wkt_version={wkt_version}"
        return self.call_endpoint(url, 'get')

    def call_endpoint(self, endpoint,  http_method='get', input_params_dict=None):
        """Get endpoint together with valid bearer token"""
        try:
            if http_method.lower() == 'get':
                if input_params_dict:
                    response = requests.get(
                        endpoint, headers=self.auth.authorization_headers(self.EGE_API_ENV), params=input_params_dict, timeout=30
                    )
                else:
                    response = requests.get(
                        endpoint, headers=self.auth.authorization_headers(self.EGE_API_ENV), timeout=30
                    )
            elif http_method.lower() == 'post':
                if not input_params_dict:
                    raise InputException("Input parameters are empty")
                json_payload = json.dumps(input_params_dict).strip(' \t\n\r')
                response = requests.post(endpoint, headers=self.auth.authorization_headers(self.EGE_API_ENV), data=json_payload, timeout=30)
            else:
                raise InputException("Invalid HTTP method specified")

            result = response.json()
            response.raise_for_status()
        except requests.exceptions.Timeout:
            raise EndpointException("Request timed out")
        except requests.exceptions.RequestException as e:
            if response.status_code == 401:
                message = result['message']
            else:
                message = result.get('detail', {}).get('reason', '')
            raise EndpointException(f"{e}. {message}")
        except ValueError as e:
            raise EndpointException(f"JSON decoding failed: {e}")
        return result