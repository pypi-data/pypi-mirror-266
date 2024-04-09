import numpy as np

from sklearn import preprocessing
from dictlearn.models import DPL
from dictlearn.datasets import yaleb


# load data
(X_train, y_train), (X_test, y_test) = yaleb.load_data()

# data normalization
X_train = preprocessing.normalize(X_train, norm='l2', axis=0)
X_test = preprocessing.normalize(X_test, norm='l2', axis=0)

# train model
dpl = DPL(n_components=30, tau=0.05, theta=0.003, gamma=0.0001)
dpl.fit(X_train, y_train, max_iter=10)

# test model
y_pred = dpl.predict(X_test)
accuracy = np.sum(y_test == y_pred) / len(y_test)
y_proba = dpl.predict_proba(X_test)
