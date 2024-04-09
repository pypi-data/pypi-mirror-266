# Copyright (c) 2019 Paul Irofti <paul@irofti.net>
# Copyright (c) 2020 Denis Ilie-Ablachim <denis.ilie_ablachim@acse.pub.ro>
#
# Permission to use, copy, modify, and/or distribute this software for any
# purpose with or without fee is hereby granted, provided that the above
# copyright notice and this permission notice appear in all copies.
#
# THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES
# WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
# MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR
# ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
# WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN
# ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF
# OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.

import numpy as np


class ReplAtoms():
    '''Unused dictionary atoms replacement strategy

    Attributes
    ----------
    ZERO : scalar
        return a zero column

    RANDOM : scalar
        return a random generated atom

    NO : scalar
        perform no replacement

    WORST : scalar
        replace ith the worst represented signal
    '''
    ZERO = 0
    RANDOM = 1
    NO = 2
    WORST = 3


def _new_atom(Y, D, X, atom_index, replatoms):
    '''Replace unused atom

    Parameters
    ----------
    replatoms : unused dictionary atoms replacement strategy
        * `'ZERO'` : return a zero column
        * `'RANDOM'` : return a random generated atom
        * `'NO'` : perform no replacement
        * `'WORST'` : replace ith the worst represented signal

    Y : ndarray of shape (n_features, n_samples)
        Data matrix.

    D : ndarray of shape (n_features, n_components)
        Initial dictionary, with normalized columns.

    X : ndarray of shape (n_components, n_features)
        The sparse codes.

    j : scalar
        atom's column index in the dictionary D


    Output
    ------
    atom : array of length n_features
        replacement atom
    '''
    if replatoms == ReplAtoms.ZERO:
        # Return a zero column
        return np.zeros(D.shape[0])

    if replatoms == ReplAtoms.RANDOM:
        # Return a random generated atom
        atom = np.random.rand(D.shape[0])
        atom = atom / np.linalg.norm(atom)
        return atom

    if replatoms == ReplAtoms.NO:
        # Perform no replacement
        return D[:, atom_index]

    if replatoms == ReplAtoms.WORST:
        # Replace with the worst represented signal
        E = Y - D @ X
        index = np.argmax(np.linalg.norm(E, axis=0))
        return Y[:, index] / np.linalg.norm(Y[:, index])


def _update_atom(Y, D, X, params, _custom_update_atom):
    '''Sequential dictionary update loop

    Parameters
    ----------
    Y : ndarray of shape (n_features, n_samples)
        Data matrix.

    D : ndarray of shape (n_features, n_components)
        Initial dictionary, with normalized columns.

    X : ndarray of shape (n_components, n_features)
        The sparse codes.

    params : Params
        Params instance with provided parameters for the DL problem.

    _custom_update_atom : handle function
        algorithm specific atom update routine

    Output
    ------
    D : ndarray of shape (n_features, n_components)
        Dictionary, with normalized columns.

    X : ndarray of shape (n_components, n_features)
        The sparse codes.
    '''
    E = Y - D @ X
    for atom_index in range(D.shape[1]):
        atom_usages = np.nonzero(X[atom_index, :])[0]

        if len(atom_usages) == 0:
            # replace with the new atom
            atom = _new_atom(Y, D, X, atom_index, params['replatoms'])
            D[:, atom_index] = atom
            continue
        else:
            F = (E[:, atom_usages] +
                 np.outer(D[:, atom_index], X[atom_index, atom_usages].T))
            atom, atom_codes = _custom_update_atom(F, D, X, atom_index,
                                                   atom_usages, params)

            D[:, atom_index] = atom
            X[atom_index, atom_usages] = atom_codes
            E[:, atom_usages] = (F - np.outer(D[:, atom_index],
                                              X[atom_index, atom_usages]))

    return D, X


def _update_patom(Y, D, X, params, _custom_update_atom):
    '''Parallel dictionary update loop

    Parameters
    ----------
    Y : ndarray of shape (n_features, n_samples)
        Data matrix.

    D : ndarray of shape (n_features, n_components)
        Initial dictionary, with normalized columns.

    X : ndarray of shape (n_components, n_features)
        The sparse codes.

    params : dict
        Dictionary with provided parameters for the DL problem.

    _custom_update_atom : handle function
        algorithm specific atom update routine

    Output
    ------
    D : ndarray of shape (n_features, n_components)
        Dictionary, with normalized columns.

    X : ndarray of shape (n_components, n_features)
        The sparse codes.
    '''

    if params['n_patoms'] is None:
        params['n_patoms'] = D.shape[1]

    for patom_index in range(int(D.shape[1]/params['n_patoms'])):
        E = Y - D @ X

        for atom_index in range(patom_index*params['n_patoms'],
                                (patom_index + 1)*params['n_patoms']):

            atom_usages = np.nonzero(X[atom_index, :])[0]

            if len(atom_usages) == 0:
                # replace with the new atom
                atom = _new_atom(Y, D, X, atom_index, params['replatoms'])
                D[:, atom_index] = atom
                continue
            else:
                F = (E[:, atom_usages] +
                     np.outer(D[:, atom_index], X[atom_index, atom_usages].T))
                atom, atom_codes = _custom_update_atom(F, D, X, atom_index,
                                                       atom_usages, params)

                D[:, atom_index] = atom
                X[atom_index, atom_usages] = atom_codes

    return D, X


def _update_atom_ker(K, A, X, params, _custom_update_atom):
    '''Kernel dictionary update loop

    Parameters
    ----------
    K : ndarray of shape (n_samples, n_samples)
        Kernel matrix.

    A : ndarray of shape (n_samples, n_components)
        Initial dictionary, with normalized columns.

    X : ndarray of shape (n_components, n_features)
        The sparse codes.

    params : dict
        Dictionary with provided parameters for the DL problem.

    _custom_update_atom : handle function
        algorithm specific atom update routine

    Output
    ------
    A : ndarray of shape (n_samples, n_components)
        Initial dictionary, with normalized columns.

    X : ndarray of shape (n_components, n_features)
        The sparse codes.
    '''
    E = np.eye(K.shape[0]) - A @ X
    for atom_index in range(A.shape[1]):
        atom_usages = np.nonzero(X[atom_index, :])[0]

        if len(atom_usages) == 0:
            # replace with the new atom
            atom = _new_atom(K, A, X, atom_index, params['replatoms'])
            A[:, atom_index] = atom / np.sqrt(atom.T @ K @ atom)
            continue
        else:
            F = (E[:, atom_usages] +
                 np.outer(A[:, atom_index], X[atom_index, atom_usages].T))
            atom, atom_codes = _custom_update_atom(F, K, A, X, atom_index,
                                                   atom_usages, params)

            A[:, atom_index] = atom
            X[atom_index, atom_usages] = atom_codes
            E[:, atom_usages] = (F - np.outer(A[:, atom_index],
                                              X[atom_index, atom_usages]))

    return A, X


def _update_patom_ker(K, A, X, params, _custom_update_atom):
    '''Parallel Kernel dictionary update loop

    Parameters
    ----------
    K : ndarray of shape (n_samples, n_samples)
        Kernel matrix.

    A : ndarray of shape (n_samples, n_components)
        Initial dictionary, with normalized columns.

    X : ndarray of shape (n_components, n_features)
        The sparse codes.

    params : dict
        Dictionary instance with provided parameters for the DL problem.

    _custom_update_atom : handle function
        algorithm specific atom update routine

    Output
    ------
    A : ndarray of shape (n_samples, n_components)
        Initial dictionary, with normalized columns.

    X : ndarray of shape (n_components, n_features)
        The sparse codes.
    '''

    if params['n_patoms'] is None:
        params['n_patoms'] = A.shape[1]

    for patom_index in range(int(A.shape[1]/params['n_patoms'])):
        E = np.eye(K.shape[0]) - A @ X

        for atom_index in range(patom_index*params['n_patoms'],
                                (patom_index + 1)*params['n_patoms']):

            atom_usages = np.nonzero(X[atom_index, :])[0]

            if len(atom_usages) == 0:
                # replace with the new atom
                atom = _new_atom(K, A, X, atom_index, params['replatoms'])
                A[:, atom_index] = atom / np.sqrt(atom.T @ K @ atom)
                continue
            else:
                F = (E[:, atom_usages] +
                     np.outer(A[:, atom_index], X[atom_index, atom_usages].T))
                atom, atom_codes = _custom_update_atom(F, K, A, X, atom_index,
                                                       atom_usages, params)

                A[:, atom_index] = atom
                X[atom_index, atom_usages] = atom_codes

    return A, X
