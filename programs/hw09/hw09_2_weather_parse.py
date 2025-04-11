# 2. 기상자료를 받아서 연 평균 기온(일평균 기온의 연평균), 5mm이상 강우일수, 총 강우량을 구하시오.


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


def statistics(column_numbers, data):
    total = 0
    for n, i in enumerate(data):
        if n == 0:
            continue
        total += i[column_numbers]
    average = total / len(data)

    return total, average


def count_if(column_numbers, condition, data):
    command = condition.strip().split(" ")
    if command[0] != "x":
        print("invalid condition format")
        return

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
        return

    value = int(command[2])

    count = 0
    for n, i in enumerate(data):
        if n == 0:
            continue
        if case == 1 and i[column_numbers] < value:
            count += 1
        elif case == 2 and i[column_numbers] <= value:
            count += 1
        elif case == 3 and i[column_numbers] > value:
            count += 1
        elif case == 4 and i[column_numbers] >= value:
            count += 1
        elif case == 5 and i[column_numbers] == value:
            count += 1
        elif case == 6 and i[column_numbers] != value:
            count += 1

    return count


def main():
    # 0 : year, 1 : month, 2 : day,
    # 3 : tmax, 4 : tavg, 5 : tmin,
    # 6 : humid, 7 : wind, 8 : sunshine, 9 : rainfall, 10 : snow, 11 : cloud
    weathers = csv_read("../../data/hw09/weather(146)_2022-2022.csv")

    make_float([3, 4, 5, 6, 7, 8, 9, 10, 11], weathers)

    print(f"연 평균 기온(일평균 기온의 연평균) : {statistics(4, weathers)[1]:0.1f}")
    print(f"5mm이상 강우일수 : {count_if(9, 'x >= 5', weathers)}")
    print(f"총 강우량 : {statistics(9, weathers)[0]:0.1f}")


if __name__ == '__main__':
    main()

