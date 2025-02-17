import os

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse

from wagtail.contrib.redirects.models import Redirect
from wagtail.core.models import Site
from wagtail.tests.utils import WagtailTestUtils

TEST_ROOT = os.path.abspath(os.path.dirname(__file__))


@override_settings(
    ALLOWED_HOSTS=["testserver", "localhost", "test.example.com", "other.example.com"]
)
class TestImportAdminViews(TestCase, WagtailTestUtils):
    def setUp(self):
        self.login()

    def get(self, params={}):
        return self.client.get(reverse("wagtailredirects:start_import"), params)

    def post(self, post_data={}, follow=False):
        return self.client.post(
            reverse("wagtailredirects:start_import"), post_data, follow=follow
        )

    def post_import(self, post_data={}, follow=False):
        return self.client.post(
            reverse("wagtailredirects:process_import"), post_data, follow=follow
        )

    def test_request_start_with_get_returns_initial_form(self):
        response = self.get()
        self.assertEqual(
            response.templates[0].name,
            "wagtailredirects/choose_import_file.html",
        )

    def test_empty_import_file_returns_error(self):
        response = self.post(
            {
                "import_file": "",
                "input_format": "0",
            }
        )

        self.assertIn("import_file", response.context["form"].errors)

    def test_non_valid_format_returns_error(self):
        f = "{}/files/example.yaml".format(TEST_ROOT)
        (_, filename) = os.path.split(f)

        with open(f, "rb") as infile:
            upload_file = SimpleUploadedFile(filename, infile.read())

            response = self.post(
                {
                    "import_file": upload_file,
                },
                follow=True,
            )

            self.assertContains(
                response, "File format of type &quot;yaml&quot; is not supported"
            )

    def test_valid_csv_triggers_confirm_view(self):
        f = "{}/files/example.csv".format(TEST_ROOT)
        (_, filename) = os.path.split(f)

        with open(f, "rb") as infile:
            upload_file = SimpleUploadedFile(filename, infile.read())

            response = self.post(
                {
                    "import_file": upload_file,
                }
            )

            self.assertEqual(
                response.templates[0].name,
                "wagtailredirects/confirm_import.html",
            )
            self.assertEqual(len(response.context["dataset"]), 3)

    def test_import_step(self):
        f = "{}/files/example.csv".format(TEST_ROOT)
        (_, filename) = os.path.split(f)

        with open(f, "rb") as infile:
            upload_file = SimpleUploadedFile(filename, infile.read())

            self.assertEqual(Redirect.objects.all().count(), 0)

            response = self.post(
                {
                    "import_file": upload_file,
                }
            )

            import_response = self.post_import(
                {
                    **response.context["form"].initial,
                    "from_index": 0,
                    "to_index": 1,
                    "permanent": True,
                }
            )

            self.assertTemplateUsed(
                import_response, "wagtailredirects/import_summary.html"
            )
            self.assertEqual(Redirect.objects.all().count(), 2)

    def test_permanent_setting(self):
        f = "{}/files/example.csv".format(TEST_ROOT)
        (_, filename) = os.path.split(f)

        with open(f, "rb") as infile:
            upload_file = SimpleUploadedFile(filename, infile.read())

            self.assertEqual(Redirect.objects.all().count(), 0)

            response = self.post(
                {
                    "import_file": upload_file,
                }
            )

            import_response = self.post_import(
                {
                    **response.context["form"].initial,
                    "from_index": 0,
                    "to_index": 1,
                    "permanent": False,
                }
            )

            self.assertTemplateUsed(
                import_response, "wagtailredirects/import_summary.html"
            )
            self.assertFalse(Redirect.objects.first().is_permanent)

    def test_site_setting(self):
        f = "{}/files/example.csv".format(TEST_ROOT)
        (_, filename) = os.path.split(f)

        default_site = Site.objects.first()
        new_site = Site.objects.create(
            hostname="hello.dev",
            root_page=default_site.root_page,
        )

        with open(f, "rb") as infile:
            upload_file = SimpleUploadedFile(filename, infile.read())

            self.assertEqual(Redirect.objects.all().count(), 0)

            response = self.post(
                {
                    "import_file": upload_file,
                }
            )

            import_response = self.post_import(
                {
                    **response.context["form"].initial,
                    "from_index": 0,
                    "to_index": 1,
                    "permanent": False,
                    "site": new_site.pk,
                }
            )

            self.assertTemplateUsed(
                import_response, "wagtailredirects/import_summary.html"
            )
            self.assertEqual(Redirect.objects.count(), 2)
            self.assertEqual(Redirect.objects.first().site, new_site)

    def test_import_xls(self):
        f = "{}/files/example.xls".format(TEST_ROOT)
        (_, filename) = os.path.split(f)

        with open(f, "rb") as infile:
            upload_file = SimpleUploadedFile(filename, infile.read())

            self.assertEqual(Redirect.objects.all().count(), 0)

            response = self.post(
                {
                    "import_file": upload_file,
                }
            )

            self.assertTemplateUsed(response, "wagtailredirects/confirm_import.html")

            import_response = self.post_import(
                {
                    **response.context["form"].initial,
                    "from_index": 0,
                    "to_index": 1,
                    "permanent": True,
                },
                follow=True,
            )

            self.assertTemplateUsed(import_response, "wagtailredirects/index.html")
            self.assertEqual(Redirect.objects.all().count(), 3)

    def test_import_xlsx(self):
        f = "{}/files/example.xlsx".format(TEST_ROOT)
        (_, filename) = os.path.split(f)

        with open(f, "rb") as infile:
            upload_file = SimpleUploadedFile(filename, infile.read())

            self.assertEqual(Redirect.objects.all().count(), 0)

            response = self.post(
                {
                    "import_file": upload_file,
                }
            )

            self.assertTemplateUsed(response, "wagtailredirects/confirm_import.html")

            import_response = self.post_import(
                {
                    **response.context["form"].initial,
                    "from_index": 0,
                    "to_index": 1,
                    "permanent": True,
                },
                follow=True,
            )

            self.assertTemplateUsed(import_response, "wagtailredirects/index.html")
            self.assertEqual(Redirect.objects.all().count(), 3)

    def test_unicode_error_when_importing(self):
        f = "{}/files/example_faulty.csv".format(TEST_ROOT)
        (_, filename) = os.path.split(f)

        with open(f, "rb") as infile:
            upload_file = SimpleUploadedFile(filename, infile.read())

            self.assertEqual(Redirect.objects.all().count(), 0)

            response = self.post(
                {
                    "import_file": upload_file,
                },
                follow=True,
            )
            self.assertIn(b"Imported file has a wrong encoding:", response.content)

    def test_not_valid_method_for_import_file(self):
        response = self.client.get(reverse("wagtailredirects:process_import"))
        self.assertEqual(response.status_code, 405)

    def test_error_in_data_renders_confirm_view_on_import(self):
        f = "{}/files/example.csv".format(TEST_ROOT)
        (_, filename) = os.path.split(f)

        with open(f, "rb") as infile:
            upload_file = SimpleUploadedFile(filename, infile.read())

            response = self.post(
                {
                    "import_file": upload_file,
                }
            )

            self.post_import(
                {
                    **response.context["form"].initial,
                    "from_index": 0,
                    "to_index": 1,
                    "permanent": True,
                    "site": 99,
                }
            )
            self.assertTemplateUsed(response, "wagtailredirects/confirm_import.html")

    def test_import_tsv(self):
        f = "{}/files/example.tsv".format(TEST_ROOT)
        (_, filename) = os.path.split(f)

        with open(f, "rb") as infile:
            upload_file = SimpleUploadedFile(filename, infile.read())

            self.assertEqual(Redirect.objects.all().count(), 0)

            response = self.post(
                {
                    "import_file": upload_file,
                }
            )

            self.assertTemplateUsed(response, "wagtailredirects/confirm_import.html")

            import_response = self.post_import(
                {
                    **response.context["form"].initial,
                    "from_index": 0,
                    "to_index": 1,
                    "permanent": True,
                }
            )

            self.assertTemplateUsed(
                import_response, "wagtailredirects/import_summary.html"
            )
            self.assertEqual(Redirect.objects.all().count(), 2)

    @override_settings(WAGTAIL_REDIRECTS_FILE_STORAGE="cache")
    def test_import_xlsx_with_cache_store_engine(self):
        f = "{}/files/example.xlsx".format(TEST_ROOT)
        (_, filename) = os.path.split(f)

        with open(f, "rb") as infile:
            upload_file = SimpleUploadedFile(filename, infile.read())

            self.assertEqual(Redirect.objects.all().count(), 0)

            response = self.post(
                {
                    "import_file": upload_file,
                }
            )

            self.assertTemplateUsed(response, "wagtailredirects/confirm_import.html")

            import_response = self.post_import(
                {
                    **response.context["form"].initial,
                    "from_index": 0,
                    "to_index": 1,
                    "permanent": True,
                },
                follow=True,
            )

            self.assertTemplateUsed(import_response, "wagtailredirects/index.html")
            self.assertEqual(Redirect.objects.all().count(), 3)

    @override_settings(WAGTAIL_REDIRECTS_FILE_STORAGE="cache")
    def test_process_validation_works_when_using_plaintext_files_and_cache(self):
        f = "{}/files/example.csv".format(TEST_ROOT)
        (_, filename) = os.path.split(f)

        with open(f, "rb") as infile:
            upload_file = SimpleUploadedFile(filename, infile.read())

            self.assertEqual(Redirect.objects.all().count(), 0)

            response = self.post(
                {
                    "import_file": upload_file,
                }
            )

            self.assertTemplateUsed(response, "wagtailredirects/confirm_import.html")

            import_response = self.post_import(
                {
                    **response.context["form"].initial,
                    "permanent": True,
                }
            )

            self.assertTemplateUsed(
                import_response, "wagtailredirects/confirm_import.html"
            )
