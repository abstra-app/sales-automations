from unittest import TestCase
from .linkedin import extract_linkedin_handle

class TestLinkedin(TestCase):
    def test_accept_handle(self):
        handle = extract_linkedin_handle("username")
        self.assertEqual(handle, "username")

    def test_accept_handle_with_hyphen(self):
        handle = extract_linkedin_handle("user-name")
        self.assertEqual(handle, "user-name")

    def test_accept_handle_with_underscore(self):
        handle = extract_linkedin_handle("user_name")
        self.assertEqual(handle, "user_name")

    def test_accept_with_url(self):
        handle = extract_linkedin_handle("https://www.linkedin.com/in/username")
        self.assertEqual(handle, "username")

    def test_remove_trailing_slash(self):
        handle = extract_linkedin_handle("https://www.linkedin.com/in/username/")
        self.assertEqual(handle, "username")

    def test_accept_company_url(self):
        handle = extract_linkedin_handle("https://www.linkedin.com/company/companyname")
        self.assertEqual(handle, "companyname")

    def test_accept_company_url_with_nested_path(self):
        handle = extract_linkedin_handle("https://www.linkedin.com/company/companyname/nested/path")
        self.assertEqual(handle, "companyname")

    def test_raise_exception_with_non_linkedin_url(self):
        with self.assertRaises(ValueError):
            extract_linkedin_handle("https://www.google.com")
