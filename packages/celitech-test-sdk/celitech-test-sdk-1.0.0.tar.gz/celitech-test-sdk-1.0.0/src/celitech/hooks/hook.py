import os
import time
import requests


class Request:
    def __init__(self, method, url, headers, body=""):
        self.method = method
        self.url = url
        self.headers = headers
        self.body = body

    def __str__(self):
        return f"method={self.method}, url={self.url}, headers={self.headers}, body={self.body})"


class Response:
    def __init__(self, status, headers, body):
        self.status = status
        self.headers = headers
        self.body = body

    def __str__(self):
        return "Response(status={}, headers={}, body={})".format(
            self.status, self.headers, self.body
        )


class CustomHook:

    def __init__(self):
        self.CURRENT_TOKEN = None
        self.CURRENT_EXPIRY = 0

    def before_request(self, request: Request):
        if request.url.endswith("/oauth/token"):
            return

        # Get the client_id and client_secret from environment variables
        client_id = os.getenv("CLIENT_ID", "")
        client_secret = os.getenv("CLIENT_SECRET", "")

        if not client_id or not client_secret:
            print("Missing CLIENT_ID and/or CLIENT_SECRET environment variables")
            return
        else:
            # Check if CURRENT_TOKEN is missing or CURRENT_EXPIRY is in the past
            if not self.CURRENT_TOKEN or self.CURRENT_EXPIRY < time.time() * 1000:
                # Assuming Celitech class and its methods are defined appropriately
                sdk = Celitech(environment=Environment.TOKEN_SERVER)

                # Prepare the request payload for fetching a fresh OAuth token
                input_data = {
                    "client_id": client_id,
                    "client_secret": client_secret,
                    "grant_type": "client_credentials",
                }

                # Fetch a fresh OAuth token
                token_response = self.do_post(request, input_data, "/oauth2/token")
                expires_in = token_response.get("expires_in")
                access_token = token_response.get("access_token")

                if not expires_in or not access_token:
                    print("There is an issue with getting the OAuth token")
                    return

                self.CURRENT_EXPIRY = time.time() * 1000 + expires_in * 1000
                self.CURRENT_TOKEN = access_token

            # Set the Bearer token in the request header
            authorization = f"Bearer {self.CURRENT_TOKEN}"
            request.headers.update({"Authorization": authorization})

    def do_post(self, request: Request, input_data: dict, url_endpoint: str):
        full_url = "https://auth.celitech.net/oauth2/token"

        try:
            response = requests.post(
                full_url,
                data=input_data,
                headers={"Content-type": "application/x-www-form-urlencoded"},
                verify=True,
            )

            return response.json() if response.ok else None
        except Exception as error:
            print("Error in posting the request:", error)
            return None

    def after_response(self, request: Request, response: Response):
        pass

    def on_error(self, error: Exception, request: Request, response: Response):
        pass
