import enum
from utils import *

# 단락 종류명
class SectionType(enum.Enum):
    METADATA = enum.auto()
    ABSTRACT = enum.auto()
    INTRODUCTION = enum.auto()
    METHODS = enum.auto()
    RESULTS = enum.auto()
    DISCUSSION = enum.auto()
    LIMITATIONS = enum.auto()
    CONCLUSION = enum.auto()
    TABLE = enum.auto()
    FIGURE = enum.auto()
    REFERENCES = enum.auto()
    OTHER = enum.auto()


# 단일 섹션
class Section:
    section_type: SectionType
    title: str
    text: str

    is_asset: bool
    asset_caption: str | None
    asset_data: dict | None

# 단일 논문
class Paper:
    pdf_path: str
    metadata: dict           # title, authors, year, doi, journal 등
    sections: list[Section]  # 본문 섹션
    raw_text: list[str]      # 페이지별 원문 텍스트
    assets_path: str | None  # 표/그림 임시 저장 위치
    llm_summary: dict

# 변환 프로세스
class PaperWork:
    papers: list[Paper]
    prompt_schema: dict
    llm: any
    embeddings: any
    retriever_factory: callable
    debug: bool
    cache_dir: str
    tmp_dir: str

    def __init__(self, pdf_paths: list[str], prompt_path: str, llm,
                 debug=False, cache_dir=".cache", temp_dir=".temp"):
        self.debug = debug
        self.cache_dir = cache_dir
        self.tmp_dir = temp_dir
        self.llm = llm
        self.prompt_schema = load_prompt_schema(prompt_path)
        self.papers = load_paper(pdf_paths)


    def process(self):
        pass

    def export(self):
        pass