from http.client import HTTPException
from typing import Any, Callable, Dict
from urllib.parse import urljoin

from pydantic import BaseModel, HttpUrl, SecretStr
from requests import Response

from galileo_core.constants.http_headers import HttpHeaders


class ApiClient(BaseModel):
    host: HttpUrl
    jwt_token: SecretStr

    @property
    def auth_header(self) -> Dict[str, str]:
        return {"Authorization": f"Bearer {self.jwt_token.get_secret_value()}"}

    @staticmethod
    def validate_response(response: Response) -> None:
        if not response.ok:
            raise HTTPException(
                "Something didn't go quite right. The api returned a non-ok status "
                f"code {response.status_code}. Error message: + {response.text}."
            ) from None

    @staticmethod
    def make_request(
        request_method: Callable[..., Response], base_url: str, endpoint: str, *args: Any, **kwargs: Any
    ) -> Any:
        response = request_method(urljoin(base_url, endpoint), *args, **kwargs)
        ApiClient.validate_response(response)
        return response.json()

    def request(
        self,
        method: Callable[..., Response],
        path: str,
        content_headers: Dict[str, str] = HttpHeaders.json(),
        **kwargs: Any,
    ) -> Any:
        return ApiClient.make_request(
            request_method=method,
            base_url=self.host.unicode_string(),
            endpoint=path,
            headers={**content_headers, **self.auth_header},
            **kwargs,
        )
