import time

import pytest
from assertpy import assert_that
from playwright.sync_api import Page, expect

from src.helpers.data_helper import extract_url


class TestSighUrlCommand:
    @pytest.fixture(autouse=True)
    def setup_test(self, sample_project, sample_bucket, sample_file_to_bucket, sign_up_preconditions,gcp_client, page):
        self.client = gcp_client
        self.project = sample_project
        self.bucket = sample_bucket
        self.bucket_file_path = sample_file_to_bucket
        self.sa = sign_up_preconditions
        self.page: Page = page

    def test_generate_sign_url(self):
        response = self.client.sign_url(
            bucket_file_path=self.bucket_file_path,
            project=self.project,
            service_account=self.sa,
        )
        assert_that(response.status_code).is_equal_to(0)
        assert_that(response.output).contains("signed_url")
        url = extract_url(response.output)
        assert_that(url).is_not_empty()
        self.page.goto(url=url)
        expect(self.page.get_by_text("Hey there!"), "No access to file ").to_be_visible()
        expect(self.page.get_by_text("You have access to the file!"), "No access to file ").to_be_visible()

    def test_access_limited_by_time(self):
        expected_duration = 5

        response = self.client.sign_url(
            bucket_file_path=self.bucket_file_path,
            project=self.project,
            service_account=self.sa,
            duration=expected_duration
        )
        assert_that(response.status_code).is_equal_to(0)
        assert_that(response.output).contains("signed_url")
        url = extract_url(response.output)
        assert_that(url).is_not_empty()
        time.sleep(expected_duration)

        self.page.goto(url=url)
        expect(self.page.locator(selector="div span", has_text="ExpiredToken").first,
               "File was not expired").to_be_visible()

    def test_account_must_be_specified_for_sign_up(self):
        random_name = "random-sa"
        response = self.client.sign_url(
            bucket_file_path="randomPath/",
            project=self.project,
            service_account=random_name,
        )
        assert_that(response.status_code).is_equal_to(1)
        assert_that(response.output).contains(f"ERROR: (gcloud.storage.sign-url) INVALID_ARGUMENT: Invalid form of account ID {random_name}. Should be [Gaia ID |Email |Unique ID |] of the account")

    def test_bucket_file_must_be_specified_for_sign_up(self):
        random_path = "random-path/file.txt"

        response = self.client.sign_url(
            bucket_file_path=random_path,
            project=self.project,
            service_account=self.sa,
        )
        assert_that(response.status_code).is_equal_to(1)
        assert_that(response.output).contains(
            "ERROR: gcloud crashed (AttributeError): 'FileUrl' object has no attribute 'is_provider")

    def test_user_ahs_access_to_bucket(self):
        response = self.client.sign_url(
            bucket_file_path=f"gs://{self.bucket}",
            project=self.project,
            service_account=self.sa,
        )
        assert_that(response.status_code).is_equal_to(0)
        assert_that(response.output).contains("signed_url")
        url = extract_url(response.output)
        assert_that(url).is_not_empty()
        self.page.goto(url=url)
        expect(self.page.locator(selector="div span", has_text=self.bucket).first,
               "No access for bucket").to_be_visible()
        expect(self.page.locator(selector="div span", has_text=self.bucket_file_path.split("/")[-1]).first,
               "No access for bucket").to_be_visible()
