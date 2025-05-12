# // 몫 - % 나머지
# 타입 : 글자(str) + 숫자 --- 숫자 : 정수(int) + 실수(float)
# 0xff = 255
# break, continue
import requests


def str2float(text: str, default_value: float = -999) -> float:
    try:
        return float(text)
    except ValueError:
        return default_value


def main():
    c_url = "https://coopjbnu.kr/function/ajax.get.rest.data.php"
    data = {"code": "mobile1"}

    with open("../data/cafeteria_menu.html", "w", encoding="UTF-8") as f:
        resp = requests.post(c_url, data=data)
        resp.encoding = "UTF-8"
        f.write(resp.text)


if __name__ == '__main__':
    main()
