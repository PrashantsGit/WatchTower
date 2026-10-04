
from dataclasses import dataclass
import json
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
            extracted.availability = self._extract_availability(soup)

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
                return str(value).strip()

        # 2. OpenGraph product price metadata
        meta_price = soup.find(
            "meta",
            attrs={"property": "product:price:amount"},
        )

        if meta_price and meta_price.get("content"):
            return meta_price["content"].strip()

        # 3. JSON-LD structured product data
        for script in soup.find_all(
            "script",
            attrs={"type": "application/ld+json"},
        ):
            try:
                data = json.loads(
                    script.string or script.get_text()
                )
            except (json.JSONDecodeError, TypeError):
                continue

            price = self._extract_json_ld_price(data)

            if price is not None:
                return price

        # 4. Prefer dedicated price elements.
        # Amazon's offscreen element normally contains the clean
        # display price, unlike its surrounding price container.
        for selector in (
            ".a-price .a-offscreen",
            '[data-a-color="price"] .a-offscreen',
        ):
            for element in soup.select(selector):
                value = (
                    element.get("content")
                    or element.get_text(" ", strip=True)
                )

                if value and value.strip():
                    return value.strip()

        # 5. Elements whose class or id contains "price"
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

        # 6. Visible text containing a currency value
        currency_pattern = re.compile(
            r"(₹|\$|€|£)\s*[\d,]+(?:\.\d{1,2})?"
        )

        for element in soup.find_all(
            string=lambda text: (
                text is not None
                and currency_pattern.search(str(text))
            )
        ):
            match = currency_pattern.search(str(element))

            if match:
                return match.group(0).strip()

        return None

    @staticmethod
    def _extract_availability(
        soup: BeautifulSoup,
    ) -> str | None:
        """Extract availability without scanning unrelated page text."""

        def normalize_status(
            value: str | None,
        ) -> str | None:
            if not value:
                return None

            normalized = (
                value.strip()
                .lower()
                .replace("_", "")
                .replace("-", "")
            )

            # Schema.org availability values.
            if any(
                marker in normalized
                for marker in (
                    "outofstock",
                    "soldout",
                    "discontinued",
                )
            ):
                return "OUT_OF_STOCK"

            if any(
                marker in normalized
                for marker in (
                    "instock",
                    "limitedavailability",
                    "onlineonly",
                )
            ):
                return "IN_STOCK"

            # Human-readable availability text.
            if any(
                phrase in normalized
                for phrase in (
                    "out of stock",
                    "currently unavailable",
                    "sold out",
                    "not available",
                    "unavailable",
                )
            ):
                return "OUT_OF_STOCK"

            if any(
                phrase in normalized
                for phrase in (
                    "in stock",
                    "available now",
                    "available for purchase",
                )
            ):
                return "IN_STOCK"

            return None

        # 1. Prefer explicit Schema.org microdata.
        for element in soup.select('[itemprop="availability"]'):
            value = (
                element.get("href")
                or element.get("content")
                or element.get_text(" ", strip=True)
            )

            status = normalize_status(str(value))

            if status:
                return status

        # 2. Inspect product-specific availability elements.
        availability_selectors = (
            "#availability",
            ".availability",
            '[id*="availability" i]',
            '[class*="availability" i]',
        )

        seen_elements = set()

        for selector in availability_selectors:
            for element in soup.select(selector):
                element_id = id(element)

                if element_id in seen_elements:
                    continue

                seen_elements.add(element_id)

                value = element.get_text(" ", strip=True)
                status = normalize_status(value)

                if status:
                    return status

        # 3. Fallback for standalone stock-status elements.
        # Do not scan arbitrary page text for broad availability phrases.
        exact_in_stock = {
            "in stock",
            "available now",
            "available for purchase",
        }

        exact_out_of_stock = {
            "out of stock",
            "sold out",
            "currently unavailable",
        }

        for element in soup.find_all(
            ["span", "button", "p", "strong"]
        ):
            normalized = " ".join(
                element.get_text(" ", strip=True).lower().split()
            )

            if normalized in exact_out_of_stock:
                return "OUT_OF_STOCK"

            if normalized in exact_in_stock:
                return "IN_STOCK"

        # Unknown availability must remain unknown.
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
