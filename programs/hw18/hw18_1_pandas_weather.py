# 1) 전주시(146)의 2012년 연 강수량은?
# 2) 전주시(146)의 2024년 최대기온은? max of tmax
# 3) 전주시(146)의 2020년 최대 일교차(tmax-tmin)는?
# 4) 수원시(119)와 전주시(146)의 2019년 총강수량 차이는(절대값)?
# * 소숫점 첫째자리에서 반올림 할것 *

# [프원실] 과제18_pandas_20249999_홍길동

import programs.hw16.hw16_5_weatherA as hw16
import os
import requests
import pandas as pd


name = ""             # 이름
affiliation = ""  # 학과
student_id = ""    # 학번


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
    hw16.submit_to_api(name, affiliation, student_id, str(a1), str(a2), str(a3), str(a4), verbose=True)


def main():
    start_year = 2010
    end_year = 2024

    j_weather_path = f'../../data/hw18/weather_146_{start_year}-{end_year}.csv'
    s_weather_path = f'../../data/hw18/weather_119_{start_year}-{end_year}.csv'

    print("")
    print("0-1) 전주 측정소 주소 저장과정 시작")
    download_weather(146, start_year, end_year, j_weather_path)
    print("")
    print("0-2) 수원 측정소 주소 저장과정 시작")
    download_weather(119, start_year, end_year, s_weather_path)

    print("")
    print("0-3) 데이터 변형")
    df_j_weather = pd.read_csv(j_weather_path, skipinitialspace=True)
    df_s_weather = pd.read_csv(s_weather_path, skipinitialspace=True)

    # print(df_j_weather.info())
    # print(df_s_weather.info())
    print("완료\n")

    print("")
    print("1) 전주시의 2012년 연 강수량")
    answer_1 = f"{df_j_weather[df_j_weather['year'] == 2012]['rainfall'].sum():0.1f}"
    print(f"> {answer_1}mm")

    print("")
    print("2) 전주시의 2024년 최고기온")
    answer_2 = f"{df_j_weather[df_j_weather['year'] == 2024]['tmax'].max():0.1f}"
    print(f"> {answer_2}'C")

    print("")
    print("3) 전주시의 2024년 최대일교차")
    different_df = pd.DataFrame()
    different_df['year'] = df_j_weather['year']
    different_df['delta_t'] = abs(df_j_weather['tmax'] - df_j_weather['tmin'])

    answer_3 = f"{different_df[different_df['year'] == 2024]['delta_t'].max():0.1f}"
    print(f"> {answer_3}'C")

    print("")
    print("4) 전주시와 수원시의 2019년 총강수량 차이")
    n1 = df_j_weather[df_j_weather['year'] == 2019]['rainfall'].sum()
    n2 = df_s_weather[df_s_weather['year'] == 2019]['rainfall'].sum()

    answer_4 = f"{abs(n1 - n2):0.1f}"
    print(f"> {answer_4}mm")

    # submit_assignment(1, 2, 3, 4)
    submit_assignment(answer_1, answer_2, answer_3, answer_4)


if __name__ == '__main__':
    main()