import numpy as np

from dictlearn.models import KDDL
from dictlearn.datasets import yaleb
from dictlearn.kernels import dl_rbf_kernel


# load data
(X_train, y_train), (X_test, y_test) = yaleb.load_data()

alpha = 2               # classification penalty
n_components = 200      # number of atoms
n_nonzero_coefs = 4     # sparsity constraint

# define general parameters
params = {}
params['gamma'] = 1e-5

# train model
kddl = KDDL('omp', n_components, n_nonzero_coefs, dl_rbf_kernel, params, alpha)
kddl.fit(X_train, y_train, max_iter=10, batches=2)

# test model
y_pred = kddl.predict(X_test)
accuracy = np.sum(y_test == y_pred) / len(y_test)
y_proba = kddl.predict_proba(X_test)
