import NeuFuzMatrix # нейронная сеть
import os # работа с файлами
import numpy as np
import pickle  # сохрание и загрузка состояния нейросети 

# Текущая директория
current_dir = os.path.dirname(os.path.abspath(__file__))

# Путь к файлу относительно текущей директории
file_path = os.path.join(current_dir, "test_matrix.txt") 

ts = np.loadtxt(file_path, usecols=[0,1,2])
X = ts[:,0:2]
Y = ts[:,2]

nfm = NeuFuzMatrix.NFM(X, Y)
nfm.algorithm="Not rules"
f_temp = nfm.create_feature("Температура", "C", 0, 150, True)
f_flow =  nfm.create_feature("Расход", "м3/ч", 0, 8, True)
f_pressure  = nfm.create_feature("Давление", "МПа", 0, 100, False)
p_temp_low = nfm.create_predicate(f_temp, 'низкая', ['Gauss',{'mean':30,'sigma':10}])
p_temp_normal = nfm.create_predicate(f_temp, 'средняя', ['Gauss',{'mean':70,'sigma':10}])
p_temp_high = nfm.create_predicate(f_temp, 'высокая', ['Gauss',{'mean':120,'sigma':10}])
p_flow_low = nfm.create_predicate(f_flow, 'малый', ['Gauss',{'mean':2,'sigma':1}])
p_flow_normal = nfm.create_predicate(f_flow, 'средний', ['Gauss',{'mean':4,'sigma':1}])
p_flow_high = nfm.create_predicate(f_flow, 'большой', ['Gauss',{'mean':6,'sigma':1}])


nfm.train(epochs=5)

print("Plotting errors")
nfm.plotErrors()
print("Plotting results")
nfm.plotResults()

x_values = np.linspace(-300, 100, 400)
nfm.plotMF(x_values,f_temp)
nfm.plotMF(x_values,f_flow)

# X_test = np.array([[35, 3],
#                    [65, 5]])
# y_test = NeuFuzMatrix.predict(nfm,X_test)

# print(y_test)

# сохранение состояния сети
with open('neuro_matrix_model1.pkl', 'wb') as f:
    pickle.dump(nfm, f)
    
# nfm.save('my_model_full.h5')








# import anfis
# import os
# import numpy as np

# # Получаем текущую директорию
# current_dir = os.path.dirname(os.path.abspath(__file__))

# # Построение пути к файлу относительно текущей директории
# file_path = os.path.join(current_dir, "trainingSet.txt")

# # Загружаем файл
# ts = np.loadtxt(file_path, usecols=[1,2,3])
# X = ts[:,0:2]
# Y = ts[:,2]

# predict_func = [[['Gauss',{'mean':0.,'sigma':1.}],
# 	   ['Gauss',{'mean':-1.,'sigma':2.}],
# 	   ['Gauss',{'mean':-4.,'sigma':10.}],
# 	   ['Gauss',{'mean':-7.,'sigma':7.}]],
#             [['Gauss',{'mean':1.,'sigma':2.}],
# 			 ['Gauss',{'mean':2.,'sigma':3.}],
# 			 ['Gauss',{'mean':-2.,'sigma':10.}],
# 			 ['Gauss',{'mean':-10.5,'sigma':5.}]]]


# mfc = anfis.Funcs(predict_func)
# nfm = anfis.ANFIS(X, Y, mfc)
# nfm.train(epochs=20)