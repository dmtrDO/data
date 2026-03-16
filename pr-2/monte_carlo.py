# 4. Використовуючи Numba, реалізуйте обчислення енергетичних
#  інтегралів методом Монте-Карло для прогнозування навантаження
# на електричну мережу. Порівняйте точність прогнозування
# енергетичних споживань при різних кількостях ітерацій.

import numpy as np
from numba import njit
import matplotlib.pyplot as plt
import time

PERIOD = 24

# @njit
def load_function(t, length, height):
    return height + length * np.sin(np.pi * t / PERIOD)

# @njit
def monte_carlo_integration(n, a, b, length, height):
    total_sum = 0.0
    for _ in range(n):
        t = np.random.uniform(a, b)
        y = load_function(t, length, height)
        total_sum += y

    return (b - a) * (total_sum / n)

def generate_points(n, a, b, length, height):
    data = [[], []]
    for _ in range(n):
        t = np.random.uniform(a, b)
        y = np.random.uniform(length) + height
        data[0].append(t)
        data[1].append(y)
    return data

length = 20
height = 50
n = 1000

# function: 50 + 20sin(pt/24), t = [0, 24]
true_value = 1200 + 20 * 15.27887453682195
print(f"\n Real value: {true_value}\n")

t = np.linspace(0, PERIOD, n)
plt.plot(t, load_function(t, length, height), c="red")

t, y = generate_points(n, 0, PERIOD, length, height)
plt.scatter(t, y)

plt.show()

###############################################################

result = monte_carlo_integration(n, 0, PERIOD, length, height)
iterations = [10**2, 10**3, 10**4, 10**5, 10**6, 10**7]

print(f"{'iters':>8} | {'res (MWt*h)':>10} | {'Loss (%)':>8} | {'Time (s)':>6}")
print("-" * 65)

for n in iterations:
    start = time.time()
    result = monte_carlo_integration(n, 0, PERIOD, length, height)
    duration = time.time() - start
    error = abs(result - true_value) / true_value * 100

    print(f"{n:8d} | {result:10.3f} | {error:8.3f}% | {duration:6.5f}")
