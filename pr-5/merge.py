
# 4. Обробка та злиття даних з різних джерел: 
# Реалізувати обробку даних з CSV, JSON та SQL,
# їх очищення та злиття в один датафрейм.

import pandas as pd
import requests
import json
import sqlite3


# json (precipitation, max wind speed) https://open-meteo.com/
url = "https://archive-api.open-meteo.com/v1/archive?latitude=50.4547&longitude=30.5238&start_date=1980-04-05&end_date=2026-04-19&daily=precipitation_sum,wind_speed_10m_max&timezone=auto&wind_speed_unit=ms"
response = requests.get(url)
data_json = response.json()["daily"]

with open('weather_data.json', 'w') as f:
    json.dump(data_json, f, indent=4)

data_json = pd.read_json('weather_data.json')
df_data_json = pd.DataFrame(data_json)

df_data_json["date"] = pd.to_datetime(df_data_json["time"])
df_data_json = df_data_json[["date", "precipitation_sum", "wind_speed_10m_max"]]
print(df_data_json.shape[0])
df_data_json = df_data_json.drop_duplicates(subset='date', keep='first')
df_data_json = df_data_json.dropna()
print(df_data_json.shape[0])
print(df_data_json)


# csv (avg temperature) https://www.kaggle.com/datasets/sudalairajkumar/daily-temperature-of-major-cities/code
df_data_csv = pd.read_csv("city_temperature.csv", low_memory=False)
df_data_csv = df_data_csv[df_data_csv["City"] == "Kiev"]
df_data_csv["date"] = pd.to_datetime(df_data_csv[["Year", "Month", "Day"]])
df_data_csv = df_data_csv[["date", "AvgTemperature"]]
df_data_csv["AvgTemperature"] = (df_data_csv["AvgTemperature"] - 32) * 5 / 9
df_data_csv["AvgTemperature"] = df_data_csv["AvgTemperature"].round(1)

print(df_data_csv.shape[0])
df_data_csv = df_data_csv.drop_duplicates(subset='date', keep='first')
df_data_csv = df_data_csv.dropna()
print(df_data_csv.shape[0])
print(df_data_csv)


# sql (daily air quality index) https://www.kaggle.com/datasets/nitirajkulkarni/kyiv-ua-703448?select=air_quality_historical.csv

# df_data_sql = pd.read_csv("kyiv_air.csv")
# conn = sqlite3.connect('aqi.db')
# df_data_sql.to_sql("aqi", conn, if_exists="replace", index=False)
# conn.close()

conn = sqlite3.connect('aqi.db')
df_data_sql = pd.read_sql_query("SELECT * FROM aqi", conn)
conn.close()

df_data_sql = df_data_sql[["date", "us_aqi"]]
df_data_sql["date"] = pd.to_datetime(df_data_sql["date"])
print(df_data_sql.shape[0])
df_data_sql = df_data_sql.dropna()
df_data_sql = df_data_sql.drop_duplicates(subset='date', keep='first')
print(df_data_sql.shape[0])
print(df_data_sql)

# merging
data = pd.merge(df_data_json, df_data_csv, on="date")
data = pd.merge(data, df_data_sql, on="date")
print(data)

