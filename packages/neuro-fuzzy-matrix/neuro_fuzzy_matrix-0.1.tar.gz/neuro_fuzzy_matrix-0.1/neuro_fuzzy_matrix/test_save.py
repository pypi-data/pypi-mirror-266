import NeuFuzMatrix # нейронная сеть
import os # работа с файлами
import numpy as np
import pickle  # сохрание и загрузка состояния нейросети 

# загрузка состояния сети
with open("neuro_matrix_model1.pkl", 'rb') as f:
    nfm_loaded = pickle.load(f)

# предсказание значений целевой переменной
X_test = np.array([[22, 3],
                   [65, 5]])
y_test = NeuFuzMatrix.predict(nfm_loaded,X_test)
print(y_test)