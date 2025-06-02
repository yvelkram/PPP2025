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

    fig, axs = plt.subplots(2)

    # 1 - 겨울철(6, 7, 8), 여름철(12, 1, 2) 온도분포
    summer = [6, 7, 8]
    winter = [12, 1, 2]
    df_winter = pd.DataFrame(columns=df_weather_data.columns)
    df_summer = pd.DataFrame(columns=df_weather_data.columns)
    for n, year in enumerate(range(start_year, end_year+1)):  # 각 년도 별로 작동
        df_winter_year = pd.DataFrame(columns=df_weather_data.columns)
        df_summer_year = pd.DataFrame(columns=df_weather_data.columns)
        for i in range(0, 3):  # 3개월 단위로 추출
            df_winter_year.loc[i] = df_weather_data[
                (df_weather_data["year"] == year) & (df_weather_data["month"] == winter[i])
            ].iloc[0].tolist()
            df_summer_year.loc[i] = df_weather_data[
                (df_weather_data["year"] == year) & (df_weather_data["month"] == summer[i])
            ].iloc[0].tolist()
        df_winter.loc[n] = df_winter_year.mean()  # 추출한 3개월을 평균내서 추가
        df_summer.loc[n] = df_summer_year.mean()

    # print(df_winter.head())
    # print(df_summer.head())
    # 데이터 플롯
    axs[0].set_title("겨울철과 여름철 온도분포")
    df_winter.plot(kind="line", x="year", y="tavg", color="blue", ax=axs[0])
    df_summer.plot(kind="line", x="year", y="tavg", color="red", ax=axs[0])

    # 2 - 생일 년도부터 기온분포
    df_birthday_weather = pd.DataFrame(columns=df_weather_data.columns)
    for n, year in enumerate(range(birthday[0], end_year+1)):  # 필터링 해서 생일 날자 데이터 찾기
        df_birthday_weather.loc[n] = df_weather_data[
            (df_weather_data["year"] == year) &
            (df_weather_data["month"] == birthday[1]) &
            (df_weather_data["day"] == birthday[2])
        ].iloc[0].tolist()
    # print(df_birthday_weather.head())
    # 데이터 플롯
    axs[1].set_title(f"{birthday[1]}월 {birthday[2]}일의 기온분포")
    df_birthday_weather.plot(kind="line", x="year", y="tmax", color="red", ax=axs[1])
    df_birthday_weather.plot(kind="line", x="year", y="tmin", color="blue", ax=axs[1])

    plt.tight_layout()
    # plt.show()
    plt.savefig('../../data/hw19/hw19_figure.png')


if __name__ == '__main__':
    main()
