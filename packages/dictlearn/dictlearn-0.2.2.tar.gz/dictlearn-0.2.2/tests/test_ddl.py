import numpy as np

from dictlearn.models import DDL
from dictlearn.datasets import yaleb


# load data
(X_train, y_train), (X_test, y_test) = yaleb.load_data()

alpha = 2               # classification penalty
n_components = 200      # number of atoms
n_nonzero_coefs = 4     # sparsity constraint

# define dl parameters
params = {}

# train model
ddl = DDL('ksvd', 'omp', n_components, n_nonzero_coefs, params, alpha)
ddl.fit(X_train, y_train, max_iter=10, batches=4)

# test model
y_pred = ddl.predict(X_test)
accuracy = np.sum(y_test == y_pred) / len(y_test)
y_proba = ddl.predict_proba(X_test)
