import pandas as pd
import numpy as np
import scipy.stats as sts
import matplotlib.pyplot as plt
from itertools import islice

def irvin_test(series, crit):
        """
        В таблице выше указаны критические значения для проверки,
        выбирать значение изходя из размера выборки и передать его в функцию

        series: pd.Series
          Передаем столбец из ДатаФрейма или же pd.Series(y)

        crit: float
          Критическое значение

        """
        y = series.to_numpy()
        y_mean = y.mean()
        n = y.shape[0]
        S_y = np.sqrt(sum((y - y_mean)**2) / (n - 1))
        lambda_ = pd.Series(abs(y[1:] - y[:-1]) / S_y)
        return series.loc[lambda_[(lambda_ > crit)].index]

def foster_stuart(y):
    n = len(y)

    k = [1] + [0]*(n - 1)
    l = [1] + [0]*(n - 1)
    for t in range(1, n):
        if y[t] > max(y[:t]): k[t] = 1
        if y[t] < min(y[:t]): l[t] = 1
    k = np.array(k)
    l = np.array(l)

    s = sum(k[1:]+l[1:])
    d = sum(k[1:]-l[1:])

    mu_s = (1.693872*np.log(n) - 0.299015)/(1 - 0.035092*np.log(n) + 0.002705*np.log(n)**2)
    mu_d = 0
    sigma_s = np.sqrt(2*np.log(n)-3.4253)
    sigma_d = np.sqrt(2*np.log(n)-0.8456)

    t_s = np.abs(s - mu_s)/sigma_s
    t_d = np.abs(d - mu_d)/sigma_d

    alpha = 0.05
    t_kr = sts.t.ppf(1 - alpha/2, df = len(y) - 1)

    trend = "Тренд отсутствует"
    if t_s > t_kr and t_d > t_kr:
        trend = "Есть тренд и тренд дисперсии"
    elif t_s > t_kr:
        trend = "Есть тренд"
    elif t_d > t_kr:
        trend = "Есть тренд дисперсии"

    return trend, t_s, t_d

def student_t_test(series):
    n = series.shape[0]
    S_y = np.std(series); S_y
    y_mean = np.mean(series)
    r_estim = abs(series - y_mean) / S_y
    t_05 = sts.t.ppf(1 - 0.05/2, n - 2)
    t_001 = sts.t.ppf(1 - 0.001/2, n - 2)
    r_05 = (t_05 * np.sqrt(n - 1)) / np.sqrt(n - 2 + t_05**2)
    r_001 = (t_001 * np.sqrt(n - 1)) / np.sqrt(n - 2 + t_001**2)
    return series.loc[r_estim[(r_estim > r_001)].index]

def series_median(y):
  y = sorted(y)

  median = np.median(y)
  ls = ['+' if i > median else '-' for i in y]

  # Подсчет числа серий
  current_series = 0
  num_series = 0
  for i in ls:
      if current_series != i:
          num_series += 1
      current_series = i

  # Вычисление максимальной протяженности серии

  max_length = 1
  current_length = 1

  for i in range(1, len(ls)):
      if ls[i-1] == ls[i]:
          current_length += 1
      else:
          max_length = max(max_length, current_length)
          current_length = 0

  print("Число серий:", num_series)
  print("Максимальная протяженность серии:", max_length)

  # Проверка условий отсутствия тренда
  n = len(y)
  no_trend_condition = max_length < 3.3 * np.log10(n + 1)
  series_condition = num_series > (1/2 * (n + 1 - 1.96 * np.sqrt(n - 1)))

  print("Условие отсутствия тренда (по макс. протяженности серии):", no_trend_condition)
  print("Условие отсутствия тренда (по числу серий):", series_condition)

def check_trend_sr(data2):
    alpha = 0.01
    # Исходный ряд разбивается на две примерно равные по числу уровней части
    split_index = len(data2) // 2
    first_half = data2[:split_index]
    second_half = data2[split_index:]
    # Вычисляем средние значения и дисперсии для двух половин
    mean_first = np.mean(first_half)
    mean_second = np.mean(second_half)
    var_first = np.var(first_half, ddof=1)
    var_second = np.var(second_half, ddof=1)

    # Вычисляем наблюдаемое и критическое значение критерия
    f_value = var_first / var_second if var_first > var_second else var_second / var_first
    critical_value_f = sts.f.ppf(1 - alpha, len(first_half)-1, len(second_half)-1)

    # Проверяем гипотезу об отсутсвии тренда с использованием t-критерия Стьюдента
    n1 = len(first_half)
    n2 = len(second_half)
    sigma = np.sqrt(((n1-1)*var_first + (n2-1)*var_second)/((n1+n2-2)))
    t_value = abs((mean_first - mean_second))/sigma*np.sqrt(1/len(first_half)+1/len(second_half))
    crit_t = sts.t.ppf(1-alpha,len(first_half)+len(second_half)-2)
    if t_value<crit_t and f_value >= critical_value_f:
        print("Тренд не обнаружен")
    else:
        print("Обнаружен тренд в данных")
    print(t_value,f_value,crit_t,critical_value_f)