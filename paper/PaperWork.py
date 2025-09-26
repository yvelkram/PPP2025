from utils import *
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
import pathlib


# 변환 프로세스
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


    def process(self):
        # 논문 파일 파싱
        for paper in self.papers:
            paper.parse_pdf()
            paper.retrieval_paper()
            if self.debug: dump(paper, stage="parsed")

        # 논문 요약 실행
        schema = self.prompt_schema
        sys_msg = schema["roles"]["system"]
        ctx_policy = schema["context_policy"]

        llm = ChatOpenAI(model=self.llm, temperature=0)  # 일관 출력
        output_parser = StrOutputParser()

        for paper in self.papers:
            # 2-1) 컨텍스트 선택(선언적 정책 사용)
            ctx_blocks = select_context_from_sections(paper, ctx_policy)
            rag_context = {
                "metadata": paper.metadata,
                **ctx_blocks
            }
            # 2-2) JSON의 user_template + rag_context로 프롬프트 조립
            user_prompt = assemble_user_prompt(schema, rag_context)

            prompt = ChatPromptTemplate.from_messages([
                ("system", sys_msg),
                ("user", user_prompt)
            ])

            chain = prompt | llm | output_parser

            raw = chain.invoke({})
            paper.llm_summary = raw  # 원문 저장(디버깅용)
            if self.debug: dump(paper, stage="llm_summary")

            # 2-3) 스키마 기반 파싱/정규화
            parsed = parse_llm_csv_line(raw, schema)
            paper.final_summary = normalize_fields(parsed, schema)

        # 검증 및 정규화
        for paper in self.papers:
            paper.validate_outputs(self.prompt_schema)
            paper.normalize_fields()

    def export(self, output_path: str):
        rows = []
        for paper in self.papers:
            row = paper.export_to_paper()
            rows.append(row)
        write_csv(output_path, rows)
        if self.debug: print(f"exported to {output_path}")
