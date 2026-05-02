# services/llmSummary.py
# Groq API를 이용한 논문 요약 서비스

import os
import json

from groq import Groq
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

SYSTEM_PROMPT = """너는 학술 논문을 쉽고 재미있게 설명하는 전문가다.
아래 규칙에 따라 논문을 한국어로 요약해라.

[출력 형식 - 반드시 아래 JSON 형식으로만 출력. JSON 외 텍스트, 마크다운, 코드블록 일체 금지.]
{
    "one_line": "(내용)",
    "key_points": "(내용)",
    "significance": "(내용)"
}

[각 항목 작성 규칙]

one_line:
- 이 논문이 무엇을 다루는지 한 문장으로 소개.
- 반드시 "~에 대해 ~한 논문." 형식으로 끝낼 것.
- 예시) "VR을 누운 상태에서 이용할 때 발생하는 신체적 제약과 조작 성능 변화를 조사한 논문."

key_points:
- 논문의 핵심 내용과 결론을 5줄 이내로 요약.
- 각 줄은 "~임.", "~함.", "~나타남." 과 같이 단답형 종결어로 끝낼 것.
- 줄바꿈으로 구분하되 번호, 기호, 글머리 기호 사용 금지.
- 예시)
  오른쪽으로 누웠을 때 오른손으로 작업 시 깔린 팔의 제약으로 인해 TP가 유의미하게 낮아짐.
  왼쪽으로 누운 자세에서는 오른손 조작 성능이 상대적으로 높게 나타남.
  자세에 따라 선호하는 입력 방식과 편안함 수준에 유의미한 차이가 존재함.

significance:
- 기존 연구들과의 차별점을 한두 문장으로 설명.
- 반드시 "기존 ~연구들은 ~한 반면, 이 논문은 ~" 형식으로 작성.
- 예시) "기존 VR 연구들은 주로 앉거나 서있는 자세에서 수행된 반면, 이 논문은 다양한 누운 자세에서의 조작 성능을 체계적으로 분석했다는 점에서 차별점이 존재함."

[반드시 지켜야 할 규칙]
1. 반드시 JSON 형식으로만 출력. (JSON 외 텍스트, 코드블록 일체 금지)
2. 마크다운 사용 금지. (번호, 기호, 굵은 글씨, 이탤릭체 등 일체 사용 금지)
3. 한국어로만 작성. (논문이 영어여도 한국어로 요약)
4. 위 형식 외 추가적인 인사말, 설명, 코멘트 일체 금지.
"""


def summarize_paper(title: str, abstract: str) -> dict | None:
    """논문 제목과 초록을 받아 한국어 요약 반환"""
    try:
        response = client.chat.completions.create(
            model="openai/gpt-oss-120b",
            messages=[
                {
                    "role": "system",
                    "content": SYSTEM_PROMPT,
                },
                {
                    "role": "user",
                    "content": f"제목: {title}\n\n초록: {abstract}",
                },
            ],
            temperature=0.5,   # 모델의 창의성 조절 (0.0~1.0, 낮을수록 더 일관적)
            max_tokens=1000,
        )

        summary_text = response.choices[0].message.content.strip()
        return _parse_summary(summary_text)

    except Exception as e:
        print(f"Groq API 오류: {e}")
        return None



def _parse_summary(text: str) -> dict:
    """JSON 응답을 dict로 변환"""
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return {"one_line": "", "key_points": "", "significance": "", "raw": text}
    
  