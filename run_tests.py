#!/usr/bin/env python3
import argparse
import os
import subprocess
import sys


def main() -> int:
    parser = argparse.ArgumentParser("Pytest Runner")
    parser.add_argument(
        "--gcp_project",
        default=None,
        help="GCP project ID (optional). If not set, gcloud default will be used.",
    )
    parser.add_argument(
        "--gcs_location",
        default="us-central1",
        help="GCS bucket location (optional, default: us-central1)",
    )
    parser.add_argument(
        "--gcs_storage_class",
        default="STANDARD",
        help="GCS bucket storage class (optional, default: STANDARD)",
    )
    parser.add_argument(
        "--gcs_bucket",
        default=None,
        help="Existing GCS bucket to use (optional). "
             "If not set, a temporary bucket will be created and deleted after tests.",
    )
    parser.add_argument(
        "--gcs_object",
        default=None,
        help="Existing GCS object path/key to use (optional). If not set, a temporary object may be created.",
    )
    parser.add_argument(
        "--gcs_bucket_prefix",
        default="tmp",
        help="Prefix for temporary buckets (optional, default: tmp)",
    )
    parser.add_argument(
        "--tests",
        default="src/tests",
        help="Path to tests to run (default: src/tests)",
    )
    parser.add_argument(
        "--create_temp_gcp_project",
        action="store_true",
        default=True,
        help="If no project is configured, create a temporary GCP project (default: true)",
    )
    parser.add_argument(
        "--gcp_billing_account",
        default=None,
        help="Billing account ID for temp project linking (optional)",
    )
    parser.add_argument(
        "--gcp_organization_id",
        default=None,
        help="Organization ID to create temp project under (optional; alternative to folder)",
    )
    parser.add_argument(
        "--gcp_folder_id",
        default=None,
        help="Folder ID to create temp project under (optional; alternative to organization)",
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Run pytest in quiet mode (-q)",
    )

    args, extra_pytest_args = parser.parse_known_args()

    env = os.environ
    if args.gcp_project:
        env["GCP_PROJECT"] = args.gcp_project
    if args.gcs_location:
        env["GCS_LOCATION"] = args.gcs_location
    if args.gcs_storage_class:
        env["GCS_STORAGE_CLASS"] = args.gcs_storage_class
    if args.gcs_bucket:
        env["GCS_BUCKET"] = args.gcs_bucket
    if args.gcs_bucket_prefix:
        env["GCS_BUCKET_PREFIX"] = args.gcs_bucket_prefix
    if args.gcs_object:
        env["GCS_OBJECT"] = args.gcs_object
    # Defaults for temp project creation
    env.setdefault("CREATE_TEMP_GCP_PROJECT", "true" if args.create_temp_gcp_project else "false")
    if args.gcp_billing_account:
        env["GCP_BILLING_ACCOUNT"] = args.gcp_billing_account
    if args.gcp_organization_id:
        env["GCP_ORGANIZATION_ID"] = args.gcp_organization_id
    if args.gcp_folder_id:
        env["GCP_FOLDER_ID"] = args.gcp_folder_id

    cmd = ["pytest"]
    if args.quiet:
        cmd.append("-q")
    # Put extra pytest args before test path so options like -rs are parsed
    cmd.extend(extra_pytest_args)
    cmd.append(args.tests)

    return subprocess.call(cmd, env=env)


if __name__ == "__main__":
    sys.exit(main())
