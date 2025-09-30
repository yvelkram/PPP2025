from utils import *
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
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
        ctx_policy = self.prompt_schema["context_policy"]
        user_template_lines = self.prompt_schema["roles"]["user_template"]

        llm_client = ChatOpenAI(model=self.llm, temperature=0)
        output_parser = StrOutputParser()

        fields_block = build_fields_block(self.prompt_schema)

        # --- 논문별 요약 실행
        for paper in self.papers:
            # (a) 컨텍스트 선택(선언적 정책 사용)
            ctx_blocks = select_context_from_sections(paper, self.ctx_policy)
            rag_context = {
                "metadata": paper.metadata,  # Paper.metadata 프로퍼티 제공(아래 utils.py 수정)
                **ctx_blocks
            }
            # (b) JSON 템플릿 + RAG 컨텍스트로 유저 프롬프트 조립
            user_prompt = assemble_user_prompt(
                user_template_lines=self.user_template_lines,
                fields_block=self.fields_block,
                schema=self.schema,
                rag_context=rag_context
            )

            prompt = ChatPromptTemplate.from_messages([
                ("system", self.sys_msg),
                ("user", user_prompt),
            ])
            chain = prompt | self.llm_client | self.output_parser

            raw = chain.invoke({})
            paper.llm_summary_raw = raw  # 원문 저장(디버깅용)

            # (c) 스키마 기반 파싱/정규화
            parsed = parse_llm_csv_line(raw, self.schema)
            paper.final_summary = normalize_fields(parsed, self.schema)  # 리스트[str] 반환

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
