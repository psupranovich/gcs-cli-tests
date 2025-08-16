import random

import pytest
from assertpy import assert_that
from faker import Faker

from src.helpers.assert_helper import AssertHelper

fake = Faker()


class TestReadBucketFiles:
    """
    Test cases for 'gcloud storage cat' command.
    Tests reading file contents from buckets with various options including
    pattern matching, byte ranges, headers, and error scenarios.
    """
    file1_name = "file1.txt"
    file2_name = "file2.txt"

    file_1_content = fake.paragraph()
    file_2_content = fake.paragraph()

    @pytest.fixture(autouse=True)
    def setup_test(self, sample_project, sample_bucket, sample_file_to_bucket, sign_up_preconditions, gcp_client,
                   assert_helper):
        self.client = gcp_client
        self.project = sample_project
        self.bucket = sample_bucket
        self.bucket_file_1 = sample_file_to_bucket(file_name=self.file1_name, file_content=self.file_1_content)
        self.bucket_file_2 = sample_file_to_bucket(file_name=self.file2_name, file_content=self.file_2_content)
        self.sa = sign_up_preconditions
        self.assert_helper: AssertHelper = assert_helper

    @staticmethod
    def _assert_successful_response(response, expected_contents):
        """Helper method to assert successful response with expected content(s)."""
        assert_that(response.status_code).is_equal_to(0)
        if isinstance(expected_contents, list):
            for content in expected_contents:
                assert_that(response.output).contains(content)
        else:
            assert_that(response.output).contains(expected_contents)

    @staticmethod
    def _get_expected_bytes_content(content, start=None, end=None):
        """Helper method to extract expected content from bytes range."""
        file_bytes = content.encode("utf-8")
        if start is not None and end is not None:
            expected_bytes = file_bytes[start:end]
        elif end is not None:  # end is negative (last n bytes)
            expected_bytes = file_bytes[end:]
        else:
            expected_bytes = file_bytes
        return expected_bytes.decode("utf-8", errors="ignore")

    def _cat_file_and_assert_success(self, urls, expected_contents, **kwargs):
        """Helper method to call cat_file_from_url and assert successful response."""
        response = self.client.cat_file_from_url(urls=urls, **kwargs)
        self._assert_successful_response(response, expected_contents)
        return response

    def test_read_single_file_from_bucket(self):
        """
        Test reading a single file from bucket using cat command.
        Verifies that file content is correctly retrieved and displayed.
        """
        self._cat_file_and_assert_success([self.bucket_file_1], self.file_1_content)

    def test_read_multiple_files_with_pattern(self):
        """
        Test reading multiple files using wildcard pattern.
        Verifies that all matching files are read and their contents are displayed.
        """
        pattern = f"gs://{self.bucket}/*.txt"
        self._cat_file_and_assert_success([pattern], [self.file_1_content, self.file_2_content])

    def test_read_file_with_display_url_header(self):
        """
        Test reading file with display URL header enabled.
        Verifies that file content is shown along with URL header information.
        """
        self._cat_file_and_assert_success(
            [self.bucket_file_1],
            [self.file_1_content, self.bucket_file_1],
            display_url=True
        )

    def test_read_file_specific_byte_range(self):
        """
        Test reading specific byte range from file.
        Verifies that only the specified byte range is returned from the file content.
        """
        start = 1
        end = 30
        expected_content = self._get_expected_bytes_content(self.file_1_content, start, end)

        self._cat_file_and_assert_success(
            [self.bucket_file_1],
            expected_content,
            range_value=f"{start}-{end}"
        )

    def test_read_file_last_n_bytes(self):
        """
        Test reading the last N bytes from file.
        Verifies that only the final N bytes of the file are returned.
        """
        n = 5
        expected_content = self._get_expected_bytes_content(self.file_1_content, end=-n)

        self._cat_file_and_assert_success(
            [self.bucket_file_1],
            expected_content,
            range_value=f"-{n}"
        )

    def test_read_nonexistent_file_returns_error(self):
        """
        Test reading a non-existent file from bucket.
        Verifies that appropriate error message is returned for invalid file path.
        """
        response = self.client.cat_file_from_url(
            urls=[f"{self.bucket}/random_file{random.randint(1000, 2000)}.txt"]
        )
        self.assert_helper.assert_error_response(
            response=response,
            expected_message="ERROR: (gcloud.storage.cat) cat only works for valid cloud URLs")

    def test_read_file_with_invalid_url_returns_error(self):
        """
        Test reading file with invalid URL format.
        Verifies that appropriate error message is returned for malformed URLs.
        """
        response = self.client.cat_file_from_url(
            urls=["invalid_url"],
        )
        self.assert_helper.assert_error_response(
            response=response,
            expected_message="ERROR: (gcloud.storage.cat) cat only works for valid cloud URLs")
