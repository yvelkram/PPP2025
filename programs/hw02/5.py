
# 5) 할인행사를 하고 있다. 물건값이 2000원일때, 15% 할인한 가격을 구하시오.

price = 2000
discount = 15
new_price = 2000 * (1 - discount/100)
print("{}원의 {}% 할인된 가격은 {}원 입니다.".format(price, discount, new_price))
