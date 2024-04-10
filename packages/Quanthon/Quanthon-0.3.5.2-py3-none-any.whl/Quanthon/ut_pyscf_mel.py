import pyscf
from pyscf import scf, gto
import numpy as np


def add_spin_one_body(operator):
    return np.kron(operator, np.eye(2))

def add_spin_two_body(operator, make_as=True):
    operator = np.kron(operator, np.einsum("pr, qs -> pqrs", np.eye(2), np.eye(2)))

    if make_as:
        operator = operator - operator.transpose(0,1,3,2)

    return operator


def get_hs(mol, is_rhf=False):
    L = mol.nao

    s = mol.intor_symmetric("int1e_ovlp")

    kinetic = mol.intor_symmetric("int1e_kin")
    potential = mol.intor_symmetric("int1e_nuc")
    h = kinetic + potential

    # "u" comes out as an (L**2, L**2) matrix. First we change it to (L,L,L,L) to fit the 4-index matrix element
    # additionally, it comes out in chemestry notation (ij|kl) = <ik|jl>, so swap axis 1 and 2 to get <ij|kl>
    u = mol.intor("int2e") 
    u = u.reshape(L, L, L, L)


    u = u.transpose(0, 2, 1, 3)
    if is_rhf:
        h, u = get_rhf(mol, h, u, s)


    # u = u.transpose(0, 2, 1, 3)

    # print(f"Before {h.shape = }")
    h = add_spin_one_body(h)
    # print(f"After  {h.shape = }")
    # # print(h)
    # print(f"Before {u.shape = }")
    u = add_spin_two_body(u)
    # print(f"After  {u.shape = }")

    return h, u


def get_rhf(mol,h,u,s):
    mf = scf.RHF(mol)
    mf.kernel()

    # print(mf.mo_coeff)
    c = mf.mo_coeff

    # print(s)

    somethingelse = np.einsum("pr,qs,pq -> rs", c, c, s)
    # print(somethingelse)

    U = np.einsum("pi,qj,rk,sl,pqrs -> ijkl", c, c, c, c, u, optimize=True)
    H = np.einsum("pr,qs,pq -> rs", c, c, h)

    U = U - U.transpose(0, 1, 3, 2)
    f = H - 0.5 * np.einsum("piqi -> pq",U)

    # print(f)

    return H, U



if __name__ == '__main__':

    # geometry = "He 0 0 0"
    #"Li 0 0 0; H 0 0 2.0"
    geometry = "H 0 0 0; H 0 0 0.7414"
    basis = "sto-3g"
    charge = 0

    mol = pyscf.gto.Mole()
    # mol.unit = "bohr" # Default is angstrom
    mol.build(atom=geometry, basis=basis, charge=charge)

    h, u = get_hs(mol, True)


    for i in range(4):
        for j in range(4):
            for k in range(4):
                for l in range(4):
                    if not np.allclose(u[i,j,k,l], 0):
                        print(f'{i}{j}{k}{l}, {u[i,j,k,l]}')
        
    # print(h)
    # print(u)
    # print(h.shape)
    # print(u.shape