import json

import pytest
from assertpy import assert_that

from src.helpers.assert_helper import AssertHelper


class TestDescribeBucketStorage:
    """
    Test cases for 'gcloud storage buckets describe' command.
    Tests bucket description functionality with various formatting options,
    headers, and error scenarios.
    """

    @pytest.fixture(autouse=True)
    def setup_test(
            self, sample_project, sample_bucket, sample_file_to_bucket, sign_up_preconditions, gcp_client,
            assert_helper):
        self.client = gcp_client
        self.project = sample_project
        self.bucket = sample_bucket
        self.sa = sign_up_preconditions
        self.assert_helper: AssertHelper = assert_helper

    @property
    def bucket_url(self):
        """Helper property to construct the bucket URL."""
        return f"gs://{self.bucket}"

    def assert_successful_response(self, response):
        """Helper method to assert successful response with standard checks."""
        assert_that(response.status_code).is_equal_to(0)
        assert_that(response.output).contains(self.bucket)

    def describe_bucket_basic(self, **kwargs):
        """Helper method to call describe_bucket with default bucket URL and additional parameters."""
        return self.client.describe_bucket(bucket_url=self.bucket_url, **kwargs)

    def test_describe_bucket_basic_functionality(self):
        """
        Test basic bucket description functionality with default settings.
        Verifies successful response and bucket name presence in output.
        """
        response = self.describe_bucket_basic()
        self.assert_successful_response(response)

    def test_describe_bucket_with_json_name_filter(self):
        """
        Test bucket description with JSON format filtering to return only the 'name' field.
        Verifies that response contains only the specified field in valid JSON format.
        """
        response = self.describe_bucket_basic(format="json(name)")
        assert_that(response.status_code).is_equal_to(0)
        assert_that(json.loads(response.output)).is_equal_to({"name": self.bucket})

    def test_describe_bucket_with_additional_headers(self):
        """
        Test bucket description with custom additional headers.
        Verifies that additional headers are properly processed and don't affect functionality.
        """
        additional_headers = {"header1": "value1", "header2": "value2"}
        response = self.describe_bucket_basic(additional_headers=additional_headers)
        self.assert_successful_response(response)

    def test_describe_bucket_with_raw_format(self):
        """
        Test bucket description with raw output format.
        Verifies that raw format returns unprocessed output while maintaining functionality.
        """
        response = self.describe_bucket_basic(raw=True)
        self.assert_successful_response(response)

    def test_describe_nonexistent_bucket_returns_error(self):
        """
        Test bucket description for a non-existent bucket.
        Verifies that appropriate 404 error is returned with expected error message.
        """
        invalid_bucket_url = "gs://non-existing-bucket"
        response = self.client.describe_bucket(
            bucket_url=invalid_bucket_url
        )
        self.assert_helper.assert_error_response(
            response=response,
            expected_message=f"ERROR: (gcloud.storage.buckets.describe) {invalid_bucket_url} not found: 404.")
