# 1. 수업시간 제시한 코드 혹은 본인이 작성한 코드를 활용하여, 칼로리 계산 프로그램을 완성하시오.
# 식품별 칼로리 정보를 파일에서 읽어서 처리


def csv_read(filename):
    lines = open(filename, encoding="UTF-8-sig").readlines()

    result = {}
    for line in lines[1:]:
        token = line.replace("\n", "").replace(" ", "").split(",")
        result[token[0]] = int(token[1]) / int(token[2])

    return result


def main():
    # 0 : 작목 / 1 : 열량(kcal/회) / 2 : 총 내용량(g)
    fruits = csv_read("../../data/hw09/calorie_db.csv")

    fruits_eat = {
        "바나나" : 100,
        "살구" : 100,
        "사과" : 100
    }

    total_calorie = 0
    for eat in fruits_eat.keys():
        total_calorie += fruits[eat] * fruits_eat[eat]

    print("섭취한 과일 목록")
    for eat in fruits_eat.keys():
        print(f"{eat} : {fruits_eat[eat]}g")
    print(f"총 섭취한 칼로리는 {total_calorie}kcal 입니다.")

if __name__ == '__main__':
    main()

