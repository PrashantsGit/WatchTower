from dataclasses import dataclass

import httpx


@dataclass
class RetrievedPage:
    url: str
    status_code: int
    html: str


class WebRetriever:

    def __init__(
        self,
        timeout: float = 30.0,
    ):
        self.timeout = timeout

    def retrieve(
        self,
        url: str,
    ) -> RetrievedPage:

        response = httpx.get(
            url,
            timeout=self.timeout,
            follow_redirects=True,
        )

        response.raise_for_status()

        return RetrievedPage(
            url=str(response.url),
            status_code=response.status_code,
            html=response.text,
        )