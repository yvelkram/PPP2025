from utils import *
from paper import PrePaper, FullPaper

from openai import OpenAI
from concurrent.futures import ThreadPoolExecutor, as_completed

import time


# --- PAPERWORK MODULE -------------------------------------------------------------------------------------------------
class PrePaperWork:
    def __init__(self, ris_path: list[str], prompt_path: str, output_path: str,
                 questions: str, model_name: str = "gpt-5"):
        self.ris_paths: list[str] = ris_path
        self.prompt_path = prompt_path
        self.output_path = output_path
        self.questions: str = questions
        self.model_name = model_name

        self.papers: list[PrePaper] = []
        self.user_prompt: str = ""
        self.system_prompt: str = ""

        self.temperature: float = 1.0       # other value is not working
        self.max_retries: int = 3
        self.request_timeout_sec: int = 60  # llm request max time wait
        self.max_workers: int = 5           # maximum async worker

    # --- PRIVATE ------------------------------------------------------------------------------------------------------
    def __read_ris(self, ris_file: str) -> None:
        """
        Read ris file and add PrePaper object.
        """
        encoding = "utf-8"
        try:
            open(ris_file, encoding=encoding).close()
        except UnicodeDecodeError:
            encoding = "cp949"
        except FileNotFoundError:
            print(f"[ERROR] invalid or empty file path : [{ris_file}]")
            return

        structure = {"title": "N/A",
                 "abstract": "N/A",
                 "doi": "N/A",
                 "database": "N/A",
                 "publish_year": "N/A",
                 "author": "N/A",
                 "keyword": "N/A"}
        current = structure.copy()
        with open(ris_file, encoding=encoding) as f:
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
                self.papers.append(PrePaper(current))  # 1st variable = PrePaper.texts
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
        doi_map: dict[str, PrePaper] = {}
        dup_count = 0

        for paper in self.papers:
            doi = paper.texts["doi"]
            if doi == "N/A":  # dismiss default value : unknown for decide duplicated
                continue
            if doi in doi_map:  # duplicated
                paper.duplicated = True
                dup_count += 1
            else:  # not duplicated
                paper.duplicated = False
                doi_map[doi] = paper
        print(f"[INFO] find_same_paper: " +
              f"unique papers = [{len(doi_map)}], " +
              f"duplicated papers = [{dup_count}]")

    # --- PUBLIC -------------------------------------------------------------------------------------------------------
    def process(self) -> None:
        """
        main process
        """
        print("[INFO] start ris reading")
        for ris_file in self.ris_paths:
            self.__read_ris(ris_file)
        print("[INFO] search duplicated paper")
        self.__find_same_paper()
        print("[INFO] make final prompt")
        self.__construct_prompt()

        print("[INFO] start paper summary")
        counter = 1
        for paper in self.papers:
            if paper.duplicated:  # don't quary duplicated paper
                continue
            while not self.__llm_quary(paper):
                continue

            print(f"{counter}/{len(self.papers)} ({100*counter/len(self.papers):0.2f}%) papers done")
            counter += 1

            if counter % 100 == 0:
                self.export()

    def process_parallel(self, max_workers: int = 3) -> None:
        print("[INFO] start ris reading")
        for ris_file in self.ris_paths:
            self.__read_ris(ris_file)
        print("[INFO] search duplicated paper")
        self.__find_same_paper()
        print("[INFO] make final prompt")
        self.__construct_prompt()

        print("[INFO] start paper screening (parallel)")

        def worker(paper: PrePaper) -> None:
            if paper.duplicated:
                return
            while not self.__llm_quary(paper):
                continue

        with ThreadPoolExecutor(max_workers=max_workers) as ex:
            futures = [ex.submit(worker, p)
                       for p in self.papers
                       if not p.duplicated]
            for i, f in enumerate(as_completed(futures), start=1):
                try:
                    f.result()
                    print(f"[INFO] {i}/{len(futures)} ({100*i/len(self.papers):0.2f}%) papers done")
                except Exception as e:
                    print(f"[WARN] worker failed: {e}")

    def export(self) -> None:
        """
        export screening result
        """
        # --- 1. output.csv
        print("[INFO] make output.csv")
        header = ["fid",
                  "DOI", "저자", "연도", "제목", "데이터베이스",
                  "검토자1", "검토자2", "마지막검토일",
                  "중복여부", "포함여부", "배제사유키워드", "배제사유내용", "다음단계여부"]
        output_rows: list[list[str]] = [header]
        for idx, paper in enumerate(self.papers, start=1):
            text_duplicated = "Y" if paper.duplicated else "N"
            text_accept = "Y" if paper.accept else "N"
            text_next_step = "진행" if paper.accept else "배제"
            row = [str(idx),
                   paper.texts["doi"], paper.texts["author"], paper.texts["publish_year"], paper.texts["title"], paper.texts["database"],
                   "", "", "",  #검토자1, 검토자2, 마지막검토일
                   text_duplicated, text_accept, paper.reject_keyword, paper.reject_reason, text_next_step]
            output_rows.append(row)
        write_csv(self.output_path + "/output.csv", output_rows)

        # --- 2. summary.csv
        print("[INFO] make summary.csv")

        total_count = len(self.papers)
        unique_count = sum(1 for paper in self.papers
                           if not paper.duplicated)

        screening_target_count = unique_count
        screening_reject_count = sum(1 for paper in self.papers
                                     if (not paper.duplicated) and (not paper.accept))
        screening_pass_count = sum(1 for paper in self.papers
                                   if (not paper.duplicated) and paper.accept)

        summary_rows = [
            ["구분","논문숫자"],
            ["검색된 총건수",f"{total_count}"],
            ["중복 제거 후건수",f"{unique_count}"],
            ["제목·초록검토 대상건수",f"{screening_target_count}"],
            ["제목·초록 단계 배제건수",f"{screening_reject_count}"],
            ["제목·초록 후 전문검토 대상건수",f"{screening_pass_count}"],
            ["전문검토 후 최종 포함건수",""],
            ["전문단계 배제건수",""],
            ["비고",""]]
        write_csv(self.output_path + "/summary.csv", summary_rows)


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

    def export(self, output_path: str):
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
