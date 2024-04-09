import numpy as np

from sklearn import preprocessing
from dictlearn.models import KDPL
from dictlearn.datasets import yaleb
from dictlearn.kernels import dl_rbf_kernel


# load data
(X_train, y_train), (X_test, y_test) = yaleb.load_data()

# data normalization
X_train = preprocessing.normalize(X_train, norm='l2', axis=0)
X_test = preprocessing.normalize(X_test, norm='l2', axis=0)

# define dl parameters
params = {}
params['gamma'] = 0.5

# train model
kdpl = KDPL(n_components=30, tau=0.05, theta=0.003, gamma=1e-4,
            alpha=1e-4, kernel_function=dl_rbf_kernel, params=params)
kdpl.fit(X_train, y_train, max_iter=10)

# test model
y_pred = kdpl.predict(X_test)
accuracy = np.sum(y_test == y_pred) / len(y_test)
y_proba = kdpl.predict_proba(X_test)
