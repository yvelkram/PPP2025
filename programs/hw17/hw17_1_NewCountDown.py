

import time


def count_down(second: int) -> None:
    while 1:
        if second < 0:
            break

        print(f"{second}초...", end="\r")
        time.sleep(1)

        second -= 1

    print(" vvvvvv")
    print("> BOOM <")
    print(" ^^^^^^")


def main() -> None:
    count_down(5)


if __name__ == '__main__':
    main()
