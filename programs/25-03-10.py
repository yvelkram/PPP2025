
# // 몫 - % 나머지
# 타입 : 글자(str) + 숫자 --- 숫자 : 정수(int) + 실수(float)
# 0xff = 255
# break, continue

mart_price = {"milk":2800, "egg":300, "bread":1200, "water":1700}
cart = ["milk", "bread", "bread", "bread", "egg"]

total_price = 0
for name in cart:
    total_price += mart_price[name]
    print(f"결제 : [{name} - {mart_price[name]:,}원], 총합 : {total_price:,}원")

print(f"전체가격은 {total_price}원 입니다.")
