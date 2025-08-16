import random

import pytest
from assertpy import assert_that
from faker import Faker

from src.helpers.data_helper import create_sample_text_file

fake = Faker()


class TestGcloudStorageRm:
    """Test cases for gcloud storage rm command with various options and scenarios"""

    test_file_name = "test-file.txt"
    test_file_content = fake.paragraph()
    
    test_file2_name = "test-file2.txt"
    test_file2_content = fake.paragraph()

    @pytest.fixture(autouse=True)
    def setup_test(self, sample_project, sample_bucket, gcp_client):
        self.client = gcp_client
        self.project = sample_project
        self.bucket = sample_bucket

    def test_upload_file_delete_file_verify_deleted(self):
        """
        Test uploading a file, deleting it, and verifying it's deleted
        """
        # Create file for upload
        local_file_path = create_sample_text_file(
            file_name=f"upload_delete_test_{random.randint(1000, 9999)}.txt",
            file_content=self.test_file_content
        )

        # Upload file
        upload_response = self.client.copy_file_to_bucket(
            local_file_path=local_file_path,
            bucket=self.bucket,
            file_name=self.test_file_name
        )
        assert_that(upload_response.status_code).is_equal_to(0)

        # Verify file exists
        check_response = self.client.check_file_in_bucket(
            bucket=self.bucket,
            file_name=self.test_file_name
        )
        assert_that(check_response.status_code).is_equal_to(0)

        # Delete file using delete_object method
        delete_response = self.client.delete_object(
            bucket=self.bucket,
            object_path=self.test_file_name
        )
        assert_that(delete_response.status_code).is_equal_to(0)

        # Verify file is deleted
        verify_response = self.client.check_file_in_bucket(
            bucket=self.bucket,
            file_name=self.test_file_name
        )
        assert_that(verify_response.status_code).is_equal_to(1)
        assert_that(verify_response.output).contains("ERROR: (gcloud.storage.ls) One or more URLs matched no objects.")

    def test_create_bucket_delete_bucket_verify_deleted(self):
        """
        Test creating a bucket, deleting it, and verifying it's deleted
        """
        # Create a unique bucket name
        test_bucket_name = f"test-bucket-rm-{random.randint(10000, 99999)}"
        
        # Create bucket
        create_response = self.client.create_bucket(
            bucket=test_bucket_name,
            project=self.project
        )
        assert_that(create_response.status_code).is_equal_to(0)

        # Verify bucket exists
        list_response = self.client.list_buckets(project=self.project)
        assert_that(list_response.status_code).is_equal_to(0)
        assert_that(list_response.output).contains(test_bucket_name)

        # Delete bucket using delete_object with recursive flag
        delete_response = self.client.delete_object(
            bucket=test_bucket_name,
            recursive=True
        )
        assert_that(delete_response.status_code).is_equal_to(0)

        # Verify bucket is deleted
        list_response_after = self.client.list_buckets(project=self.project)
        assert_that(list_response_after.status_code).is_equal_to(0)
        assert_that(list_response_after.output).does_not_contain(test_bucket_name)

    def test_create_multiple_files_delete_all_objects_with_wildcard(self):
        """
        Test creating 2 files in bucket and delete all objects using gs://bucket/**
        """
        file_names = [self.test_file_name, self.test_file2_name]
        file_contents = [self.test_file_content, self.test_file2_content]

        # Upload multiple files
        for file_name, file_content in zip(file_names, file_contents):
            local_file_path = create_sample_text_file(
                file_name=f"wildcard_test_{random.randint(1000, 9999)}_{file_name}",
                file_content=file_content
            )
            
            upload_response = self.client.copy_file_to_bucket(
                local_file_path=local_file_path,
                bucket=self.bucket,
                file_name=file_name
            )
            assert_that(upload_response.status_code).is_equal_to(0)

        # Verify both files exist
        for file_name in file_names:
            check_response = self.client.check_file_in_bucket(
                bucket=self.bucket,
                file_name=file_name
            )
            assert_that(check_response.status_code).is_equal_to(0)

        # Delete all objects using ** pattern
        delete_response = self.client.delete_object(
            bucket=self.bucket,
            pattern="**"
        )
        assert_that(delete_response.status_code).is_equal_to(0)

        # Verify all files are deleted
        for file_name in file_names:
            verify_response = self.client.check_file_in_bucket(
                bucket=self.bucket,
                file_name=file_name
            )
            assert_that(verify_response.status_code).is_equal_to(1)
            assert_that(verify_response.output).contains(
                "ERROR: (gcloud.storage.ls) One or more URLs matched no objects.")

    def test_delete_bucket_recursive(self):
        """
        Test deleting bucket and all contents using --recursive flag
        """
        # Create a unique bucket name
        test_bucket_name = f"test-bucket-recursive-{random.randint(10000, 99999)}"
        
        # Create bucket
        create_response = self.client.create_bucket(
            bucket=test_bucket_name,
            project=self.project
        )
        assert_that(create_response.status_code).is_equal_to(0)

        # Create and upload a file to the bucket
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
        list_response = self.client.list_buckets(project=self.project)
        assert_that(list_response.status_code).is_equal_to(0)
        assert_that(list_response.output).does_not_contain(test_bucket_name)

    def test_delete_txt_files_with_pattern_recursive(self):
        """
        Test deleting text files using pattern gs://bucket/*.txt with recursive flag
        """
        txt_file_names = [f"text1-{random.randint(1000, 9999)}.txt", f"text2-{random.randint(1000, 9999)}.txt"]
        other_file_name = f"document-{random.randint(1000, 9999)}.pdf"
        all_file_names = txt_file_names + [other_file_name]

        # Upload txt files
        for file_name in txt_file_names:
            local_file_path = create_sample_text_file(
                file_name=f"pattern_test_{random.randint(1000, 9999)}_{file_name}",
                file_content=fake.text()
            )
            
            upload_response = self.client.copy_file_to_bucket(
                local_file_path=local_file_path,
                bucket=self.bucket,
                file_name=file_name
            )
            assert_that(upload_response.status_code).is_equal_to(0)

        # Upload non-txt file (create as .txt but upload with .pdf extension)
        local_file_path = create_sample_text_file(
            file_name=f"pattern_test_{random.randint(1000, 9999)}_pdf.txt",
            file_content="PDF content"
        )
        
        upload_response = self.client.copy_file_to_bucket(
            local_file_path=local_file_path,
            bucket=self.bucket,
            file_name=other_file_name
        )
        assert_that(upload_response.status_code).is_equal_to(0)

        # Verify all files exist
        for file_name in all_file_names:
            check_response = self.client.check_file_in_bucket(
                bucket=self.bucket,
                file_name=file_name
            )
            assert_that(check_response.status_code).is_equal_to(0)

        # Delete only .txt files using pattern
        delete_response = self.client.delete_object(
            bucket=self.bucket,
            pattern="*.txt",
            recursive=True
        )
        assert_that(delete_response.status_code).is_equal_to(0)

        # Verify txt files are deleted
        for txt_file in txt_file_names:
            verify_response = self.client.check_file_in_bucket(
                bucket=self.bucket,
                file_name=txt_file
            )
            assert_that(verify_response.status_code).is_equal_to(1)
            assert_that(verify_response.output).contains("ERROR: (gcloud.storage.ls) One or more URLs matched no objects.")

        # Verify non-txt file still exists
        check_response = self.client.check_file_in_bucket(
            bucket=self.bucket,
            file_name=other_file_name
        )
        assert_that(check_response.status_code).is_equal_to(0)

        # Clean up remaining files
        self.client.delete_object(bucket=self.bucket, object_path=other_file_name)

    def test_delete_with_additional_headers(self):
        """
        Test deleting a file with additional headers
        """
        # Create and upload file to bucket
        local_file_path = create_sample_text_file(
            file_name=f"headers_test_{random.randint(1000, 9999)}.txt",
            file_content=self.test_file_content
        )

        upload_response = self.client.copy_file_to_bucket(
            local_file_path=local_file_path,
            bucket=self.bucket,
            file_name=self.test_file_name
        )
        assert_that(upload_response.status_code).is_equal_to(0)

        # Delete file with additional headers
        additional_headers = {"x-custom-header": "test-value", "x-test": "delete"}
        delete_response = self.client.delete_object(
            bucket=self.bucket,
            object_path=self.test_file_name,
            additional_headers=additional_headers
        )
        assert_that(delete_response.status_code).is_equal_to(0)

        # Verify file is deleted
        verify_response = self.client.check_file_in_bucket(
            bucket=self.bucket,
            file_name=self.test_file_name
        )
        assert_that(verify_response.status_code).is_equal_to(1)
        assert_that(verify_response.output).contains("ERROR: (gcloud.storage.ls) One or more URLs matched no objects.")


    def test_delete_with_all_versions_flag(self):
        """
        Test deleting file with --all-versions flag
        """
        # Create and upload file to bucket
        local_file_path = create_sample_text_file(
            file_name=f"versions_test_{random.randint(1000, 9999)}.txt",
            file_content=self.test_file_content
        )

        upload_response = self.client.copy_file_to_bucket(
            local_file_path=local_file_path,
            bucket=self.bucket,
            file_name=self.test_file_name
        )
        assert_that(upload_response.status_code).is_equal_to(0)

        # Delete file with all versions
        delete_response = self.client.delete_object(
            bucket=self.bucket,
            object_path=self.test_file_name,
            all_versions=True
        )
        assert_that(delete_response.status_code).is_equal_to(0)

        # Verify file is deleted
        verify_response = self.client.check_file_in_bucket(
            bucket=self.bucket,
            file_name=self.test_file_name
        )
        assert_that(verify_response.status_code).is_equal_to(1)
        assert_that(verify_response.output).contains("ERROR: (gcloud.storage.ls) One or more URLs matched no objects.")

    def test_delete_with_continue_on_error_flag(self):
        """
        Test deleting multiple files with --continue-on-error flag (some files don't exist)
        """
        # Create and upload one file to bucket
        local_file_path = create_sample_text_file(
            file_name=f"continue_error_test_{random.randint(1000, 9999)}.txt",
            file_content=self.test_file_content
        )

        upload_response = self.client.copy_file_to_bucket(
            local_file_path=local_file_path,
            bucket=self.bucket,
            file_name=self.test_file_name
        )
        assert_that(upload_response.status_code).is_equal_to(0)

        # Try to delete existing file with continue on error
        delete_response = self.client.delete_object(
            bucket=self.bucket,
            object_path=self.test_file_name,
            continue_on_error=True
        )
        assert_that(delete_response.status_code).is_equal_to(0)

        # Verify file is deleted
        verify_response = self.client.check_file_in_bucket(
            bucket=self.bucket,
            file_name=self.test_file_name
        )
        assert_that(verify_response.status_code).is_equal_to(1)
        assert_that(verify_response.output).contains("ERROR: (gcloud.storage.ls) One or more URLs matched no objects.")

    def test_delete_with_exclude_managed_folders_flag(self):
        """
        Test deleting with --exclude-managed-folders flag
        """
        # Create and upload file to bucket
        local_file_path = create_sample_text_file(
            file_name=f"exclude_folders_test_{random.randint(1000, 9999)}.txt",
            file_content=self.test_file_content
        )

        upload_response = self.client.copy_file_to_bucket(
            local_file_path=local_file_path,
            bucket=self.bucket,
            file_name=self.test_file_name
        )
        assert_that(upload_response.status_code).is_equal_to(0)

        # Delete file with exclude managed folders
        delete_response = self.client.delete_object(
            bucket=self.bucket,
            object_path=self.test_file_name,
            exclude_managed_folders=True
        )
        assert_that(delete_response.status_code).is_equal_to(0)

        # Verify file is deleted
        verify_response = self.client.check_file_in_bucket(
            bucket=self.bucket,
            file_name=self.test_file_name
        )
        assert_that(verify_response.status_code).is_equal_to(1)
        assert_that(verify_response.output).contains("ERROR: (gcloud.storage.ls) One or more URLs matched no objects.")

    def test_delete_with_generation_match(self):
        """
        Test deleting file with --if-generation-match condition
        """
        # Create and upload file to bucket
        local_file_path = create_sample_text_file(
            file_name=f"generation_test_{random.randint(1000, 9999)}.txt",
            file_content=self.test_file_content
        )

        upload_response = self.client.copy_file_to_bucket(
            local_file_path=local_file_path,
            bucket=self.bucket,
            file_name=self.test_file_name
        )
        assert_that(upload_response.status_code).is_equal_to(0)

        # Try to delete with a fake generation (should fail)
        delete_response = self.client.delete_object(
            bucket=self.bucket,
            object_path=self.test_file_name,
            if_generation_match="99999"
        )
        # This should fail due to generation mismatch
        assert_that(delete_response.status_code).is_not_equal_to(1)
        assert_that(delete_response.output).contains("ERROR: HTTPError 412: At least one of the pre-conditions you specified did not hold")

        # Verify file still exists
        verify_response = self.client.check_file_in_bucket(
            bucket=self.bucket,
            file_name=self.test_file_name
        )
        assert_that(verify_response.status_code).is_equal_to(0)

        # Clean up - delete without generation match
        cleanup_response = self.client.delete_object(
            bucket=self.bucket,
            object_path=self.test_file_name
        )
        assert_that(cleanup_response.status_code).is_equal_to(0)

    def test_delete_with_metageneration_match(self):
        """
        Test deleting file with --if-metageneration-match condition
        """
        # Create and upload file to bucket
        local_file_path = create_sample_text_file(
            file_name=f"metageneration_test_{random.randint(1000, 9999)}.txt",
            file_content=self.test_file_content
        )

        upload_response = self.client.copy_file_to_bucket(
            local_file_path=local_file_path,
            bucket=self.bucket,
            file_name=self.test_file_name
        )
        assert_that(upload_response.status_code).is_equal_to(0)

        # Try to delete with a fake metageneration (should fail)
        delete_response = self.client.delete_object(
            bucket=self.bucket,
            object_path=self.test_file_name,
            if_metageneration_match="99999"
        )

        # This should fail due to metageneration mismatch
        assert_that(delete_response.status_code).is_not_equal_to(1)
        assert_that(delete_response.output).contains(
            "ERROR: HTTPError 412: At least one of the pre-conditions you specified did not hold")

        # Verify file still exists
        verify_response = self.client.check_file_in_bucket(
            bucket=self.bucket,
            file_name=self.test_file_name
        )
        assert_that(verify_response.status_code).is_equal_to(0)

        # Clean up - delete without metageneration match
        cleanup_response = self.client.delete_object(
            bucket=self.bucket,
            object_path=self.test_file_name
        )
        assert_that(cleanup_response.status_code).is_equal_to(0)
