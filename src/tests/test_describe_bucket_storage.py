import json

import pytest
from assertpy import assert_that


class TestCDescribeBucket:


    @pytest.fixture(autouse=True)
    def setup_test(self, sample_project, sample_bucket, sample_file_to_bucket, sign_up_preconditions, gcp_client):
        self.client = gcp_client
        self.project = sample_project
        self.bucket = sample_bucket
        self.sa = sign_up_preconditions

    def test_describe_bucket(self):
        """
        Test describing a bucket using gcloud storage buckets describe
        """
        response = self.client.describe_bucket(
            bucket_url=f"gs://{self.bucket}",
        )
        assert_that(response.status_code).is_equal_to(0)
        assert_that(response.output).contains(self.bucket)

    def test_describe_bucket_name_only(self):
        """
        Test describing a bucket with JSON formatting, only returning the 'name' key
        """
        response = self.client.describe_bucket(
            bucket_url=f"gs://{self.bucket}",
            format="json(name)"
        )
        assert_that(response.status_code).is_equal_to(0)
        assert_that(json.loads(response.output)).is_equal_to({"name": self.bucket})


    def test_describe_bucket_supports_custom_additional_headers(self):
        """
        Test describing a bucket with additional headers
        """
        additional_headers = {"header1": "value1", "header2": "value2"}
        response = self.client.describe_bucket(
            bucket_url=f"gs://{self.bucket}",
            additional_headers=additional_headers
        )
        assert_that(response.status_code).is_equal_to(0)
        assert_that(response.output).contains(self.bucket)


    def test_describe_bucket_raw_output(self):
        """
        Test describing a bucket with raw output
        """
        response = self.client.describe_bucket(
            bucket_url=f"gs://{self.bucket}",
            raw=True
        )
        assert_that(response.status_code).is_equal_to(0)
        assert_that(response.output).contains(self.bucket)

    def test_describe_non_existing_bucket(self):
        """
        Test describing a non-existing bucket
        """
        invalid_bucket_url = "gs://non-existing-bucket"
        response = self.client.describe_bucket(
            bucket_url=invalid_bucket_url
        )
        assert_that(response.status_code).is_equal_to(1)
        assert_that(response.output).contains(
            f"ERROR: (gcloud.storage.buckets.describe) {invalid_bucket_url} not found: 404.\n")

