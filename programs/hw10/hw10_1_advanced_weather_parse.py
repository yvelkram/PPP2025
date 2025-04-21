

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


def statistics(column_numbers, data):
    total = 0
    for ln in data[1:]:
        total += ln[column_numbers]
    average = total / len(data)

    return total, average


def count_if(column_numbers, condition, data):
    command = condition.strip().split(" ")
    if command[0] != "x":
        print("invalid condition format")
        return None

    if command[1] == "<":
        case = 1
    elif command[1] == "<=":
        case = 2
    elif command[1] == ">":
        case = 3
    elif command[1] == ">=":
        case = 4
    elif command[1] == "==":
        case = 5
    elif command[1] == "!=":
        case = 6
    else:
        print("invalid condition format")
        return None

    value = int(command[2])

    count = 0
    for ln in data[1:]:
        if case == 1 and ln[column_numbers] < value:
            count += 1
        elif case == 2 and ln[column_numbers] <= value:
            count += 1
        elif case == 3 and ln[column_numbers] > value:
            count += 1
        elif case == 4 and ln[column_numbers] >= value:
            count += 1
        elif case == 5 and ln[column_numbers] == value:
            count += 1
        elif case == 6 and ln[column_numbers] != value:
            count += 1

    return count


def max_repeat(column_numbers, data):
    try_number = 0        # 현재 최대값
    try_start_date = ""   # 현재 연속 시작일
    repeat_flag = False   # 연속 상태 여부
    try_biggest_value = 0  # 연속일 중에 최대값

    max_number = 0       # 최종 연속일
    max_start_date = ""  # 최종 연속 시작일
    max_last_date = ""   # 최종 연속 종료일
    max_biggest_value = 0  # 연속일 중에 최대값

    for ln in data[1:]:
        if ln[column_numbers] > 0:
            if not repeat_flag:
                try_start_date = f"{ln[0]}-{ln[1]}-{ln[2]}"
                repeat_flag = True

            if ln[column_numbers] > try_biggest_value:
                try_biggest_value = ln[column_numbers]
            try_number += 1
            continue

        elif try_number > max_number:
            max_number = try_number
            max_biggest_value = try_biggest_value
            max_last_date = f"{ln[0]}-{ln[1]}-{ln[2]}"
            max_start_date = try_start_date

        try_number = 0
        try_biggest_value = 0
        repeat_flag = False

    # print(max_start_date)
    # print(max_last_date)
    return max_number, max_start_date, max_last_date, max_biggest_value


def top_n_date(column_numbers, n, data):
    top_list = [[0, ""] for _ in range(n)]
    date = "null"

    current_max = 0
    # 최대값
    for ln in data[1:]:
        if ln[column_numbers] >= current_max:
            current_max = ln[column_numbers]
            date = f"{ln[0]}-{ln[1]}-{ln[2]}"

    top_list[0][0] = current_max
    top_list[0][1] = date

    # print(top_list)

    # 최대값 제외하고 나머지 경우 반복
    for i in range(n - 1):
        try_max = 0
        date = "null"
        for ln in data[1:]:
            # 최대값과 같을경우 날짜 겹치는지 확인하기
            if ln[column_numbers] == current_max:
                test_date = f"{ln[0]}-{ln[1]}-{ln[2]}"
                exist = False
                for t in top_list:
                    if test_date == t[1]:
                        exist = True
                if exist:
                    # print("중복입니다")
                    continue
                else:
                    # print("found new biggest value!")
                    # print(f"try_max : {try_max}, date : {date}")
                    try_max = ln[column_numbers]
                    date = test_date
                    break

            # 최대값보다는 작은 경우
            if try_max < ln[column_numbers] < current_max:
                date = f"{ln[0]}-{ln[1]}-{ln[2]}"
                try_max = ln[column_numbers]

        top_list[i+1][0] = try_max
        top_list[i+1][1] = date
        current_max = try_max

    # print(top_list)

    result = []
    for i in top_list:
        result.append(f"{i[1]}_{i[0]}")

    return result


def sum_if(column_numbers, target_column, condition, data):
    total = 0
    for ln in data[1:]:
        if int(ln[target_column]) in condition:
            total += ln[column_numbers]

    return total


def main():
    # 0:year, 1:month, 2:day,
    # 3:tmax, 4:tavg, 5:tmin,
    # 6:humid, 7:wind, 8:sunshine, 9:rainfall, 10:snow, 11:cloud
    weathers_2022 = csv_read("../../data/hw10/weather(146)_2022-2022.csv")
    weathers_2001to2022 = csv_read("../../data/hw10/weather(146)_2001-2022.csv")

    make_float([3, 4, 5, 6, 7, 8, 9, 10, 11], weathers_2022)
    make_float([3, 4, 5, 6, 7, 8, 9, 10, 11], weathers_2001to2022)

    print("")
    print(f"1-1) 연 평균 기온(일평균 기온의 연평균) : {statistics(4, weathers_2022)[1]:0.1f}'C")
    print(f"1-2) 5mm이상 강우일수 : {count_if(9, 'x >= 5', weathers_2022)}일")
    print(f"1-3) 총 강우량 : {statistics(9, weathers_2022)[0]:0.1f}mm")
    print(f"1-4) 최장연속강우일수 : {max_repeat(9, weathers_2022)[0]}일")
    print(f"1-5) 강우이벤트 중 최대 강수량은 : {max_repeat(9, weathers_2022)[3]}mm")

    tops = top_n_date(3, 10, weathers_2022)
    # print(tops)
    print(f"1-6) 가장 더운날 top 3 : {tops[0].split('_')[0]}, {tops[1].split('_')[0]}, {tops[2].split('_')[0]}")

    print("")
    print(f"2-1) 여름철(6월-8월) 총 강수량은 {sum_if(9,1, [6, 7, 8], weathers_2022):0.1f}mm")
    print(f"2-2) 2021년과 2022년 총 강수량은 {sum_if(9, 0,[2021, 2022], weathers_2001to2022):0.1f}mm")

if __name__ == '__main__':
    main()

