from dataclasses import dataclass
import re
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
        # 1. Schema.org itemprop="price"
        price_element = soup.find(
            attrs={"itemprop": "price"}
        )

        if price_element:
            value = (
                price_element.get("content")
                or price_element.get_text(strip=True)
            )

            if value:
                return value

        # 2. OpenGraph product price metadata
        meta_price = soup.find(
            "meta",
            attrs={"property": "product:price:amount"},
        )

        if meta_price and meta_price.get("content"):
            return meta_price["content"]

        # 3. JSON-LD structured product data
        for script in soup.find_all(
            "script",
            attrs={"type": "application/ld+json"},
        ):
            try:
                import json

                data = json.loads(
                    script.string or script.get_text()
                )
            except (json.JSONDecodeError, TypeError):
                continue

            price = self._extract_json_ld_price(data)

            if price is not None:
                return price

        # 4. Elements whose class or id contains "price"
        for element in soup.find_all(
            lambda tag: (
                tag.name
                and (
                    "price" in " ".join(
                        tag.get("class", [])
                    ).lower()
                    or "price" in tag.get("id", "").lower()
                )
            )
        ):
            text = element.get_text(
                " ",
                strip=True,
            )

            if text:
                return text

        # 5. Visible text containing a currency value
        currency_pattern = re.compile(
            r"(₹|\$|€|£)\s*[\d,]+(?:\.\d{1,2})?"
        )

        for element in soup.find_all(
            string=lambda text: (
                text
                and currency_pattern.search(text)
            )
        ):
            match = currency_pattern.search(element)

            if match:
                return match.group(0).strip()

        return None

    def _extract_availability(
        self,
        soup: BeautifulSoup,
    ) -> str | None:
        page_text = soup.get_text(
            " ",
            strip=True,
        ).lower()

        # Strong out-of-stock signals should be checked first.
        out_of_stock_signals = (
            "out of stock",
            "out-of-stock",
            "currently unavailable",
            "not available",
            "unavailable",
        )

        for signal in out_of_stock_signals:
            if signal in page_text:
                return "OUT_OF_STOCK"

        # Common in-stock signals.
        in_stock_signals = (
            "in stock",
            "in-stock",
            "available",
        )

        for signal in in_stock_signals:
            if signal in page_text:
                return "IN_STOCK"

        return None

    def _extract_json_ld_price(
        self,
        data,
    ) -> str | None:

        if isinstance(data, list):
            for item in data:
                price = self._extract_json_ld_price(item)

                if price is not None:
                    return price

            return None

        if not isinstance(data, dict):
            return None

        offers = data.get("offers")

        if isinstance(offers, dict):
            price = offers.get("price")

            if price is not None:
                return str(price)

        if isinstance(offers, list):
            for offer in offers:
                if isinstance(offer, dict):
                    price = offer.get("price")

                    if price is not None:
                        return str(price)

        return None