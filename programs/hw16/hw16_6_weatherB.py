# 1) 전주시(146)의 2015년 연 강수량은?
# 2) 전주시(146)의 2022년 최대기온은? max of tavg
# 3) 전주시(146)의 2024년 최대 일교차(tmax-tmin)는?
# 4) 수원시(119)와 전주시(146)의 2024년 총강수량 차이는(절대값)?
# * 소숫점 첫째자리에서 반올림 할것 *

# 0:year, 1:month, 2:day,
# 3:tmax, 4:tavg, 5:tmin,
# 6:humid, 7:wind, 8:sunshine, 9:rainfall, 10:snow, 11:cloud

import hw16_5_weatherA
import os
import requests


name = ""             # 이름
affiliation = ""  # 학과
student_id = ""    # 학번


def csv_read(filename: str) -> list[list[str]]:
    """
    csv 파일 읽어서 리스트화, 쉼표 단위로 끊음

    :param filename:
    :return:
    """
    lines = open(filename, encoding="UTF-8-sig").readlines()

    result = []
    for line in lines:
        line = line.replace("\n", "").replace(" ", "").split(",")
        result.append(line)

    return result


def make_float(column_numbers: list[int], data: list[list]):
    """
    리스트를 받아서 지정된 열을 소수(float)로 변환 후 저장

    :param column_numbers: 변환 열 번호 목록 리스트
    :param data: 데이터 리스트, 리턴 불필요
    :return: 성공시 1, 실패시 0
    """
    if len(column_numbers) == 0:
        print("invalid column number input")
        return 0

    for n, i in enumerate(data):
        if n == 0:
            continue

        for number in column_numbers:
            i[number] = float(i[number])
            data[n] = i[:]
    return 1


def statistics(column_number: int, data: list[list], years: list[int] = None) -> tuple[int or float, float]:
    """
    입력한 열의 합과 평균을 출력해주는 함수

    :param column_number: 계산할 열 번호, int
    :param data: 데이터 리스트, 리턴 불필요
    :param years: 년도 리스트, 기본값은 전체년도
    :return: 0: 총합, 1: 평균
    """
    total = 0
    counter = 0
    for ln in data[1:]:
        # 년도 지정을 했는데, 해당 연도가 아니라면 스킵
        if years is not None and int(ln[0]) not in years:
            continue

        total += ln[column_number]
        counter += 1

    average = total / counter

    return total, average


def find_max(column_number: int, data: list[list], years: list[int] = None) -> int or float:
    """
    최대값 찾아서 리턴

    :param years: 탐색 년도, 기본값은 전체조사
    :param column_number: 탐색 열 번호
    :param data: 데이터 리스트
    :return: 최대값
    """
    trial = data[1][column_number]

    for ln in data[1:]:
        # 년도 지정을 했는데, 해당 연도가 아니라면 스킵
        if years is not None and int(ln[0]) not in years:
            continue

        if ln[column_number] > trial:
            trial = ln[column_number]

    return trial


def find_max_different(column_a: int, column_b: int, data: list[list], years: list[int] = None) -> int or float:
    """
    두개의 열의 차이가 가장 큰 값을 내보냄, 절댓값으로 크기비교

    :param column_b: 탐색 열, 순서무관
    :param column_a: 탐색 열
    :param years: 탐색 년도, 기본값은 전체조사
    :param data: 데이터 리스트
    :return: 최대값
    """
    trial = abs(data[1][column_a] - data[1][column_b])

    for ln in data[1:]:
        # 년도 지정을 했는데, 해당 연도가 아니라면 스킵
        if years is not None and int(ln[0]) not in years:
            continue

        if abs(ln[column_a] - ln[column_b]) > trial:
            trial = abs(ln[column_a] - ln[column_b])

    return trial


def download_file(url: str, filepath: str) -> None:
    """
    링크에 접속하여 지정된 경로에 파일 다운로드, 이미 존재하면 다시 다운로드 하지 않음

    :param url: 링크
    :param filepath: 파일 경로, 파일 저장 위치
    """
    if os.path.exists(filepath):
        print(f"다운로드 할 파일이 이미 존재합니다! : {os.path.abspath(filepath)}")

    with open(filepath, "w", encoding="UTF-8-sig") as f:
        resp = requests.get(url)
        resp.encoding = "UTF-8"
        f.write(resp.text)

    print(f"다운로드를 완료하였습니다! : {os.path.abspath(filepath)}")


def download_weather(station_id: int, start_year: int, end_year: int, filepath: str) -> None:
    """
    날씨 데이터 다운로드 하는 함수

    :param station_id: 관측소 번호
    :param start_year: 시작년도
    :param end_year: 종료년도
    :param filepath: 파일 경로
    """
    print(f"Download option : station_id={station_id}, [{start_year}-{end_year}]")
    c_url = f"https://api.taegon.kr/stations/{station_id}/?sy={start_year}&ey={end_year}&format=csv"
    download_file(c_url, filepath)


def submit_assignment(a1, a2, a3, a4) -> None:
    """
    과제 제출 하는 함수
    """
    hw16_5_weatherA.submit_to_api(name, affiliation, student_id, str(a1), str(a2), str(a3), str(a4), verbose=True)


def main():
    j_weather_path = '../../data/hw16/weather_146_2015-2024.csv'
    s_weather_path = '../../data/hw16/weather_119_2015-2024.csv'

    print("")
    print("0-1) 전주 측정소 주소 저장과정 시작")
    download_weather(146, 2015, 2024, j_weather_path)
    print("0-2) 수원 측정소 주소 저장과정 시작")
    download_weather(119, 2015, 2024, s_weather_path)

    print("0-3) 데이터 변형")
    j_weathers = csv_read(j_weather_path)
    s_weathers = csv_read(s_weather_path)

    make_float([3, 4, 5, 6, 7, 8, 9, 10, 11], j_weathers)
    make_float([3, 4, 5, 6, 7, 8, 9, 10, 11], s_weathers)
    print("완료\n")

    print("")
    print("1) 전주시의 2015년 연 강수량")
    answer_1 = f"{statistics(9, j_weathers, [2015])[0]:0.1f}"
    print(f"> {answer_1}mm")

    print("")
    print("2) 전주시의 2022년 최고기온")
    answer_2 = find_max(4, j_weathers, [2022])
    print(f"> {answer_2}'C")

    print("")
    print("3) 전주시의 2024년 최대일교차")
    answer_3 = find_max_different(3, 5, j_weathers, [2024])
    print(f"> {answer_3}'C")

    print("")
    print("4) 전주시와 수원시의 2024년 총강수량 차이")
    n1 = statistics(9, j_weathers, [2024])[0]
    n2 = statistics(9, s_weathers, [2024])[0]

    answer_4 = f"{abs(n1 - n2):0.1f}"
    print(f"> {answer_4}mm")

    # submit_assignment(1, 2, 3, 4)
    submit_assignment(answer_1, answer_2, answer_3, answer_4)


if __name__ == '__main__':
    main()