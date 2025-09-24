import enum
from utils import *

# 단락 종류명
class SectionType(enum.Enum):
    pass


# 단일 섹션
class Section:
    section_type: SectionType
    title: str
    text: str

    is_data: bool
    caption: str | None
    payload: dict | None

# 단일 논문
class Paper:
    pdf_path: str
    metadata: dict
    

# 변환 프로세스
class PaperWork:
    papers: [Paper]

