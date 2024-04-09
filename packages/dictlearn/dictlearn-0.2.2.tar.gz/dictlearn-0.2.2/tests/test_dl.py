import matplotlib.pyplot as plt

from dictlearn import DictionaryLearning
from sklearn.datasets import make_sparse_coded_signal

#############################################################################

n_components = 50      # number of atoms
n_features = 20        # signal dimension
n_nonzero_coefs = 3    # sparsity
n_samples = 100        # number of signals
n_iterations = 20      # number of dictionary learning iterations

#############################################################################

max_iter = 10
fit_algorithm = "aksvd"
transform_algorithm = "omp"

Y, D_origin, X_origin = make_sparse_coded_signal(
    n_samples=n_samples,
    n_components=n_components,
    n_features=n_features,
    n_nonzero_coefs=n_nonzero_coefs,
    random_state=0
)

dl = DictionaryLearning(
    n_components=n_components,
    max_iter=max_iter,
    fit_algorithm=fit_algorithm,
    transform_algorithm=transform_algorithm,
    n_nonzero_coefs=n_nonzero_coefs,
    code_init=None,
    dict_init=None,
    verbose=False,
    random_state=None,
    kernel_function=None,
    params=None,
    data_sklearn_compat=False
)

dl.fit(Y)

plt.plot(range(max_iter), dl.error_, label=fit_algorithm)
plt.legend()
plt.show()