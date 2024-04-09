# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import requests
import os
import time
from importlib.metadata import version, PackageNotFoundError
from language_utils.language_mode import LanguageMode

DEFAULT_TIMEOUT = int(os.environ.get("DEFAULT_TEST_TIMEOUT", "60"))
PACKAGE = "promptflow-azure-ai-language"


# Client class to connect to and call Azure AI Language APIs:
class LanguageClient():

    def __init__(self,
                 endpoint,
                 api_key,
                 inter_path,
                 region=None,
                 cert=None,
                 session: requests.Session = None):
        self.endpoint = endpoint
        self.region = region
        self.inter_path = inter_path
        self.url = endpoint + inter_path
        self.cert = cert
        self.api_key = api_key
        self.session = session

    def get_headers(self):
        pkg_version = "dev"
        try:
            pkg_version = version(PACKAGE)
        except PackageNotFoundError:
            pass

        headers = {
            "Ocp-Apim-Subscription-Key": self.api_key,
            "Content-Type": "application/json",
            "User-Agent": f"{PACKAGE}/{pkg_version}"
        }
        if self.region:
            headers["Ocp-Apim-Subscription-Region"] = self.region
        return headers

    # Synchronous API request:
    def run_sync_endpoint(self,
                          json_obj: dict,
                          query_parameters: dict,
                          max_retries: int,
                          max_wait: int,
                          method="post"):
        headers = self.get_headers()
        session = requests.Session() if self.session is None else self.session

        response = submit_request(request_func=lambda:
                                  session.request(method=method,
                                                  url=self.url,
                                                  params=query_parameters,
                                                  headers=headers,
                                                  json=json_obj,
                                                  cert=self.cert),
                                  max_retries=max_retries,
                                  max_wait=max_wait)
        return response

    # Asynchronous API request:
    def run_async_endpoint(self,
                           json_obj: dict,
                           query_parameters: dict,
                           max_retries: int,
                           max_wait: int,
                           method="post",
                           timeout=DEFAULT_TIMEOUT,
                           sleep_time=5):
        headers = self.get_headers()
        session = requests.Session() if self.session is None else self.session

        response = submit_request(request_func=lambda:
                                  session.request(method=method,
                                                  url=self.url,
                                                  params=query_parameters,
                                                  headers=headers,
                                                  json=json_obj,
                                                  cert=self.cert),
                                  max_retries=max_retries,
                                  max_wait=max_wait)

        try:
            response.raise_for_status()
        except requests.HTTPError:
            return response

        # Poll until completion of job:
        status_url = response.headers["Operation-Location"]
        start = time.time()
        while (True):
            if time.time() - start > timeout:
                print(response)
                print(response.content.decode(response.encoding or "utf-8"))
                print(response.headers)
                raise TimeoutError("Operation timed out")

            response = submit_request(request_func=lambda:
                                      session.get(url=status_url,
                                                  headers=headers,
                                                  cert=self.cert),
                                      max_retries=max_retries,
                                      max_wait=max_wait)

            try:
                response.raise_for_status()
                json_res = response.json()
                status = json_res["status"]
                if status == "succeeded" or status == "failed":
                    break
            except requests.HTTPError:
                pass

            time.sleep(sleep_time)

        return response

    # Run either sync or async endpoint.
    def run_endpoint(self,
                     json_obj: dict,
                     query_parameters: dict,
                     mode: LanguageMode,
                     max_retries: int,
                     max_wait: int):
        if mode == LanguageMode.SYNC:
            return self.run_sync_endpoint(json_obj=json_obj,
                                          query_parameters=query_parameters,
                                          max_retries=max_retries,
                                          max_wait=max_wait)
        else:
            return self.run_async_endpoint(json_obj=json_obj,
                                           query_parameters=query_parameters,
                                           max_retries=max_retries,
                                           max_wait=max_wait)


# Calculate exponential backoff wait time:
def exponential_backoff(max_retries: int,
                        max_wait: int,
                        retry_count: int):
    wait_time = max_wait ** (retry_count / max_retries)
    return wait_time


# Submit HTTP request with exponential backoff logic:
def submit_request(request_func,
                   max_retries: int,
                   max_wait: int):
    retries = 0
    response = None
    while (retries < max_retries):
        try:
            if retries != 0:
                print(f"Status code: {response.status_code}; Retrying...")
                wait_time = exponential_backoff(max_wait=max_wait,
                                                max_retries=max_retries,
                                                retry_count=retries)
                time.sleep(wait_time)
            response = request_func()
            retries += 1
            response.raise_for_status()
            return response
        except requests.HTTPError:
            pass

    print("Maximum number of retries reached.")
    return response
