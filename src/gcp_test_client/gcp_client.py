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

    def delete_object(self, 
                     bucket: str, 
                     object_path: str = None, 
                     *, 
                     project: Optional[str] = None,
                     additional_headers: Optional[dict] = None,
                     all_versions: bool = False,
                     continue_on_error: bool = False,
                     exclude_managed_folders: bool = False,
                     recursive: bool = False,
                     if_generation_match: Optional[str] = None,
                     if_metageneration_match: Optional[str] = None,
                     pattern: Optional[str] = None) -> GCPCommandResponse:
        """
        Delete objects using gcloud storage rm command with various options.
        
        Args:
            bucket: Bucket name
            object_path: Object path (optional if using pattern or deleting entire bucket)
            project: Project ID (optional)
            pattern: Pattern to match objects (e.g., '*.txt', '**' for all objects)
            additional_headers: Additional headers for the request
            all_versions: Delete all versions of objects
            continue_on_error: Continue on errors
            exclude_managed_folders: Exclude managed folders
            recursive: Recursively delete (for bucket deletion)
            if_generation_match: Generation match condition
            if_metageneration_match: Metageneration match condition
        """
        if pattern:
            # Use pattern for deletion (e.g., *.txt, **)
            object_uri = f"gs://{bucket}/{pattern}"
        elif object_path:
            # Delete specific object
            object_uri = f"gs://{bucket}/{object_path}"
        else:
            # Delete entire bucket (requires recursive=True)
            object_uri = f"gs://{bucket}"
            
        cmd = [
            "gcloud",
            "storage",
            "rm",
            object_uri,
            "--quiet",
        ]
        
        if project:
            cmd += ["--project", project]

        if additional_headers:
            for header, value in additional_headers.items():
                cmd += ["--additional-headers", f"{header}={value}"]

        if all_versions:
            cmd.append("--all-versions")

        if continue_on_error:
            cmd.append("--continue-on-error")

        if exclude_managed_folders:
            cmd.append("--exclude-managed-folders")

        if recursive:
            cmd.append("--recursive")

        if if_generation_match:
            cmd += ["--if-generation-match", if_generation_match]

        if if_metageneration_match:
            cmd += ["--if-metageneration-match", if_metageneration_match]

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

    def add_policy_binding(self, project_id) -> tuple[GCPCommandResponse, str]:
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

    def create_folder(self, bucket: str, folder_path: str, recursive: bool = False) -> GCPCommandResponse:
        folder_uri = f"gs://{bucket}/{folder_path}"
        cmd = [
            "gcloud",
            "storage",
            "folders",
            "create",
            folder_uri,
        ]
        if recursive:
            cmd.append("--recursive")
        response = run_subprocess(cmd)
        return response

    def describe_bucket(self, bucket_url: str, additional_headers: Optional[dict] = None, raw: bool = False, format: Optional[str] = None) -> GCPCommandResponse:
        cmd = [
            "gcloud",
            "storage",
            "buckets",
            "describe",
            bucket_url
        ]

        if additional_headers:
            for header, value in additional_headers.items():
                cmd += ["--additional-headers", f"{header}={value}"]

        if raw:
            cmd.append("--raw")

        if format:
            cmd += ["--format", format]

        response = run_subprocess(cmd)
        return response


