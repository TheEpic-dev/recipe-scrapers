import os
from typing import Any, Iterator, Optional, Tuple
import unittest

import responses


class ScraperTest(unittest.TestCase):

    maxDiff = None
    online = False
    test_file_name: Optional[str] = None
    test_file_extension = "testhtml"
    scraper_class: Any

    @property
    def expected_requests(self) -> Iterator[Tuple[str, str, str]]:
        """
        Descriptions of the expected requests that the scraper-under-test will make, as
        tuples of: HTTP method, URL, path-to-content-file
        """
        filename = self.test_file_name or self.scraper_class.__name__.lower()
        path = f"tests/test_data/{filename}.{self.test_file_extension}"
        yield responses.GET, "https://test.example.com", path

    def setUp(self):
        os.environ[
            "RECIPE_SCRAPERS_SETTINGS"
        ] = "tests.test_data.test_settings_module.test_settings"

        with responses.RequestsMock() as rsps:
            start_url = None
            for method, url, path in self.expected_requests:
                start_url = start_url or url
                with open(path, encoding="utf-8") as f:
                    response = responses.Response(method, url, body=f.read())
                    response.passthrough = self.online
                    rsps.add(response)

            self.harvester_class = self.scraper_class(url=start_url)
