
def add(n_list):
    n_list.append(10)
    return n_list


def main():
    a = [1, 2, 3, 4, 5]
    b = add(a)[:]
    c = add(b)[:]
    d = add(c)[:]

    e = a[:]

    print(id(a))
    print(id(b))
    print(id(c))
    print(id(d))
    print(id(e))


if __name__ == '__main__':
    main()
