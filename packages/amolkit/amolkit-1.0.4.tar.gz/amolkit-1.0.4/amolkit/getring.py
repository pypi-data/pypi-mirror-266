#def getAtomsInRing(atom,visited,bond_dict):
#    """Make a list of list of dihedral quads with atomnames and atomindices"""
#    if atom not in visited:
#       visited.add(atom)
#       for atm in bond_dict[atom]:
#           getAtomsInRing(atm,visited,bond_dict)
#
#visited = set()
class Atom:
    def __init__(self, idx):
        self.idx = idx
        self.bonds = set()
        self.visited = False

def find_atoms_in_rings(molecule):
    # Step 1: Parse the molecular structure and create Atom objects
    atoms = [Atom(idx) for idx in range(molecule.num_atoms)]

    # Step 2: Identify bonds between atoms
    for bond in molecule.bonds:
        print (bond)
        atoms[bond.atom1].bonds.add(bond.atom2)
        atoms[bond.atom2].bonds.add(bond.atom1)

    # Step 3: Traverse the graph to find rings
    atoms_in_rings = set()
    for atom in atoms:
        if not atom.visited:
            ring_atoms = dfs(atom, atoms, set())
            atoms_in_rings.update(ring_atoms)

    return atoms_in_rings

def dfs(atom, atoms, path):
    atom.visited = True
    path.add(atom.idx)

    ring_atoms = set()
    for neighbor_idx in atom.bonds:
        neighbor = atoms[neighbor_idx]
        if not neighbor.visited:
            ring_atoms.update(dfs(neighbor, atoms, path))
        elif neighbor_idx in path:
            ring_atoms.add(neighbor_idx)

    path.remove(atom.idx)
    return ring_atoms

# Example usage
class Molecule:
    def __init__(self, num_atoms, bonds):
        self.num_atoms = num_atoms
        self.bonds = bonds

# Define your molecule (replace this with your own molecule data)
num_atoms = 6
bonds = [(0, 1), (1, 2), (2, 3), (3, 4), (4, 5), (5, 0)]
molecule = Molecule(num_atoms, bonds)

atoms_in_rings = find_atoms_in_rings(molecule)
print("Atoms in rings:", atoms_in_rings)

#    @staticmethod
#    def getAtomsInRing(aatomname,atom,visited,bond_dict):
#        """Make a list of list of dihedral quads with atomnames and atomindices"""
#        if atom not in visited:
#            visited.add(atom)
#            for i in bond_dict[atom]:
#                getAtomsInRing(aat:q)
#        #= []
#        for k0,v0 in list(bond_dict.items()):
#            dih0 = k0
#            for k1 in v0:
#                if bond_dict.get(k1) and len(bond_dict[k1]) != 1:
#                    dih1 = k1
#                    for k2 in bond_dict[k1]:
#                        if bond_dict.get(k2) and len(bond_dict[k2]) != 1 and k2 != dih0:
#                            visited.append(k2)
#                            for k3 in bond_dict[k2]:
#                                if k3 != dih1 and k3 != dih0:
#                                    dih3 = k3
#                                    if [dih3,dih2,dih1,dih0] not in adihedrallist:
#                                        adihedrallist.append([dih0,dih1,dih2,dih3])
#                                        idihedrallist.append([int(aatomname[dih0]),int(aatomname[dih1]),int(aatomname[dih2]),int(aatomname[dih3])])
#        return(adihedrallist,idihedrallist)

