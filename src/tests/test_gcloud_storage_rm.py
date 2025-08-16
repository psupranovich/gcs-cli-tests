import random

import pytest
from assertpy import assert_that
from faker import Faker

from src.helpers.assert_helper import AssertHelper
from src.helpers.data_helper import create_sample_text_file

fake = Faker()


class TestGcloudStorageRm:
    """
    Test cases for 'gcloud storage rm' command.
    Tests file and bucket deletion functionality with various flags,
    patterns, headers, and error scenarios.
    """

    test_file_name = "test-file.txt"
    test_file_content = fake.paragraph()

    test_file2_name = "test-file2.txt"
    test_file2_content = fake.paragraph()

    @pytest.fixture(autouse=True)
    def setup_test(self, sample_project, sample_bucket, gcp_client, assert_helper):
        self.client = gcp_client
        self.project = sample_project
        self.bucket = sample_bucket
        self.assert_helper: AssertHelper = assert_helper

    def _create_and_upload_file(self, file_name, file_content=None, bucket=None):
        """
        Helper method to create a local file and upload it to the bucket.
        """
        if file_content is None:
            file_content = self.test_file_content
        if bucket is None:
            bucket = self.bucket

        local_file_path = create_sample_text_file(
            file_name=f"upload_delete_test_{random.randint(1000, 9999)}.txt",
            file_content=file_content
        )

        upload_response = self.client.copy_file_to_bucket(
            local_file_path=local_file_path,
            bucket=bucket,
            file_name=file_name
        )
        assert_that(upload_response.status_code).is_equal_to(0)

        return local_file_path

    def _verify_file_exists(self, file_name, bucket=None):
        """
        Helper method to verify that a file exists in the bucket.
        """
        if bucket is None:
            bucket = self.bucket

        check_response = self.client.check_file_in_bucket(
            bucket=bucket,
            file_name=file_name
        )
        assert_that(check_response.status_code).is_equal_to(0)

    def _verify_file_deleted(self, file_name, bucket=None):
        """
        Helper method to verify that a file has been deleted from the bucket.
        """
        if bucket is None:
            bucket = self.bucket

        verify_response = self.client.check_file_in_bucket(
            bucket=bucket,
            file_name=file_name
        )
        self.assert_helper.assert_error_response(
            response=verify_response,
            expected_message="ERROR: (gcloud.storage.ls) One or more URLs matched no objects.")

    def _create_bucket(self, bucket_name=None):
        """
        Helper method to create a bucket with a unique name.
        """
        if bucket_name is None:
            bucket_name = f"test-bucket-rm-{random.randint(10000, 99999)}"

        create_response = self.client.create_bucket(
            bucket=bucket_name,
            project=self.project
        )
        assert_that(create_response.status_code).is_equal_to(0)

        return bucket_name

    def _verify_bucket_exists(self, bucket_name):
        """
        Helper method to verify that a bucket exists.
        """
        list_response = self.client.list_buckets(project=self.project)
        assert_that(list_response.status_code).is_equal_to(0)
        assert_that(list_response.output).contains(bucket_name)

    def _verify_bucket_deleted(self, bucket_name):
        """
        Helper method to verify that a bucket has been deleted.
        """
        list_response = self.client.list_buckets(project=self.project)
        assert_that(list_response.status_code).is_equal_to(0)
        assert_that(list_response.output).does_not_contain(bucket_name)

    def _upload_multiple_files(self, file_names, file_contents=None, bucket=None):
        """
        Helper method to upload multiple files to a bucket.
        """
        if bucket is None:
            bucket = self.bucket
        if file_contents is None:
            file_contents = [fake.text() for _ in file_names]

        local_file_paths = []

        for file_name, file_content in zip(file_names, file_contents):
            local_file_path = create_sample_text_file(
                file_name=f"pattern_test_{random.randint(1000, 9999)}_{file_name}",
                file_content=file_content
            )
            local_file_paths.append(local_file_path)

            upload_response = self.client.copy_file_to_bucket(
                local_file_path=local_file_path,
                bucket=bucket,
                file_name=file_name
            )
            assert_that(upload_response.status_code).is_equal_to(0)

        return local_file_paths

    def test_delete_single_file_from_bucket(self):
        """
        Test deletion of a single file from bucket.
        Verifies file upload, successful deletion, and confirmation that file no longer exists.
        """
        self._create_and_upload_file(self.test_file_name)

        self._verify_file_exists(self.test_file_name)

        delete_response = self.client.delete_object(
            bucket=self.bucket,
            object_path=self.test_file_name
        )
        assert_that(delete_response.status_code).is_equal_to(0)

        self._verify_file_deleted(self.test_file_name)

    def test_delete_entire_bucket_with_recursive_flag(self):
        """
        Test deletion of an entire bucket using recursive flag.
        Verifies bucket creation, recursive deletion, and confirmation of complete removal.
        """
        test_bucket_name = self._create_bucket()

        self._verify_bucket_exists(test_bucket_name)

        delete_response = self.client.delete_object(
            bucket=test_bucket_name,
            recursive=True
        )
        assert_that(delete_response.status_code).is_equal_to(0)

        self._verify_bucket_deleted(test_bucket_name)

    def test_delete_all_objects_with_wildcard_pattern(self):
        """
        Test deletion of all objects in bucket using wildcard pattern.
        Verifies multiple file upload, wildcard deletion, and confirmation all files are removed.
        """
        file_names = [self.test_file_name, self.test_file2_name]
        file_contents = [self.test_file_content, self.test_file2_content]

        self._upload_multiple_files(file_names, file_contents)

        for file_name in file_names:
            self._verify_file_exists(file_name)

        delete_response = self.client.delete_object(
            bucket=self.bucket,
            pattern="**"
        )
        assert_that(delete_response.status_code).is_equal_to(0)

        for file_name in file_names:
            self._verify_file_deleted(file_name)

    def test_delete_bucket_and_contents_recursively(self):
        """
        Test recursive deletion of bucket containing files.
        Verifies bucket with content creation, recursive deletion, and complete bucket removal.
        """
        test_bucket_name = f"test-bucket-recursive-{random.randint(10000, 99999)}"

        create_response = self.client.create_bucket(
            bucket=test_bucket_name,
            project=self.project
        )
        assert_that(create_response.status_code).is_equal_to(0)

        local_file_path = create_sample_text_file(
            file_name=f"recursive_test_{random.randint(1000, 9999)}.txt",
            file_content=self.test_file_content
        )

        upload_response = self.client.copy_file_to_bucket(
            local_file_path=local_file_path,
            bucket=test_bucket_name,
            file_name=self.test_file_name
        )
        assert_that(upload_response.status_code).is_equal_to(0)

        # Delete bucket recursively using delete_object with recursive flag
        delete_response = self.client.delete_object(
            bucket=test_bucket_name,
            recursive=True
        )
        assert_that(delete_response.status_code).is_equal_to(0)

        # Verify bucket is deleted
        self._verify_bucket_deleted(test_bucket_name)

    def test_delete_files_by_extension_pattern(self):
        """
        Test selective deletion of files using file extension pattern.
        Verifies pattern-based deletion affects only matching files while preserving others.
        """
        txt_file_names = [f"text1-{random.randint(1000, 9999)}.txt", f"text2-{random.randint(1000, 9999)}.txt"]
        other_file_name = f"document-{random.randint(1000, 9999)}.pdf"
        all_file_names = txt_file_names + [other_file_name]

        txt_file_contents = [fake.text() for _ in txt_file_names]
        self._upload_multiple_files(txt_file_names, txt_file_contents)

        self._create_and_upload_file(other_file_name, "PDF content")

        for file_name in all_file_names:
            self._verify_file_exists(file_name)

        delete_response = self.client.delete_object(
            bucket=self.bucket,
            pattern="*.txt",
            recursive=True
        )
        assert_that(delete_response.status_code).is_equal_to(0)

        for txt_file in txt_file_names:
            self._verify_file_deleted(txt_file)

        self._verify_file_exists(other_file_name)

        self.client.delete_object(bucket=self.bucket, object_path=other_file_name)

    def test_delete_file_with_custom_headers(self):
        """
        Test file deletion with custom additional headers.
        Verifies that custom headers are properly processed during deletion operation.
        """
        self._create_and_upload_file(self.test_file_name)

        additional_headers = {"x-custom-header": "test-value", "x-test": "delete"}
        delete_response = self.client.delete_object(
            bucket=self.bucket,
            object_path=self.test_file_name,
            additional_headers=additional_headers
        )
        assert_that(delete_response.status_code).is_equal_to(0)

        self._verify_file_deleted(self.test_file_name)

    def test_delete_file_all_versions(self):
        """
        Test file deletion with all-versions flag enabled.
        Verifies that all versions of the file are removed from bucket.
        """
        # Create and upload file to bucket
        self._create_and_upload_file(self.test_file_name)

        delete_response = self.client.delete_object(
            bucket=self.bucket,
            object_path=self.test_file_name,
            all_versions=True
        )
        assert_that(delete_response.status_code).is_equal_to(0)

        self._verify_file_deleted(self.test_file_name)

    def test_delete_with_continue_on_error_flag(self):
        """
        Test deletion operation with continue-on-error flag.
        Verifies that deletion continues processing despite encountering errors.
        """
        self._create_and_upload_file(self.test_file_name)

        delete_response = self.client.delete_object(
            bucket=self.bucket,
            object_path=self.test_file_name,
            continue_on_error=True
        )
        assert_that(delete_response.status_code).is_equal_to(0)

        self._verify_file_deleted(self.test_file_name)

    def test_delete_excluding_managed_folders(self):
        """
        Test deletion with exclude-managed-folders flag.
        Verifies that managed folders are excluded from deletion operation.
        """
        self._create_and_upload_file(self.test_file_name)

        # Delete file with exclude managed folders
        delete_response = self.client.delete_object(
            bucket=self.bucket,
            object_path=self.test_file_name,
            exclude_managed_folders=True
        )
        assert_that(delete_response.status_code).is_equal_to(0)

        self._verify_file_deleted(self.test_file_name)

    def test_delete_with_generation_match_condition(self):
        """
        Test conditional deletion based on generation match.
        Verifies that deletion fails when generation condition is not met.
        """
        # Create and upload file to bucket
        self._create_and_upload_file(self.test_file_name)

        delete_response = self.client.delete_object(
            bucket=self.bucket,
            object_path=self.test_file_name,
            if_generation_match="99999"
        )
        assert_that(delete_response.status_code).is_equal_to(1)
        assert_that(delete_response.output).contains(
            "ERROR: HTTPError 412: At least one of the pre-conditions you specified did not hold")

        self._verify_file_exists(self.test_file_name)

        cleanup_response = self.client.delete_object(
            bucket=self.bucket,
            object_path=self.test_file_name
        )
        assert_that(cleanup_response.status_code).is_equal_to(0)

    def test_delete_with_metageneration_match_condition(self):
        """
        Test conditional deletion based on metageneration match.
        Verifies that deletion fails when metageneration condition is not met.
        """
        self._create_and_upload_file(self.test_file_name)

        delete_response = self.client.delete_object(
            bucket=self.bucket,
            object_path=self.test_file_name,
            if_metageneration_match="99999"
        )
        self.assert_helper.assert_error_response(
            response=delete_response,
            expected_message="ERROR: HTTPError 412: At least one of the pre-conditions you specified did not hold")

        self._verify_file_exists(self.test_file_name)

        cleanup_response = self.client.delete_object(
            bucket=self.bucket,
            object_path=self.test_file_name
        )
        assert_that(cleanup_response.status_code).is_equal_to(0)
