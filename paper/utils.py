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

    def score_chunk_by_terms(self, term_weights: dict[str, float]) -> float:
        """
        청크를 term_weights의 가중치 정보로 점수화
        """
        terms: dict[str, int] = self.chunk_indexed.get("terms", {})
        score: float = 0.0
        for term, w in term_weights.items():
            score += w * float(terms.get(term.lower(), 0))  # 소문자 기준
        return score

@dataclass
class Asset:
    asset_title: str    # 에셋 명 (Fig. 1)
    asset_caption: str  # 에셋 캡션
    asset_data: any     # 에셋 데이터 위치

# --- MAIN MODULE ------------------------------------------------------------------------------------------------------
class Paper:
    def __init__(self, pdf_path):
        self.pdf_path: pathlib.Path = pdf_path  # 원본 파일 위치

        self.raw_text: str = ""        # 원문 텍스트
        self.chunks: list[Chunk] = []  # 분할되어 가공된 텍스트
        self.assets: list[Asset] = []  # 논문의 표, 그림 등

        self.llm_summary_raw: str = ""
        self.final_summary: any = None  # 콤마로 구분된 최종 요약물

    # --- PRIVATE ------------------------------------------------------------------------------------------------------
    @staticmethod
    def __join_chunks_with_limit(chunks: list[Chunk], max_chars: int) -> str:
        """문자수 제한 안에서 청크들을 순서대로 결합"""
        out, used = [], 0
        for c in chunks:
            t = c.chunk_text.strip()
            if used + len(t) + 2 > max_chars:
                remain = max_chars - used - 2
                if remain > 0:
                    out.append(t[:remain])
                break
            out.append(t)
            used += len(t) + 2  # \n\n 여유
        return "\n\n".join(out)

    def __select_chunks_by_keywords(self, keyword_groups: list[str], top_k: int, ) -> list[Chunk]:
        """
        키워드 목록으로 청크 점수화 후 상위 K개 선택.
        keyword_groups는 'introduction', 'methods' 같은 섹션명 힌트가 아니라,
        실제 점수화에 쓸 토큰 문자열 리스트입니다.
        """
        # 간단 가중치: 모든 키워드 1.0
        weights = {k.lower(): 1.0 for k in keyword_groups if k and k.strip()}
        scored = [(c, c.score_chunk_by_terms(weights)) for c in self.chunks]
        # 점수 0인 것도 fallback을 위해 포함하되, 높은 점수부터
        scored.sort(key=lambda x: x[1], reverse=True)
        picked = [c for c, s in scored[:max(1, top_k)]]
        return picked

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
            top_terms = sorted(terms.items(), key=lambda x: x[1], reverse=True)[:30]

            index_dict = {"lenght": len(tokens), "terms": terms, "top_terms": top_terms}
            chunk.chunk_indexed = index_dict

    def build_context_blocks_from_freq(self, schema: dict) -> dict:
        """
        스키마의 context_policy(top_k, max_chars)를 반영하여
        intro/methods/results 블록을 빈도 기반으로 구성
        """
        kw_intro = ["introduction", "background", "overview", "motivation", "문헌", "배경", "서론", "관련연구"]
        kw_methods = ["method", "methods", "methodology", "data", "dataset", "실험", "모형", "모델", "자료", "변수", "방법"]
        kw_results = ["result", "results", "finding", "findings", "discussion", "conclusion", "시사점", "결과", "논의", "결론"]

        cp = schema.get("context_policy", {})
        intro_cfg = cp.get("intro_block", {})
        methods_cfg = cp.get("methods_block", {})
        results_cfg = cp.get("results_block", {})

        intro_top_k = int(intro_cfg.get("top_k", 6))
        methods_top_k = int(methods_cfg.get("top_k", 8))
        results_top_k = int(results_cfg.get("top_k", 8))

        intro_max = int(intro_cfg.get("max_chars", 2500))
        methods_max = int(methods_cfg.get("max_chars", 3000))
        results_max = int(results_cfg.get("max_chars", 3000))

        # 상위 K 청크 선정
        intro_chunks = self.__select_chunks_by_keywords(kw_intro, top_k=intro_top_k)
        methods_chunks = self.__select_chunks_by_keywords(kw_methods, top_k=methods_top_k)
        results_chunks = self.__select_chunks_by_keywords(kw_results, top_k=results_top_k)

        # 문자수 제한 내 결합
        intro_text = self.__join_chunks_with_limit(intro_chunks, intro_max)
        methods_text = self.__join_chunks_with_limit(methods_chunks, methods_max)
        results_text = self.__join_chunks_with_limit(results_chunks, results_max)

        return {
            "intro_block": intro_text,
            "methods_block": methods_text,
            "results_block": results_text,
        }

    def dump(self, preview_chars: int = 160) -> None:
        """
        객체의 내용을 덤프하는 기능
        """
        print(f"[DEBUG] file = {self.pdf_path.name}, sections = {len(self.chunks)}")
        for c in self.chunks[:5]:  # 앞부분만 미리보기
            txt = (c.chunk_text[:preview_chars] + "…") if len(c.chunk_text) > preview_chars else c.chunk_text
            print(f"  - #{c.chunk_no} ({len(c.chunk_text)} chars): {txt.replace('\\n', ' ')}")

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


def assemble_user_prompt(*, user_template_lines: list[str], fields_block: str, schema: dict, rag_context: dict) -> str:
    """
    prompt_schema.json의 user_template(list[str])에 rag_context를 채워 넣어 최종 문자열로 변환
    """
    # 메타 블록은 key: value 줄바꿈 나열
    meta = rag_context.get("metadata", {}) or {}
    meta_lines = []
    include_list = schema.get("context_policy", {}).get("metadata_block", {}).get("include", [])
    if include_list:
        for k in include_list:
            v = meta.get(k, "n/a")
            # authors, keywords가 리스트면 join
            if isinstance(v, list):
                v = ", ".join(v) if v else "n/a"
            meta_lines.append(f"- {k}: {v}")
    metadata_block = "\n".join(meta_lines) if meta_lines else "n/a"

    # 필드 헤더
    fields_block_text = fields_block

    _fmt = {
        "metadata_block": metadata_block,
        "intro_block": rag_context.get("intro_block", ""),
        "methods_block": rag_context.get("methods_block", ""),
        "results_block": rag_context.get("results_block", ""),
        "fields_block": fields_block_text
    }
    return "\n".join(user_template_lines).format(**_fmt)
