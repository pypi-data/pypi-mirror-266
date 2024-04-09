# Dictionary Learning Toolbox

Official documentation [here](https://unibuc.gitlab.io/graphomaly/dictionary-learning/).

This work was supported in part by the [Graphomaly Research Grant](http://graphomaly.upb.ro/)
and is based on the [Matlab Dictionary Learning Toolbox](https://gitlab.com/pirofti/dl-box)
that accompanied the Springer book mentioned bellow.

If you use our work in your research, please cite as:

B. Dumitrescu and P. Irofti, Dictionary Learning Algorithms and Applications, Springer, 2018
```
@book{DL_book,
author    = {Dumitrescu, B. and Irofti, P.},
title     = {Dictionary Learning Algorithms and Applications},
year      = {2018},
publisher = {Springer},
}
```

## Installation and setup
Install via pip from the [PyPi repository](https://pypi.org/project/dictlearn/):
```
pip install dictlearn
```

or for the latest changes not yet in the official release:
```
pip install git+https://gitlab.com/unibuc/graphomaly/dictionary-learning
```

## Usage

The package follows the [sklearn](https://scikit-learn.org/) API and can be included in your projects via
```
from dictlearn import DictionaryLearning
```
which will provide you with a standard scikit-learn estimator that you can use in your pipeline.

### Example

```
import matplotlib.pyplot as plt

from dictlearn import DictionaryLearning
from sklearn.datasets import make_sparse_coded_signal

n_components = 50      # number of atoms
n_features = 20        # signal dimension
n_nonzero_coefs = 3    # sparsity
n_samples = 100        # number of signals
n_iterations = 20      # number of dictionary learning iterations

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
```

For configuration and tweaks please consult the [documentation](https://unibuc.gitlab.io/graphomaly/dictionary-learning/).

## Development and testing

First clone the repository and change directory to the root of your fresh checkout.

#### 0. Install Prerequisites
Install PyPA’s [build](https://packaging.python.org/en/latest/key_projects/#build):
```
python3 -m pip install --upgrade build
```

#### 1. Build
Inside the `dictonary-learning` directory
```
python -m build
```

#### 2. Virtual Environment

Create a virtual environment with Python:
```
python -m venv venv
```

Activate the environment:
```
source venv/bin/activate
```

For Windows execute instead:
```
venv\Scripts\activate
```

#### 3. Install
Inside the virutal environment execute:
```
pip install dist/dictlearn-*.whl
```
