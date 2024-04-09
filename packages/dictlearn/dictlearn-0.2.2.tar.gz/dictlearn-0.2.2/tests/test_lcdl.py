import numpy as np

from dictlearn.models import LCDL
from dictlearn.datasets import yaleb


# load data
(X_train, y_train), (X_test, y_test) = yaleb.load_data()

alpha = 2               # classification penalty
beta = 4                # label consistent penalty
n_components = 5        # number of atoms
n_nonzero_coefs = 4     # sparsity constraint

# define general parameters
params = {}

# train model
lcdl = LCDL('aksvd', 'omp', n_components, n_nonzero_coefs, params, alpha, beta,
            init_method=0)
lcdl.fit(X_train, y_train, max_iter=10)

# test model
y_pred = lcdl.predict(X_test)
accuracy = np.sum(y_test == y_pred) / len(y_test)
y_proba = lcdl.predict_proba(X_test)
