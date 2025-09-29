from PaperWork import PaperWork
import pathlib


def main():
    paper_input = pathlib.Path("./paper_input")
    prompt_path = pathlib.Path("prompt_schema.json")
    output_path = pathlib.Path("./paper_output")

    pw = PaperWork(paper_input, prompt_path, "gpt-5", True)
    pw.process()
    pw.export(output_path)


if __name__ == '__main__':
    try:
        main()
    except NotImplementedError:
        pass
