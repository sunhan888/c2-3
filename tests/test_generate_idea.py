import unittest

from api.generate_idea import _extract_gemini_text, _normalise_idea


class NormaliseIdeaTests(unittest.TestCase):
    def test_valid_json_response_is_preserved(self):
        idea = _normalise_idea(
            '{"title":"우리 동네 소리 지도","tagline":"귀를 기울이면 이야기가 보여요.",'
            '"summary":"동네의 소리를 기록해 지도로 만들어요.",'
            '"steps":["장소 세 곳 고르기","소리 녹음하기","지도로 정리하기"],'
            '"tip":"친구 의견을 더해 보세요."}'
        )
        self.assertEqual(idea["title"], "우리 동네 소리 지도")
        self.assertEqual(len(idea["steps"]), 3)

    def test_markdown_fenced_json_is_supported(self):
        idea = _normalise_idea(
            '```json\n{"title":"테스트","summary":"설명",'
            '"steps":["하나"],"tagline":"응원","tip":"팁"}\n```'
        )
        self.assertEqual(idea["title"], "테스트")
        self.assertEqual(idea["steps"], ["하나"])

    def test_non_json_response_uses_safe_fallback(self):
        idea = _normalise_idea("JSON이 아닌 응답")
        self.assertTrue(idea["title"])
        self.assertGreaterEqual(len(idea["steps"]), 3)

    def test_gemini_response_text_is_extracted(self):
        response = {"candidates": [{"content": {"parts": [{"text": '{"title":"테스트"}'}]}}]}
        self.assertEqual(_extract_gemini_text(response), '{"title":"테스트"}')


if __name__ == "__main__":
    unittest.main()
