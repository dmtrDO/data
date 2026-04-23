## Джерела даних

- **CSV** - отримано середньодобову температуру з [Kaggle](https://www.kaggle.com/datasets/sudalairajkumar/daily-temperature-of-major-cities/code). Проведено конвертацію з градусів фаренгейта у цельсії;
- **JSON** - отримано через [Open-Meteo API](https://open-meteo.com/). Тут є щоденні показники опадів та максимальної швидкості вітру.<br> Доступ до даних по конкретному [API](https://archive-api.open-meteo.com/v1/archive?latitude=50.4547&longitude=30.5238&start_date=1980-04-05&end_date=2026-04-19&daily=precipitation_sum,wind_speed_10m_max&timezone=auto&wind_speed_unit=ms);
- **SQL** - дані про щоденний індекс якості повітря (US AQI), отримані з [Kaggle](https://www.kaggle.com/datasets/nitirajkulkarni/kyiv-ua-703448?select=air_quality_historical.csv) і записані до локальної бази даних SQLite3.
## Обробка, очищення та злиття

**Обробка та очищення:**
- Приведення всіх форматів дат до єдиного типу `datetime64` за допомогою `pandas.to_datetime()`;
- Видалення дублікатів та пропущених значень за допомогою `pandas.dtop_duplicates()` та `pandas.dropna()`;
- Фільтарція міст наступним чином: `df_data_csv = df_data_csv[df_data_csv["City"] == "Kiev"]`, оскільки нам треба дані саме для Києва;
- Обчислення температур за цельсієм, оскільки в дадасеті дані, отримані з [Kaggle](https://www.kaggle.com/datasets/sudalairajkumar/daily-temperature-of-major-cities/code), записані у фаренгейтах.

**Злиття:** Об'єднання трьох датафреймів за спільним ключем `date` методом **Inner Join** за допомогою `pandas.merge()`.

## Результат

На виході отримуємо об'єднаний датафрейм, що містить наступні колонки:
- `date`: дата спостереження;
- `precipitation_sum`: сума опадів (мм);
- `wind_speed_10m_max`: максимальна швидкість вітру (м/с);
- `AvgTemperature`: середня температура (°C);
- `us_aqi`: індекс якості повітря (стандарт США).
<br>
З таким датасетом, наприклад, можна будувати моделі передбачення якості повітря в Києві та експерементувати з ними.
