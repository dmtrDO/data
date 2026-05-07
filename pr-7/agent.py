
# Варіант 4. Агент класифікації споживачів 
# Аналіз поведінки споживачів і автоматична
# класифікація (домогосподарства, бізнес). 
# Методи: K-means, Random Forest.

import pandas as pd

import os
from dotenv import load_dotenv

import warnings
from langchain_core._api.deprecation import LangChainPendingDeprecationWarning
warnings.filterwarnings("ignore", category=LangChainPendingDeprecationWarning)

from google import genai
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import create_agent
from langchain.tools import tool

from sklearn.ensemble import RandomForestClassifier
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

load_dotenv()
client = genai.Client(api_key=os.environ.get("GOOGLE_API_KEY"))

def save_available_models():
    with open("available_models.txt", "w") as f:
        for model in client.models.list():
            try:
                if "generateContent" not in model.supported_actions:
                    continue

                client.models.generate_content(model=model.name,contents="")

                f.write(f"{model.name}\n")

            except Exception:
                pass

# save_available_models()
# exit()

model_name = "models/gemini-3.1-flash-lite-preview"
google_llm = ChatGoogleGenerativeAI(model=model_name)


@tool
def analyze_dataset(csv_path: str):
    """
    Аніз структури датасету і визначення 
    чи існує цільова колонка (мітка)
    """

    try:
        df = pd.read_csv(csv_path)
        columns = df.columns.tolist()
        numeric_columns = df.select_dtypes(include=["number"]).columns.tolist()
        possible_targets = [ 
            col for col in columns
                if col.lower() in ["target", "type", "class", "label" ]
        ]
        samples = df.head()

        return {
            "columns": columns,
            "numeric_columns": numeric_columns,
            "dataset_size": len(df),
            "possible_targets": possible_targets,
            "samples": samples
        }

    except Exception as e:
        return {
            "status": "error",
            "message": f"Помилка при обробці датасету: {str(e)}",
        }


@tool
def run_kmeans(path_to_csv_file: str, n_clusters: int = 3):
    """
    Запускає кластеризацію KMeans для набору даних.
    Аргументи:
        path_to_csv_file: Шлях до файлу CSV.
        n_clusters: Кількість кластерів (за замовчуванням 3).
    """

    try:
        df = pd.read_csv(path_to_csv_file)
        numeric_df = df.select_dtypes(include=["number"])
        scaler = StandardScaler()
        scaled_data = scaler.fit_transform(numeric_df)
        model = KMeans(n_clusters=n_clusters,random_state=42)
        clusters = model.fit_predict(scaled_data)
        df["cluster"] = clusters

        return {
            "cluster_count": n_clusters,
            "dataset_size": len(df),
            "cluster_distribution": df["cluster"].value_counts().to_dict()
        }
    
    except Exception as e:
        return {
            "status": "error",
            "message": f"Помилка при навчанні моделі через kmeans: {str(e)}",
        }


@tool
def run_random_forest(path_to_csv_file: str, target_column: str):
    """
    Запускає метод класифікації Random Forest для набору даних.
    Аргументи:
        path_to_csv_file: Шлях до файлу CSV.
        target_column: Цільова мітка (Кількість спожитої енергії).
    """

    try:
        df = pd.read_csv(path_to_csv_file)
        X = df.drop(columns=[target_column])
        X = X.select_dtypes(include=["number"])
        y = df[target_column]
        X_train, X_test, y_train, y_test =\
            train_test_split(X, y, test_size=0.2, random_state=42)

        model = RandomForestClassifier(n_estimators=100, random_state=42)
        model.fit(X_train, y_train)
        predictions = model.predict(X_test)
        accuracy = accuracy_score(y_test, predictions)
        feature_importance = dict(
            zip(X.columns, model.feature_importances_)
        )

        return {
            "algorithm": "RandomForest",
            "accuracy": round(float(accuracy), 4),
            "dataset_size": len(df),
            "features": X.columns.tolist(),
            "feature_importance": feature_importance
        }
    
    except Exception as e:
        return {
            "status": "error",
            "message": f"Помилка при навчанні моделі через random forest: {str(e)}",
            "suggestion": "Переконайся, що цільова колонка не містить порожніх значень або спробуй KMeans."
        }


system_prompt = """
Ти — агент аналізу споживачів на основі штучного інтелекту
для автоматичної класифікації (домогосподарства, бізнес).

Твоє завдання:

В першу чергу завжди починай з інструменту analyze_dataset.

1. Проаналізувати структуру набору даних. Окрім цього тобі
ще буде надано посилання на джерело, де ти можеш
дізнатись більше детально про структуру датасету

2. Визнач, чи містить набір даних цільовий стовпець.

Правила:
- Якщо набір даних містить ціль/тип/клас/мітку, 
важливо, щоб це було нечислове значення, мітка
має означати клас споживача, наприклад 
(бізнес-компанія, домогосподарство):
використовуй класифікацію Random Forest.
- Якщо набір даних не містить цільових міток:
використовуй кластеризацію KMeans.

Поясни результат після запуску машинного навчання, а саме:

1. “Аналіз поведінки споживачів”
Це вивчення того, як користувачі або клієнти використовують ресурс або послугу.
Наприклад: скільки електроенергії споживають в який час активні
чи є стабільне споживання, чи різкі піки як змінюється
споживання з часом. Тобто ти дивишся на “патерни” поведінки в даних.

2. “класифікація”
Ти маєш визначаити категорію об’єкта, тобто у твоєму випадку:
є дані по споживачу, ти маєш сказати: домогосподарство чи бізнес.
“Домогосподарства / бізнес” - це класи (labels), які ти маєш передбачити:

Також важлива примітка: не обов'язково такі мітки, можна й інші
на твій власний розгляд
"""

agent = create_agent(
    model=google_llm,
    tools=[analyze_dataset, run_kmeans, run_random_forest],
    system_prompt=system_prompt
)

data = { 
    "data1": {
        "csv_file_name": "Energy_consumption.csv",
        "df_link": "https://www.kaggle.com/datasets/mrsimple07/energy-consumption-prediction"
    }, 
    "data2": {
        "csv_file_name": "global_energy_consumption.csv",
        "df_link": "https://www.kaggle.com/datasets/atharvasoundankar/global-energy-consumption-2000-2024"
    }, 
    "data3": {
        "csv_file_name": "Energy_Consumption_Efficiency.csv",
        "df_link": "https://www.kaggle.com/datasets/taruneshburman/energy-consumption-efficiency-dataset"
    },
}

user_content = f"""
Проаналізуй датасет: {data["data3"]}
"""

response = agent.invoke({
    "messages": [
        {
            "role": "user",
            "content": user_content
        }
    ]
})

print(response["messages"][-1].content[0]["text"])


