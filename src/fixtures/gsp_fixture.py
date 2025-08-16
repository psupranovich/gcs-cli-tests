import pytest
from assertpy import assert_that

from src.gcp_test_client.gcp_client import GcpStorage
from src.helpers.assert_helper import AssertHelper
from src.helpers.config_helper import get_config_value
from src.helpers.data_helper import extract_ids, extract_bucket_ids, create_sample_text_file, delete_temp_files


# Pytest hooks
def sign_up_preconditions(gcp_client, sample_bucket, sample_project, service_account):
    """Preconditions"""
    sa = service_account
    response = gcp_client.enable_credentials(project=sample_project)
    assert_that(response.status_code).is_equal_to(0)
    response = gcp_client.add_policy_binding(sa=sa, project_id=sample_project)
    assert_that(response.status_code).is_equal_to(0)
    response = gcp_client.allow_bucket_access(
        service_account=sa, bucket=sample_bucket, project_id=sample_project)
    assert_that(response.status_code).is_equal_to(0)


def _is_controller(config):
    return not hasattr(config, "workerinput")


def pytest_configure(config):
    """Preconditions hook"""
    if _is_controller(config):
        gcp_client = GcpStorage()
        sample_bucket = get_config_value("default_bucket")
        sample_project = get_config_value("default_project")
        service_account = f"url-signer@{sample_project}.iam.gserviceaccount.com"
        sign_up_preconditions(gcp_client, sample_bucket, sample_project, service_account)


def cleanup_buckets_after_test(gcp_client, sample_project):
    """Clean up projects after test run"""
    result = gcp_client.list_buckets(project=sample_project)
    bucket_ids = extract_bucket_ids(output_data=result.output)
    for bucket in bucket_ids:
        if "test-bucket" in bucket:
            gcp_client.delete_bucket(project=sample_project, bucket=bucket)


def cleanup_txt_files_in_sample_bucket(gcp_client, sample_bucket):
    """Cleanup .txt files in the sample bucket and .txt files in the fixtures folder at the end of the session."""
    gcp_client.delete_object(bucket=sample_bucket, pattern="*.txt")
    delete_temp_files()


def pytest_unconfigure(config):
    """Teardown hook"""
    if _is_controller(config):
        gcp_client = GcpStorage()
        sample_project = get_config_value("default_project")
        cleanup_buckets_after_test(gcp_client, sample_project)
        cleanup_txt_files_in_sample_bucket(gcp_client, sample_project)


# Pytest scope session fixtures

@pytest.fixture(scope="session")
def sample_project(gcp_client):
    """Fixture to ensure a sample project exists and return its ID."""
    project_id = get_config_value("default_project")

    result = gcp_client.list_gcp_projects()
    project_ids = extract_ids(result.output)

    if project_id in project_ids:
        return project_id
    gcp_client.create_gcp_project(project_id=project_id, name=project_id)
    return project_id


@pytest.fixture(scope="session")
def sample_bucket(gcp_client, sample_project):
    bucket_id = get_config_value("default_bucket")
    result = gcp_client.list_buckets(project=sample_project)
    bucket_ids = extract_bucket_ids(output_data=result.output)
    if bucket_id in bucket_ids:
        return bucket_id
    gcp_client.create_bucket(
        project=sample_project, bucket=bucket_id)
    return bucket_id


@pytest.fixture(scope="session")
def sample_file_to_bucket(gcp_client, sample_bucket):
    def _upload_file(file_name, file_content=None):
        result = gcp_client.check_file_in_bucket(bucket=sample_bucket, file_name=file_name)
        if result.status_code != 0:
            local_file_path = create_sample_text_file(file_name=file_name, file_content=file_content)
            response = gcp_client.copy_file_to_bucket(
                bucket=sample_bucket,
                local_file_path=local_file_path,
                file_name=file_name)
            assert_that(response.status_code).is_equal_to(0)
        return f"gs://{sample_bucket}/{file_name}"

    return _upload_file


@pytest.fixture(scope="session")
def service_account(sample_project):
    return f"url-signer@{sample_project}.iam.gserviceaccount.com"

# Other fixtures
@pytest.fixture
def assert_helper() -> AssertHelper:
    return AssertHelper()
