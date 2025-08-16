from typing import Optional

from src.helpers.base_helpers import run_subprocess
from src.helpers.data_helper import GCPCommandResponse


class GcpStorage:

    def create_gcp_project(
            self,
            project_id: str,
            name: Optional[str] = None,
            organization_id: Optional[str] = None,
            folder_id: Optional[str] = None,
    ) -> GCPCommandResponse:

        cmd = ["gcloud", "projects", "create", project_id]
        if name:
            cmd += ["--name", name]
        if organization_id:
            cmd += ["--organization", organization_id]
        if folder_id:
            cmd += ["--folder", folder_id]
        response = run_subprocess(cmd)
        return response

    def create_bucket(
            self,
            bucket: str,
            project: str,
            location: Optional[str] = None,
            storage_class: Optional[str] = None,
    ) -> GCPCommandResponse:
        bucket_uri = f"gs://{bucket}"
        cmd = [
            "gcloud",
            "storage",
            "buckets",
            "create",
            bucket_uri,
            "--quiet",
            "--project",
            project,
        ]
        if location:
            cmd += ["--location", location]
        if storage_class:
            cmd += ["--default-storage-class", storage_class]
        response = run_subprocess(cmd)
        return response

    def list_buckets(self, project: str) -> GCPCommandResponse:
        cmd = [
            "gcloud",
            "storage",
            "buckets",
            "list",
            "--project",
            project,
        ]
        response = run_subprocess(cmd)
        return response

    def delete_bucket(self, bucket: str, project: str, force: bool = False) -> GCPCommandResponse:
        bucket_uri = f"gs://{bucket}"
        cmd = [
            "gcloud",
            "storage",
            "buckets",
            "delete",
            bucket_uri,
            "--quiet",
            "--project",
            project,
        ]
        if force:
            rm_cmd = ["gcloud", "storage", "rm", "-r", bucket_uri]
            run_subprocess(rm_cmd)
        response = run_subprocess(cmd)
        return response

    def delete_object(self, bucket: str, object_path: str, *, project: Optional[str] = None) -> GCPCommandResponse:
        object_uri = f"gs://{bucket}/{object_path}"
        cmd = [
            "gcloud",
            "storage",
            "rm",
            object_uri,
            "--quiet",
        ]
        if project:
            cmd += ["--project", project]
        response = run_subprocess(cmd)
        return response

    def list_gcp_projects(self, limit: Optional[int] = 20) -> GCPCommandResponse:
        cmd = ["gcloud", "projects", "list", "--sort-by=projectId"]
        if limit is not None:
            cmd += ["--limit", str(limit)]
        response = run_subprocess(cmd)
        return response

    def sign_url(self, bucket_file_path: str, project: str, service_account: str, duration: int = 3600,
                 region: str = None) -> GCPCommandResponse:
        if region is None:
            region = "EUROPE-WEST1"

        # get service_account_url
        cmd = [
            "gcloud",
            "storage",
            "sign-url",
            bucket_file_path,
            "--project",
            project,
            "--duration",
            str(duration),
            "--impersonate-service-account",
            service_account,
            "--http-verb",
            "GET",
            "--region",
            region
        ]
        response = run_subprocess(cmd)
        return response

    def check_file_in_bucket(self, bucket: str, file_name: str) -> GCPCommandResponse:
        cmd = [
            "gcloud",
            "storage",
            "ls",
            f"gs://{bucket}/{file_name}"
        ]
        response = run_subprocess(cmd)
        return response

    def copy_file_to_bucket(self, local_file_path, bucket, file_name) -> GCPCommandResponse:
        cmd = [
            "gcloud",
            "storage",
            "cp",
            local_file_path,
            f"gs://{bucket}/{file_name}"
        ]
        response = run_subprocess(cmd)
        return response

    def enable_credentials(self, project: str) -> GCPCommandResponse:
        cmd = [
            "gcloud",
            "services",
            "enable", "iamcredentials.googleapis.com",
            "--project",
            project,
        ]
        response = run_subprocess(cmd)
        return response

    def add_policy_binding(self, project_id) -> (GCPCommandResponse, str):
        sa = f"url-signer@{project_id}.iam.gserviceaccount.com"
        user = "p.supranovich@gmail.com"  # add take from config user email address
        cmd = [
            "gcloud",
            "iam",
            "service-accounts",
            "add-iam-policy-binding",
            sa,
            "--member",
            f"user:{user}",
            "--role",
            "roles/iam.serviceAccountTokenCreator",
            "--project",
            project_id,
        ]
        response = run_subprocess(cmd)
        return response, sa

    def allow_bucket_access(self, service_account, bucket, project_id):
        cmd = [
            "gcloud",
            "storage",
            "buckets",
            "add-iam-policy-binding",
            f"gs://{bucket}",
            "--member",
            f"serviceAccount:{service_account}",
            "--role",
            "roles/storage.objectViewer",
            "--project",
            project_id,
        ]
        response = run_subprocess(cmd)
        return response

    def allow_file_access(self, bucket, project_id):
        cmd = [
            "gcloud",
            "storage",
            "buckets",
            "update",
            f"gs://{bucket}",
            "--no-requester-pays",
            "--project",
            project_id,
        ]
        response = run_subprocess(cmd)
        return response

    def list_files_in_bucket(self, bucket: str) -> GCPCommandResponse:
        cmd = [
            "gcloud",
            "storage",
            "ls",
            f"gs://{bucket}/"
        ]
        response = run_subprocess(cmd)
        return response

    def cat_file_from_url(self,
                          urls,
                          additional_headers: Optional[dict] = None,
                          display_url: bool = False,
                          range_value: Optional[str] = None,
                          decryption_keys: Optional[list] = None,
                          ) -> GCPCommandResponse:
        if isinstance(urls, str):
            urls = [urls]
        cmd = ["gcloud", "storage", "cat"] + urls

        if additional_headers:
            for header, value in additional_headers.items():
                cmd += ["--additional-headers", f"{header}={value}"]

        if display_url:
            cmd.append("--display-url")

        if range_value:
            cmd += ["--range", range_value]

        if decryption_keys:
            keys_str = ",".join(decryption_keys)
            cmd += [f"--decryption-keys={keys_str}"]

        response = run_subprocess(cmd)
        return response
