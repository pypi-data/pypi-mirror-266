from typing import Iterable, List, Literal, Optional, Required, TypedDict, Union
import httpx

from prodpadlm_client.client_types.messages import Message

# default timeout is 10 minutes
DEFAULT_TIMEOUT = httpx.Timeout(timeout=600.0, connect=5.0)
DEFAULT_MAX_RETRIES = 2
DEFAULT_CONNECTION_LIMITS = httpx.Limits(max_connections=1000, max_keepalive_connections=100)

__all__ = ["MessageParam"]


class MessageParam(TypedDict, total=False):
    content: str

    role: Required[Literal["user", "assistant"]]
    
class ProdPADLM_API():

    class Client:
        def __init__(self, api_key:str, base_url:str, default_headers:str=""):
            headers = {
                "Content-Type": "application/json",
                "X-API-Key":api_key
            }
            self._post = httpx.Client(headers=headers)
            self.url = base_url

            
        def create(self, **params) -> Message :
            response = self._post.post(self.url + "/api/v1/generate", json=params)
            resp = Message(**response.json())
            return resp

    class AsyncClient:
        def __init__(self, api_key:str, base_url:str, default_headers:str=""):
            headers = {
                "Content-Type": "application/json",
                "X-API-Key":api_key
            }
            self._post = httpx.AsyncClient(headers=headers,timeout=DEFAULT_TIMEOUT)
            self.url = base_url
        
        def create(self, **params) -> Message :
            response = self._post.post(self.url + "/api/v1/generate", json=params)
            resp = Message(**response.json())
            return resp

    def create(
        self,
        *,
        max_tokens: int,
        messages: Iterable[MessageParam],
        model: str,
        stop_sequences: List[str],
        stream: Literal[False] | Literal[True],
        system: str,
        temperature: float,
        top_k: int,
        top_p: float,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        timeout: float | httpx.Timeout = 600,
    ) -> Message :
        return self._post.post(
            self.url + "/v1/generate",
            json={
                    "max_tokens": max_tokens,
                    "messages": messages,
                    "model": model,
                    "stop_sequences": stop_sequences,
                    "stream": stream,
                    "system": system,
                    "temperature": temperature,
                    "top_k": top_k,
                    "top_p": top_p,
                }
        
        )