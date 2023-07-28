from wsrepl import Plugin
import requests

# Set to None if no proxy required
plugin_proxy = {
    "http": "http://127.0.0.1:8080",
    "https": "http://127.0.0.1:8080"
}

class MultiStepAuthDemo(Plugin):
    url = None # Required to pass dynamic wss url to MessageHandler.py

    def init(self):
        # Step one: Get a JWT
        response = self.send_jwt_request()
        jwt_token = self.extract_jwt_from_response(response)
        if jwt_token:
            # Step 2: Get a access/bearer token
            response_jwt = self.request_access_token(jwt_token)   
            access_token = self.extract_access_token_from_response(response_jwt)
            if access_token:
                # Step 3: Get the dynamic wss link 
                wss_start = self.get_wss_endpoint(access_token)
                self.url = self.extract_url_from_response(wss_start)
    
    def send_jwt_request(self):
        url = "https://example.com/users/auth"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/112.0",
            "Accept": "application/json",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate",
            "Content-Type": "application/x-www-form-urlencoded",
            "Origin": "https://example-origin.com",
            "Referer": "https://example-referer.com/",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "cross-site"
        }

        data = {
            "clientId": "your-client-id",
            "secret": "your-client-secret",
            "identity": "user-identity",
            "aud": "public",
            "isAnonymous": "true",
            "sid": "session-id",
            "page": "contactus",
            "lang": "en_US",
            "role": "VISITOR"
        }

        response = requests.post(url, headers=headers, data=data, proxies=plugin_proxy, verify=False)
        return response

    def extract_jwt_from_response(self, response):
        try:
            json_data = response.json()
            jwt_token = json_data.get("token")
            return jwt_token
        except ValueError:
            return None

    def request_access_token(self, jwt_token):
        url = "https://example.com/api/token/jwtgrant"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/112.0",
            "Accept": "*/*",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate",
            "Content-Type": "application/json",
            "Origin": "https://example-origin.com",
            "Referer": "https://example-referer.com/",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "cross-site"
        }

        data = {
            "assertion": jwt_token,
            "botInfo": {
                "chatBot": "example-bot",
                "botId": "task-bot-id"
            }
        }

        response = requests.post(url, headers=headers, json=data, proxies=plugin_proxy, verify=False)
        return response

    def extract_access_token_from_response(self, response):
        try:
            json_data = response.json()
            access_token = json_data["authorization"]["accessToken"]
            return access_token
        except (ValueError, KeyError):
            return None

    def get_wss_endpoint(self, access_token):
        url = "https://example.com/api/chat/start"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/112.0",
            "Accept": "application/json",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate",
            "Content-Type": "application/json",
            "Authorization": f"Bearer {access_token}",
            "Origin": "https://example-origin.com",
            "Referer": "https://example-referer.com/",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "cross-site"
        }

        data = {
            "botInfo": {
                "chatBot": "example-bot",
                "botId": "task-bot-id"
            }
        }

        response = requests.post(url, headers=headers, json=data, proxies=plugin_proxy, verify=False)
        return response

    def extract_url_from_response(self, response):
        try:
            json_data = response.json()
            url = json_data["endpoint"]
            return url
        except (ValueError, KeyError):
            return None
