import random

import pytest
from assertpy import assert_that

from faker import Faker

fake = Faker()


class TestCreateFolder:
    file1_name = "file1.txt"
    file2_name = "file2.txt"

    file_1_content = fake.paragraph()
    file_2_content = fake.paragraph()

    @pytest.fixture(autouse=True)
    def setup_test(self, sample_project, sample_bucket, sample_file_to_bucket, sign_up_preconditions, gcp_client):
        self.client = gcp_client
        self.project = sample_project
        self.bucket = sample_bucket
        self.bucket_file_1 = sample_file_to_bucket(file_name=self.file1_name, file_content=self.file_1_content)
        self.bucket_file_2 = sample_file_to_bucket(file_name=self.file2_name, file_content=self.file_2_content)
        self.sa = sign_up_preconditions

    def test_read_bucket_file(self):
        """
        gcloud storage cp url
        assert file name and content
        """
        response = self.client.cat_file_from_url(
            urls=[self.bucket_file_1],
        )
        assert_that(response.status_code).is_equal_to(0)
        assert_that(response.output).contains(self.file_1_content)

    def test_read_bucket_files(self):
        """
        gcloud storage cat gs://bucket/*.txt
        assert files from setup exists here
        """
        pattern = f"gs://{self.bucket}/*.txt"
        response = self.client.cat_file_from_url(
            urls=[pattern],
        )
        assert_that(response.status_code).is_equal_to(0)
        assert_that(response.output).contains(self.file_1_content)
        assert_that(response.output).contains(self.file_2_content)

    def test_read_file_short_header(self):
        """
        The following command outputs a short header describing file.txt, along with its contents:

        gcloud storage cat -d gs://my-bucket/file.txt
        assert files from setup exists here
        """
        response = self.client.cat_file_from_url(
            urls=[self.bucket_file_1],
            display_url=True
        )
        assert_that(response.status_code).is_equal_to(0)
        assert_that(response.output).contains(self.file_1_content)
        assert_that(response.output).contains(self.bucket_file_1)
       
    def test_read_file_specific_bytes(self):
        file_bytes = self.file_1_content.encode("utf-8")
        start = 1
        end = 30
        expected_bytes = file_bytes[start:end]
        expected_content = expected_bytes.decode("utf-8", errors="ignore")

        response = self.client.cat_file_from_url(
            urls=[self.bucket_file_1],
            range_value=f"{start}-{end}"
        )
        assert_that(response.status_code).is_equal_to(0)
        assert_that(response.output).contains(expected_content)


    def test_read_file_last_n_bytes(self):
        file_bytes = self.file_1_content.encode("utf-8")
        n = 5
        expected_bytes = file_bytes[-n:]
        expected_content = expected_bytes.decode("utf-8", errors="ignore")

        response = self.client.cat_file_from_url(
            urls=[self.bucket_file_1],
            range_value=f"-{n}"
        )
        assert_that(response.status_code).is_equal_to(0)
        assert_that(response.output).contains(expected_content)

    def test_error_when_user_cat_non_existing_file(self):
        response = self.client.cat_file_from_url(
            urls=[f"{self.bucket}/random_file{random.randint(1000, 2000)}.txt"]
        )
        assert_that(response.status_code).is_equal_to(1)
        assert_that(response.output).contains("ERROR: (gcloud.storage.cat) cat only works for valid cloud URLs")

    def test_user_tries_cat_file_with_invalid_url(self):
        response = self.client.cat_file_from_url(
            urls=["invalid_url"],
        )
        assert_that(response.status_code).is_equal_to(1)
        assert_that(response.output).contains("ERROR: (gcloud.storage.cat) cat only works for valid cloud URLs")

    