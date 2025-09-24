from utils import *
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI


# 변환 프로세스
class PaperWork:
    papers: list[Paper]
    prompt_schema: dict
    llm: any
    debug: bool
    temp_path: str

    def __init__(self, pdf_paths: list[str], prompt_path: str, llm, debug=False, temp_dir=".temp"):
        self.debug = debug
        self.temp_path = temp_dir
        self.llm = llm
        self.prompt_schema = load_prompt_schema(prompt_path)
        self.papers = load_paper(pdf_paths)


    def process(self):
        # 논문 파일 파싱
        for paper in self.papers:
            paper.parse_pdf()        # pdf 읽어들이기
            paper.retrieval_paper()  # 인덱싱하기
            if self.debug: dump(paper, stage="parsed")

        # 논문 요약 실행
        chain = ChatPromptTemplate(self.prompt_schema) | ChatOpenAI(model=self.llm)
        for paper in self.papers:
            paper.select_context()
            paper.llm_summary = chain.invoke(paper.rag_context)
            if self.debug: dump(paper, stage="llm_summary")

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
        