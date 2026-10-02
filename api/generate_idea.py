"""Vercel Serverless Function for SparkIdea AI.

The handler receives school grade, interests, and a project topic. The OpenAI key is
read only from Vercel's OPENAI_API_KEY environment variable.
"""

import json
import os
from http.server import BaseHTTPRequestHandler
from typing import Any

from openai import APIConnectionError, APIStatusError, APITimeoutError, OpenAI

MAX_BODY_BYTES = 8_192
FIELD_LIMITS = {"grade": 50, "interest": 120, "topic": 300}
DEFAULT_MODEL = "gpt-5-mini"

SYSTEM_PROMPT = """You are SparkIdea AI, a warm Korean project-idea coach for students.
Return exactly one practical project idea that matches the user's grade, interest, and topic.
Keep the scope small enough to begin this week. Answer ONLY valid JSON with this exact shape:
{
  "title": "short Korean project title",
  "tagline": "one encouraging Korean sentence",
  "summary": "2-3 Korean sentences explaining what to make and why it fits",
  "steps": ["first concrete action", "second action", "third action"],
  "tip": "one Korean expansion tip"
}
Use friendly Korean. Do not include markdown, a preface, or extra keys.
"""


def _clean_text(value: Any, limit: int) -> str:
    if not isinstance(value, str):
        return ""
    return " ".join(value.strip().split())[:limit]


def _normalise_idea(raw_content: str) -> dict[str, Any]:
    """Return a safe UI shape even if the model wraps JSON in a code fence."""
    content = raw_content.strip()
    if content.startswith("```"):
        content = content.split("\n", 1)[1] if "\n" in content else ""
        if content.endswith("```"):
            content = content[:-3].strip()

    try:
        parsed = json.loads(content)
    except json.JSONDecodeError:
        parsed = {}

    title = _clean_text(parsed.get("title"), 100) if isinstance(parsed, dict) else ""
    tagline = _clean_text(parsed.get("tagline"), 180) if isinstance(parsed, dict) else ""
    summary = _clean_text(parsed.get("summary"), 700) if isinstance(parsed, dict) else ""
    tip = _clean_text(parsed.get("tip"), 280) if isinstance(parsed, dict) else ""
    raw_steps = parsed.get("steps", []) if isinstance(parsed, dict) else []
    steps = [_clean_text(step, 220) for step in raw_steps if _clean_text(step, 220)] if isinstance(raw_steps, list) else []

    if title and summary and steps:
        return {
            "title": title,
            "tagline": tagline or "작게 시작해도 충분히 멋진 결과가 될 수 있어요.",
            "summary": summary,
            "steps": steps[:4],
            "tip": tip or "과정을 사진이나 메모로 남기면 다음 아이디어를 발전시키기 쉬워져요.",
        }

    fallback_summary = _clean_text(raw_content, 700)
    return {
        "title": "나만의 작은 프로젝트 설계하기",
        "tagline": "좋아하는 것에서 출발해 첫 결과물을 만들어 보세요.",
        "summary": fallback_summary or "아이디어를 다시 만들 수 있도록 입력 내용을 조금 더 구체적으로 적어 보세요.",
        "steps": ["주제와 관련된 사진·자료를 3개 모아보기", "가장 재미있는 한 가지 질문 정하기", "30분 안에 만들 수 있는 첫 결과물 시작하기"],
        "tip": "완성도를 높이기보다 친구 한 명에게 보여 줄 수 있는 작은 버전을 먼저 만들어 보세요.",
    }


class handler(BaseHTTPRequestHandler):
    """File-based handler served by Vercel at /api/generate_idea."""

    def log_message(self, format: str, *args: Any) -> None:
        # Avoid printing request contents, which may contain user-entered text.
        return

    def _send_json(self, status: int, payload: dict[str, Any]) -> None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self) -> None:
        self.send_response(204)
        self.send_header("Allow", "POST, OPTIONS")
        self.send_header("Content-Length", "0")
        self.end_headers()

    def do_GET(self) -> None:
        self._send_json(405, {"error": "POST 요청만 사용할 수 있습니다."})

    def do_POST(self) -> None:
        content_length = self.headers.get("Content-Length", "0")
        try:
            body_length = int(content_length)
        except ValueError:
            self._send_json(400, {"error": "요청 형식을 읽을 수 없습니다."})
            return

        if body_length <= 0 or body_length > MAX_BODY_BYTES:
            self._send_json(400, {"error": "입력 내용이 비어 있거나 너무 깁니다."})
            return

        try:
            payload = json.loads(self.rfile.read(body_length).decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError):
            self._send_json(400, {"error": "JSON 형식의 입력이 필요합니다."})
            return

        values = {name: _clean_text(payload.get(name), limit) for name, limit in FIELD_LIMITS.items()}
        if not all(values.values()):
            self._send_json(400, {"error": "학년, 관심사, 주제를 모두 입력해 주세요."})
            return

        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            self._send_json(503, {"error": "AI 서비스 설정이 아직 완료되지 않았습니다. 잠시 후 다시 시도해 주세요."})
            return

        user_prompt = (
            f"학년: {values['grade']}\n"
            f"관심사: {values['interest']}\n"
            f"주제 또는 고민: {values['topic']}"
        )

        try:
            client_options = {"api_key": api_key, "timeout": 15.0, "max_retries": 1}
            compatible_base_url = os.environ.get("OPENAI_BASE_URL") or os.environ.get("OPENAI_API_BASE")
            if compatible_base_url:
                client_options["base_url"] = compatible_base_url
            client = OpenAI(**client_options)
            completion = client.chat.completions.create(
                model=os.environ.get("OPENAI_MODEL", DEFAULT_MODEL),
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_prompt},
                ],
                response_format={"type": "json_object"},
                max_completion_tokens=1800,
            )
            raw_content = completion.choices[0].message.content or ""
            self._send_json(200, {"idea": _normalise_idea(raw_content)})
        except APITimeoutError:
            self._send_json(504, {"error": "AI 응답이 늦어지고 있어요. 잠시 후 다시 시도해 주세요."})
        except APIConnectionError:
            self._send_json(503, {"error": "AI 서비스에 연결하지 못했어요. 잠시 후 다시 시도해 주세요."})
        except APIStatusError as error:
            if error.status_code == 429:
                self._send_json(429, {"error": "요청이 많아요. 잠시 후 다시 시도해 주세요."})
            else:
                self._send_json(502, {"error": "AI 서비스에서 응답을 받지 못했어요. 잠시 후 다시 시도해 주세요."})
        except Exception:
            self._send_json(500, {"error": "아이디어를 만드는 중 문제가 생겼어요. 잠시 후 다시 시도해 주세요."})
