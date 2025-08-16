import pytest
from assertpy import assert_that

from src.helpers.data_helper import extract_ids, extract_bucket_ids, create_sample_text_file


@pytest.fixture(scope="function", autouse=True)
def cleanup_buckets_after_test(gcp_client, sample_project):
    """Clean up projects after test run"""
    yield
    result = gcp_client.list_buckets(project=sample_project)
    bucket_ids = extract_bucket_ids(output_data=result.output)
    for bucket in bucket_ids:
        if "test-bucket" in bucket:
            gcp_client.delete_bucket(project=sample_project, bucket=bucket)


@pytest.fixture(scope="session")
def sample_project(gcp_client):
    """Fixture to ensure a sample project exists and return its ID."""
    project_id = "test-gcp-id-1755265919"

    # List existing projects
    result = gcp_client.list_gcp_projects()
    project_ids = extract_ids(result.output)

    # Check if the project already exists
    if project_id in project_ids:
        return project_id
    # Create the project if it does not exist
    gcp_client.create_gcp_project(project_id=project_id, name=project_id)
    return project_id


@pytest.fixture(scope="session")
def sample_bucket(gcp_client, sample_project):
    bucket_id = "sample-bucket-id"
    result = gcp_client.list_buckets(project=sample_project)
    bucket_ids = extract_bucket_ids(output_data=result.output)
    if bucket_id in bucket_ids:
        return bucket_id
    gcp_client.create_bucket(
        project=sample_project, bucket=bucket_id)
    return bucket_id


@pytest.fixture(scope="session")
def sample_file_to_bucket(gcp_client, sample_bucket):
    result = gcp_client.check_file_in_bucket(bucket=sample_bucket, file_name="hello.txt")
    if result.status_code != 0:
        local_file_path = create_sample_text_file(file_name="hello.txt")
        response = gcp_client.copy_file_to_bucket(
            bucket=sample_bucket,
            local_file_path=local_file_path,
            file_name="hello.txt")
        assert_that(response.status_code).is_equal_to(0)
    return f"gs://{sample_bucket}/hello.txt"


@pytest.fixture(scope="session")
def sign_up_preconditions(gcp_client, sample_bucket, sample_project,sample_file_to_bucket):
    """Preconditions"""
    response = gcp_client.enable_credentials(project=sample_project)
    assert_that(response.status_code).is_equal_to(0)
    response, sa = gcp_client.add_policy_binding(project_id=sample_project)
    assert_that(response.status_code).is_equal_to(0)
    response = gcp_client.allow_bucket_access(
        service_account=sa, bucket=sample_bucket, project_id=sample_project)
    assert_that(response.status_code).is_equal_to(0)
    response = gcp_client.allow_file_access(bucket=sample_bucket, project_id=sample_project)
    assert_that(response.status_code).is_equal_to(0)
    return sa


# TODO add fixture to delete files in bucket at the end







