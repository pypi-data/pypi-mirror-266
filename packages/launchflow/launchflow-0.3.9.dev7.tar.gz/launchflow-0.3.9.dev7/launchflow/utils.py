from typing import Union

import httpx
from requests import Response


# TODO: Move "potential fix" messsages into the server.
# Server should return a json payload with a message per client type, i.e.
# {status: 409, message: "Conflict...", fix: {"cli": "Run this command..."}}
# Use details to return the fix payload:
# details = {message: "...", fix: {"cli": "Run this command..."}}
def get_failure_text(response: Union[httpx.Response, Response]) -> str:
    status_code = response.status_code
    try:
        json_response = response.json()
        return f"({status_code}): {json_response['detail']}"
    except Exception:
        if isinstance(response, Response):
            return f"({status_code}): {response.reason}"
        return f"({status_code}): {response.reason_phrase}"
