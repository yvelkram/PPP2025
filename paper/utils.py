import enum


# --- ENUM -------------------------------------------------------------------------------------------------------------
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

# --- STRUCTURE --------------------------------------------------------------------------------------------------------
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
    rag_context: dict        # RAG 적용한 압축
    llm_summary: any         # 최종 요약물

    def parse_pdf(self) -> None:
        pass

    def retrieval_paper(self) -> None:
        pass

    def select_context(self) -> None:
        pass

    def validate_outputs(self, prompt_schema) -> None:
        pass

    def normalize_fields(self) -> None:
        pass

    def export_to_paper(self):
        pass


# --- FEATURES ---------------------------------------------------------------------------------------------------------
def load_prompt_schema(prompt_path: str) -> dict:
    pass


def load_paper(pdf_paths: list[str]) -> list[Paper]:
    pass


def dump(paper: Paper, stage: str) -> None:
    pass


def write_csv(output_path: str, rows: list[str]) -> None:
    pass
