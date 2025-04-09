# // 몫 - % 나머지
# 타입 : 글자(str) + 숫자 --- 숫자 : 정수(int) + 실수(float)
# 0xff = 255
# break, continue


def csv_read(filename):
    lines = open(filename, encoding="UTF-8-sig").readlines()

    result = {}
    for line in lines[1:]:
        token = line.replace("\n", "").replace(" ", "").split(",")
        result[token[0]] = int(token[1]) / int(token[2])

    return result


def main():
    # 0 : 작목 / 1 : 열량(kcal/회) / 2 : 총 내용량(g)
    fruits = csv_read("../data/hw09/calorie_db.csv")

    fruits_eat = {
        "바나나" : 100,
        "살구" : 100,
        "사과" : 100
    }

    total_calorie = 0
    for eat in fruits_eat.keys():
        total_calorie += fruits[eat] * fruits_eat[eat]

    print(total_calorie)

if __name__ == '__main__':
    main()
