import os
import base64
import requests as req
from .afas_filter import AfasFilter, afas_filters_to_query

class AfasConnector:
    """
    A class representing an AFAS Connector.

    This class provides methods to interact with AFAS Connectors through HTTP requests.
    """

    def __init__(self, connector_url: str | None = None, token: str | None = None):
        """
        Initializes an instance of the AfasConnector class.

        The AFAS connector URL and token are retrieved from environment variables.
        """
        # AFAS connector URL
        self.AFAS_CONNECTORS_URL = os.getenv('AFAS_CONNECTORS_URL') if connector_url is None else connector_url

        # Get AFAS token
        self.afas_token = base64.b64encode((os.getenv('AFAS_TOKEN') if token is None else token).encode()).decode()

        # Create AFAS headers
        self.headers = {
            'Authorization': 'AfasToken ' + self.afas_token
        }

    def get(self, endpoint: str, take=1000000, skip=0, filters: list[AfasFilter] | None=None, order_by: str | None=None, ascending=True):
        """
        Sends a GET request to the AFAS Connector.

        Args:
            endpoint (str): The endpoint of the AFAS Connector.
            take (int, optional): The number of records to retrieve. Defaults to 1000000.
            skip (int, optional): The number of records to skip. Defaults to 0.
            filters (list[AfasFilter], optional): A list of AfasFilter objects to apply as filters. Defaults to None.
            order_by (str, optional): The field to order the records by. Defaults to None.
            ascending (bool, optional): Whether to sort the records in ascending order. Defaults to True.

        Returns:
            tuple: A tuple containing the status code and the JSON response from the AFAS Connector.
        """
        # Check if endpoint starts with "/"
        if endpoint[0] != "/":
            endpoint = "/" + endpoint

        # Create the URL
        url = self.AFAS_CONNECTORS_URL + endpoint + f'?take={take}&skip={skip}'

        # Add ordering
        if order_by is not None:
            if ascending:
                url += f'&orderbyfieldids={order_by}'
            else:
                url += f'&orderbyfieldids=-{order_by}'

        # Add filters
        if filters is not None:
            url += afas_filters_to_query(filters)

        # Make the GET request
        print(f"GET {url}")
        response = req.get(url, headers=self.headers)

        if response.status_code < 200 or response.status_code >= 300:
            print(f"Request error: {response.status_code} {response.text}")
            return response.status_code, None
        
        return response.status_code, response.json()


    def put(self, endpoint: str, payload: dict):
        """
        Sends a PUT request to the AFAS Connector.

        Args:
            endpoint (str): The endpoint of the AFAS Connector.
            payload (dict): The payload to send in the request.

        Returns:
            tuple: A tuple containing the status code and the JSON response from the AFAS Connector.
        """
        # Check if endpoint starts with "/"
        if endpoint[0] != "/":
            endpoint = "/" + endpoint

        # Create the URL
        url = self.AFAS_CONNECTORS_URL + endpoint

        # Make the PUT request
        print(f"PUT {url}")
        response = req.put(url, headers=self.headers, json=payload)

        if response.status_code < 200 or response.status_code >= 300:
            print(f"Request error: {response.status_code} - {response.text}")
            return response.status_code, None
        
        # Try to parse the response as JSON
        try:
            data = response.json()
        except:
            data = response.text

        return response.status_code, data
    
    def post(self, endpoint: str, payload: dict):
        """
        Sends a POST request to the AFAS Connector.

        Args:
            endpoint (str): The endpoint of the AFAS Connector.
            payload (dict): The payload to send in the request.

        Returns:
            tuple: A tuple containing the status code and the JSON response from the AFAS Connector.
        """
        # Check if endpoint starts with "/"
        if endpoint[0] != "/":
            endpoint = "/" + endpoint

        # Create the URL
        url = self.AFAS_CONNECTORS_URL + endpoint

        # Make the POST request
        print(f"POST {url}")
        response = req.post(url, headers=self.headers, json=payload)

        if response.status_code < 200 or response.status_code >= 300:
            print(f"Request error: {response.status_code} - {response.text}")
            return response.status_code, None
        
        # Try to parse the response as JSON
        try:
            data = response.json()
        except:
            data = response.text

        return response.status_code, data