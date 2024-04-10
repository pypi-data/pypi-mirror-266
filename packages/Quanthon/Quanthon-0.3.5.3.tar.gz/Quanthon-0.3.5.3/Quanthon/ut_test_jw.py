from qiskit_nature.second_q.mappers import JordanWignerMapper
from qiskit_nature.second_q.operators import FermionicOp

from mappers import jordan_wigner
from physics import Hamiltonian

import numpy as np

def matrix_to_fermionic_op(one_body_matrix, two_body_matrix):
    # Get the size of the one-body matrix
    n = one_body_matrix.shape[0]

    # Initialize an empty FermionicOp dictionary
    op_dict = {}

    # Handle one-body terms
    for i in range(n):
        for j in range(n):
            if one_body_matrix[i, j] != 0:
                key = f"+_{i} -_{j}"
                op_dict[key] = one_body_matrix[i, j]

    # Handle two-body terms
    # Assuming two_body_matrix is a 4-dimensional array
    for i in range(n):
        for j in range(n):
            for k in range(n):
                for l in range(n):
                    if two_body_matrix[i, j, k, l] != 0:
                        # Create the corresponding fermionic operator for the two-body term
                        key = f"+_{i} +_{j} -_{k} -_{l}"
                        op_dict[key] = two_body_matrix[i, j, k, l]

    # Create and return the FermionicOp
    return FermionicOp(op_dict)


# Convert the matrix to FermionicOp




a=np.complex64(1.5)
b=np.complex64(2+1j)
c=np.complex64(2)

# one_body = np.zeros((4,4), dtype=np.complex_)
# np.fill_diagonal(one_body, [c,a])
# # one_body[0,2] = b
# # one_body[2,0] = b.conj()
# h = Hamiltonian(one_body, np.zeros((4,4,4,4)))

# # rng = np.random.default_rng()
# # a = np.complex64(rng.random() + 1j*rng.random())
# # b = np.complex64(rng.random() + 1j*rng.random())
# # c = np.complex64(rng.random() + 1j*rng.random())

# # h = Hamiltonian(np.array([[a, b], [b.conj(), c]]), np.zeros((2,2,2,2)))
# k = dict(jordan_wigner(h))

# fermionic_op = matrix_to_fermionic_op(one_body)

# # op = FermionicOp({
# #     "+_0 -_0": c,
# #     "+_0 -_1": b.conj(),
# #     "+_1 -_0": b,
# #     "+_1 -_1": a
# # })

# op = matrix_to_fermionic_op(one_body)

# mapper = JordanWignerMapper()
# q = mapper.map(second_q_ops=op)


def test_1():

    h = Hamiltonian(np.array([[a, b], [b.conj(), c]]), np.zeros((2,2,2,2)))
    k = dict(jordan_wigner(h))
    op = FermionicOp({
        "+_0 -_0": c,
        "+_0 -_1": b.conj(),
        "+_1 -_0": b,
        "+_1 -_1": a
    })

    mapper = JordanWignerMapper()
    q = mapper.map(second_q_ops=op)


    d = {"II":0.5*a+0.5*c, 
        "IZ":-0.5*c, 
        "XX":0.25*(b+b.conj()), 
        "XY":0.25j*(b-b.conj()), 
        "YX": 0.25j*(b.conj()-b), 
        "YY":0.25*(b+b.conj()), 
        "ZI":-0.5*a}

    print("Pauli, Qiskit, Paper, Quanthon")
    for i,p in enumerate(q.paulis.to_labels()):
        print(p, q.coeffs[i], d[p], k[p])
        np.testing.assert_equal(q.coeffs[i], d[p])
        np.testing.assert_equal(q.coeffs[i], k[p])


    print(len(k) == len(d))

def test_one_body():

    n = 4
    a=np.complex64(1.5)
    b=np.complex64(2+1j)
    c=np.complex64(2)

    one_body = np.zeros((n,n), dtype=np.complex_)
    np.fill_diagonal(one_body, [a,c])
    one_body[0,2] = b
    one_body[2,0] = b.conj()
    one_body[1,3] = b
    one_body[3,1] = b.conj()
   
    # h = Hamiltonian(np.array([[a, b], [b.conj(), c]]), np.zeros((2,2,2,2)))
    
    op = matrix_to_fermionic_op(one_body)

    h = Hamiltonian(np.flip(one_body), np.zeros((n,n,n,n))) 
    # flip cuz qiskit is weird

    k = dict(sorted(jordan_wigner(h)))
    mapper = JordanWignerMapper()
    q = mapper.map(second_q_ops=op)

    print("Pauli, Qiskit, Quanthon")
    for i,p in enumerate(q.paulis.to_labels()):
        print(p, q.coeffs[i], k[p]) 
        np.testing.assert_equal(q.coeffs[i], k[p])


    print(f"my dict: {len(k)}, qiskit: {len(q.coeffs)}")
    # for i in k:
    #     print(i, k[i])

def test_two_body():
    n = 4

    a,b,c = np.array([2,8,6], dtype=np.complex_)
    b = np.complex_(8+1j)
    c = np.complex_(6)
    # one_body = np.zeros((n,n))
    one_body = np.random.rand(n,n) + 1j*np.random.rand(n,n)
    one_body = one_body + one_body.conj().T

    two_body = np.random.rand(n,n,n,n) + 1j*np.random.rand(n,n,n,n)
    two_body = two_body + two_body.conj().T

    # # diagonal
    # two_body[0,1,0,1] = a
    # two_body[0,2,2,0] = b
    # two_body[2,0,0,2] = b
    # two_body[1,3,3,1] = c
    # two_body[3,1,1,3] = c

    # # 4 unique
    # two_body[0,1,2,3] = b # ijkl
    # two_body[2,3,0,1] = b.conj() # klij
    # two_body[2,3,1,0] = c
    # two_body[1,0,2,3] = c.conj()

    # # 3 unique
    # two_body[0,1,1,3] = b
    # two_body[1,3,0,1] = b.conj()


    op = matrix_to_fermionic_op(one_body,two_body)

    h = Hamiltonian(np.flip(one_body), np.flip(two_body))

    return h, op

debug = True

if debug:
    # test_1()
    # test_one_body()
    h, op = test_two_body()

    k = dict(sorted(jordan_wigner(h)))

    mapper = JordanWignerMapper()

    q = mapper.map(second_q_ops=op)
    # print(q)
    # print(k)

    print("Pauli, Qiskit, Quanthon")
    for i,p in enumerate(q.paulis.to_labels()):
        print(p, q.coeffs[i], k[p]) 
        assert(np.allclose(q.coeffs[i], k[p]))
        # np.testing.assert_equal(q.coeffs[i], k[p])

    # for key in k.keys():
    #     if key not in q.paulis.to_labels():
    #         print(f"Key {key} not in qiskit, has value {k[key]}")

    print(f"my dict: {len(k)}, qiskit: {len(q.coeffs)}")