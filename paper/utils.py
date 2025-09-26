import re
import json
import pathlib

# --- STRUCTURE --------------------------------------------------------------------------------------------------------
# 단일 섹션
class Section:
    section_title: str  # 단락 명 (1. Introduction 또는 2.1. SVF application possibilities)
    text: str           # 단락 내용
    indexed_text: any   # 인덱싱된 내용

class Asset:
    asset_title: str    # 에셋 명 (Fig. 1)
    asset_caption: str  # 에셋 캡션
    asset_data: any     # 에셋 데이터 위치

# 단일 논문
class Paper:
    pdf_path: pathlib.Path   # 원본 파일 위치
    metadata: dict           # title, authors, year, doi, journal 등
    sections: list[Section]  # 본문 섹션 데이터
    assets: list[Asset]      # 논문의 표, 그림 등
    raw_text: list[str]      # 페이지별 원문 텍스트
    final_summary: any       # 콤마로 구분된 최종 요약물

    def __init__(self, pdf_path):
        self.pdf_path = pdf_path


    def parse_pdf(self) -> None:
        """
        논문 pdf를 불러와서 sections로 분리하는 기능
        """
        # 파일 열기, self.raw_text에 전체 택스트 저장
        pass

        # 섹션별로 데이터 소분, self.sections에 저장.
        # 표, 그림은 self.assets에 저장. (캡션 번호가 key, 단락 내용이 valye)
        pass


    def retrieval_paper(self) -> None:
        """
        논문 데이터 인덱싱
        """
        # 각각 self.sections의 .text 내용을 인덱싱하여 .indexed_text에 저장
        pass

    def select_context(self) -> None:
        pass

    def validate_outputs(self, prompt_schema) -> None:
        pass

    def normalize_fields(self) -> None:
        pass

    def export_to_paper(self):
        pass


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


def dump(paper: Paper, stage: str) -> None:
    """
    Paper 객체 덤프
    :param paper: 객체
    :param stage: 각 단계별
    """
    pass


def write_csv(output_path: str, rows: list[str]) -> None:
    """
    최종 파일 제작
    :param output_path: 저장 위치
    :param rows: 저장할 데이터들
    """
    pass


# LLM FEATURES ---------------------------------------------------------------------------------------------------------
def build_fields_block(schema: dict) -> str:
    """
    프롬프트의 항목을 한줄로 생성
    :param schema: 프롬프트
    :return: 한줄로 만들어진 항목
    """
    return ", ".join([f["key"] for f in schema["fields"]])


def escape_commas(text: str, escape_comma: str) -> str:
    # 콤마 전환 기능 (아직 이해못함)
    if text is None:
        return ""
    return text.replace(",", escape_comma)


def format_list_inline(items: list[str], prefix: str) -> str:
    """
    하위항목 리스트를 한줄로 병합
    :param items: 하위항목 리스트
    :param prefix: 구분자
    :return: 한줄로 만들어진 하위항목 내용
    """
    line = [i.strip() for i in items if i and i.strip()]
    return " ".join([f"{prefix}{s}" for s in line])


def assemble_user_prompt(schema: dict, rag_ctx: dict) -> str:
    """
    LLM에 넣을 프롬프트 조립
    :param schema:
    :param rag_ctx:
    :return:
    """
    tpl_lines = schema["roles"]["user_template"]
    comma_escape = schema["output"]["comma_escape_char"]
    list_prefix = schema["output"]["list_item_prefix"]

    # metadata block
    md = rag_ctx.get("metadata", {})
    md_lines = []
    for k in ["title","authors","year","journal","keywords"]:
        v = md.get(k, "")
        if isinstance(v, list):
            v = ", ".join(v)
        md_lines.append(f"- {k}: {escape_commas(str(v), comma_escape)}")
    metadata_block = "\n".join(md_lines)

    # intro/methods/results block (이미 select_context에서 만들어온 요약 문자열 사용)
    intro_block = escape_commas(rag_ctx.get("intro_block", ""), comma_escape)
    methods_block = escape_commas(rag_ctx.get("methods_block", ""), comma_escape)
    results_block = escape_commas(rag_ctx.get("results_block", ""), comma_escape)

    fields_block = build_fields_block(schema)

    prompt = "\n".join(tpl_lines)
    prompt = prompt.replace("{metadata_block}", metadata_block)
    prompt = prompt.replace("{intro_block}", intro_block)
    prompt = prompt.replace("{methods_block}", methods_block)
    prompt = prompt.replace("{results_block}", results_block)
    prompt = prompt.replace("{fields_block}", fields_block)
    return prompt


def parse_llm_csv_line(raw: str, schema: dict) -> dict:
    # 아주 단순한 CSV-like 파서 (필드 개수로 split)
    keys = [f["key"] for f in schema["fields"]]
    parts = [p.strip() for p in raw.split(",")]
    if len(parts) < len(keys):
        parts += [""] * (len(keys) - len(parts))
    parts = parts[:len(keys)]
    return dict(zip(keys, parts))


def normalize_fields(parsed: dict, schema: dict) -> dict:
    # 리스트형 필드는 "*항목1 *항목2"를 다시 리스트로 복원해서 저장(내보낼 땐 다시 인라인)
    list_prefix = schema["output"]["list_item_prefix"]
    list_keys = {f["key"] for f in schema["fields"] if f["type"] == "list"}
    out = {}
    for k, v in parsed.items():
        if k in list_keys:
            # "*a *b" -> ["a","b"]
            items = [s.strip() for s in v.split(list_prefix) if s.strip()]
            out[k] = items
        else:
            out[k] = v.strip()
    return out


def to_csv_line_for_export(rec: dict, schema: dict) -> str:
    # 내보낼 때: 리스트는 다시 "*a *b"로 합치고, 내부 콤마는 이미 전각으로 치환되어 있다고 가정
    list_prefix = schema["output"]["list_item_prefix"]
    ordered = []
    for f in schema["fields"]:
        k = f["key"]
        v = rec.get(k, "")
        if isinstance(v, list):
            v = " ".join([f"{list_prefix}{x}" for x in v])
        ordered.append(v)
    return ",".join(ordered)


def select_context_from_sections(paper, context_policy: dict) -> dict:
    # 실제 구현에서는 embedding/RAG를 써서 top_k 선택.
    # 여기서는 구조만: 섹션 이름으로 필터 후 상위 k개 문단을 이어 붙이고 글자수 제한 적용.
    def gather(section_names, top_k, max_chars):
        chunks = []
        # paper.sections: Section(section_title, text, indexed_text)
        for s in paper.sections:
            title = (s.section_title or "").lower()
            if any(name in title for name in section_names):
                # indexed_text가 있다면 그 중 score 상위 k개를 사용했다고 가정
                if s.indexed_text and isinstance(s.indexed_text, list):
                    # [(score, text), ...] 형태라고 가정
                    tops = sorted(s.indexed_text, key=lambda x: x[0], reverse=True)[:top_k]
                    chunks.extend([t[1] for t in tops])
                else:
                    chunks.append(s.text)
        joined = " ".join(chunks)[:max_chars]
        return joined

    return {
        "intro_block":   gather(context_policy["intro_block"]["sections"],
                                context_policy["intro_block"]["top_k"],
                                context_policy["intro_block"]["max_chars"]),
        "methods_block": gather(context_policy["methods_block"]["sections"],
                                context_policy["methods_block"]["top_k"],
                                context_policy["methods_block"]["max_chars"]),
        "results_block": gather(context_policy["results_block"]["sections"],
                                context_policy["results_block"]["top_k"],
                                context_policy["results_block"]["max_chars"])
    }
