import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from seaborn import pairplot
from sklearn.svm import SVC
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.datasets import load_iris

iris_data = load_iris()
iris = pd.DataFrame(data= np.c_[iris_data['data'], iris_data['target']], columns= iris_data['feature_names'] + ['species'])

print(pairplot(data=iris, hue='species', palette='Set2'))
x = iris.iloc[:, :-1]
y = iris.iloc[:, -1]
x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.30, random_state=42)
model = SVC()
model.fit(x_train, y_train)
pred = model.predict(x_test)
print(confusion_matrix(y_test, pred))
print(classification_report(y_test, pred))
plt.show()