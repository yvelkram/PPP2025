from paperwork import FullPaperWork, PrePaperWork


def main2():
    paper_input = "./paper_input"
    prompt_path = "./prompt_schema.json"
    output_path = "./paper_output"

    pw = FullPaperWork(paper_input, prompt_path,
                       "gpt-5", "text-embedding-3-small",
                       1)
    pw.process()
    pw.export(output_path)


def main():
    ris_filepath = "./ris_input/scopus_export_Nov-13-2025.ris"
    prompt_path = "./prework_prompt_schema.json"
    output_path = "./ris_output"
    quary_questions = "연구 대상이 “도시지역”인가? 연구 주제가 “녹지 형태 또는 구성 변수”인가? 결과변수가 “도시 온열환경 지표(예: 지표온도, 열섬강도, 보행자 열쾌적성)”인가?"

    pw = PrePaperWork(ris_filepath, prompt_path, quary_questions)
    pw.process()
    pw.export(output_path)


if __name__ == '__main__':
    try:
        main()
    except NotImplementedError:
        pass
