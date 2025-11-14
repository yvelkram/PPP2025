from utils import *
from langchain_core.output_parsers import StrOutputParser
from openai import OpenAI
import pathlib
import time

class PaperWork:
    papers: list[Paper]
    prompt_schema: dict
    llm_model_name: str
    debug: bool
    temp_path: str

    def __init__(self, pdf_master_path: pathlib.Path, prompt_path: pathlib.Path, llm_model_name, debug=False, temp_dir=".temp"):
        self.debug = debug
        self.temp_path = temp_dir
        self.prompt_schema = load_prompt_schema(prompt_path)
        self.papers = load_paper(pdf_master_path)

        # llm setting
        self.llm_model_name = llm_model_name
        self.max_retries: int = 3
        self.request_timeout_sec: int = 120

    # --- PRIVATE ------------------------------------------------------------------------------------------------------
    def __call_openai_chat(self, system_msg: str, user_msg: str) -> str:
        """
        system/user 메시지로 OpenAI Chat API 호출하여 텍스트를 반환.
        """
        messages = [
            {"role": "system", "content": system_msg},
            {"role": "user", "content": user_msg},
        ]

        client = OpenAI()
        last_err = None
        for attempt in range(1, self.max_retries + 1):
            try:
                # Chat Completions 스타일
                resp = client.chat.completions.create(
                    model=self.llm_model_name,
                    messages=messages,
                    timeout=self.request_timeout_sec,
                )
                text = resp.choices[0].message.content or ""
                return text.strip()

            except Exception as e:
                last_err = e
                if attempt < self.max_retries:
                    # 간단한 지수 백오프
                    time.sleep(1.5 * attempt)
                else:
                    raise e
        return ""

    # --- PUBLIC -------------------------------------------------------------------------------------------------------
    def process(self):
        print("start PaperWork")
        # --- 논문 파일 파싱
        for paper in self.papers:
            paper.parse_pdf()
            paper.retrieval_paper()
            # if self.debug: paper.dump()
        print("read all papers")

        # --- 요약 실행 준비 ---
        sys_msg = self.prompt_schema["roles"]["system"]
        user_template_lines = self.prompt_schema["roles"]["user_template"]

        output_parser = StrOutputParser()

        fields_block = build_fields_block(self.prompt_schema)
        print("basic pre-summary complete")

        # --- 논문별 요약 실행 ---
        for paper in self.papers:
            # - 자료준비 -
            blocks = paper.build_context_blocks_from_freq(self.prompt_schema)

            rag_context = {
                "metadata": {
                    "title": "알 수 없음",
                    "authors": [],
                    "year": "알 수 없음",
                    "journal": "알 수 없음",
                    "keywords": []
                },
                "intro_block": blocks["intro_block"],
                "methods_block": blocks["methods_block"],
                "results_block": blocks["results_block"],
            }
            user_prompt = assemble_user_prompt(
                user_template_lines=user_template_lines,
                fields_block=fields_block,
                schema=self.prompt_schema,
                rag_context=rag_context
            )
            paper.llm_input = f"{sys_msg}\n\n{user_prompt}"

            # if self.debug: print(f"\n{paper.llm_input}\n")

            # --- 호출 ---
            print("call chatgpt")
            llm_text = self.__call_openai_chat(sys_msg, user_prompt)
            paper.final_summary = llm_text
            print("\tyes")

            if self.debug:
                pass
            # parsed = validate_and_normalize(llm_text, self.prompt_schema)
            # paper.llm_summary = parsed

    def export(self, output_path: pathlib.Path):
        """
        LLM 요약 결과를 하나의 CSV 파일로 내보내는 함수.

        - 1행: prompt_schema.fields[].key 를 그대로 사용한 헤더
        - 2행 이후: 각 논문당 1행
          paper.llm_response_text (csv_line 형식)을 콤마로 분리해 사용
        """
        rows: list[list[str]] = []

        # 1) 헤더 생성 (필드 순서 고정)
        field_defs = self.prompt_schema.get("fields", [])
        header = [f["key"] for f in field_defs]
        rows.append(header)

        n_fields = len(header)

        # 2) 각 논문 row 생성
        for paper in self.papers:
            raw = paper.final_summary
            raw = raw.strip()

            if not raw:
                # LLM 결과가 없으면 빈 칸으로 채움 (스키마 길이에 맞춤)
                row = ["" for _ in range(n_fields)]
            else:
                # LLM이 준 csv_line을 기준으로 split
                cols = [c.strip() for c in raw.split(",")]

                # 필드 개수 보정 (스키마와 길이 맞추기)
                if len(cols) < n_fields:
                    cols.extend([""] * (n_fields - len(cols)))
                elif len(cols) > n_fields:
                    cols = cols[:n_fields]

                row = cols

            rows.append(row)

        # 3) CSV 파일로 쓰기
        write_csv(str(output_path) + "/result.csv", rows)

        if self.debug:
            print(f"[DEBUG] exported {len(self.papers)} papers to {output_path}")

