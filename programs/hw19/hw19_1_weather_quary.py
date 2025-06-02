# 1980-2024년 45년치 기상자료
# - 겨울철, 여름철 온도분포는?
# - 내 생일날 기온은 어땠나? 몇살 생일때가 춥고, 더웠나? 내가 태어나기 전에도
# 날씨가 동일한 패턴이었던가

import programs.hw18.hw18_1_pandas_weather as hw18
import matplotlib.pyplot as plt
import pandas as pd


birthday = []
plt.rcParams['font.family'] = ['D2Coding', 'sans-serif']
plt.rcParams['axes.unicode_minus'] = False


def main():
    start_year = 1980
    end_year = 2024
    station_id = 146

    # 다운로드
    weather_path = f'../../data/hw19/weather_{station_id}_{start_year}-{end_year}.csv'
    hw18.download_weather(station_id, start_year, end_year, weather_path)

    # 파일 처리
    df_weather_data = pd.read_csv(weather_path, skipinitialspace=True)
    # df_weather_data.info()

    # 1 - 겨울철(6, 7, 8), 여름철(12, 1, 2) 온도분포
    

    # 2 - 생일 년도부터 기온분포
    df_birthday_weather = pd.DataFrame(columns=df_weather_data.columns)
    for n, year in enumerate(range(birthday[0], end_year+1)):
        df_birthday_weather.loc[n] = df_weather_data[(df_weather_data["year"] == year) & (df_weather_data["month"] == birthday[1]) & (df_weather_data["day"] == birthday[2])].iloc[0].tolist()






if __name__ == '__main__':
    main()
