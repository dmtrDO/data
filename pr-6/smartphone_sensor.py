
# 4. Визначення змін у русі транспорту під час поворотів. 
# Потрібно виявити різкі зміни кута нахилу транспортного 
# засобу під час поворотів і побудувати графік змін 
# кута нахилу, що допоможе оцінити стабільність руху під 
# час маневрів. Обробка даних включає обчислення кутових 
# змін і визначення точок різких коливань.

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Завантаження даних
DIR = "bicycle movement analysis (phyphox)"
DIR = "experiment_2"
FILE_ACCELEROMETER = "Accelerometer.csv"
FILE_GYROSCOPE = "Gyroscope.csv"
FILE_ORIENTATION = "Orientation.csv"
FILE_META_TIME = "time.csv"

# df_accelerometer = pd.read_csv(f"{DIR}/{FILE_ACCELEROMETER}")
# df_gyroscope = pd.read_csv(f"{DIR}/{FILE_GYROSCOPE}")
df_orientation = pd.read_csv(f"{DIR}/{FILE_ORIENTATION}")

DF_META_TIME = pd.read_csv(f"{DIR}/meta/{FILE_META_TIME}")
TIME_LABEL = "Time (s)"

COLORS = ["tab:blue", "tab:green", "tab:red", "tab:orange"]


def show_graph(df, nrows, idx, legend):
    fig, axes = plt.subplots(nrows, 1)
    fig.set_size_inches(15, 7)
    fig.canvas.manager.window.wm_geometry("+20+20")

    df_start = DF_META_TIME[DF_META_TIME["event"] == "START"]
    starts = df_start["experiment time"].values

    # delete graph between 5th and 6th vertical lines
    # df1 = df[df["Time (s)"] < starts[4]]
    # df2 = df[df["Time (s)"] > starts[5]]
    # df = pd.concat([df1, df2])
    # starts = np.delete(starts, range(4, 5))
    
    time = df.iloc[:, 0]

    for i in range(nrows):
        axes[i].plot(time, df.iloc[:, idx[i]], 
                     label=df.columns[idx[i]], c=COLORS[i])
        axes[i].legend(loc=legend)
        for start in starts:
            axes[i].axvline(x=start, color="black")

    axes[-1].set_xlabel(TIME_LABEL)

    plt.show()


# show_graph(df_accelerometer, 3, [1, 2, 3], "lower left")
# show_graph(df_gyroscope, 3, [1, 2, 3], "upper left")

# show_graph(df_orientation, 4, [5, 6, 7, 8], "upper left")

################################################################
# визначення критичних кутів нахилу (точки різких коливань)

values = []
ranges = sorted(set(DF_META_TIME["experiment time"].to_list()))
df_pitch = df_orientation[["Time (s)", "Pitch (°)"]]
for i in range(len(ranges) - 1):
    df_rng = df_pitch[
        (df_pitch["Time (s)"] > ranges[i]) & 
        (df_pitch["Time (s)"] < ranges[i+1])
    ]
    values.append(np.abs(df_rng["Pitch (°)"].min()))

values = np.array(values, dtype=np.int8)
max_value = np.max(values)
print(f"Min angle values (°) ​​for each range: {values}\nMax value: {max_value}°")



