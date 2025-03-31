
# 2. 삼각형 별 그리기

n = int(input("n : "))

for i in range(1, n+1):
    print("*" * i)

print("")

for i in range(1, n+1):
    print(" " * (n - i) + "*" * i)

print("")

# even
if n % 2 == 0:
    for i in range(1, n//2 + 1):
        print(" " * (n//2 - i) + "**" * i + " " * (n//2 - i))
# odd
else:
    for i in range(0, (n//2) + 1):
        print(" " * (n//2 - i) + "*" * (1 + 2 * i) +  " " * (n//2 - i))
