from assertpy import assert_that

from src.helpers.time_helper import get_current_epoch_time


class TestCreateBucket:
    def test_user_can_create_bucket(self, gcp_client, sample_project):
        """Smoke test for creating project with unique name"""
        unique_id = get_current_epoch_time()
        bucket_id = f"test-bucket-id-{unique_id}"
        response = gcp_client.create_bucket(
            project=sample_project, bucket=bucket_id)
        assert_that(response.status_code).is_equal_to(0)
        assert_that(response.output).contains(bucket_id)
