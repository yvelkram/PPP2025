
# 4. 딸기 300g, 한라봉 150g 섭취하였을 때, 입력자료를 사전형으로 전달하면, 총 칼로리를 계산하는 함수를 만드시오.
# fruits={“딸기”: 300, “한라봉”: 150}, fruits_calorie_dic={"한라봉": 50, "딸기": 34, "바나나": 77}.
# 과제 #06-01 활용. 함수명은 total_calorie(fruits, fruits_calorie_dic)


def total_calorie(fruits, fruits_calorie_dic):
    total_gram = 0
    calorie_sum = 0
    for name in fruits:
        total_gram += fruits[name]
        cal = fruits_calorie_dic[name] * fruits[name] / 100
        calorie_sum += cal
        print(f"[{name}] : {fruits[name]}g, {cal:,.1f}kcal")

    print(f"과일을 총 {total_gram:,}g 드셨으며, 칼로리는 총 {calorie_sum:,.1f}kcal 입니다.")


def main():
    fruits = {"딸기": 300, "한라봉": 150}
    fruits_calorie_dic = {"한라봉": 50, "딸기": 34, "바나나": 77}
    total_calorie(fruits, fruits_calorie_dic)


if __name__ == '__main__':
    main()
