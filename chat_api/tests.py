import json
from types import SimpleNamespace

from django.test import SimpleTestCase

from .views import _format_catalog_answer, _get_tool_calls, _plain_text


class CatalogAnswerTests(SimpleTestCase):
    def test_plain_text_removes_common_markdown(self):
        source = """# عنوان
| نام | قیمت |
|---|---|
| **کالا** | `120` |
- [لینک](https://example.com)
> نقل‌قول
"""
        result = _plain_text(source)

        self.assertNotIn("**", result)
        self.assertNotIn("`", result)
        self.assertNotIn("|", result)
        self.assertNotIn("# عنوان", result)
        self.assertNotIn("[لینک]", result)
        self.assertIn("کالا", result)
        self.assertIn("لینک (https://example.com)", result)
        self.assertIn("نقل‌قول", result)
        self.assertNotIn("\n", result)
        self.assertNotIn("•", result)

    def test_formats_only_products_from_catalog_and_omits_out_of_stock(self):
        result = _format_catalog_answer(json.dumps({
            "products": [
                {"title": "محصول واقعی", "price": 350000, "stock": 2},
                {"title": "ناموجود", "price": 100000, "stock": 0},
            ]
        }))

        self.assertIn("محصول واقعی", result)
        self.assertIn("350000 تومان", result)
        self.assertNotIn("ناموجود", result)
        self.assertNotIn("|", result)
        self.assertNotIn("**", result)

    def test_returns_no_matches_message_for_empty_catalog_results(self):
        result = _format_catalog_answer('{"products": []}')
        self.assertEqual(result, "در حال حاضر محصول موجودی در نتایج فروشگاه پیدا نشد.")

    def test_does_not_generate_products_for_invalid_tool_result(self):
        result = _format_catalog_answer("upstream error")
        self.assertEqual(result, "در حال حاضر نتوانستم اطلاعات محصولات را از فروشگاه دریافت کنم.")

    def test_processes_tool_calls_even_if_provider_finish_reason_is_stop(self):
        choice = SimpleNamespace(
            finish_reason="stop",
            message=SimpleNamespace(tool_calls=["catalog-call"]),
        )
        self.assertEqual(_get_tool_calls(choice), ["catalog-call"])
