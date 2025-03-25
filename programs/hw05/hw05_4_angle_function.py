
# 4. 삼각함수 표를 만드시오.

import math

print(f"각(º)| 라디안 |   sin   |   cos   |   tan  ")
for a in range(0, 361):
    ra = math.radians(a)
    print(f"{a:>3}º | {ra:>6.4f} | {math.sin(ra):>7.4f} | {math.cos(ra):>7.4f} | {math.tan(ra):>7.4f}")
