from utils import *
from paper import *
from openai import OpenAI
import pathlib
import time


# --- PAPERWORK MODULE -------------------------------------------------------------------------------------------------
class PrePaperWork:
    def __init__(self, ris_path: str, prompt_path: str, questions: str, model_name: str = "gpt-5"):
        self.ris_path: str = ris_path
        self.prompt_path = prompt_path
        self.questions: str = questions
        self.model_name = model_name

        self.papers: list[PrePaper] = []
        self.user_prompt: str = ""
        self.system_prompt: str = ""

        self.temperature: float = 1.0
        self.max_retries: int = 3
        self.request_timeout_sec: int = 60

    # --- PRIVATE ------------------------------------------------------------------------------------------------------
    def __read_ris(self) -> None:
        """
        Read ris file and add PrePaper object.
        """
        encoding = "utf-8"
        try:
            open(self.ris_path, encoding=encoding).close()
        except UnicodeDecodeError:
            encoding = "cp949"

        structure = {"title": "N/A",
                 "abstract": "N/A",
                 "doi": "N/A",
                 "database": "N/A",
                 "publish_year": "N/A",
                 "author": "N/A",
                 "keyword": "N/A"}
        current = structure.copy()
        with open(self.ris_path, encoding=encoding) as f:
            raw_texts = f.readlines()
        for ln in raw_texts:
            if ln.startswith("TI"):  # title
                current["title"] = ln[6:-1]
            elif ln.startswith("AB"):  # abstract
                current["abstract"] = ln[6:-1]
            elif ln.startswith("DO"):  # DOI
                current["doi"] = ln[6:-1]
            elif ln.startswith("DB"):  # database
                current["database"] = ln[6:-1]
            elif ln.startswith("PY"):  # publish_year
                current["publish_year"] = ln[6:-1]

            elif ln.startswith("AU"):  # author
                if current["author"] != "N/A":  # if there is multiple authors, combine with |
                    current["author"] += f"|{ln[6:-1]}"
                else:
                    current["author"] = ln[6:-1]
            elif ln.startswith("KW"):  # keyword
                if current["keyword"] != "N/A":  # if there is multiple keywords, combine with |
                    current["keyword"] += f"|{ln[6:-1]}"
                else:
                    current["keyword"] = ln[6:-1]

            elif ln.startswith("ER"):  # last record
                self.papers.append(PrePaper(current))
                current = structure.copy()  # need to init again for deep copy

    def __construct_prompt(self) -> None:
        """
        read prework_prompt_schema.json and self.questions to make final prompt
        """
        schema = load_prompt_schema(self.prompt_path)
        roles = schema["roles"]

        self.system_prompt = "\n".join(roles["system"])
        self.user_prompt = "\n".join(roles["user_template"])

    def __llm_quary(self, paper: PrePaper) -> bool:
        """
        llm deside either paper will accept as screening or not accept, with a reason
        :return: is responce correct?
        """
        client = OpenAI()

        user_msg = self.user_prompt.format(
            title=paper.texts.get("title", "N/A"),
            abstract=paper.texts.get("abstract", "N/A"),
            questions=self.questions)
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": user_msg},
        ]

        content: str = ""
        for attempt in range(1, self.max_retries + 1):
            try:
                resp = client.chat.completions.create(
                    model=self.model_name,
                    messages=messages,
                    temperature=self.temperature,
                    timeout=self.request_timeout_sec,
                )
                content = (resp.choices[0].message.content or "").strip()
                break
            except Exception as e:
                print(f"[WARN] llm_quary attempt {attempt} failed: {e}")
                if attempt < self.max_retries:
                    time.sleep(1.5 * attempt)
                    continue
                else:
                    # 더 이상 재시도하지 않음 → process()에서 while not __llm_quary 로 다시 한 바퀴
                    return False

        if not content:
            print("[INFO] llm_quary: empty response")
            return False

        first_line = ""
        for ln in content.splitlines():
            ln = ln.strip()
            if ln:
                first_line = ln
                break

        if not first_line:
            print("[INFO] llm_quary: no non-empty line in response")
            return False

        parts = [p.strip() for p in first_line.split(",", 2)]
        if len(parts) < 3:
            print(f"[INFO] llm_quary: malformed csv line: {first_line}")
            return False

        yn, keyword, reason = parts[0], parts[1], parts[2]
        yn = yn.upper()

        if yn not in ("Y", "N"):
            print(f"[INFO] llm_quary: first field is not Y/N: {yn}")
            return False

        # 5) PrePaper에 결과 기록
        if yn == "Y":
            paper.accept = True
            paper.reject_keyword = "N/A"
            paper.reject_reason = "N/A"
        else:
            paper.accept = False
            paper.reject_keyword = keyword or "N/A"
            paper.reject_reason = reason or "N/A"

        return True

    def __find_same_paper(self) -> None:
        """
        Find duplicated paper by PrePaper.texts[doi] value and mark PrePaper.duplicated to True
        """

        # doi로 중복 논문 찾아서, 중복시 변수로 플래그 세움

    # --- PUBLIC -------------------------------------------------------------------------------------------------------
    def process(self):
        print("[INFO] start ris reading")
        self.__read_ris()
        print("[INFO] search duplicated paper")
        self.__find_same_paper()
        print("[INFO] make final prompt")
        self.__construct_prompt()

        print("[INFO] start paper summary")
        for paper in self.papers:
            if paper.duplicated:  # don't quary duplicated paper
                continue
            while not self.__llm_quary(paper):
                continue

    def export(self, output_path: str):
        print("[INFO] make output.csv")
        """
        id | DOI | 저자 | 연도 | 제목 | 데이터베이스 | 검토자1 | 검토자2 | 검토일 | 중복여부 | 포함여부 | 배제사유키워드 | 배제사유내용 | 다음단계여부 
        1 | PrePaper.texts["doi"] | "author" | "publish_year" | "title" | "database" | 공백 | 공백 | 공백 | PrePaper.duplicated | PrePaper.accept | PrePaper.reject_keyword | PrePaper.reject_reason | accept면 진행, 아니면 배제    
        2 | 위와 동일하게 연장
        ...
        """

        print("[INFO] make summary.csv")
        """
        항목 | 검색된 총건수 | 중복 제거 후건수 | 제목·초록검토 대상건수 | 제목·초록 단계 배제건수 | 제목·초록 후 전문검토 대상건수 | 전문검토 후 최종 포함건수 | 전문단계 배제건수 | 비고
        숫자 | len(self.papers) | PrePaper.duplicated로 판단 | PrePaper.duplicated로 판단 | PrePaper.duplicated로 판단 | PrePaper.accept로 판단 | 공백 | 공백 | 공백
        """

        print("[INFO] make paper dump")
        for paper in self.papers:
            paper.dump()


class FullPaperWork:
    papers: list[FullPaper]
    prompt_schema: dict
    llm_model_name: str
    debug: bool
    temp_path: str

    def __init__(self, pdf_master_path: str, prompt_path: str, llm_model_name, embedding_model_name,
                 temperature=0.0, debug=False, temp_dir=".temp"):
        self.debug = debug
        self.temp_path = temp_dir
        self.prompt_schema = load_prompt_schema(prompt_path)
        self.papers = load_paper(pdf_master_path)

        # llm setting
        self.temperature = temperature
        self.llm_model_name = llm_model_name
        self.embedding_model_name = embedding_model_name
        self.max_retries: int = 3
        self.request_timeout_sec: int = 120

    # --- PRIVATE ------------------------------------------------------------------------------------------------------
    def __llm_summarize(self, system_msg: str, user_msg: str) -> str:
        """
        system/user 메시지로 OpenAI Chat API 호출하여 텍스트를 반환.
        """
        messages = [
            {"role": "system", "content": system_msg},
            {"role": "user", "content": user_msg},
        ]

        client = OpenAI()
        for attempt in range(1, self.max_retries + 1):
            try:
                # Chat Completions 스타일
                resp = client.chat.completions.create(
                    model=self.llm_model_name,
                    messages=messages,
                    timeout=self.request_timeout_sec,
                    temperature=self.temperature
                )
                text = resp.choices[0].message.content or ""
                return text.strip()

            except Exception as e:
                if attempt < self.max_retries:
                    # 간단한 지수 백오프
                    time.sleep(1.5 * attempt)
                else:
                    raise e
        return ""

    def __llm_create_embeddings(self, input_texts: list[str]) -> list[list[float]]:
        """
        인베딩 호출하여 생성
        """
        client = OpenAI()

        resp = client.embeddings.create(
            model=self.embedding_model_name,
            input=input_texts,
        )
        return [d.embedding for d in resp.data]

    def __llm_create_quary_embedding(self, input_text: str) -> list[float]:
        """
        임베딩 질문 문구를 임베딩함
        """
        client = OpenAI()

        resp = client.embeddings.create(
            model=self.embedding_model_name,
            input=[input_text],
        )
        return resp.data[0].embedding

    # --- PUBLIC -------------------------------------------------------------------------------------------------------
    def process(self):
        print("[INFO] start PaperWork")
        # --- 논문 파일 파싱
        for paper in self.papers:
            paper.parse_pdf()
            paper.retrieval_paper()
            paper.prepare_embeddings(self.__llm_create_embeddings, self.embedding_model_name)
        print(f"[INFO] read all papers : [{len(self.papers)}] papers")

        # --- 요약 실행 준비
        sys_msg = self.prompt_schema["roles"]["system"]
        user_template_lines = self.prompt_schema["roles"]["user_template"]

        fields_block = build_fields_block(self.prompt_schema)
        print("[INFO] basic pre-summary complete")

        # --- 논문별 요약 실행
        for paper in self.papers:
            # - 자료준비
            blocks = paper.build_context_blocks_from_embedding(self.prompt_schema,
                                                               self.__llm_create_quary_embedding)

            rag_context = {
                "intro_block": blocks.get("intro_block", ""),
                "methods_block": blocks.get("methods_block", ""),
                "results_block": blocks.get("results_block", ""),
            }
            user_prompt = assemble_user_prompt(
                user_template_lines=user_template_lines,
                fields_block=fields_block,
                schema=self.prompt_schema,
                rag_context=rag_context,
            )
            paper.llm_input = f"{sys_msg}\n\n{user_prompt}"

            # if self.debug: print(f"\n{paper.llm_input}\n")

            # - 호출
            print("[GPT] call chatgpt")
            llm_text = self.__llm_summarize(sys_msg, user_prompt)
            paper.llm_summary_raw = llm_text
            print(f"[GPT] get response : {paper.llm_summary_raw[0:100]}")

    def export(self, output_path: pathlib.Path):
        """
        LLM 요약 결과를 하나의 CSV 파일로 내보내는 함수.

        - 1행: prompt_schema.fields[].key 를 그대로 사용한 헤더
        - 2행 이후: 각 논문당 1행
          paper.llm_response_text (csv_line 형식)을 콤마로 분리해 사용
        """
        rows: list[list[str]] = []

        # 1) 헤더 생성 (필드 순서 고정)
        field_defs = self.prompt_schema.get("fields", [])
        header = [f["key"] for f in field_defs]
        rows.append(header)

        n_fields = len(header)

        # 2) 각 논문 row 생성
        for n, paper in enumerate(self.papers):
            raw = paper.llm_summary_raw.strip()

            if not raw:
                # LLM 결과가 없으면 빈 칸으로 채움 (스키마 길이에 맞춤)
                row = ["" for _ in range(n_fields)]
            else:
                # LLM이 준 csv_line을 기준으로 split
                cols = [c.strip() for c in raw.split(",")]

                # 필드 개수 보정 (스키마와 길이 맞추기)
                if len(cols) < n_fields:
                    cols.extend([""] * (n_fields - len(cols)))
                elif len(cols) > n_fields:
                    cols = cols[:n_fields]

                row = cols

            rows.append(row)
            paper.final_summary = row

            if self.debug:
                paper.dump(str(output_path) + f"/{n}.csv")

        # 3) CSV 파일로 쓰기
        write_csv(str(output_path) + "/result.csv", rows)

        if self.debug:
            print(f"[DEBUG] exported {len(self.papers)} papers to {output_path}")
