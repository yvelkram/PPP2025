import matplotlib.pyplot as plt
import numpy as np


def example_1():
    dices = np.random.randint(1, 7, size=100)  # random 모듈과 다름
    print(dices)
    plt.hist(dices, bins=6, color="b")
    plt.show()


def example_2():
    tmax = np.random.rand(30) * 15 + 15
    tmin = tmax - (np.random.rand(30) * 5 + 5)
    plt.plot(tmax, color="r", label="TMAX")
    plt.plot(tmin, color="b", label="TMIN")
    plt.ylabel("Temperature(℃)")
    plt.legend()
    plt.show()
    # plt.savefig("./line_temp.png")


def example_3():
    tmax = np.random.rand(30) * 15 + 15
    tmin = tmax - (np.random.rand(30) * 5 + 5)
    plt.plot(tmax, color="r", label="최고기온")
    plt.plot(tmin, color="b", label="최저기온")
    plt.ylabel("기온(℃)")
    plt.legend()
    plt.show()
    # plt.savefig("./line_temp_hangul.png")


def example_4():
    tmax = np.random.rand(30) * 15 + 15
    tmin = tmax - (np.random.rand(30) * 5 + 5)
    plt.plot(tmax, color="r", label="최고기온")
    plt.plot(tmin, color="b", label="최저기온")
    plt.ylabel("기온(℃)")
    plt.legend()
    plt.show()
    # plt.savefig("./line_temp_hangul.png")


def example_5():
    fig, ax = plt.subplots(figsize=(15, 6))
    year = [str(x + 2001) for x in range(20)]
    rain = np.random.rand(20) * 200 + 1000
    ax.bar(year, rain, color="b")
    ax.set_ylabel("연평균강우량(mm)")
    plt.show()
    # fig.savefig("./bar_rain.png")


def example_6():
    np.random.seed(0)
    n = 50
    x = np.random.rand(n)
    y = np.random.rand(n)
    plt.scatter(x, y)
    plt.show()
    # plt.savefig("./scatter.png")


def main():
    plt.rcParams['font.family'] = ['D2Coding', 'sans-serif']
    plt.rcParams['axes.unicode_minus'] = False

    # example_1()
    example_2()
    # example_3()
    # example_4()
    # example_5()
    # example_6()


if __name__ == "__main__":
    main()
