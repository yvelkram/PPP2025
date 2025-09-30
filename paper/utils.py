import re
import csv
import json
import pypdf
import pathlib
from dataclasses import dataclass

# --- STRUCTURE --------------------------------------------------------------------------------------------------------
@dataclass
class Chunk:
    chunk_no: int        # 청크 일련번호
    chunk_text: str      # 청크 원본텍스트
    chunk_indexed: dict  # 청크 인덱스

@dataclass
class Asset:
    asset_title: str    # 에셋 명 (Fig. 1)
    asset_caption: str  # 에셋 캡션
    asset_data: any     # 에셋 데이터 위치

# --- MAIN MODULE ------------------------------------------------------------------------------------------------------
class Paper:
    pdf_path: pathlib.Path   # 원본 파일 위치
    title: str
    authors: str
    year: int

    raw_text: str        # 원문 텍스트
    chunks: list[Chunk]  # 분할되어 가공된 텍스트
    assets: list[Asset]  # 논문의 표, 그림 등

    llm_summary_raw: str
    final_summary: any   # 콤마로 구분된 최종 요약물

    def __init__(self, pdf_path):
        self.pdf_path = pdf_path

    # --- PRIVATE ------------------------------------------------------------------------------------------------------


    # --- PUBLIC -------------------------------------------------------------------------------------------------------
    def parse_pdf(self, chunk_chars: int = 2500, overlap_chars: int = 300) -> None:
        """
        논문 pdf를 불러와서 sections로 분리하는 기능
        :param chunk_chars: 한 청크당 글자수
        :param overlap_chars: 겹쳐지는 글자수
        """
        # --- pdf 파일에서 텍스트 추출
        reader = pypdf.PdfReader(str(self.pdf_path))
        texts: list[str] = []
        for i, page in enumerate(reader.pages):
            t = page.extract_text()
            texts.append(t)
        self.raw_text = "\n".join(texts).strip()

        # --- 텍스트를 일정 길이로 청크화
        text_length = len(self.raw_text)
        start = 0
        i = 0
        step = chunk_chars - overlap_chars  # 시작점 = 한 청크당 글자수 - 오버랩 글자수
        while start < text_length:
            end = min(start + chunk_chars, text_length)
            self.chunks.append(Chunk(i, self.raw_text[start:end], dict()))
            start += step
            i += 1

    def retrieval_paper(self) -> None:
        """
        논문 데이터 인덱싱, 용어-빈도 인덱스 생성
        """
        for chunk in self.chunks:
            tokens = [t.lower()  # 소문자화
                      for t in re.findall(r"[A-Za-z0-9]+|[가-힣]+", chunk.chunk_text)  # 글자만 추출
                      if len(t) > 1]  # 한글자는 노이즈로 간주
            terms: dict[str, int] = {}
            for token in tokens:
                terms[token] = terms.get(token, 0) + 1
            top_terms = sorted(terms.items(), key=lambda x: x[1], reverse=True[:30])

            index_dict = {"lenght": len(tokens), "terms": terms, "top_terms": top_terms}
            chunk.chunk_indexed = index_dict

    def dump(self, preview_chars: int = 160) -> None:
        """
        객체의 내용을 덤프하는 기능
        """
        print(f"[DEBUG] file = {self.pdf_path.name}, sections = {len(self.chunks)}")
        for c in self.chunks[:5]:  # 앞부분만 미리보기
            txt = (c.chunk_text[:preview_chars] + "…") if len(c.chunk_text) > preview_chars else c.chunk_text
            print(f"  - #{c.chunk_no} ({len(c.chunk_text)} chars): {txt.replace('\\n', ' ')}")

    def validate_outputs(self, prompt_schema) -> None:
        raise NotImplementedError

    def normalize_fields(self) -> None:
        raise NotImplementedError

    def export_to_paper(self):
        raise NotImplementedError


# --- COMMON FEATURES --------------------------------------------------------------------------------------------------
def load_prompt_schema(prompt_path: pathlib.Path) -> dict:
    """
    프롬프트 불러오기 (json 양식)
    :param prompt_path: 파일 경로
    :return: json
    """
    with open(pathlib.Path(prompt_path), "r", encoding="utf-8") as f:
        return json.load(f)


def load_paper(pdf_master_path: pathlib.Path) -> list[Paper]:
    """
    주어진 폴더의 파일들을 불러오는 함수
    :param pdf_master_path: 주어진 폴더
    :return: 논문 객체
    """
    pdf_files = sorted(pdf_master_path.glob("*.pdf"))

    return [Paper(pdf) for pdf in pdf_files]


def write_csv(path: str, rows: list[list[str]]) -> None:
    pathlib.Path(path).parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        for r in rows:
            writer.writerow(r)

# LLM FEATURES ---------------------------------------------------------------------------------------------------------
def build_fields_block(schema: dict) -> str:
    """
    프롬프트의 항목을 한줄로 생성
    :param schema: 프롬프트
    :return: 한줄로 만들어진 항목
    """
    return ", ".join([f["key"] for f in schema["fields"]])


def format_list_inline(items: list[str], prefix: str) -> str:
    """
    하위항목 리스트를 한줄로 병합
    :param items: 하위항목 리스트
    :param prefix: 구분자
    :return: 한줄로 만들어진 하위항목 내용
    """
    line = [i.strip() for i in items if i and i.strip()]
    return " ".join([f"{prefix}{s}" for s in line])

