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

        self.llm_input: str = ""
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

    def dump(self, output_path: str,
             include_raw_text: bool, include_chunk: bool, include_asset: bool) -> None:
        """
        객체의 내용을 덤프하는 기능.

        - output_path 가 None 이면: 간단한 콘솔용 프리뷰만 출력 (기존 동작 유지)
        - output_path 가 주어지면: 상세 내용을 txt 파일로 저장
        """
        output_path = pathlib.Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        lines: list[str] = []

        # --- pdf 경로 ---
        lines.append("### pdf 경로 ###")
        lines.append(str(self.pdf_path))
        lines.append("")

        # --- raw_text ---
        if include_raw_text:
            lines.append("raw_text:")
            if self.raw_text:
                lines.append(self.raw_text)
            else:
                lines.append("[empty]")
            lines.append("")

        # --- chunks ---
        if include_chunk:
            lines.append("chunks:")
            if not self.chunks:
                lines.append("[no chunks]")
            else:
                for i, c in enumerate(self.chunks):
                    lines.append(f"{i} - chunk_no={c.chunk_no}")
                    lines.append("chunk_text:")
                    # chunk_text 그대로 기록 (줄바꿈 유지)
                    lines.append(c.chunk_text if c.chunk_text else "[empty]")
                    lines.append("chunk_indexed:")
                    # dict -> 문자열
                    try:
                        import json
                        lines.append(json.dumps(c.chunk_indexed, ensure_ascii=False, indent=2))
                    except Exception:
                        lines.append(str(c.chunk_indexed))
                    lines.append("")  # 청크 사이 빈 줄

            lines.append("")

        # --- assets ---
        if include_asset:
            lines.append("assets:")
            if not self.assets:
                lines.append("[no assets]")
            else:
                for i, a in enumerate(self.assets):
                    lines.append(f"{i} - asset_title: {a.asset_title}")
                    lines.append("asset_caption:")
                    lines.append(a.asset_caption if a.asset_caption else "[empty]")
                    lines.append("asset_data:")
                    lines.append(str(a.asset_data))
                    lines.append("")

            lines.append("")

        # --- llm_input ---
        lines.append("llm_input:")
        lines.append(self.llm_input if self.llm_input else "[empty]")
        lines.append("")

        # --- llm_summary_raw (gpt 호출 결과 원문) ---
        lines.append("llm_summary_raw:")
        lines.append(self.llm_summary_raw if self.llm_summary_raw else "[empty]")
        lines.append("")

        # --- final_summary (정규화된 최종 요약이 있다면) ---
        lines.append("final_summary:")
        if self.final_summary is None:
            lines.append("[empty]")
        else:
            # dict/list일 수도 있으니 json으로 한 번 정리
            try:
                import json
                lines.append(json.dumps(self.final_summary, ensure_ascii=False, indent=2))
            except Exception:
                lines.append(str(self.final_summary))
        lines.append("")

        # 실제 파일 저장
        with open(output_path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))

        print(f"[DEBUG] Paper dump written to {output_path}")

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
