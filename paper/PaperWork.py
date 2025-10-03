from utils import *
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI
from openai import OpenAI
import pathlib
import time

class PaperWork:
    papers: list[Paper]
    prompt_schema: dict
    llm: any
    debug: bool
    temp_path: str

    def __init__(self, pdf_master_path: pathlib.Path, prompt_path: pathlib.Path, llm, debug=False, temp_dir=".temp"):
        self.debug = debug
        self.temp_path = temp_dir
        self.prompt_schema = load_prompt_schema(prompt_path)
        self.papers = load_paper(pdf_master_path)

        # llm setting
        self.llm = llm
        self.max_retries: int = 3
        self.request_timeout_sec: int = 120

    # --- PRIVATE ------------------------------------------------------------------------------------------------------
    def __call_openai_chat(self, system_msg: str, user_msg: str) -> str:
        """
        system/user 메시지로 OpenAI Chat API 호출하여 텍스트를 반환.
        - 재시도(간단 백오프) 내장
        - 모델은 self.model 사용
        """
        client = OpenAI()  # OPENAI_API_KEY 사용

        messages = [
            {"role": "system", "content": system_msg},
            {"role": "user", "content": user_msg},
        ]

        last_err = None
        for attempt in range(1, self.max_retries + 1):
            try:
                # Chat Completions 스타일
                resp = client.chat.completions.create(
                    model=self.llm,
                    messages=messages,
                    temperature=0,
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
        # 논리상 여기 오지 않음
        raise last_err

    # --- PUBLIC -------------------------------------------------------------------------------------------------------
    def process(self):
        # --- 논문 파일 파싱
        for paper in self.papers:
            paper.parse_pdf()
            paper.retrieval_paper()
            if self.debug: paper.dump()

        # --- 요약 실행 준비
        sys_msg = self.prompt_schema["roles"]["system"]
        user_template_lines = self.prompt_schema["roles"]["user_template"]

        llm_client = ChatOpenAI(model=self.llm, temperature=0)
        output_parser = StrOutputParser()

        fields_block = build_fields_block(self.prompt_schema)

        # --- 논문별 요약 실행
        for paper in self.papers:
            # 1) 블록 텍스트(빈도 기반) 만들기
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

            input_text = f"{sys_msg}\n\n{user_prompt}"
            print(input_text)

            paper.llm_prompt_system = sys_msg
            paper.llm_prompt_user = user_prompt
            paper.llm_summary_raw = f"{sys_msg}\n\n{user_prompt}"

            if self.debug:
                preview = paper.llm_summary_raw[:600].replace("\n", " ")
                print(f"[DEBUG] prompt preview for {paper.pdf_path.name}: {preview}...")

            # (신규) 실제 모델 호출 (옵션)
            if self.llm:
                try:
                    llm_text = self.__call_openai_chat(sys_msg, user_prompt)
                    # 결과 저장 지점(가벼운 후처리 훅 포함)
                    paper.llm_response_text = llm_text

                    if self.debug:
                        print(
                            f"[DEBUG] LLM response head for {paper.pdf_path.name}: {llm_text[:400].replace('\n', ' ')}...")

                    # ↓ 후속 파이프라인 자리: 검증/정규화가 준비되면 여기에 연결
                    # parsed = validate_and_normalize(llm_text, self.prompt_schema)
                    # paper.llm_summary = parsed
                except Exception as e:
                    paper.llm_error = repr(e)
                    if self.debug:
                        print(f"[ERROR] LLM call failed for {paper.pdf_path.name}: {e}")
            else:
                if self.debug:
                    print(f"[DEBUG] execute_llm=False → call skipped for {paper.pdf_path.name}")


    def export(self, output_path: pathlib.Path):
        rows = []
        for paper in self.papers:
            row = paper.export_to_paper()
            rows.append(row)
        write_csv(str(output_path), rows)
        if self.debug: print(f"exported to {output_path}")
