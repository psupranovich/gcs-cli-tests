import os
import re
from dataclasses import dataclass


@dataclass
class GCPCommandResponse:
    status_code: int
    output: str
    error: str

    def __str__(self):
        return (f"Command output:\n"
                f"Code: {self.status_code}\n"
                f"Output: {self.output}\n"
                f"Error: {self.error}")


def extract_ids(output: str) -> list:
    """
    Extracts the PROJECT_IDs from the given output string.

    :param output: The output string containing project details.
    :return: A list of PROJECT_IDs.
    """
    lines = output.strip().split('\n')
    project_ids = []
    for line in lines[1:]:  # Skip the header line
        parts = line.split()
        if parts:
            project_ids.append(parts[0])
    return project_ids


def extract_bucket_ids(output_data) -> list:
    bucket_ids = []
    lines = output_data.split('---')
    for line in lines:
        # Find the line that starts with 'name:' and extract the bucket ID
        for sub_line in line.split('\n'):
            if sub_line.strip().startswith('name:'):
                bucket_id = sub_line.split(':', 1)[1].strip()
                bucket_ids.append(bucket_id)
    return bucket_ids


def create_sample_text_file(file_name):
    test_file_path = os.path.join(os.path.dirname(__file__), file_name)
    with open(test_file_path, "w") as test_file:
        test_file.write("Hey there!\n")
        test_file.write("You have access to the file!")
    return test_file_path


def extract_url(output_data):
    m = re.search(r"signed_url:\s*(https?://\S+)", output_data)
    if m:
        return m.group(1)
    m = re.search(r"(https?://storage\.googleapis\.com/\S+)", output_data)
    if m:
        return m.group(1)
    return None