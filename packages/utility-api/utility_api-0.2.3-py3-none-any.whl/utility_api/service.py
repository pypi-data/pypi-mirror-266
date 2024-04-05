"""Interface wrapper for Utilities API."""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Iterator, List, Optional

from requests import Response, delete, get, post
from utility_api.models.endpoints.authorization import (
    Authorization,
    AuthorizationListing,
)
from utility_api.models.endpoints.bill import Bill, BillsListing
from utility_api.models.endpoints.form import Form
from utility_api.models.endpoints.interval import (
    DataPoint,
    Interval,
    IntervalsListing,
)
from utility_api.models.endpoints.meter import Meter
from utility_api.models.object_types.test_scenario import TestScenario

UTILITIES_API: str = "api"
UTILITIES_VERSION: str = "v2"


@dataclass
class UtilitiesService:
    """Integrations related to Utilities API."""

    utilities_token: str
    headers: Dict[str, str] = field(default_factory=dict)
    utilities_base_url: str = (
        f"https://utilityapi.com/{UTILITIES_API}/{UTILITIES_VERSION}"
    )

    def __post_init__(self) -> None:
        """Populate the headers dictionary."""
        authorization_key: str = "Authorization"
        if authorization_key not in self.headers:
            self.headers[authorization_key] = f"Bearer {self.utilities_token}"

    @property
    def utilities_forms_url(self) -> str:  # noqa: D102
        return f"{self.utilities_base_url}/forms"

    @property
    def utilities_authorizations_url(self) -> str:  # noqa: D102
        return f"{self.utilities_base_url}/authorizations"

    @property
    def utilities_meters_url(self) -> str:  # noqa: D102
        return f"{self.utilities_base_url}/meters"

    @property
    def utilities_bills_url(self) -> str:  # noqa: D102
        return f"{self.utilities_base_url}/bills"

    @property
    def utilities_intervals_url(self) -> str:  # noqa: D102
        return f"{self.utilities_base_url}/intervals"

    def create_new_form(self) -> Form:
        """Create a new form for authorizing a utilities customer.

        Returns:
            An authorization form

        Raises:
            ValueError: If the HTTP request fails
        """
        response: Response = post(f"{self.utilities_forms_url}", headers=self.headers)
        if response.status_code != 200:
            raise ValueError(f"{response.status_code}: Failed to create Form")

        return Form.from_json(response.text)

    def get_form_by_uid(self, form_uid: str) -> Form:
        """Get an authorization form from a form UID.

        Args:
            form_uid: The UID of a form of interest

        Returns:
            The authorization form of the provided UID

        Raises:
            ValueError: If the HTTP request fails
        """
        response: Response = get(
            f"{self.utilities_forms_url}/{form_uid}", headers=self.headers
        )
        if response.status_code != 200:
            raise ValueError(
                f"{response.status_code}: Failed to retrieve Form {form_uid}"
            )

        return Form.from_json(response.text)

    def simulate_form_submission(self, form_uid: str, scenario: TestScenario) -> str:
        """Simulate a user submitting a form.

        Args:
            form_uid: The UID of a form of interest
            scenario: The test scenario to simulate

        Returns:
            The referral code to look up the authorization

        Raises:
            ValueError: If the HTTP request fails
        """
        response: Response = post(
            f"{self.utilities_forms_url}/{form_uid}/test-submit",
            headers=self.headers,
            json={"utility": "DEMO", "scenario": scenario.value},
        )
        if response.status_code != 200:
            raise ValueError(
                f"{response.status_code}: Failed to simulate submission for Form {form_uid}"  # noqa: E501
            )

        return str(response.json()["referral"])

    def get_authorizations_from_referral(
        self, referral_code: str, include_meters: bool
    ) -> List[Authorization]:
        """Get the client's authorization from a referral code.

        Args:
            referral_code: The referral code
            include_meters: Flag to include basic meter information

        Returns:
            A list of authorizations from the referral code

        Raises:
            ValueError: If the HTTP request fails
        """
        url = f"{self.utilities_authorizations_url}?referrals={referral_code}"
        if include_meters:
            url += "&include=meters"
        response: Response = get(url, headers=self.headers)
        if response.status_code != 200:
            raise ValueError(
                f"{response.status_code}: Failed to retrieve authorization from Referral {referral_code}"  # noqa: E501
            )

        listing = AuthorizationListing.from_json(response.text)
        authorizations: List[Authorization] = listing.authorizations
        return authorizations

    def list_all_authorizations(self) -> List[Authorization]:
        """List all authorizations available to the Utility API account.

        Returns:
            A list authorizations.

        Raises:
            ValueError: If the HTTP request fails
        """
        response: Response = get(
            f"{self.utilities_authorizations_url}", headers=self.headers
        )
        if response.status_code != 200:
            raise ValueError(
                f"{response.status_code}: Failed to retrieve authorizations"
            )

        listing = AuthorizationListing.from_json(response.text)
        authorizations: List[Authorization] = listing.authorizations
        return authorizations

    def get_authorizations_by_uid(self, authorization_uid: str) -> List[Authorization]:
        """Get an authorization object from an authorization UID.

        Args:
            authorization_uid: The UID of the authorization of interest

        Returns:
            A list of authorizations from the provided uid

        Raises:
            ValueError: If the HTTP request fails
        """
        response: Response = get(
            f"{self.utilities_authorizations_url}/{authorization_uid}",
            headers=self.headers,
        )
        if response.status_code != 200:
            raise ValueError(
                f"{response.status_code}: Failed to get Authorization {authorization_uid}"  # noqa: E501
            )

        authorization = Authorization.from_json(response.text)
        authorizations: List[Authorization] = []
        for referral_code in authorization.referrals:
            authorizations.extend(
                self.get_authorizations_from_referral(
                    referral_code, include_meters=True
                )
            )
        return authorizations

    def get_meter_by_uid(self, meter_uid: str) -> Meter:
        """Get a meter object from a meter UID.

        Args:
            meter_uid: The UID of the meter of interest

        Returns:
            The Meter object of the provided UID

        Raises:
            ValueError: If the HTTP request fails
        """
        response: Response = get(
            f"{self.utilities_meters_url}/{meter_uid}", headers=self.headers
        )
        if response.status_code != 200:
            raise ValueError(f"{response.status_code}: Failed to get Meter {meter_uid}")

        return Meter.from_json(response.text)

    def trigger_historical_collection(self, meter_uids: list[str]) -> int:
        """Trigger the collection of historical data for list of meters.

        Args:
            meter_uids: A list of meter UIDs

        Returns:
            The response code from triggering the historical collection
        """
        response: Response = post(
            f"{self.utilities_meters_url}/historical-collection",
            headers=self.headers,
            data=json.dumps({"meters": meter_uids}),
        )

        return response.status_code

    def delete_test_authorizations(self) -> None:
        """Delete authorizations from the Demo account."""
        test_authorization_uids = [
            authorization.uid
            for authorization in self.list_all_authorizations()
            if authorization.is_test
        ]
        for authorization_uid in test_authorization_uids:
            response = delete(
                f"{self.utilities_authorizations_url}/{authorization_uid}",
                headers=self.headers,
            )
            print(response, response.text)

    def bills_by_meter_uid(self, meter_uid: str) -> Iterator[Bill]:
        """Collect the bills associated with a meter of interest.

        Args:
            meter_uid: The UID of the meter of interest

        Yields:
            A bill associated with the meter

        Raises:
            ValueError: If the HTTP request fails
        """
        response: Response = get(
            f"{self.utilities_bills_url}?meters={meter_uid}", headers=self.headers
        )
        if response.status_code != 200:
            raise ValueError(
                f"{response.status_code}: Failed to get bills from Meter {meter_uid}"  # noqa: E501
            )

        listing = BillsListing.from_json(response.text)
        for bill in listing.bills:
            yield bill

    def intervals_by_meter_uid(self, meter_uid: str) -> Iterator[Interval]:
        """Collect the intervals associated with a meter of interest.

        Args:
            meter_uid: The UID of the meter of interest

        Yields:
            An interval associated with the meter

        Raises:
            ValueError: If the HTTP request fails
        """
        response: Response = get(
            f"{self.utilities_intervals_url}?meters={meter_uid}", headers=self.headers
        )
        if response.status_code != 200:
            raise ValueError(
                f"{response.status_code}: Failed to get intervals from Meter {meter_uid}"  # noqa: E501
            )

        listing = IntervalsListing.from_json(response.text)
        for interval in listing.intervals:
            yield interval

    def datapoints_from_interval_readings_by_meter_uid(
        self, meter_uid: str
    ) -> Iterator[DataPoint]:
        """Get the interval readings from a meter of interest.

        Args:
            meter_uid: The UID of the meter of interest

        Yields:
            A datapoint for the meter of interest
        """
        for interval in self.intervals_by_meter_uid(meter_uid):
            for reading in interval.readings:
                for datapoint in reading.datapoints_with_reading_metadata():
                    yield datapoint

    def export_meter_billing_summaries_csv(
        self, meter_uid: str, export_path: Optional[Path] = None
    ) -> str:
        """Get the billing summaries csv contents for a meter of interest.

        Args:
            meter_uid: The UID of the meter of interest
            export_path: The path to export the local file

        Returns:
            The string contents of the billing summaries csv

        Raises:
            ValueError: If the HTTP request fails
        """
        url = f"https://utilityapi.com/api/v2/files/billing_summaries_csv?{meter_uid}"
        response: Response = get(url, headers=self.headers)
        if response.status_code != 200:
            raise ValueError(f"Response code {response.status_code} for request {url}")

        if export_path:
            with open(export_path.with_suffix(".csv"), "w") as file:
                file.write(response.text)

        return response.text

    def export_meter_bills_csv(
        self, meter_uid: str, export_path: Optional[Path] = None
    ) -> str:
        """Get the bills csv contents for a meter of interest.

        Args:
            meter_uid: The UID of the meter of interest
            export_path: The path to export the local file

        Returns:
            The string contents of the bills csv

        Raises:
            ValueError: If the HTTP request fails
        """
        url = f"https://utilityapi.com/api/v2/files/meters_bills_csv?meters={meter_uid}"
        response: Response = get(url, headers=self.headers)
        if response.status_code != 200:
            raise ValueError(f"Response code {response.status_code} for request {url}")

        if export_path:
            with open(export_path.with_suffix(".csv"), "w") as file:
                file.write(response.text)

        return response.text

    def export_meter_intervals_csv(
        self, meter_uid: str, export_path: Optional[Path] = None
    ) -> str:
        """Get the intervals csv contents for a meter of interest.

        Args:
            meter_uid: The UID of the meter of interest
            export_path: The path to export the local file

        Returns:
            The string contents of the intervals csv

        Raises:
            ValueError: If the HTTP request fails
        """
        url = f"https://utilityapi.com/api/v2/files/intervals_csv?{meter_uid}"
        response: Response = get(url, headers=self.headers)
        if response.status_code != 200:
            raise ValueError(f"Response code {response.status_code} for request {url}")

        if export_path:
            with open(export_path.with_suffix(".csv"), "w") as file:
                file.write(response.text)

        return response.text

    def export_meter_lineitems_csv(
        self, meter_uid: str, export_path: Optional[Path] = None
    ) -> str:
        """Get the lineitems csv contents for a meter of interest.

        Args:
            meter_uid: The UID of the meter of interest
            export_path: The path to export the local file

        Returns:
            The string contents of the lineitems csv

        Raises:
            ValueError: If the HTTP request fails
        """
        url = f"https://utilityapi.com/api/v2/files/meters_lineitems_csv?meters={meter_uid}"  # noqa: E501
        response: Response = get(url, headers=self.headers)
        if response.status_code != 200:
            raise ValueError(f"Response code {response.status_code} for request {url}")

        if export_path:
            with open(export_path.with_suffix(".csv"), "w") as file:
                file.write(response.text)

        return response.text

    def export_meter_bill_pdf_zipped(self, meter_uid: str, export_path: Path) -> None:
        """Download the zipfile of available bill pdfs for a meter of interest.

        Args:
            meter_uid: The UID of the meter of interest
            export_path: The path to export the local file

        Raises:
            ValueError: If the HTTP request fails
        """
        url = f"https://utilityapi.com/api/v2/files/meters_bills_zip?meters={meter_uid}"
        response: Response = get(url, headers=self.headers)
        if response.status_code != 200:
            raise ValueError(f"Response code {response.status_code} for request {url}")

        with open(export_path.with_suffix(".zip"), "wb") as f:
            for chunk in response.iter_content(chunk_size=512):
                if chunk:
                    f.write(chunk)

    def export_meter_latest_pdf(self, meter_uid: str, export_path: Path) -> None:
        """Download the pdf of the latest bill for a meter of interest.

        Args:
            meter_uid: The UID of the meter of interest
            export_path: The path to export the local file

        Raises:
            ValueError: If the HTTP request fails
        """
        url = f"https://utilityapi.com/api/v2/files/latest_pdf/{meter_uid}"
        response: Response = get(url, headers=self.headers)
        if response.status_code != 200:
            raise ValueError(f"Response code {response.status_code} for request {url}")

        with open(export_path.with_suffix(".pdf"), "wb") as f:
            f.write(response.content)
