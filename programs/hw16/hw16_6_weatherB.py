# 1) 전주시(146)의 2015년 연 강수량은?
# 2) 전주시(146)의 2022년 최대기온은? max of tavg
# 3) 전주시(146)의 2024년 최대 일교차(tmax-tmin)는?
# 4) 수원시(119)와 전주시(146)의 2024년 총강수량 차이는(절대값)?
# * 소숫점 첫째자리에서 반올림 할것 *

import hw16_5_weatherA
import os
import requests


def csv_read(filename):
    lines = open(filename, encoding="UTF-8-sig").readlines()

    result = []
    for line in lines:
        line = line.replace("\n", "").replace(" ", "").split(",")
        result.append(line)

    return result


def make_float(column_numbers, data):
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


def download_file(url, filepath):
    if os.path.exists(filepath):
        print(f"다운로드 할 파일이 이미 존재합니다! : {os.path.abspath(filepath)}")

    with open(filepath, "w", encoding="UTF-8-sig") as f:
        resp = requests.get(url)
        resp.encoding = "UTF-8"
        f.write(resp.text)

    print(f"다운로드를 완료하였습니다! : {os.path.abspath(filepath)}")


def download_weather(station_id, start_year, end_year, filepath):
    print(f"Download option : station_id={station_id}, [{start_year}-{end_year}]")
    c_url = f"https://api.taegon.kr/stations/{station_id}/?sy={start_year}&ey={end_year}&format=csv"
    download_file(c_url, filepath)


def submit_assignment():
    name = ""
    affiliation = ""
    student_id = ""

    answer1 = 1
    answer2 = 2
    answer3 = 1
    answer4 = 2

    hw16_5_weatherA.submit_to_api(name, affiliation, student_id, answer1, answer2, answer3, answer4, verbose=True)


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

    print("")
    print("1) 전주시의 2015년 연 강수량")

    print("")
    print("2) 전주시의 2022년 최고기온")

    print("")
    print("3) 전주시의 2024년 최대일교차")

    print("")
    print("4) 전주시와 수원시의 2024년 총강수량 차이")

    # submit_assignment()


if __name__ == '__main__':
    main()
