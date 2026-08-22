from dataclasses import dataclass

from bs4 import BeautifulSoup

from app.models.monitoring_rule import MonitoringRule
from app.monitoring.retriever import RetrievedPage


@dataclass
class ExtractedData:
    price: str | None = None
    availability: str | None = None
    text: str | None = None


class MonitoringExtractor:

    def extract(
        self,
        page: RetrievedPage,
        rules: list[MonitoringRule],
    ) -> ExtractedData:

        soup = BeautifulSoup(
            page.html,
            "html.parser",
        )

        rule_types = {
            rule.rule_type.upper()
            for rule in rules
            if rule.is_enabled
        }

        extracted = ExtractedData()

        if "PRICE" in rule_types:
            extracted.price = self._extract_price(soup)

        if "AVAILABILITY" in rule_types:
            extracted.availability = self._extract_availability(
                soup
            )

        if "KEYWORD" in rule_types:
            extracted.text = soup.get_text(
                separator=" ",
                strip=True,
            )

        return extracted

    def _extract_price(
        self,
        soup: BeautifulSoup,
    ) -> str | None:
        return None

    def _extract_availability(
        self,
        soup: BeautifulSoup,
    ) -> str | None:
        return None