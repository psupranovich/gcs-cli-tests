# gcs-cli-tests

A comprehensive pytest suite for testing Google Cloud Storage (GCS) functionality using the `gcloud storage` CLI tool.

## What this project tests

This test suite validates:
- **Sign URL functionality** - Tests `gcloud storage sign-url` command with various parameters
- **Bucket operations** - Create, describe, and delete GCS buckets
- **File operations** - Upload, download, and remove files from GCS
- **Authentication flows** - Verify proper authentication and permission handling

The tests run against **real GCS infrastructure** using your configured Google Cloud Project and require proper billing setup.

---

## Prerequisites

- Python 3.10+ and pip
- Google Cloud account with billing enabled
- Gcloud CLI installed and available on PATH

## Quick Setup

1.**Installing gcloud CLI (if not installed)**

If you don't have gcloud CLI installed:

*macOS (Homebrew):*
```bash
brew install --cask google-cloud-sdk
```

*Linux (Official installer):*
```bash
curl https://sdk.cloud.google.com | bash
exec -l $SHELL
```

*Verify installation:*
```bash
gcloud version
```

If `gcloud: command not found`, ensure it's in your PATH or follow the [official installation guide](https://cloud.google.com/sdk/docs/install).

2.**Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3.**Configure your GCP settings** in `src/config.json`:
   ```json
   {
     "user_with_billing_setup": "your-email@gmail.com",
     "default_project": "your-gcp-project-id", 
     "default_bucket": "your-test-bucket-name",
     "region": "EUROPE-WEST1"
   }
   ```

4.**Authenticate with GCP:**
   ```bash
   gcloud auth login your-email@gmail.com
   gcloud config set project your-gcp-project-id
   ```

5.**Run tests:**
   ```bash
   python -m pytest src/tests/ -n auto -v
   ```
---

## Detailed Setup (if needed)

### Creating a new GCP Project

If you don't have a GCP project, ypu may create it manually or it willbe created in scope of fixture **sample_project**:

```bash
# Create project
gcloud projects create your-project-id --name="Your-Project-Name"
Add project name to **config.json**

# Link billing (get BILLING_ACCOUNT_ID from: gcloud billing accounts list)
gcloud billing projects link your-project-id --billing-account=BILLING_ACCOUNT_ID

# Enable required APIs
gcloud services enable storage.googleapis.com storage-component.googleapis.com
```

### Configuration file details

The `src/config.json` values explained:
- **`user_with_billing_setup`**: Your Google account email that has billing enabled
- **`default_project`**: Your GCP Project ID (found in GCP Console → Project Info)  
- **`default_bucket`**: A GCS bucket name for testing (created if doesn't exist)
- **`region`**: Default region for GCS operations (currently set to `EUROPE-WEST1`, update if needed for your location)


---
## Running Tests

### Basic Test Execution

Run all tests in sequential mode:

```bash
python -m pytest src/tests/ -v
```

Run tests in parallel using xdist (**recommended for faster execution**):

```bash
python -m pytest src/tests/ -n auto -v
```

Run tests with specific number of parallel workers:

```bash
python -m pytest src/tests/ -n 4 -v
```

### Running Specific Tests

Run a specific test file:

```bash
python -m pytest src/tests/test_sign_url.py -v
```

Run tests matching a pattern:

```bash
python -m pytest src/tests/ -k "sign_url" -v
```

Run a specific test function:

```bash
python -m pytest src/tests/test_sign_url.py::test_specific_function -v
```

---

## What happens during tests

- **Temporary resources**: Tests create temporary buckets and objects for testing
- **Cleanup**: All temporary resources are automatically cleaned up after tests complete
- **Your data**: Tests only use the bucket specified in your config.json and don't affect other GCS resources

## Advanced Configuration (Optional)

You can override config.json settings with environment variables:
- `GCP_PROJECT`: Override default project
- `GCS_LOCATION`: Override storage location (default: `us-central1`)
- `GCS_STORAGE_CLASS`: Override storage class (default: `STANDARD`)
- `GCS_BUCKET`: Use specific bucket (otherwise creates temporary)
- `GCS_OBJECT`: Use specific object for sign-url tests 
