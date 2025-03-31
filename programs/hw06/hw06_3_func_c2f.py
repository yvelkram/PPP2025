
# 3. 섭씨를 화씨로 바꾸는 함수 c2f(t_c) 함수를 만드시오.


def c2f(t_c):
    temp_c = t_c
    temp_f = (temp_c * 1.8) + 32

    print(f"{temp_c}'C => {temp_f:0.1f}'F")
    return temp_f


def main():
    c2f(100)


if __name__ == '__main__':
    main()
