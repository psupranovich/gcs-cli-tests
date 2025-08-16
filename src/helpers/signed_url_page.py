from playwright.sync_api import Page, expect, Locator


class SignedUrlPage:
    """Page object for interacting with signed URL pages."""

    def __init__(self, page: Page):
        self.page = page

    # LOCATORS
    @property
    def hey_there_message(self) -> Locator:
        """Locator for 'Hey there!' message."""
        return self.page.get_by_text("Hey there!")

    @property
    def file_access_message(self) -> Locator:
        """Locator for 'You have access to the file!' message."""
        return self.page.get_by_text("You have access to the file!")

    @property
    def expired_token_message(self) -> Locator:
        """Locator for ExpiredToken message."""
        return self.page.locator(selector="div span", has_text="ExpiredToken").first

    def bucket_name_locator(self, bucket_name: str) -> Locator:
        """Locator for bucket name in the page."""
        return self.page.locator(selector="div span", has_text=bucket_name).first

    def filename_locator(self, filename: str) -> Locator:
        """Locator for filename in the bucket listing."""
        return self.page.locator(selector="div span", has_text=filename).first

    # ACTIONS
    def navigate_to_signed_url(self, url: str) -> None:
        """Navigate to the signed URL."""
        self.page.goto(url=url)

    # ASSERTIONS
    def assert_file_access_granted(self) -> None:
        """Assert that file access is granted by checking for success messages."""
        expect(
            self.hey_there_message, "Expected 'Hey there!' message not found"
        ).to_be_visible()
        expect(
            self.file_access_message,
            "Expected 'You have access to the file!' message not found",
        ).to_be_visible()

    def assert_token_expired(self) -> None:
        """Assert that the token has expired."""
        expect(
            self.expired_token_message,
            "ExpiredToken message not found - file was not expired",
        ).to_be_visible()

    def assert_bucket_access(self, bucket_name: str) -> None:
        """Assert that bucket access is visible."""
        expect(
            self.bucket_name_locator(bucket_name),
            f"Bucket name '{bucket_name}' not visible - no access for bucket",
        ).to_be_visible()

    def assert_file_visible_in_bucket(self, filename: str) -> None:
        """Assert that a specific file is visible in the bucket listing."""
        expect(
            self.filename_locator(filename),
            f"File '{filename}' not visible in bucket listing",
        ).to_be_visible()

    def assert_bucket_and_file_access(self, bucket_name: str, filename: str) -> None:
        """Assert both bucket access and file visibility."""
        self.assert_bucket_access(bucket_name)
        self.assert_file_visible_in_bucket(filename)
