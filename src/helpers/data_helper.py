"""
Data helper utilities for GCP CLI testing.

This module provides utility functions and data structures for processing
GCP command outputs, managing test files, and extracting data from various
response formats used in Google Cloud Storage testing.
"""

import glob
import os
import re
from dataclasses import dataclass


@dataclass
class GCPCommandResponse:
    """
    Data structure representing the response from a GCP command execution.
    """

    status_code: int
    output: str
    error: str

    def __str__(self):
        return (
            f"Command output:\n"
            f"Code: {self.status_code}\n"
            f"Output: {self.output}\n"
        )


def extract_ids(output: str) -> list:
    """
    Extracts PROJECT_IDs from gcloud project list command output.
    """
    lines = output.strip().split("\n")
    project_ids = []
    for line in lines[1:]:  # Skip the header line
        parts = line.split()
        if parts:
            project_ids.append(parts[0])
    return project_ids


def extract_bucket_ids(output_data) -> list:
    """
    Extracts bucket IDs from gcloud storage buckets list YAML output.
    """
    bucket_ids = []
    lines = output_data.split("---")
    for line in lines:
        for sub_line in line.split("\n"):
            if sub_line.strip().startswith("name:"):
                bucket_id = sub_line.split(":", 1)[1].strip()
                bucket_ids.append(bucket_id)
    return bucket_ids


def create_sample_text_file(file_name, file_content: str = None):
    """
    Creates a temporary text file for testing purposes.
    """
    # Use absolute path to project root for consistent file creation
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    temp_dir = os.path.join(project_root, "temp")

    # Create temp directory if it doesn't exist
    os.makedirs(temp_dir, exist_ok=True)

    test_file_path = os.path.join(temp_dir, file_name)
    with open(test_file_path, "w") as test_file:
        if not file_content:
            file_content = "Hey there!\nYou have access to the file!"
        test_file.write(file_content)
    return test_file_path


def delete_temp_files():
    """
    Cleans up temporary text files created during testing.
    """
    # Use the same temp directory path as create_sample_text_file
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    temp_dir = os.path.join(project_root, "temp")

    if os.path.exists(temp_dir):
        txt_files = glob.glob(os.path.join(temp_dir, "*.txt"))
        for txt_file in txt_files:
            try:
                os.remove(txt_file)
            except Exception:
                pass

        # Try to remove the temp directory if it's empty
        try:
            os.rmdir(temp_dir)
        except (OSError, Exception):
            pass  # Directory not empty or other error, that's fine


def extract_url(output_data):
    """
    Extracts URLs from gcloud command output using regex patterns.
    """
    m = re.search(r"signed_url:\s*(https?://\S+)", output_data)
    if m:
        return m.group(1)
    m = re.search(r"(https?://storage\.googleapis\.com/\S+)", output_data)
    if m:
        return m.group(1)
    return None
