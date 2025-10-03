from utils import *
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI
import pathlib

class PaperWork:
    papers: list[Paper]
    prompt_schema: dict
    llm: any
    debug: bool
    temp_path: str

    def __init__(self, pdf_master_path: pathlib.Path, prompt_path: pathlib.Path, llm, debug=False, temp_dir=".temp"):
        self.debug = debug
        self.temp_path = temp_dir
        self.llm = llm
        self.prompt_schema = load_prompt_schema(prompt_path)
        self.papers = load_paper(pdf_master_path)

    # --- PRIVATE ------------------------------------------------------------------------------------------------------

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

            paper.llm_summary_raw = f"{sys_msg}\n\n{user_prompt}"

            if self.debug:
                # 프롬프트 처음 600자 미리보기
                preview = paper.llm_summary_raw[:600].replace("\n", " ")
                print(f"[DEBUG] prompt preview for {paper.pdf_path.name}: {preview}...")

        # --- 검증 및 정규화
        for paper in self.papers:
            paper.validate_outputs(self.prompt_schema)
            paper.normalize_fields()

    def export(self, output_path: pathlib.Path):
        rows = []
        for paper in self.papers:
            row = paper.export_to_paper()
            rows.append(row)
        write_csv(str(output_path), rows)
        if self.debug: print(f"exported to {output_path}")
