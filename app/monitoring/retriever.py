
from dataclasses import dataclass

import httpx


@dataclass
class RetrievedPage:
    url: str
    status_code: int
    html: str


class PageAccessBlockedError(RuntimeError):
    """Raised when a website returns an access challenge instead of its page."""


class WebRetriever:
    _BLOCKED_PAGE_MARKERS = (
        "automated access",
        "robot check",
        "validatecaptcha",
        "unusual traffic",
        "verify you are human",
        "access denied",
        "sorry, we just need to make sure you're not a robot",
        "enter the characters you see below",
    )

    def __init__(self, timeout: float = 30.0):
        self.timeout = timeout

    def retrieve(self, url: str) -> RetrievedPage:
        response = httpx.get(
            url,
            timeout=self.timeout,
            follow_redirects=True,
        )
        response.raise_for_status()

        html = response.text
        lowered_html = html.lower()

        matched_marker = next(
            (
                marker
                for marker in self._BLOCKED_PAGE_MARKERS
                if marker in lowered_html
            ),
            None,
        )

        if matched_marker:
            raise PageAccessBlockedError(
                "Website returned an access challenge instead of the requested "
                f"page (detected marker: {matched_marker!r})."
            )

        return RetrievedPage(
            url=str(response.url),
            status_code=response.status_code,
            html=html,
        )
