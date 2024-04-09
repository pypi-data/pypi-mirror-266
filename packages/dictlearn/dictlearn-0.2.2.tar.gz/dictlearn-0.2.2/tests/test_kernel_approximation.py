import time
import numpy as np

from sklearn import preprocessing
from sklearn.cluster import KMeans
from sklearn.kernel_approximation import RBFSampler

from dictlearn.models.DPL import DPL
from dictlearn.datasets import yaleb
from dictlearn import DictionaryLearning
from dictlearn.kernel_approximation import Nystroem

# DPL params
n_components = 30
tau = 30
theta = 0.003
gamma = 0.0001
max_iter = 10

# Nystrom params
nyst_gamma = 1e-8
nyst_random_state = 0
nyst_n_components = 400


rounds = 10

dl_acc = 0
nyst_dl_acc = 0
nyst_rsvd_dl_acc = 0
nyst_basis_dl_acc = 0
nyst_rff_basis_dl_acc = 0
nyst_kmeans_basis_dl_acc = 0
rff_dl_acc = 0

dl_time = 0
nyst_dl_time = 0
nyst_rsvd_dl_time = 0
nyst_basis_dl_time = 0
nyst_rff_basis_dl_time = 0
nyst_kmeans_basis_dl_time = 0
rff_dl_time = 0


for i in range(rounds):
    ####################### Standard DL #######################
    t0 = time.time()
    # load data
    (X_train, y_train), (X_test, y_test) = yaleb.load_data()
    
    # data normalization
    X_train = preprocessing.normalize(X_train, norm='l2', axis=0)
    X_test = preprocessing.normalize(X_test, norm='l2', axis=0)
    
    # train model
    dpl = DPL(n_components=n_components, tau=tau, theta=theta, gamma=gamma)
    dpl.fit(X_train, y_train, max_iter=max_iter)
    
    # test model
    y_pred = dpl.predict(X_test)
    accuracy = np.sum(y_test == y_pred) / len(y_test)
    t1 = time.time()
    dl_acc += accuracy
    dl_time += t1- t0
    ###########################################################
    
    
    ####################### Nystrom DL #######################
    t0 = time.time()
    # load data
    (X_train, y_train), (X_test, y_test) = yaleb.load_data()
    
    # Nystroem sampling
    X = np.vstack((X_train.T, X_test.T))
    feature_map_nystroem = Nystroem(gamma=nyst_gamma,
                                    random_state=nyst_random_state,
                                    n_components=nyst_n_components,
                                    use_rsvd=False)
    X = feature_map_nystroem.fit_transform(X).T
    X_train = X[:, :X_train.shape[1]]
    X_test = X[:, -X_test.shape[1]:]
    
    # data normalization
    X_train = preprocessing.normalize(X_train, norm='l2', axis=0)
    X_test = preprocessing.normalize(X_test, norm='l2', axis=0)
    
    # train model
    dpl = DPL(n_components=n_components, tau=tau, theta=theta, gamma=gamma)
    dpl.fit(X_train, y_train, max_iter=max_iter)
    
    # test model
    y_pred = dpl.predict(X_test)
    accuracy = np.sum(y_test == y_pred) / len(y_test)
    t1 = time.time()
    nyst_dl_acc += accuracy
    nyst_dl_time += t1- t0
    ###########################################################
    
    
    ####################### Nystrom rsvd DL #######################
    t0 = time.time()
    # load data
    (X_train, y_train), (X_test, y_test) = yaleb.load_data()
    
    # Nystroem sampling
    X = np.vstack((X_train.T, X_test.T))
    feature_map_nystroem = Nystroem(gamma=nyst_gamma,
                                    random_state=nyst_random_state,
                                    n_components=nyst_n_components,
                                    use_rsvd=True)
    X = feature_map_nystroem.fit_transform(X).T
    X_train = X[:, :X_train.shape[1]]
    X_test = X[:, -X_test.shape[1]:]
    
    # data normalization
    X_train = preprocessing.normalize(X_train, norm='l2', axis=0)
    X_test = preprocessing.normalize(X_test, norm='l2', axis=0)
    
    # train model
    dpl = DPL(n_components=n_components, tau=tau, theta=theta, gamma=gamma)
    dpl.fit(X_train, y_train, max_iter=max_iter)
    
    # test model
    y_pred = dpl.predict(X_test)
    accuracy = np.sum(y_test == y_pred) / len(y_test)
    t1 = time.time()
    nyst_rsvd_dl_acc += accuracy
    nyst_rsvd_dl_time += t1 - t0
    ###########################################################
    
    
    ####################### Nystrom basis DL #######################
    t0 = time.time()
    # load data
    (X_train, y_train), (X_test, y_test) = yaleb.load_data()
    
    # Nystroem sampling
    Y = np.vstack((X_train.T, X_test.T))
    
    # dl problem
    dl = DictionaryLearning(
        n_components=nyst_n_components,
        max_iter=10,
        fit_algorithm='aksvd',
        transform_algorithm='omp',
        n_nonzero_coefs=100,
        code_init=None,
        dict_init=None,
        verbose=False,
        random_state=None,
        kernel_function=None,
        params=None,
        data_sklearn_compat=False
    )
    dl.fit(Y.T)
    
    # Nystroem sampling
    X = np.vstack((X_train.T, X_test.T))
    feature_map_nystroem = Nystroem(gamma=nyst_gamma,
                                    random_state=nyst_random_state,
                                    n_components=nyst_n_components,
                                    use_rsvd=False,
                                    basis=dl.D_.T)
    X = feature_map_nystroem.fit_transform(X).T
    X_train = X[:, :X_train.shape[1]]
    X_test = X[:, -X_test.shape[1]:]
    
    # data normalization
    X_train = preprocessing.normalize(X_train, norm='l2', axis=0)
    X_test = preprocessing.normalize(X_test, norm='l2', axis=0)
    
    # train model
    dpl = DPL(n_components=n_components, tau=tau, theta=theta, gamma=gamma)
    dpl.fit(X_train, y_train, max_iter=max_iter)
    
    # test model
    y_pred = dpl.predict(X_test)
    accuracy = np.sum(y_test == y_pred) / len(y_test)
    t1 = time.time()
    nyst_basis_dl_acc += accuracy
    nyst_basis_dl_time += t1 - t0
    ###########################################################

    
    ####################### Nystrom RFF DL #######################
    t0 = time.time()
    # load data
    (X_train, y_train), (X_test, y_test) = yaleb.load_data()
    
    # rbf sampler    
    X = np.vstack((X_train.T, X_test.T))
    rbf_feature = RBFSampler(gamma=nyst_gamma,
                              random_state=1,
                              n_components=nyst_n_components)
    basis = rbf_feature.fit_transform(X.T)

    # Nystroem sampling
    X = np.vstack((X_train.T, X_test.T))
    feature_map_nystroem = Nystroem(gamma=nyst_gamma,
                                    random_state=nyst_random_state,
                                    n_components=nyst_n_components,
                                    use_rsvd=False,
                                    basis=basis.T)
    X = feature_map_nystroem.fit_transform(X).T
    X_train = X[:, :X_train.shape[1]]
    X_test = X[:, -X_test.shape[1]:]

    # data normalization
    X_train = preprocessing.normalize(X_train, norm='l2', axis=0)
    X_test = preprocessing.normalize(X_test, norm='l2', axis=0)
    basis = preprocessing.normalize(basis, norm='l2', axis=0)
    
    # train model
    dpl = DPL(n_components=n_components, tau=tau, theta=theta, gamma=gamma)
    dpl.fit(X_train, y_train, max_iter=max_iter)
    
    # test model
    y_pred = dpl.predict(X_test)
    accuracy = np.sum(y_test == y_pred) / len(y_test)
    t1 = time.time()
    nyst_rff_basis_dl_acc += accuracy
    nyst_rff_basis_dl_time += t1 - t0
    ###########################################################
    
    
    ####################### Nystrom kmeans DL #######################
    t0 = time.time()
    # load data
    (X_train, y_train), (X_test, y_test) = yaleb.load_data()
    
    # rbf sampler    
    X = np.vstack((X_train.T, X_test.T))
    kmeans = KMeans(n_clusters=nyst_n_components, random_state=0).fit(X)
    basis = kmeans.cluster_centers_

    # Nystroem sampling
    X = np.vstack((X_train.T, X_test.T))
    feature_map_nystroem = Nystroem(gamma=nyst_gamma,
                                    random_state=nyst_random_state,
                                    n_components=nyst_n_components,
                                    use_rsvd=False,
                                    basis=basis)
    X = feature_map_nystroem.fit_transform(X).T
    X_train = X[:, :X_train.shape[1]]
    X_test = X[:, -X_test.shape[1]:]

    # data normalization
    X_train = preprocessing.normalize(X_train, norm='l2', axis=0)
    X_test = preprocessing.normalize(X_test, norm='l2', axis=0)
    basis = preprocessing.normalize(basis, norm='l2', axis=0)
    
    # train model
    dpl = DPL(n_components=n_components, tau=tau, theta=theta, gamma=gamma)
    dpl.fit(X_train, y_train, max_iter=max_iter)
    
    # test model
    y_pred = dpl.predict(X_test)
    accuracy = np.sum(y_test == y_pred) / len(y_test)
    t1 = time.time()
    nyst_kmeans_basis_dl_acc += accuracy
    nyst_kmeans_basis_dl_time += t1 - t0
    ###########################################################
    
    
    ####################### RFF DL #######################
    t0 = time.time()
    # load data
    (X_train, y_train), (X_test, y_test) = yaleb.load_data()
    
    # rbf sampler    
    X = np.vstack((X_train.T, X_test.T))
    rbf_feature = RBFSampler(gamma=nyst_gamma,
                              random_state=1,
                              n_components=nyst_n_components)
    X = rbf_feature.fit_transform(X).T
    X_train = X[:, :X_train.shape[1]]
    X_test = X[:, -X_test.shape[1]:]

    # data normalization
    X_train = preprocessing.normalize(X_train, norm='l2', axis=0)
    X_test = preprocessing.normalize(X_test, norm='l2', axis=0)
    
    # train model
    dpl = DPL(n_components=n_components, tau=tau, theta=theta, gamma=gamma)
    dpl.fit(X_train, y_train, max_iter=max_iter)
    
    # test model
    y_pred = dpl.predict(X_test)
    accuracy = np.sum(y_test == y_pred) / len(y_test)
    t1 = time.time()
    rff_dl_acc += accuracy
    rff_dl_time += t1 - t0
    ###########################################################


dl_acc /= rounds
nyst_dl_acc /= rounds
nyst_rsvd_dl_acc /= rounds
nyst_basis_dl_acc /= rounds
nyst_rff_basis_dl_acc /= rounds
nyst_kmeans_basis_dl_acc /= rounds
rff_dl_acc /= rounds

dl_time /= rounds
nyst_dl_time /= rounds
nyst_rsvd_dl_time /= rounds
nyst_basis_dl_time /= rounds
nyst_rff_basis_dl_time /= rounds
nyst_kmeans_basis_dl_time /= rounds
rff_dl_time /= rounds

print('\n')
print('Standard DL acc: {}'.format(dl_acc))
print('Nystrom acc: {}'.format(nyst_dl_acc))
print('Nystrom rsvd acc: {}'.format(nyst_rsvd_dl_acc))
print('Nystrom basis acc: {}'.format(nyst_basis_dl_acc))
print('Nystrom rff basis acc: {}'.format(nyst_rff_basis_dl_acc))
print('Nystrom kmeans basis acc: {}'.format(nyst_kmeans_basis_dl_acc))
print('RFF acc: {}'.format(rff_dl_acc))

print('\n')
print('Standard DL time: {}'.format(dl_time))
print('Nystrom time: {}'.format(nyst_dl_time))
print('Nystrom rsvd time: {}'.format(nyst_rsvd_dl_time))
print('Nystrom basis time: {}'.format(nyst_basis_dl_time))
print('Nystrom rff basis time: {}'.format(nyst_rff_basis_dl_time))
print('Nystrom kmeans basis time: {}'.format(nyst_kmeans_basis_dl_time))
print('RFF time: {}'.format(rff_dl_time))


