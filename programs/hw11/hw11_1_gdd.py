

def csv_read(filename):
    lines = open(filename, encoding="UTF-8-sig").readlines()

    result = []
    for line in lines:
        line = line.replace("\n", "").replace(" ", "").split(",")
        result.append(line)

    return result


def make_float(column_numbers, data):
    if len(column_numbers) == 0:
        print("invalid column number input")
        return 0

    for n, i in enumerate(data):
        if n == 0:
            continue

        for number in column_numbers:
            i[number] = float(i[number])
            data[n] = i[:]
    return 1


# 해당 년도의 일교차가 가장 큰 날과 그 값을 찾음
def maximum_temp_gap(year, data):
    max_date = "0000-00-00"
    max_temp = 0

    for token in data[1:]:
        if token[0] != str(year):
            # 해당 년도가 아님
            continue

        temp_gap = abs(token[3] - token[5])
        if temp_gap > max_temp:
            # 최대값이여서 업데이트 해야함
            max_temp = temp_gap
            max_date = f"{token[0]}-{token[1]}-{token[2]}"

    return max_date, max_temp


# 해당 년도의 기준 적산온도로 총 유효적산온도를 계산함.
# 합의 임계값을 적으면 최초로 합이 임계점을 넘는 날을 대신에 리턴함.
def gdd_calc(year, month_threshold, gdd_threshold, data, gdd_sum_threshold=-1):
    total_gdd = 0
    gdd_sum_threshold_date = "0000-00-00"

    for token in data[1:]:
        if token[0] != str(year):
            # 해당 년도가 아님
            continue
        if int(token[1]) not in month_threshold:
            # 해당 월이 아님
            continue

        gdd = token[4] - gdd_threshold

        if gdd < 0:  # 0보다 작으면 0으로 간주함
            gdd = 0

        total_gdd += gdd

        if gdd_sum_threshold == -1:  # '최초합 넘는 날 구하는 옵션'이 아님 (기본값이 -1임)
            continue
        if total_gdd > gdd_sum_threshold:  # 최초합 넘었으니 업데이트
            gdd_sum_threshold_date = f"{token[0]}-{token[1]}-{token[2]}"
            break

    return total_gdd, gdd_sum_threshold_date


def main():
    # 0:year, 1:month, 2:day,
    # 3:tmax, 4:tavg, 5:tmin,
    # 6:humid, 7:wind, 8:sunshine, 9:rainfall, 10:snow, 11:cloud
    # 데이터 원본
    weathers = csv_read("../../data/hw10/weather(146)_2001-2022.csv")

    # 정수화
    make_float([3, 4, 5, 6, 7, 8, 9, 10, 11], weathers)

    # 1 - 해당기간동안 연도별로 최대일교차가 발생한 일자와 일교차를 표시하시오.
    print(f"1 - 일교차가 가장 큰 날 | 그날의 일교차")
    for year_number in range(2001, 2023):
        max_gap_date, max_temp_gap = maximum_temp_gap(year_number, weathers)
        print(f"    {max_gap_date:<19} | {max_temp_gap:0.1f}'C")

    print("")
    # 2 - 해당기간동안 각 연도별로 5월부터 9월까지 적산온도를 구하시오
    print(f"2 - 기준년도 | GDD값")
    for year_number in range(2001, 2023):
        gdd_value, _ = gdd_calc(year_number, [5, 6, 7, 8, 9],5, weathers)
        print(f"    {year_number:<8} | {gdd_value:0.1f}")

    print("")
    # 3 - 각 해마다 4월부터 시작해서, 적산온도가 200이 넘는 최초일을 구하시오.
    gdd_threshold = 200
    print(f"3 - 기준년도 | 초과일 ({gdd_threshold}) | 초과 당시 GDD값")
    for year_number in range(2001, 2023):
        gdd_value, date = gdd_calc(year_number, [4, 5, 6, 7, 8, 9, 10, 11, 12], 5, weathers,
                                   200)
        print(f"    {year_number:<8} | {date:<12} | {gdd_value:0.1f}")

if __name__ == '__main__':
    main()

