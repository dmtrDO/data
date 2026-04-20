# 4. Байєсівський аналіз споживання
# Реалізуйте байєсівську регресію для моделювання залежностей між погодними
# умовами та енергоспоживанням. Порівняйте отримані висновки з результатами,
# отриманими за допомогою класичної лінійної регресії. Побудуйте графіки для
# візуалізації отриманих залежностей.

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# псевдогенератор з деяким зерном щоб можна було відтворити результати
RNG = np.random.default_rng(seed=42)

# https://www.kaggle.com/datasets/sudhirsingh27/electricity-consumption-based-on-weather-data
FILE = "data.csv"

# date, AWND, PRCP, TMAX, TMIN, daily_consumption
df = pd.read_csv(FILE)
df = df.dropna()
df["date"] = pd.to_datetime(df["date"]).dt.month
df = df.rename(columns={"date": "month"})

# перемішуємо дані
df = df.sample(frac=1, random_state=42)

# ділимо на ознаки та мітки
X = df.iloc[:, [0, 1, 2, 3, 4]]
y = df.iloc[:, 5]

# ділимо на тренувальну та тестову вибірки
num_of_train = int(len(X) * 0.95)
X_train, y_train = X.iloc[:num_of_train].to_numpy(), y.iloc[:num_of_train].to_numpy()
X_test, y_test = X.iloc[num_of_train:len(X)].to_numpy(), y.iloc[num_of_train:len(y)].to_numpy()

# стандартизація
X_mean = X_train.mean(axis=0)
X_std = X_train.std(axis=0)

X_train = (X_train - X_mean) / X_std
X_test = (X_test - X_mean) / X_std

y_mean = y_train.mean()
y_std = y_train.std()

y_train = (y_train - y_mean) / y_std
y_test = (y_test - y_mean) / y_std


class MyLinearRegression():
    def __init__(self, num_of_features):
        # ініціалізуємо ваги та зміщення
        self.__weights = RNG.random(num_of_features)
        self.__bias = RNG.random()

    def train(self, X_train, y_train):
        # y = w1x1 + w2x2 + w3x3 ... + wnxn + bias
        # l = loss function (mse)
        # l = 1/num_of_x * sum((yi - y_predi)**2) (i = 1...num_of_x)

        # для мінімізації функції втрат будемо використовувати
        # градієнтний спуск

        # grad = (dl/dw1; dl/dw2 ... ; dl/dwn) 
        
        # i = 3, num_of_x = 2
        # l = 1/2 * ((y1-(w1x11+w2x12+w3x13+b))**2 + (y2-(w1x21+w2x22+w3x33+b))**2)
        
        # dl/db = 1/2 * (2 * (y1-(w1x11+w2x12+w3x13) * -1) + 2 * (y2-(w1x21+w2x22+x3x23) * -1)) = 
        # 1/2 * -2 (y1-ypred_1 + y2-ypred2) = -2/2 * sum(error), error = error_1 + error_2
        
        # dl/dw1 = 1/2 * (2 * (y1-(w1x11+w2x12+w3x13) * -x11) + 2 * (y2-(w1x21+w2x22+x3x23) * -x21)) = 
        # 1/2 * ((-2 * error_1 * x11) + (-2 * error_2 * x21)) = -2/2 * (error_1 * x11 + error_2 * x21)
        # dl/dw = -2/2 * [error_1 * x11 + error_2 * x21, error_1 * x12 + error_2 * x22, error_1 * x13 + error_2 * x23]

        # error = [error_1, error_2]
        # x = [[x11, x12, x13],
        #      [x21, x22, x23]]
 
        y_train = np.array(y_train)

        epochs = 100
        lr = 0.1
        print("Training...")
        for epoch in range(epochs):
            error = y_train - self.predict(X_train)
            
            db = -2/len(X_train) * np.sum(error)
            dw = -2/len(X_train) * np.dot(error, X_train)

            self.__bias -= lr * db
            self.__weights -= lr * dw

            if epoch % 10 == 0:
                print(f"epoch {epoch}, loss: {np.mean(error**2)}")

        # X = np.append(np.ones((X_train.shape[0], 1)), X_train, 1)
        # B = np.linalg.inv(X.T @ X) @ X.T @ y_train
        # self.__bias = B[0]
        # self.__weights = B[1:]

    def predict(self, X): 
        return np.dot(X, self.__weights) + self.__bias


class MyBayesRegression():
    def __init__(self, s, sigma):
        self.__s = s
        self.__sigma = sigma

    def train(self, X_train, y_train):
        # y^ ~ N(mu, sigma^2)
        # mu = w0 + w1*x1 + w2*x2 + ... + wn*xn, B = (w0, w1, ..., wn)
        # y^ ~ N(XW, sigma^2*I)

        # P(A|B) = P(B|A) * P(A) / P(B)
        # P(Model|New Data) = P(New Data | Model) * P(Model) / P(New Data)
        #     poesterior          likelihood         prior       evidence 

        # p(W | D) ∝ p(W) * p(D | W)
        # W ~ N(0, S)
        
        X = np.append(np.ones((X_train.shape[0], 1)), X_train, axis=1)
        S = self.__s * np.identity(X.shape[1])
        self.__E_inv = 1/self.__sigma**2 * (X.T @ X) + np.linalg.inv(S)
        self.__mu = 1/self.__sigma**2 * (np.linalg.inv(self.__E_inv) @ X.T @ y_train)

    def predict(self, X_test):
        X = np.append(np.ones((X_test.shape[0], 1)), X_test, axis=1)
        mu_pred = X @ self.__mu
        sigma_pred = self.__sigma**2 + np.sum(X @ np.linalg.inv(self.__E_inv) * X, axis=1)
        return mu_pred, sigma_pred


def run_linear_regression():
    # sklearn
    from sklearn.linear_model import LinearRegression
    linear_regression_model = LinearRegression()
    linear_regression_model.fit(X_train, y_train)
    y_pred_sk = linear_regression_model.predict(X_test)

    # власна реалізація
    linear_regression_model = MyLinearRegression(5)
    linear_regression_model.train(X_train, y_train)

    # тестування та оцінка точності через MSE
    y_pred = linear_regression_model.predict(X_test)
    mse_test = np.mean((y_test - y_pred)**2)
    print(f"Test MSE: {mse_test}")

    # зворотна стандартизація
    y_test_copy = y_test * y_std + y_mean
    y_pred = np.array(y_pred) * y_std + y_mean
    y_pred_sk = np.array(y_pred_sk) * y_std + y_mean

    # візуалізація
    plt.figure(figsize=(15, 4))
    plt.title("Linear regression")
    plt.ylabel("Energy consumption")
    plt.plot(y_test_copy, label="y_test")
    plt.plot(y_pred_sk, label="y_pred_sk")
    plt.plot(y_pred, label="y_pred")
    plt.legend()
    plt.show()


def run_bayes():
    # sklearn
    from sklearn.linear_model import BayesianRidge
    linear_bayes_regression_model = BayesianRidge()
    linear_bayes_regression_model.fit(X_train, y_train)
    y_pred_sk = linear_bayes_regression_model.predict(X_test, return_std=True)

    # власна реалізація
    linear_bayes_regression_model = MyBayesRegression(1, 0.1)
    linear_bayes_regression_model.train(X_train, y_train)
    y_pred = linear_bayes_regression_model.predict(X_test)

    # зворотна стандартизація
    y_test_copy = y_test * y_std + y_mean
    y_pred = np.array(y_pred) * y_std + y_mean
    y_pred_sk = np.array(y_pred_sk) * y_std + y_mean

    # візуалізація
    plt.figure(figsize=(15, 4))
    plt.plot(y_test_copy, label="y_test", c="green")
    plt.plot(y_pred_sk[0], label="y_pred_sk", c="red")
    plt.plot(y_pred[0], label="y_pred", c="orange")
    plt.fill_between(
        range(len(y_pred[0])), 
        y_pred[0] - y_pred[1], 
        y_pred[0] + y_pred[1], 
        color='red', alpha=0.2, label="1σ"
    )
    plt.fill_between(
        range(len(y_pred_sk[0])), 
        y_pred_sk[0] - y_pred_sk[1], 
        y_pred_sk[0] + y_pred_sk[1], 
        color='brown', alpha=0.1, label="1σ sk"
    )
    plt.legend()
    plt.show()


run_linear_regression()
run_bayes()


