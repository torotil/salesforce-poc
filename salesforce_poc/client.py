import requests
import urllib.parse


class Client:
    """REST API client for the Salesforce / Lightning Platform REST API.

    At the time of writing the API-documentation could be found on:
    https://developer.salesforce.com/docs/atlas.en-us.api_rest.meta/api_rest/intro_what_is_rest_api.htm
    """

    VERSION = "v51.0"

    def __init__(self, instance_url: str, access_token: str, request_timeout=2):
        """Create a new API client instance."""
        self.session = requests.Session()
        self.session.headers["Authorization"] = f"Bearer {access_token}"
        self.base_url = instance_url
        self.timeout = request_timeout

    def get(self, *path_parts, **kwargs):
        """Send a GET-request."""
        return self.request("GET", *path_parts, **kwargs)

    def delete(self, *path_parts, **kwargs):
        """Send a DELETE-request."""
        return self.request("DELETE", *path_parts, **kwargs)

    def post(self, *path_parts, **kwargs):
        """Send a POST-request."""
        return self.request("POST", *path_parts, **kwargs)

    def patch(self, *path_parts, **kwargs):
        """Send a POST-request."""
        return self.request("PATCH", *path_parts, **kwargs)

    def put(self, *path_parts, **kwargs):
        """Send a PUT-request."""
        return self.request("PUT", *path_parts, **kwargs)

    def request(self, method, *path_parts, path=None, url=None, **kwargs):
        """Send a request to the API-endpoint and handle the response.

        This accepts either of (the first of these wins):
        - A url passed as kwarg.
        - A path passed as kwarg.
        - Path parts that will be escaped and joined passed as positional arguments.
        """
        if not path and path_parts:
            path = "/".join(urllib.parse.quote_plus(part) for part in path_parts)
            path = f"/services/data/{self.VERSION}/" + path
        if url:
            if not url.startswith(self.base_url):
                raise requests.exceptions.URLRequired(
                    f"This client only sends requests to {self.base_url}"
                )
        elif path:
            url = self.base_url + path
        kwargs.setdefault("timeout", self.timeout)
        kwargs.setdefault("allow_redirects", False)
        response = self.session.request(method, url, **kwargs)
        # response.raise_for_status()
        return response

    def find_contact(self, email, first_name, last_name):
        query = f"SELECT Id, FirstName, LastName FROM Contact WHERE Email = '{email}'"
        result = self.get("query", params={"q": query})
        contacts = result.json()["records"]
        if not contacts:
            return None
        if len(contacts) == 1:
            return contacts[0]["attributes"]["url"]
        for record in contacts:
            if record["FirstName"] == first_name and record["LastName"] == last_name:
                return record["attributes"]["url"]
        return None

    def new_contact(self, data):
        return self.post("sobjects", "Contact", json=data)

    def update_contact(self, contact_id, data):
        return self.patch("sobjects", "Contact", contact_id, json=data)
