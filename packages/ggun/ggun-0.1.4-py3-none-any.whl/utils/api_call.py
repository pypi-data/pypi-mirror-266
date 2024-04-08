import requests
import os

API_URL = os.getenv("GGUN_API_URL", "https://api.ggun.app:8080")
TIMEOUT_TIME = 300
print(f"GGUN: using api url: {API_URL}")


def api_call(api_key, endpoint, req_type, data=None, files=None):
    endpoint_fmtd = f"/{endpoint}" if not endpoint.startswith("/") else endpoint
    url = f"{API_URL}/{endpoint_fmtd}"

    headers = {
        "X-API-KEY": api_key,
        # "Content-Type": "application/json" # This is set automatically when using files in requests
    }
    if req_type == "POST":
        if files and data:
            raise ValueError(
                "Sending both files and data in the same request not yet tested"
            )
        # When uploading files, the 'files' parameter is used in requests.post
        # The 'Content-Type' header is set automatically by requests, so it's omitted here
        response = requests.post(
            url, headers=headers, json=data, files=files, timeout=TIMEOUT_TIME
        )
    elif req_type == "GET":
        response = requests.get(url, headers=headers, timeout=TIMEOUT_TIME)
    else:
        raise ValueError(f"Invalid request type: {req_type}")

    if response.status_code == 200:
        print(f"({req_type}) {endpoint} API Call Successful")
        return response.json()
    else:
        error_message = (
            f"API Call failed with status code: {response.status_code}, "
            f"Error: {response.text}"
        )
        print(error_message)
        return None
