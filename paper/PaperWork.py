from utils import *
from langchain_core.output_parsers import StrOutputParser
from openai import OpenAI, embeddings
import pathlib
import time

class PaperWork:
    papers: list[Paper]
    prompt_schema: dict
    llm_model_name: str
    debug: bool
    temp_path: str

    def __init__(self, pdf_master_path: pathlib.Path, prompt_path: pathlib.Path, llm_model_name, embedding_model_name,
                 temperature=0.0, debug=False, temp_dir=".temp"):
        self.debug = debug
        self.temp_path = temp_dir
        self.prompt_schema = load_prompt_schema(prompt_path)
        self.papers = load_paper(pdf_master_path)

        # llm setting
        self.temperature = temperature
        self.llm_model_name = llm_model_name
        self.embedding_model_name = embedding_model_name
        self.max_retries: int = 3
        self.request_timeout_sec: int = 120

    # --- PRIVATE ------------------------------------------------------------------------------------------------------
    def __llm_summarize(self, system_msg: str, user_msg: str) -> str:
        """
        system/user 메시지로 OpenAI Chat API 호출하여 텍스트를 반환.
        """
        messages = [
            {"role": "system", "content": system_msg},
            {"role": "user", "content": user_msg},
        ]

        client = OpenAI()
        for attempt in range(1, self.max_retries + 1):
            try:
                # Chat Completions 스타일
                resp = client.chat.completions.create(
                    model=self.llm_model_name,
                    messages=messages,
                    timeout=self.request_timeout_sec,
                    temperature=self.temperature
                )
                text = resp.choices[0].message.content or ""
                return text.strip()

            except Exception as e:
                if attempt < self.max_retries:
                    # 간단한 지수 백오프
                    time.sleep(1.5 * attempt)
                else:
                    raise e
        return ""

    def __llm_create_embeddings(self, input_texts: list[str]) -> list[list[float]]:
        """
        인베딩 호출하여 생성
        """
        client = OpenAI()

        resp = client.embeddings.create(
            model=self.embedding_model_name,
            input=input_texts,
        )
        return [d.embedding for d in resp.data]

    def __llm_create_quary_embedding(self, input_text: str) -> list[float]:
        """
        임베딩 질문 문구를 임베딩함
        """
        client = OpenAI()

        resp = client.embeddings.create(
            model=self.embedding_model_name,
            input=[input_text],
        )
        return resp.data[0].embedding

    # --- PUBLIC -------------------------------------------------------------------------------------------------------
    def process(self):
        print("[INFO] start PaperWork")
        # --- 논문 파일 파싱
        for paper in self.papers:
            paper.parse_pdf()
            paper.retrieval_paper()
            paper.prepare_embeddings(self.__llm_create_embeddings, self.embedding_model_name)
        print(f"[INFO] read all papers : [{len(self.papers)}] papers")

        # --- 요약 실행 준비
        sys_msg = self.prompt_schema["roles"]["system"]
        user_template_lines = self.prompt_schema["roles"]["user_template"]

        fields_block = build_fields_block(self.prompt_schema)
        print("[INFO] basic pre-summary complete")

        # --- 논문별 요약 실행
        for paper in self.papers:
            # - 자료준비
            blocks = paper.build_context_blocks_from_embedding(self.prompt_schema,
                                                               self.__llm_create_quary_embedding)

            rag_context = {
                "intro_block": blocks.get("intro_block", ""),
                "methods_block": blocks.get("methods_block", ""),
                "results_block": blocks.get("results_block", ""),
            }
            user_prompt = assemble_user_prompt(
                user_template_lines=user_template_lines,
                fields_block=fields_block,
                schema=self.prompt_schema,
                rag_context=rag_context,
            )
            paper.llm_input = f"{sys_msg}\n\n{user_prompt}"

            # if self.debug: print(f"\n{paper.llm_input}\n")

            # - 호출
            print("[GPT] call chatgpt")
            llm_text = self.__llm_summarize(sys_msg, user_prompt)
            paper.llm_summary_raw = llm_text
            print(f"[GPT] get response : {paper.llm_summary_raw[0:100]}")

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
        for n, paper in enumerate(self.papers):
            raw = paper.llm_summary_raw.strip()

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
            paper.final_summary = row

            if self.debug:
                paper.dump(str(output_path) + f"/{n}.csv")

        # 3) CSV 파일로 쓰기
        write_csv(str(output_path) + "/result.csv", rows)

        if self.debug:
            print(f"[DEBUG] exported {len(self.papers)} papers to {output_path}")

