import csv
import json
import pathlib
from paper import FullPaper

# --- COMMON FEATURES --------------------------------------------------------------------------------------------------
def load_prompt_schema(prompt_path: pathlib.Path) -> dict:
    """
    프롬프트 불러오기 (json 양식)
    :param prompt_path: 파일 경로
    :return: json
    """
    with open(pathlib.Path(prompt_path), "r", encoding="utf-8") as f:
        return json.load(f)


def load_paper(pdf_master_path: pathlib.Path) -> list[FullPaper]:
    """
    주어진 폴더의 파일들을 불러오는 함수
    :param pdf_master_path: 주어진 폴더
    :return: 논문 객체
    """
    pdf_files = sorted(pdf_master_path.glob("*.pdf"))

    return [FullPaper(pdf) for pdf in pdf_files]


def write_csv(path: str, rows: list[list[str]]) -> None:
    pathlib.Path(path).parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        for r in rows:
            writer.writerow(r)

# --- LLM FEATURES -----------------------------------------------------------------------------------------------------
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


def assemble_user_prompt(*, user_template_lines: list[str], fields_block: str,
                         schema: dict, rag_context: dict,) -> str:
    """
    prompt_schema.json의 user_template(list[str])에 rag_context를 채워 넣어 최종 문자열로 변환
    """
    fields_block_text = fields_block

    _fmt = {
        "intro_block": rag_context.get("intro_block", ""),
        "methods_block": rag_context.get("methods_block", ""),
        "results_block": rag_context.get("results_block", ""),
        "fields_block": fields_block_text,
    }
    return "\n".join(user_template_lines).format(**_fmt)
