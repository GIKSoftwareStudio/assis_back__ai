import json
from types import SimpleNamespace

from django.test import SimpleTestCase

from .views import (
    _clarification_message,
    _format_catalog_answer,
    _format_categories_answer,
    _get_tool_calls,
    _missing_product_details,
    _plain_text,
)


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
        self.assertIn("350000", result)
        self.assertIn("تومان", result)
        self.assertNotIn("ناموجود", result)
        self.assertNotIn("|", result)
        self.assertNotIn("**", result)
        self.assertEqual(len(result.splitlines()), 2)
        self.assertTrue(result.splitlines()[0].startswith("\u200f"))
        self.assertIn("\u2066محصول واقعی\u2069", result)
        self.assertIn("\u2066125000\u2069", _format_catalog_answer(json.dumps({
            "products": [{"title": "Product-1", "price": 125000, "stock": 2}]
        })))

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

    def test_recommendation_requires_product_scope_and_budget(self):
        self.assertEqual(
            _missing_product_details("recommend_products", {}),
            ["نوع یا دسته‌بندی محصول", "حداکثر بودجه"],
        )
        self.assertEqual(
            _missing_product_details("recommend_products", {"category_id": 2, "max_price": 600000}),
            [],
        )
        self.assertEqual(
            _missing_product_details("recommend_products", {"query": "هدفون", "max_price": None}),
            ["حداکثر بودجه"],
        )

    def test_category_answer_uses_only_api_category_names(self):
        result = _format_categories_answer('[{"id":2,"name":"صوتی"},{"id":3,"name":"جانبی"}]')
        self.assertIn("صوتی", result)
        self.assertIn("جانبی", result)
        self.assertNotIn("محصول نمونه", result)

    def test_clarification_is_plain_text(self):
        result = _clarification_message(["نوع محصول", "حداکثر بودجه"])
        self.assertIn("نوع محصول و حداکثر بودجه", result)
        self.assertNotIn("*", result)
