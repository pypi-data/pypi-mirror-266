import json
import os
import tempfile
from pathlib import Path
from urllib.parse import urljoin

import pytest

from regscale.core.app.api import Api
from regscale.core.app.utils.catalog_utils.download_catalog import get_new_catalog
from regscale.core.app.utils.catalog_utils.update_catalog_v2 import import_catalog
from regscale.models.app_models.catalog_compare import CatalogCompare
from tests.models.test_fixture import CLITestFixture


class TestImport(CLITestFixture):
    """
    Test for AWS integration
    """

    @pytest.fixture(autouse=False)
    def setup(self, catalog_id):
        # Setup code goes here. This will execute before each test method.
        print("Setting up before test")
        my_dir = tempfile.mkdtemp()
        api = Api()
        # You can initialize variables, create necessary objects, or set up any necessary preconditions for the test here.
        data = CatalogCompare.get_master_catalogs(api=api)
        # download json file with requests
        for catalog in data["catalogues"]:
            if catalog["download"] and catalog["name"] == "Australian-ISM":
                url = catalog["link"]
                name = Path(catalog["link"]).name
                cat = get_new_catalog(url=url)
                with open(Path(tempfile.gettempdir()) / my_dir / name, "w") as f:
                    json.dump(cat, f)
                catalog_id["name"] = name
                catalog_id["file"] = Path(tempfile.gettempdir()) / my_dir / name
        # Download a bad file
        bad_url = (
            "https://gist.githubusercontent.com/moredip/4165313/raw/ad00ee5bc70016a70976736d5cdf0463d5f7ea15/test.json"
        )
        bad_name = Path(bad_url).name
        bad_cat = get_new_catalog(url=bad_url)
        catalog_id["bad_name"] = "Invalid JSON"
        catalog_id["bad_file"] = Path(tempfile.gettempdir()) / my_dir / bad_name
        with open(catalog_id["bad_file"], "w") as bad_file:
            json.dump(bad_cat, bad_file)

    @pytest.fixture(scope="module")
    def catalog_id(self):
        return {}

    @pytest.fixture(autouse=False)
    def teardown(self, catalog_id):
        yield  # This is where the test function will execute
        # Teardown code goes here. This will execute after each test method.
        print("Tearing down after test")
        api = Api()
        if catalog_id.get("id"):
            # Delete the newly created catalog
            res = api.delete(url=urljoin(api.app.config["domain"], f"/api/catalogues/{catalog_id['id']}"))
            print(res.text)
            assert res.status_code == 200  # Assert the catalog has been deleted.

    def test_import_catalog_invalid(self, setup, catalog_id):
        # Arrange
        catalog_path = Path(catalog_id["bad_file"])

        # Act
        res = import_catalog(catalog_path)
        # Assert
        assert res.json()["success"] is False

    def test_import_catalog_valid(self, setup, teardown, catalog_id):
        # Arrange
        catalog_path = Path(catalog_id["file"])

        # Act
        res = import_catalog(catalog_path)
        # Assert
        assert res.json()["success"] is True
        catalog_id["id"] = res.json()["catalogId"]
