import numpy as np
import itertools
import copy
import matplotlib.pyplot as plt

# Вычисляем значение х функции принадлежности
# гауусова функция
def Gauss(mean, sigma):
    def own(x):
        return np.exp(-((x - mean)**2) / (2 * sigma**2))
    return own
# колоколообразная функция
def Bell(a, b, c):
    def own(x):
        return 1 / (1 + np.abs((x - c) / a) ** (2 * b))
    return own
# сигмоидная функция
def Sigmoid(b, c):
    def own(x):
        return 1 / (1 + np.exp(- c * (x - b)))
    return own

class Funcs:
    # Все возможные функции
    funcs_dict = {'Gauss': Gauss, 'Bell': Bell, 'Sigmoid': Sigmoid}

    def __init__(self, funcs_predicates):
        self.funcs_predicates = funcs_predicates

    def list_values(self, rowInput):
        if len(rowInput) != len(self.funcs_predicates):
            print("Number of variables does not match number of rule sets")

        results = []
        # Перебираем все входные значения
        for x in range(len(rowInput)):
            # Хранения результатов текущей строки
            row_results = []

            # Перебираем все функции для текущего x
            for k in range(len(self.funcs_predicates[x])):

                # Функция
                predict_func_name = self.funcs_predicates[x][k][0]

                # Параметры функции
                predict_func_params = self.funcs_predicates[x][k][1]

                # Вычисляем значение функции
                func=self.funcs_dict[predict_func_name](**predict_func_params)
                predict_func_value = func(rowInput[x])

                row_results.append(predict_func_value)

            results.append(row_results)

        return results
    
# Вычисляем частную производную функции принадлежности в точке x
def partial_dMF(x, predict_func_definition, partial_parameter):
    # Имя функции
    predict_func_name = predict_func_definition[0]

    if predict_func_name == 'Gauss':

        sigma = predict_func_definition[1]['sigma']
        mean = predict_func_definition[1]['mean']

        if partial_parameter == 'sigma':
            result = (2./sigma**3) * np.exp(-(((x-mean)**2)/(sigma)**2))*(x-mean)**2
        elif partial_parameter == 'mean':
            result = (2./sigma**2) * np.exp(-(((x-mean)**2)/(sigma)**2))*(x-mean)

    elif predict_func_name == 'Bell':

        a = predict_func_definition[1]['a']
        b = predict_func_definition[1]['b']
        c = predict_func_definition[1]['c']

        if partial_parameter == 'a':
            result = (2. * b * np.power((c-x),2) * np.power(np.absolute((c-x)/a), ((2 * b) - 2))) / \
                (np.power(a, 3) * np.power((np.power(np.absolute((c-x)/a),(2*b)) + 1), 2))
        elif partial_parameter == 'b':
            result = -1 * (2 * np.power(np.absolute((c-x)/a), (2 * b)) * np.log(np.absolute((c-x)/a))) / \
                (np.power((np.power(np.absolute((c-x)/a), (2 * b)) + 1), 2))
        elif partial_parameter == 'c':
            result = (2. * b * (c-x) * np.power(np.absolute((c-x)/a), ((2 * b) - 2))) / \
                (np.power(a, 2) * np.power((np.power(np.absolute((c-x)/a),(2*b)) + 1), 2))

    elif predict_func_name == 'Sigmoid':

        b = predict_func_definition[1]['b']
        c = predict_func_definition[1]['c']

        if partial_parameter == 'b':
            result = -1 * (c * np.exp(c * (b + x))) / \
                np.power((np.exp(b*c) + np.exp(c*x)), 2)
        elif partial_parameter == 'c':
            result = ((x - b) * np.exp(c * (x - b))) / \
                np.power((np.exp(c * (x - c))) + 1, 2)


    return result

# нечеткий вектор
class FuzzyVector():
    def __init__(self, positive):
        self.truth = positive

    def __str__(self):
        return f"truth: {round(self.truth, 2)}"

    def truth(self):
        return self.truth

    def inverse(self):
        return FuzzyVector(1-self.truth)

    def conjunction(self, other):
        positive = self.truth * other.truth
        return FuzzyVector(positive)

    def disjunction(self, other):
        positive = 1 - (1-self.truth) * (1-other.truth)
        return FuzzyVector(positive)

    def implication(self, other):
        return FuzzyVector(max(self.truth+other.truth-1, 0))

def conjunction(vectors):
    v = FuzzyVector(1)
    for vector in vectors:
        v = v.conjunction(vector)
    return v

def disjunction(vectors):
    v = FuzzyVector(0)
    for vector in vectors:
        v = v.disjunction(vector)
    return v

# лингвистическая переменная
class Feature():    
    def __init__(self, name, units, min, max, inout):
        self.name = name
        self.units = units
        self.min = min
        self.max = max
        self.predicates=[]
        # Входной или рассчётный признак.
        self.inout = inout
        #Текущее значение для входных признаков
        self.value=None
        self.linspace = None
        self.ruleswithpredict = []

# термы ЛП
class FuzzyPredicate():
    def __init__(self, feature: Feature, name, func=None, const=None):
        self.feature: Feature = feature
        self.name = name
        #Для центроидного метода дефаззификации
        self.func = func
        #Для упрощённого метода дефаззификации
        self.const = const

    def scalar(self,x=None):
        if x is None:
            if self.const is None:  
                raise ValueError(f"Const value for predicate {self.feature.name} '{self.name}' is not specified!") 
            else:
                return self.const

        if self.func is None:
            raise ValueError(f"Function for predicate {self.feature.name} '{self.name}' is not specified!")    

        return self.func(x)

    def vector(self,x=None):
        return FuzzyVector(self.scalar(x))
    
# правила 
class Rule():
    def __init__(self, input_pridicates, weight):
        self.inputs = input_pridicates
        self.weight=weight
        self.truth = None

class NFM:
    def __init__(self, X, Y):
        self.X = np.array(copy.copy(X)) # X
        self.Y = np.array(copy.copy(Y)) # Y
        self.XLen = len(self.X) # длина X
        self.func_class = None # функции принадлежности
        self.Funcs = None # список функций принадлежностей из объекта класса
        self.FuncsByVariable = None # номера функций принадлежности из списка по переменным
        self.rules = None # правила в виде индексов термов лп
        self.conditions = None # веса линейной комбинации
        self.weights = None # смещение линейной комбинации
        self.errors = None # массив ошибок
        self.residuals = None # разница между ожидаемым и предсказанным значением 
        self.FuncsHomo = None # проверка количества функций принадлежности
        self.features_in = [] # входные лп
        self.features_out = [] # выходные лп
        self.term_in = []  # термы входных параметров
        self.func_predict_in = [] # функции термов входных параметров
        self.func_predict_out = [] # функции термов входных параметров
        self.ruleswithpredict = [] # правила в виде формул с предикатами
        self.algorithm= None #With rules or Not rules
        self.num = 100

    def create_feature(self, name, units, min, max, inout):
        feature = Feature(name, units, min, max, inout)
        if inout:
            self.features_in.append(feature)
            self.func_predict_in.append([])
            self.term_in.append([])
        else:
            feature.linspace = np.linspace(feature.min, feature.max, self.num)
            self.features_out.append(feature)
            self.func_predict_out.append([])
        return feature

    def create_predicate(self, feature: Feature, name, func=None, const=None):
        predicate = FuzzyPredicate(feature, name, func, const)
        feature.predicates.append(predicate)
        if feature in self.features_in:
            self.func_predict_in[self.features_in.index(feature)].append(func)
            self.term_in[self.features_in.index(feature)].append(predicate)
        return predicate

    def create_rule(self, input_predicates, weight):
        rule = Rule(input_predicates, weight)
        self.ruleswithpredict.append(rule)
        return rule
    
    def initialize_parameters(self):
        mfc=Funcs(self.func_predict_in)
        self.func_class = copy.deepcopy(mfc)
        self.Funcs = self.func_class.funcs_predicates
        self.FuncsByVariable = [[x for x in range(len(self.Funcs[z]))] for z in range(len(self.Funcs))]
        self.errors = np.empty(0) 
        self.FuncsHomo = all(len(i)==len(self.FuncsByVariable[0]) for i in self.FuncsByVariable) 

        if self.algorithm=="With rules":
            len_rules=len(self.ruleswithpredict)
            rules_i=[]
            rules_i=[[None] * (len(self.features_in)) for _ in range(len_rules)]
            for i in range(len_rules):
                rule=self.ruleswithpredict[i].inputs
                for term in rule:
                    index = next(((i, j) for i, sublist in enumerate(self.term_in) for j, elem in enumerate(sublist) if elem == term), None)
                    rules_i[i][index[0]]=index[1]

            self.rules = np.array(rules_i)
        elif self.algorithm=="Not rules":
            self.rules = np.array(list(itertools.product(*self.FuncsByVariable))) 

        self.weights = np.random.uniform(50, 100, ((self.Y.ndim,len(self.rules))))
        # self.weights = np.random.randn(self.Y.ndim,len(self.rules))
        # self.biases = np.zeros((self.Y.ndim, len(self.X[:,0])))
        self.biases = np.random.randn(self.Y.ndim, len(self.X[:,0]))

    # функция обучения сети 
    def train(self, epochs=5, tolerance=1e-1, k=0.01):
        self.initialize_parameters()
        convergence = False
        epoch = 0
        while (epoch < epochs) and (convergence is not True):

            # 4-й слой: композиция и дефаззификация
            [layerThree, wSum, w] = self.forwardPass(self.X)
            # Вычисление значений выходов нейронов четвертого слоя
            layerFour = layerThree @ self.weights.T

            # функция потерь MSE
            error = np.sum((self.Y-layerFour)**2)/len(self.Y)
            # функция потерь SSE 
            # error = np.sum((self.Y-layerFour)**2)

            print('current error: '+ str(error))

            # Добавление текущего значения ошибки в список ошибок
            self.errors = np.append(self.errors,error)

            if len(self.errors) != 0:
                if self.errors[len(self.errors)-1] < tolerance:
                    convergence = True

            # back propagation: обратный проход
            if convergence is not True:
                # количество входных параметров
                colsX = len(self.X[0,:])
                colsY = self.Y.ndim
                cols = range(len(self.X[0,:]))

                # обратное распространение для весов 
                dE_dW=np.zeros((self.Y.ndim, len(self.X[:,0])))
                if (colsY>1):
                    for y in range(colsY):
                        for x in range(colsX):
                            err=self.Y[y][x]-layerFour[y][x]
                            dE_dW[y][x]=layerFour[y][x] * err
                else:
                    for x in range(colsX):
                        err=self.Y[x]-layerFour[x]
                        dE_dW = layerFour[x] * err
                    
                # обратное распространение для функций принадлежности
                dE_dAlpha = list(self.backprop(colX, cols, wSum, w, layerFour) for colX in range(self.X.shape[1]))

            # изменение шага для градиентного спуска
            if len(self.errors) >= 4:
                if (self.errors[-4] > self.errors[-3] > self.errors[-2] > self.errors[-1]):
                    k = k * 1.1

            if len(self.errors) >= 5:
                if (self.errors[-1] < self.errors[-2]) and (self.errors[-3] < self.errors[-2]) and (self.errors[-3] < self.errors[-4]) and (self.errors[-5] > self.errors[-4]):
                    k = k * 0.9

            # обновление параметров функций принадлежности
            t = []
            for x in range(len(dE_dAlpha)):
                for y in range(len(dE_dAlpha[x])):
                    for z in range(len(dE_dAlpha[x][y])):
                        t.append(dE_dAlpha[x][y][z])

            eta = k / np.abs(np.sum(t))

            if(np.isinf(eta)):
                eta = k

            # корректировка параметров 
            dAlpha = copy.deepcopy(dE_dAlpha)
            if not(self.FuncsHomo):
                for x in range(len(dE_dAlpha)):
                    for y in range(len(dE_dAlpha[x])):
                        for z in range(len(dE_dAlpha[x][y])):
                            dAlpha[x][y][z] = -eta * dE_dAlpha[x][y][z]
            else:
                dAlpha = -eta * np.array(dE_dAlpha)

            for varsWithFuncs in range(len(self.Funcs)):
                for MFs in range(len(self.FuncsByVariable[varsWithFuncs])):
                    paramList = sorted(self.Funcs[varsWithFuncs][MFs][1])
                    for param in range(len(paramList)):
                        self.Funcs[varsWithFuncs][MFs][1][paramList[param]] = self.Funcs[varsWithFuncs][MFs][1][paramList[param]] + dAlpha[varsWithFuncs][MFs][param]
            if (colsY>1):
                for y in range(colsY):
                    for x in range(colsX):
                        self.weights[y][x] -= eta*dE_dW[y][x]
            else:
                self.weights -= dE_dW *eta 
            epoch += 1

        # выходы обученной сети
        self.predictedValues = predict(self,self.X)
        # итоговые ошибки
        self.residuals = self.Y - self.predictedValues

        return self.predictedValues

    # график ошибки
    def plotErrors(self):
        plt.plot(range(len(self.errors)),self.errors,'ro', label='errors')
        plt.ylabel('error')
        plt.xlabel('epoch')
        plt.show()
    # график функции принадлежности
    def plotMF(self, x, feature):
        i=self.features_in.index(feature)
        for mf in range(len(self.Funcs[i])):
            if self.Funcs[i][mf][0] == 'Gauss':
                y = Gauss(**self.func_class.funcs_predicates[i][mf][1])(x)
            elif self.Funcs[i][mf][0] == 'Bell':
                y = Bell(**self.func_class.funcs_predicates[i][mf][1])(x)
            elif self.Funcs[i][mf][0] == 'Sigmoid':
                y = Sigmoid(**self.func_class.funcs_predicates[i][mf][1])(x)

            plt.plot(x,y,'r')
        plt.ylabel('Степень принадлежности')
        plt.xlabel(feature.units)
        plt.title(feature.name)
        plt.show()
    # график выходного значения
    def plotResults(self):
        plt.plot(range(len(self.predictedValues)),self.predictedValues,'r', label='trained')
        plt.plot(range(len(self.Y)),self.Y,'b', label='original')
        plt.legend(loc='upper left')
        plt.show()

    # прямой проход до 3 слоя
    def forwardPass(self, Xs):
        layerThree = []
        wSum = []
        # проход по каждой строке обучающего множества
        for row in range(len(Xs[:,0])):
            # 1-й слой: вычисление функций принадлежности для входных переменных
            layerOne = self.func_class.list_values(Xs[row,:])

            # 2-й слой: агрегирование подусловий
            miAlloc = []
            for rule in range(len(self.rules)): # проход по всем правилам
                ruleAlloc = []
                for x in range(len(self.rules[0])): 
                    if (self.rules[rule][x]) is not None:
                        mfValue=FuzzyVector(layerOne[x][self.rules[rule][x]])
                        ruleAlloc.append(mfValue)
                miAlloc.append(ruleAlloc)
            # конъюнкцию подусловий
            listruletruth=[]
            for onerule in miAlloc:
                oneruletruth=conjunction(onerule)
                listruletruth.append(oneruletruth.truth)

            layerTwo = np.array(listruletruth).T

            # сохранение весов
            if row == 0:
                w = layerTwo
            else:
                w = np.vstack((w,layerTwo))
            wSum.append(np.sum(layerTwo))

            # 3-й слой: активация правил
            activisation=[]
            for aggregation in range(len(layerTwo)):
                if self.algorithm=="With rules":
                    a=FuzzyVector(FuzzyVector(layerTwo[aggregation]).implication(FuzzyVector(self.ruleswithpredict[aggregation].weight))).truth
                elif self.algorithm=="Not rules":
                    a=FuzzyVector(FuzzyVector(layerTwo[aggregation]).implication(FuzzyVector(1))).truth
                activisation.append(a.truth)
            layerThree = np.append(layerThree,np.array(activisation))
            layerThree = np.array(np.array_split(layerThree,row + 1))
        w = w.T
        return layerThree, wSum, w

    # метод обратного распространения ошибки для  корректировки параметров функций принадлежности
    def backprop(self, columnX, columns, theWSum, theW, thelayerFour):
        # градиент
        gradient = [0]* len(self.Funcs[columnX])
        # проход по функциям принадлежности переданной переменной
        for MF in range(len(self.Funcs[columnX])):
            parameters = np.empty(len(self.Funcs[columnX][MF][1]))
            timesThru = 0
            for alpha in sorted(self.Funcs[columnX][MF][1].keys()):
                bucket3 = np.empty(len(self.X))
                for rowX in range(len(self.X)):
                    varToX = self.X[rowX,columnX]
                    tmpRow = np.empty(len(self.Funcs))
                    tmpRow.fill(varToX)
                    bucket2 = np.empty(self.Y.ndim)
                    # Цикл по всем столбцам выходных данных
                    for colY in range(self.Y.ndim):
                        rulesWithAlpha = np.array(np.where(self.rules[:,columnX]==MF))[0]
                        adjCols = np.delete(columns,columnX)
                        # вычисление производной входного параметра
                        senSit = partial_dMF(self.X[rowX,columnX],self.Funcs[columnX][MF],alpha)
                        prod_list = []
                        for r in rulesWithAlpha:
                            prod = 1
                            for c in adjCols:
                                if (self.rules[r][c]) is not None:
                                    prod *= self.func_class.list_values(tmpRow)[c][self.rules[r][c]]
                                prod_list.append(prod)
                        dW_dAplha = senSit * np.array(prod_list)

                        # Вычисление вклада текущего правила в общую ошибку
                        bucket1 = np.empty(len(self.rules[:,0]))
                        # вычисление производной функции ошибки по отношению к параметрам линейной функции для последнего слоя
                        for condition in range(len(self.rules[:,0])):
                            input_val_row = np.array(self.X[rowX,:])
                            condition_weights = self.weights[colY,condition]
                            fcondition = np.sum(input_val_row * condition_weights)
                            acum = 0
                            if condition in rulesWithAlpha:
                                acum = dW_dAplha[np.where(rulesWithAlpha==condition)] * theWSum[rowX]

                            acum = acum - theW[condition,rowX] * np.sum(dW_dAplha)
                            acum = acum / theWSum[rowX]**2
                            bucket1[condition] = fcondition * acum

                        sum1 = np.sum(bucket1)

                        if self.Y.ndim == 1:
                            bucket2[colY] = sum1 * (self.Y[rowX]-thelayerFour[rowX])*(-2)
                        else:
                            bucket2[colY] = sum1 * (self.Y[rowX,colY]-thelayerFour[rowX][colY])*(-2)

                    sum2 = np.sum(bucket2)
                    bucket3[rowX] = sum2

                sum3 = np.sum(bucket3)
                parameters[timesThru] = sum3
                timesThru = timesThru + 1

            gradient[MF] = parameters
        # возврат параметров для текущего входного параметра
        return gradient

# предсказание выходного параметра по входным
def predict(NeuFuzzyMatrix, varsToTest):

    [layerThree, wSum, w] = NFM.forwardPass(NeuFuzzyMatrix, varsToTest)

    #layer five
    layerFour = layerThree @ NeuFuzzyMatrix.weights.T
    return layerFour


if __name__ == "__main__":
    print("I am main!")

    
