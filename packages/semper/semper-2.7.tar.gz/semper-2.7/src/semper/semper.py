
class q5:
    def pictures(number, search=-1):
        sklad = {1: ["""1. Предварительный анализ временных рядов. Построить график и провести визуальный анализ. Результаты описать. (5 баллов)											

           
plt.figure(figsize=(10, 6))
plt.plot(data.index, data['Sales'], marker='o', linestyle='-', color='b')
plt.title('Monthly Sales Data')
plt.xlabel('Date')
plt.ylabel('Sales')
plt.grid(True)
plt.show()

"""],
                 2: ["""2. Провести выявление аномальных наблюдений с помощью использования распределения Стьюдента. Написать выводы. (7 баллов)											

import numpy as np
from scipy.stats import t

def max_relative_deviation(y_star, y_mean, Sy):
    return (y_star - y_mean) / Sy

def test_max_relative_deviation(alpha, n):
    t_critical = t.ppf(1 - alpha / 2, n - 2)
    tau_alpha_1 = np.sqrt(n - 1) *t_critical
    tau_alpha_2 = np.sqrt(n - 2 + t_critical**2)
    return tau_alpha_1 / tau_alpha_2

# Пример временного ряда (замените этот ряд своим)
y = np.array([3, 2, 1, 3, 2, 1, 3, 2, 3, 1, 2, 3, 101, 4, 3, 2, 1])#np.array(df['IP2_DEA_M'])
# Среднее значение и среднеквадратическое отклонение временного ряда
y_mean = np.mean(y)
Sy = y.std(ddof=1)
print(y_mean, Sy)

# Определение критических значений
alpha = 0.05  # Уровень значимости
n = len(y)    # Размер выборки
t_alpha_1= test_max_relative_deviation(alpha, n)
t_alpha_2= test_max_relative_deviation(0.001, n)
for yi in y:
    t_ = abs(yi - y_mean) / Sy
    if yi > 100:
        print(t_, t_alpha_1, t_alpha_2)
    if t_ <= t_alpha_1:
        print('Наблюдение нельзя считать аномальным.')
    elif t_alpha_1 < t_ <= t_alpha_2:
        print('Смотреть другие признаки.')
    else:
        print('Наблюдение аномально.')

# второй варик

import numpy as np
from scipy.stats import t

def max_relative_deviation(y_star, y_mean, Sy):
    return (y_star - y_mean) / Sy

def test_max_relative_deviation(tau, alpha, n):
    t_critical = t.ppf(1 - alpha / 2, n - 2)
    tau_alpha_1 = (n - 2) / (n - 2 + t_critical**2)
    tau_alpha_2 = (n - 2 + t_critical**2) / (n - 2)
    return tau_alpha_1, tau_alpha_2

# Пример временного ряда (замените этот ряд своим)
y = np.array(df['IP2_DEA_M'])
# Среднее значение и среднеквадратическое отклонение временного ряда
y_mean = np.mean(y)
Sy = np.std(y)

# Вычисление статистики максимального относительного отклонения для каждого элемента ряда
tau_values = [max_relative_deviation(y_star, y_mean, Sy) for y_star in y]

# Определение критических значений
alpha = 0.05  # Уровень значимости
n = len(y)    # Размер выборки
tau_alpha_1, tau_alpha_2 = test_max_relative_deviation(max(tau_values), alpha, n)

# Вывод результатов
print("Максимальное относительное отклонение (τ):", max(tau_values))
print("Критические значения относительного отклонения (τ_alpha_1, τ_alpha_2):", tau_alpha_1, tau_alpha_2)

# Проверка наличия аномальных значений
k = 0
Sy = np.sqrt(np.sum((y - np.mean(y))**2) / (len(y) - 1))
for i in tau_values[1:]:
    k += 1
    if i <= tau_alpha_2:
        print("Наблюдение нельзя считать аномальным.")
    else:
        if abs(y[k] - y[k-1]) / Sy > 1:
            print("Наблюдение можно считать аномальным.")
        else:
            print("Наблюдение нельзя считать аномальным.")
"""],
                 3: ["""3. Провести проверку наличия тренда с помощью: Критерия серий, основанный на медиане. Сделать выводы. (9 баллов)											
							
median_sales = data['Sales'].median()

# Определение, лежит ли каждое значение выше или ниже медианы
above_median = data['Sales'] > median_sales

# Подсчет серий
current_flag = None
num_series = 0

for flag in above_median:
    if current_flag is None:
        current_flag = flag
        num_series = 1
    elif flag != current_flag:
        current_flag = flag
        num_series += 1

# Расчет ожидаемого количества серий и его дисперсии
n = len(data)
expected_num_series = (2 * n - 1) / 3
variance_num_series = (16 * n - 29) / 90

# Z-статистика
z = (num_series - expected_num_series) / np.sqrt(variance_num_series)

num_series, z
				
											
 """],
                 4: ["""4. Построить прогноз для 5 последних точек (тестовая часть) с помощью кривой роста. Выбрать оптимальную кривую роста на основе разностей. (9 баллов)											
											
				
# Разделение данных на обучающую и тестовую выборки
train_data = data[:-5]
test_data = data[-5:]

from scipy.optimize import curve_fit

# Линейная функция
def linear_func(x, a, b):
    return a * x + b

# Экспоненциальная функция
def exponential_func(x, a, b):
    return a * np.exp(b * x)

# Подгонка моделей
x_train = np.arange(len(train_data))
y_train = train_data['Sales'].values

# Линейная модель
linear_params, _ = curve_fit(linear_func, x_train, y_train)

# Экспоненциальная модель
# Для экспоненциальной модели сначала преобразуем y_train
y_train_log = np.log(y_train)
exponential_params, _ = curve_fit(exponential_func, x_train, y_train, p0=(1, 0.001))

# Прогноз для тестовых данных
x_test = np.arange(len(train_data), len(data))
linear_predictions = linear_func(x_test, *linear_params)
exponential_predictions = exponential_func(x_test, *exponential_params)

# Вычисление ошибок
from sklearn.metrics import mean_squared_error

linear_mse = mean_squared_error(test_data['Sales'].values, linear_predictions)
exponential_mse = mean_squared_error(test_data['Sales'].values, exponential_predictions)

linear_mse, exponential_mse
							
 """],
                 5: ["""Провести проверку наличия тренда с помощью Метода проверки разности средних уровней. Сделать выводы. (9 баллов)
n1 = n // 2
n2 = n - n1
y1_ = y[: n1].mean()
y2_ = y[n1: ].mean()
s1_ = y[: n1].var(ddof=1)
s2_ = y[n1: ].var(ddof=1)
print(s1_, s2_)

print(max(s2_, s1_) / min(s1_, s2_))  

from scipy.stats import f
print(f(n1 - 1, n2 - 1).isf(0.05))
# если max(s2_, s1_) / min(s1_, s2_) < f(n1 - 1, n2 - 1).isf(0.05) то продолжаем, иначе не работает метод
sigma_viktor_chagai = np.sqrt(((n1 - 1)*s1_**2 + (n2 - 1)*s2_**2) / (n1 + n2 - 2))

audi_tt = abs(y1_.mean() - y2_.mean()) / (sigma_viktor_chagai * np.sqrt((1 / n1 + 1 / n2)))
from scipy.stats import t
audi_tt, t(n1 + n2 - 2).isf(0.05)        
# если рассчёт меньше, то гипотеза принимается   
"""],
                 6: ["""2.Провести выявление аномальных наблюдений с помощью Метода Ирвина. Написать выводы. (7 баллов)											
							
import numpy as np
import pandas as pd

# Генерация временного ряда с одним аномальным значением
np.random.seed(0)
dates = pd.date_range(start='2021-01-01', end='2021-12-31', freq='M')
sales = np.random.randn(len(dates)) * 10 + 200
sales[6] += 50  # Добавление аномалии

data = pd.DataFrame(data={'Sales': sales}, index=dates)

# Расчет среднего и стандартного отклонения
mean_sales = np.mean(data['Sales'])
std_dev_sales = np.std(data['Sales'])

# Вычисление разностей между последовательными значениями
differences = np.abs(np.diff(data['Sales']))

# Вычисление тестовой статистики Ирвина для каждой разницы
irwin_test_statistic = differences / std_dev_sales

# Определение порогового значения (обычно используется 2 или 3 для уровня значимости 0.05 или 0.01 соответственно)
threshold = 2

# Идентификация аномальных наблюдений
anomalies = data.iloc[1:][irwin_test_statistic > threshold]

# Выводы
print(f"Обнаруженные аномалии:\n{anomalies}")

data = {
    'Количество наблюдений n': [2, 3, 10, 20, 30, 50, 100],
    'P=0,95': [2.8, 2.2, 1.5, 1.3, 1.2, 1.1, 1.0],
    'P=0,99': [3.7, 2.9, 2.0, 1.8, 1.7, 1.6, 1.5]
}
											
 """],
                 
                 7: ["""3. Провести проверку наличия тренда с помощью Метода Фостера-Стьюарта. Сделать выводы. (9 баллов)											
# хардкод								
import numpy as np
from scipy.stats import t
def foster_stuart(data):
    k = np.array([1] + [int(el > max(data[: i + 1])) for i, el in enumerate(data[1:])])
    l = np.array([1] + [int(el < min(data[: i + 1])) for i, el in enumerate(data[1:])])
    s = sum(k[2:] + l[2: ])
    d = sum(k[2:] - l[2: ])
    n = len(data)
    mu = (1.693872 * np.log(n) - 0.299) / (1 - 0.35092 * np.log(n) + 0.002705 * np.log(n) ** 2)
    sigma1 = np.sqrt(2 * np.log(n) - 3.4253)
    sigma2 = np.sqrt(2 * np.log(n) - 0.84556)
    ts = abs(s - mu) / sigma1
    td = abs(d) / sigma2
    trk = t(n - 1).isf(0.05)
    if ts < trk:
        print('Тренда ряда нет')
    else:
        print('Тренд ряда есть')
    
    if td < trk:
        print('Тренда дисперсии нет')
    else:
        print('Тренд дисперсии есть')
#бабл метод
from scipy import stats

# Делим временной ряд на две части
n = len(data)
half = n // 2
first_half = data['Sales'][:half]
second_half = data['Sales'][half:]

# Вычисляем средние значения для каждой части
mean_first_half = first_half.mean()
mean_second_half = second_half.mean()

# Используем t-тест для сравнения двух выборок
t_stat, p_value = stats.ttest_ind(first_half, second_half, equal_var=False)

# Выводы
mean_first_half, mean_second_half, t_stat, p_value

from scipy.stats import t

def get_t_critical(n, alpha):
    # Степени свободы для двух выборок
    df = (n // 2 - 1) + (n // 2 - 1)
    # t-критическое значение для двустороннего теста
    t_critical = t.ppf(1 - alpha / 2, df)
    return t_critical

# Пример использования:
n = 30  # Количество наблюдений
alpha = 0.05  # Уровень значимости

t_critical = get_t_critical(n, alpha)
print(f"t-критическое значение для {n} наблюдений и уровня значимости {alpha} равно {t_critical:.3f}")

											
 """],

                9: ["""1. Осуществить прогнозирование с применением адаптивной модели прогнозирования Брауна.  (10 баллов)											
											
def brown_exponential_smoothing(series, alpha):
    #Прогнозирование с использованием экспоненциального сглаживания Брауна.
    result = [series[0]]  # первое значение прогноза равно первому значению серии
    for n in range(1, len(series)):
        result.append(alpha * series[n] + (1 - alpha) * result[n-1])
    return result

# Пример использования модели Брауна для прогнозирования
alpha = 0.3  # примерное значение параметра сглаживания
sales_predictions = brown_exponential_smoothing(data['Sales'], alpha)

# Добавляем прогноз на следующие 5 точек за пределами нашего временного ряда
for _ in range(5):
    sales_predictions.append(alpha * sales_predictions[-1] + (1 - alpha) * sales_predictions[-1])

# Визуализация фактических и прогнозируемых значений
import matplotlib.pyplot as plt

plt.figure(figsize=(10, 6))
plt.plot(data.index, data['Sales'], label='Фактические продажи')
plt.plot(data.index.append(pd.date_range(start=data.index[-1] + pd.Timedelta(days=31), periods=5, freq='M')), sales_predictions, label='Прогноз', linestyle='--')
plt.legend()
plt.title('Прогноз продаж с использованием модели Брауна')
plt.xlabel('Дата')
plt.ylabel('Продажи')
plt.xticks(rotation=45)
plt.show()

											
 """],
                10: ["""2. Моделирование тренд-сезонных процессов. Применить Модель Хольта-Уинтерса. (10 баллов) 											
											
from statsmodels.tsa.holtwinters import ExponentialSmoothing
from sklearn.metrics import mean_absolute_percentage_error
import numpy as np

# Предположим, что data['Sales'] - это ваш временной ряд

# Разделение данных на обучающую и валидационную выборки
train, test = data['Sales'][:-12], data['Sales'][-12:]

# Функция для оценки MAPE
def evaluate_model(train, test, seasonal_model):
    model = ExponentialSmoothing(train, trend='add', seasonal=seasonal_model, seasonal_periods=12)
    model_fit = model.fit(optimized=True)
    predictions = model_fit.forecast(len(test))
    mape = mean_absolute_percentage_error(test, predictions)
    return mape

# Оценка аддитивной модели
additive_mape = evaluate_model(train, test, 'add')
print(f'Аддитивная модель MAPE: {additive_mape}')

# Оценка мультипликативной модели
multiplicative_mape = evaluate_model(train, test, 'mul')
print(f'Мультипликативная модель MAPE: {multiplicative_mape}')

# Выбор модели
if additive_mape < multiplicative_mape:
    print("Выбрана аддитивная модель.")
else:
    print("Выбрана мультипликативная модель.")
    
from statsmodels.tsa.holtwinters import ExponentialSmoothing

holt_winters_model = ExponentialSmoothing(y, trend='additive', seasonal='additive', seasonal_periods=12).fit()

new = 40
holt_winters_forecast = holt_winters_model.forecast(new)

time_index_extended = np.arange(n + new)

plt.plot(y)
plt.plot(time_index_extended[n:], holt_winters_forecast)
plt.xlabel('t', fontsize=14)
plt.ylabel('y', fontsize=14)
plt.grid()
plt.show()
											
 """],
                11: [""""3. Выделение компонент тренд-сезонного временного ряда. Метод Четверикова: По заданным значениям временного ряда y_t выделить компоненты временного ряда: тренд f_t, сезонную компоненту S_t и остаточную последовательность ε_t.   (10 баллов)
Построить следующие диаграммы: 
1. Исходный ряд, тренды: предварительный, первый и второй. 
2. Сезонную волну: первую и вторую. 
3. Остаточную компоненту."											
					# предварительная оценка тренда
def preliminary_trend_estimation(x, T=12):
    b = len(x)
    c = np.convolve(x, np.ones(T)/T, mode='valid')
    d = (T - 1) // 2
    e = b - T // 2
    return c, d, e

# нормирование отклонений
def normalize_deviations(x, g, h, i, T=12):
    j = x[h:i] - g
    k = len(j) // T
    l = np.zeros_like(j)
    for m in range(k):
        n = slice(m * T, (m+1) * T)
        o = np.std(j[n])
        l[n] = j[n] / o if o != 0 else j[n]
    return l

# Проведем предварительную оценку тренда и нормирование отклонений
trend_preliminary, start, end = preliminary_trend_estimation(y)
normalized_deviations = normalize_deviations(y, trend_preliminary, start, end)

plt.figure(figsize=(14, 6))
trend_indexes = np.arange(start, end)
# Исходный ряд
plt.plot(np.array(time_)[:97], y, label='Исходный ряд')

# Предварительный тренд с выравниванием по индексам
plt.plot(np.array(time_)[trend_indexes], trend_preliminary, label='Предварительный тренд', color='red', linestyle='--')

plt.title('Исходный ряд и предварительный тренд')
plt.xlabel('Время')
plt.ylabel('Значения')
plt.legend()

plt.show()

# предварительная средняя сезонная волна
def preliminary_seasonal_wave(n, T=12):
    m = len(n) // T
    S = [np.mean(n[j::T]) for j in range(T)]
    return np.tile(S, m)
# первая оценка тренда
def first_trend_estimate(y, S, s, e, T=4):
    years = (e - s) // T
    sigma = [np.std(y[s + i * T:s + (i + 1) * T] - S[i * T:(i + 1) * T]) for i in range(years)]
    f_ij = y[s:e-1] - np.array(S) * np.repeat(sigma, T)
    return f_ij, sigma
# вторая оценка тренда (сглаживание)
def second_trend_estimate(f_ij, T=12):
    f_ij2 = np.convolve(f_ij, np.ones(5) / 5, mode='valid')
    f_ij2 = np.insert(f_ij2, 0, (5 * f_ij[0] + 2 * f_ij[1] - f_ij[2]) / 6)
    f_ij2 = np.append(f_ij2, (5 * f_ij[-1] + 2 * f_ij[-2] - f_ij[-3]) / 6)
    return f_ij2


S_j1 = preliminary_seasonal_wave(normalized_deviations)
f_ij1, sigma_i = first_trend_estimate(y, S_j1, start, end)
f_ij2 = second_trend_estimate(f_ij1)

# Построение диаграмм для первой и второй оценки тренда, а также для предварительной сезонной волны
plt.figure(figsize=(14, 12))

# Первая оценка тренда
plt.subplot(3, 1, 1)
plt.plot(np.array(time_)[:97], y, label='Исходный ряд')
tr = np.arange(start, end-1)
plt.plot(np.array(time_)[tr], f_ij1, label='Первая оценка тренда', color='green', linestyle='--')
plt.title('Первая оценка тренда')
plt.legend()

# Вторая оценка тренда
plt.subplot(3, 1, 2)
plt.plot(np.array(time_)[:97], y, label='Исходный ряд')
tr = np.arange(start+2, end-1)
plt.plot(np.array(time_)[tr], f_ij2, label='Вторая оценка тренда', color='purple', linestyle='--')
plt.title('Вторая оценка тренда')
plt.legend()
seasonal_component_full = np.tile(S_j1[:4], (len(y) + 3) // 4)[:len(y)]
# Сезонная компонента
plt.subplot(3, 1, 3)
plt.plot(seasonal_component_full, label='Сезонная компонента', color='orange')
plt.title('Сезонная компонента')
plt.legend()
plt.tight_layout()
plt.show()
											
 """],
                12: ["""1. Провести предобработку данны. Устранить выбросы, если они есть. Посмотреть соотношение классов и сделать выводы на этапе предобработки. (5 баллов)											
					
# Устранение выбросов
z_scores = np.abs(stats.zscore(data[['feature1', 'feature2']]))
filtered_entries = (z_scores < 3).all(axis=1)
data_cleaned = data[filtered_entries]

# Посмотреть соотношение классов
class_counts = data_cleaned['class'].value_counts(normalize=True)
print("Соотношение классов после очистки данных:")
print(class_counts)

# Визуализация соотношения классов
class_counts.plot(kind='bar')
plt.title('Соотношение классов')
plt.xlabel('Класс')
plt.ylabel('Частота')
plt.xticks(rotation=0)
plt.show()

# 2-е решение
def hrono_sr(sr, t0 = 4): #t0 = 12 если данные по месяцам и 4 если поквартально
    new_sr = []
    for i in range(t0 // 2, len(sr) - t0//2):
        new_sr.append(((sum(sr[i - t0//2 : i + t0//2 + 1]) - (sr[i - t0//2] + sr[i + t0//2]) / 2)) / t0)
    return new_sr
    
y_first = hrono_sr(y)

plt.plot(y_first, label='Предварительная оценка')
plt.plot(y[6 : -6], label= 'Исходный ряд')
plt.xlabel('t', fontsize=14)
plt.ylabel('y', fontsize=14)
plt.grid()
plt.legend()
plt.show()

l = np.array(y[2: -2]) - y_first # t0 / 2 # без концов
l

T0 = 4
def get_sigma(l):
    sigma_i = []
    for i in range(0, len(l), T0):
        sigma_i.append(np.sqrt((sum(l[i: i + T0] ** 2) - sum(l[i: i + T0]) ** 2 / T0) / (T0 - 1)))
    sigma_i = np.array(sigma_i)
    return sigma_i
sigma_i = get_sigma(l)
sigma_i

def norm_ost(l, sigma_i):
    l_ = []
    for i in range(len(l)):
        l_.append(l[i] / sigma_i[i // T0])
    l_ = np.array(l_) # нормированные отклонения
    return l_
l_ = norm_ost(l, sigma_i)
l_[:3]

def get_s(l_):
    Sj = []
    for j in range(T0):
        Sj.append(np.mean(l_[j: : T0]))
    return Sj
Sj  = get_s(l_)
Sj# предварительная сезонная волна

Y = y[T0//2 : -T0//2]
Y.shape

f1 = []
for i in range(0, len(Y)):
    f1.append(y[i] - sigma_i[i // T0] * Sj[i % T0])
f1 = np.array(f1)

plt.plot(f1, label='Первая оценка тренда')
plt.plot(Y, label= 'Исходный ряд')
plt.xlabel('t', fontsize=14)
plt.ylabel('y', fontsize=14)
plt.grid()
plt.legend()
plt.show()

f2 = np.convolve(f1, np.ones(5)/5, mode='valid')
f2 = np.insert(f2, 0, (5*f1[0] + 2*f1[1] - f1[2]) / 6)
f2 = np.insert(f2, 0, (f1[0] + f1[1] + f1[2]) / 3)
f2 = np.append(f2, (f1[-1] + f1[-2] + f1[-3]) / 3)
f2 = np.append(f2, (5*f1[-1] + 2*f1[-2] - f1[-3]) / 6)

plt.plot(f2, label='Вторая оценка тренда')
plt.plot(Y, label= 'Исходный ряд')
plt.xlabel('t', fontsize=14)
plt.ylabel('y', fontsize=14)
plt.grid()
plt.legend()
plt.show()

l2 = np.array(Y - f2)
l2

sigma_i = get_sigma(l2)
l_ = norm_ost(l2, sigma_i)
Sj2  = get_s(l_)
Sj2

plt.plot(Sj2, label='Окончательная средняя сезонная волна')
plt.plot(Sj, label='Предварительная средняя сезонная волна')
plt.xlabel('t', fontsize=14)
plt.grid()
plt.legend()
plt.show()

eij = []
for i in range(0, len(Y)):
    eij.append(l2[i] - sigma_i[i // T0] * Sj2[i % T0])
eij = np.array(f1)

plt.plot(eij, label='Остаточная компонента')
plt.xlabel('t', fontsize=14)
plt.grid()
plt.legend()
plt.show()


						
											
 """],
                13: ["""2. Разделить на трейн (70%) и тест (30%) датасет. Оценить логит и пробит модели, записать спецификации моделей. Сделать выводы о статистической значимости факторов. (9 баллов)											
			
from sklearn.model_selection import train_test_split
import statsmodels.api as sm
import statsmodels.formula.api as smf


# Разделение на тренировочный и тестовый наборы данных
X = data[['feature1', 'feature2']]
y = data['class']
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=0)

# Добавляем константу для оценки коэффициента сдвига
X_train_const = sm.add_constant(X_train)

# Оценка логит модели
logit_model = sm.Logit(y_train, X_train_const).fit()
print("Логит модель:\n", logit_model.summary())

# Оценка пробит модели
probit_model = sm.Probit(y_train, X_train_const).fit()
print("Пробит модель:\n", probit_model.summary())
								
											
 """],
                14: ["""3. Посчитать accuracy, precision, recall, f1 и confusion matrix (для теста) для двух моделей и сравнить их качество. (9 баллов)											
											
										
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix

# Добавляем константу к тестовым данным для предсказаний
X_test_const = sm.add_constant(X_test)

# Предсказания логит модели
y_pred_logit = logit_model.predict(X_test_const)
y_pred_logit = [1 if x > 0.5 else 0 for x in y_pred_logit]

# Предсказания пробит модели
y_pred_probit = probit_model.predict(X_test_const)
y_pred_probit = [1 if x > 0.5 else 0 for x in y_pred_probit]

# Метрики для логит модели
accuracy_logit = accuracy_score(y_test, y_pred_logit)
precision_logit = precision_score(y_test, y_pred_logit)
recall_logit = recall_score(y_test, y_pred_logit)
f1_logit = f1_score(y_test, y_pred_logit)
confusion_logit = confusion_matrix(y_test, y_pred_logit)

# Метрики для пробит модели
accuracy_probit = accuracy_score(y_test, y_pred_probit)
precision_probit = precision_score(y_test, y_pred_probit)
recall_probit = recall_score(y_test, y_pred_probit)
f1_probit = f1_score(y_test, y_pred_probit)
confusion_probit = confusion_matrix(y_test, y_pred_probit)

# Вывод результатов
print("Логит модель метрики:")
print(f"Accuracy: {accuracy_logit}, Precision: {precision_logit}, Recall: {recall_logit}, F1: {f1_logit}")
print(f"Confusion Matrix:\n{confusion_logit}\n")

print("Пробит модель метрики:")
print(f"Accuracy: {accuracy_probit}, Precision: {precision_probit}, Recall: {recall_probit}, F1: {f1_probit}")
print(f"Confusion Matrix:\n{confusion_probit}")
	
 """],
                15: ["""4. Пусть для попадания в класс 1 вероятность должна быть не меньше, чем 70%. Как изменится соотношение классов в двух моделях? А если 90%? (7 баллов)											
							
# Для логит модели
threshold_70 = 0.7
threshold_90 = 0.9

# Предсказания логит модели для новых порогов
y_pred_logit_70 = [1 if x > threshold_70 else 0 for x in y_pred_logit]
y_pred_logit_90 = [1 if x > threshold_90 else 0 for x in y_pred_logit]

# Соотношение классов для логит модели
class_ratio_logit_70 = np.mean(y_pred_logit_70)
class_ratio_logit_90 = np.mean(y_pred_logit_90)

# Предсказания пробит модели для новых порогов
y_pred_probit_70 = [1 if x > threshold_70 else 0 for x in y_pred_probit]
y_pred_probit_90 = [1 if x > threshold_90 else 0 for x in y_pred_probit]

# Соотношение классов для пробит модели
class_ratio_probit_70 = np.mean(y_pred_probit_70)
class_ratio_probit_90 = np.mean(y_pred_probit_90)

# Вывод результатов
(class_ratio_logit_70, class_ratio_logit_90), (class_ratio_probit_70, class_ratio_probit_90)
				
											
 """],}
        if number == -1:
            numbers = []
            for i, j in sklad.items():
                if search in j[0]:
                    numbers.append(i)
            return 'есть в этих номерах: ', numbers
        return sklad[number][0]


