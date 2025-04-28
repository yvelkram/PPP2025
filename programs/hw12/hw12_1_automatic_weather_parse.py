import programs.hw11.hw11_1_gdd as hw11
import programs.hw10.hw10_1_advanced_weather_parse as hw10
import requests
import os


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


def main():
    weather_path = '../../data/hw12/weather_146_2022.csv'

    print("")
    print(f"1-0) 전주 측정소 주소 저장과정 시작")
    download_weather(146, 2020, 2020, weather_path)

    weathers = hw11.csv_read(weather_path)

    hw11.make_float([3, 4, 5, 6, 7, 8, 9, 10, 11], weathers)

    print("")
    print(f"1-1) 연평균 기온 : {hw10.statistics(4, weathers, ['2020'])[1]:0.1f}'C")
    print(f"1-2) 5mm이상 강우일수 : {hw10.count_if(9, 'x >= 5', weathers, ['2020'])}일")
    print(f"1-3) 총 강우량 : {hw10.statistics(9, weathers, ['2020'])[0]:0.1f}mm")


if __name__ == '__main__':
    main()

