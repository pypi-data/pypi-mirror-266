import NeuFuzMatrix # нейронная сеть
import os # работа с файлами
import numpy as np
import pickle  # сохрание и загрузка состояния нейросети 

# Текущая директория
current_dir = os.path.dirname(os.path.abspath(__file__))

# Путь к файлу относительно текущей директории
file_path = os.path.join(current_dir, "output.txt")

ts = np.loadtxt(file_path, usecols=[0,1,2])
X = ts[:,0:2]
Y = ts[:,2]

nfm = NeuFuzMatrix.NFM(X, Y)
nfm.algorithm="With rules"
f_temp = nfm.create_feature("Температура", "C", 0, 150, True)
f_flow =  nfm.create_feature("Расход", "м3/ч", 0, 8, True)
f_pressure  = nfm.create_feature("Давление", "МПа", 0, 100, False)
p_temp_low = nfm.create_predicate(f_temp, 'низкая', ['Gauss',{'mean':30,'sigma':10}])
p_temp_normal = nfm.create_predicate(f_temp, 'средняя', ['Gauss',{'mean':70,'sigma':10}])
p_temp_high = nfm.create_predicate(f_temp, 'высокая', ['Gauss',{'mean':120,'sigma':10}])
p_flow_low = nfm.create_predicate(f_flow, 'малый', ['Gauss',{'mean':2,'sigma':1}])
p_flow_normal = nfm.create_predicate(f_flow, 'средний', ['Gauss',{'mean':4,'sigma':1}])
p_flow_high = nfm.create_predicate(f_flow, 'большой', ['Gauss',{'mean':6,'sigma':1}])
r_1 = nfm.create_rule([p_temp_low, p_flow_low], 1)
r_2 = nfm.create_rule([p_temp_normal], 1)
r_3 = nfm.create_rule([p_temp_high], 1)
r_4 = nfm.create_rule([p_flow_high], 1)

nfm.train(epochs=200)
print("Plotting errors")
nfm.plotErrors()
print("Plotting results")
nfm.plotResults()

x_values = np.linspace(-300, 100, 400)
nfm.plotMF(x_values,f_temp)
nfm.plotMF(x_values,f_flow)

X_test = np.array([[22, 3],
                   [65, 5]])
y_test = NeuFuzMatrix.predict(nfm,X_test)

print(y_test)

with open('NeuFuzMatrix_model.pkl', 'wb') as f:
    pickle.dump(nfm, f)