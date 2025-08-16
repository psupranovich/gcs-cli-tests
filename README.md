# gcs-cli-tests

Small pytest suite to validate `gcloud storage sign-url` using real GCS.

## Prerequisites
- Python 3.10+ and pip
- gcloud CLI available on PATH

Install dependencies:
```bash
pip install -r requirements.txt
```

Install gcloud on macOS (Homebrew):
```bash
brew install --cask google-cloud-sdk
```
Then initialize and authenticate:
```bash
gcloud init
gcloud auth application-default login
gcloud auth login
gcloud config set project YOUR_PROJECT_ID
```

If `gcloud` is not found on PATH, tests are skipped by a session precondition.

## Environment variables
- `GCP_PROJECT` (optional): GCP project ID
- `GCS_LOCATION` (optional, default: `us-central1`)
- `GCS_STORAGE_CLASS` (optional, default: `STANDARD`)
- `GCS_BUCKET` (optional): if provided, tests use this bucket and DO NOT delete it
- `GCS_BUCKET_PREFIX` (optional, default: `tmp`): prefix for temporary buckets
- `GCS_OBJECT` (optional): object path in the bucket

Notes:
- If you provide `GCS_BUCKET` but not `GCS_OBJECT`, the sign-url test may be skipped. Either set `GCS_OBJECT` as well, or omit `GCS_BUCKET` to let the precondition create a temporary bucket and object automatically.

## Running tests
Basic run (creates temporary bucket and object, cleans up after):
```bash
python3 run_tests.py -q
```

Run with an existing bucket and object:
```bash
python3 run_tests.py \
  --gcp_project my-project \
  --gcs_bucket my-bucket \
  --gcs_object path/to/file.txt \
  -q
```

Override defaults (location, storage class, temp bucket prefix):
```bash
python3 run_tests.py \
  --gcs_location europe-west1 \
  --gcs_storage_class NEARLINE \
  --gcs_bucket_prefix ci-tmp \
  -q
```

Pass extra pytest args after `--`:
```bash
python3 run_tests.py -- -k test_sign_url -vv
```

## What gets created
- Temporary bucket: if `GCS_BUCKET` is not provided, named `${GCS_BUCKET_PREFIX}-gcs-cli-tests-<random>`
- Temporary object: if `GCS_OBJECT` is not provided and a temp bucket is created, a small text object is uploaded and later deleted

Cleanup happens at the end of the pytest session (bucket removal is recursive when a temp bucket was created by the suite).


# TODO Add instruction to add billing account
# TODO Add implementation  to set the user email address 
# TODO Add logger 
# TODO add run tests file 
