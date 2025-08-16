import time

import pytest
from assertpy import assert_that
from faker import Faker
from playwright.sync_api import Page

from src.helpers.assert_helper import AssertHelper
from src.helpers.data_helper import extract_url
from src.helpers.signed_url_page import SignedUrlPage
from src.helpers.time_helper import get_current_epoch_time
fake = Faker()

class TestSignUrlCommand:
    """
    Test cases for 'gcloud storage sign-url' command.
    Tests signed URL generation functionality with various parameters,
    time-based access control, and error scenarios.
    """
    file_name = f"file-{get_current_epoch_time()}.txt"

    @pytest.fixture(autouse=True)
    def setup_test(self, sample_project, sample_bucket, service_account, gcp_client, page,
                   assert_helper):
        self.client = gcp_client
        self.project = sample_project
        self.bucket = sample_bucket
        # self.bucket_file_path = sample_file_to_bucket(file_name=self.file_name)
        self.sa = service_account
        self.page: Page = page
        self.signed_url_page = SignedUrlPage(page)
        self.assert_helper: AssertHelper = assert_helper

    @staticmethod
    def _assert_sign_up_url(response):
        assert_that(response.status_code).is_equal_to(0)
        assert_that(response.output).contains("signed_url")
        url = extract_url(response.output)
        return url


    def test_generate_signed_url_for_file_access(self, sample_file_to_bucket):
        """
        Test generation of signed URL for file access.
        Verifies that signed URL is generated and provides valid file access.
        """
        file_name = f"file-{get_current_epoch_time()}.txt"
        bucket_file_path = sample_file_to_bucket(file_name=file_name)
        response = self.client.sign_url(
            bucket_file_path=bucket_file_path,
            project=self.project,
            service_account=self.sa,
        )
        url = self._assert_sign_up_url(response=response)
        assert_that(url).is_not_empty()
        self.signed_url_page.navigate_to_signed_url(url)
        self.signed_url_page.assert_file_access_granted()

    def test_signed_url_expires_after_duration(self, sample_file_to_bucket):
        """
        Test time-limited access with signed URL expiration.
        Verifies that signed URL becomes invalid after specified duration.
        """
        expected_duration = 5
        file_name = f"file-{get_current_epoch_time()}.txt"
        bucket_file_path = sample_file_to_bucket(file_name=file_name)
        response = self.client.sign_url(
            bucket_file_path=bucket_file_path,
            project=self.project,
            service_account=self.sa,
            duration=expected_duration
        )
        url = self._assert_sign_up_url(response=response)

        assert_that(url).is_not_empty()
        time.sleep(expected_duration)

        self.signed_url_page.navigate_to_signed_url(url)
        self.signed_url_page.assert_token_expired()

    def test_generate_signed_url_for_bucket_access(self, sample_file_to_bucket):
        """
        Test generation of signed URL for bucket-level access.
        Verifies that signed URL provides access to bucket and its contents.
        """
        file_name = f"file-{get_current_epoch_time()}.txt"
        bucket_file_path = sample_file_to_bucket(file_name=file_name)

        response = self.client.sign_url(
            bucket_file_path=f"gs://{self.bucket}",
            project=self.project,
            service_account=self.sa,
        )
        url = self._assert_sign_up_url(response=response)

        assert_that(url).is_not_empty()
        self.signed_url_page.navigate_to_signed_url(url)

        filename = bucket_file_path.split("/")[-1]
        self.signed_url_page.assert_bucket_and_file_access(self.bucket, filename)

    def test_invalid_service_account_returns_error(self, sample_file_to_bucket):
        """
        Test signed URL generation with invalid service account.
        Verifies that appropriate error is returned for malformed account ID.
        """
        random_name = "random-sa"
        file_name = f"file-{get_current_epoch_time()}.txt"
        bucket_file_path = sample_file_to_bucket(file_name=file_name)

        response = self.client.sign_url(
            bucket_file_path=bucket_file_path,
            project=self.project,
            service_account=random_name,
        )
        self.assert_helper.assert_error_response(
            response=response,
            expected_message=f"ERROR: (gcloud.storage.sign-url) INVALID_ARGUMENT: Invalid form of account ID {random_name}. Should be [Gaia ID |Email |Unique ID |] of the account")

    def test_invalid_file_path_returns_error(self):
        """
        Test signed URL generation with invalid file path.
        Verifies that appropriate error is returned for malformed file path.
        """
        random_path = "random-path/file.txt"

        response = self.client.sign_url(
            bucket_file_path=random_path,
            project=self.project,
            service_account=self.sa,
        )
        self.assert_helper.assert_error_response(
            response=response,
            expected_message="ERROR: gcloud crashed (AttributeError): 'FileUrl' object has no attribute 'is_provider")
