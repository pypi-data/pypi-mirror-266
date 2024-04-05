#class PsfAtom:
#    def __init__(self, atom_name, atom_index, atom_type, atom_charge, atom_mass, atom_resname, atom_resid, atom_segn, atom_qlp):
#        self.name = atom_name
#        self.index = atom_index
#        self.type = atom_type
#        self.charge = atom_charge
#        self.mass = atom_mass
#        self.resname = atom_resname
#        self.resid = atom_resid
#        self.segn = atom_segn
#        self.qlp = atom_qlp
#        self.alpha = None
#        self.thole = None
#
#class Psf:
#    def __init__(self):
#        self.atoms = {}
#        self.bond_indices = []
#        self.lpbond_indices = []
#        self.drudebond_indices = []
#        self.angle_indices = []
#        self.dihedral_indices = []
#        self.improper_indices = []
#        self.donor_indices = []
#        self.acceptor_indices = []
#        self.cmap_indices = []
#        self.lpics = []
#        self.anisotropies = []
#        self.drudebonds = []
#        self.groups = []
#
#    def add_atom(self, atom_name, atom_index, atom_type, atom_charge, atom_mass, atom_resname, atom_resid, atom_segn, atom_qlp, atom_alpha=None, atom_thole=None):
#        atom = PsfAtom(atom_name, atom_index, atom_type, atom_charge, atom_mass, atom_resname, atom_resid, atom_segn, atom_qlp)
#        atom.alpha = atom_alpha
#        atom.thole = atom_thole
#        self.atoms[atom_index] = atom
#
#    def add_bond(self, atom_a, atom_b):
#        self.bond_indices.append([atom_a, atom_b])

class TopAtom():
    def __init__(self,atom_index,atom_name,atom_type,atom_symbol,atom_mass,atom_charge,
                 atom_alpha=None,atom_thole=None,atom_drudetype=None,
                 atom_penalty=None,atom_comment=None):
        self.index  =  atom_index
        self.name   =  atom_name
        self.type   =  atom_type
        self.symbol =  atom_symbol
        self.mass   =  atom_mass
        self.charge =  atom_charge
        self.alpha  =  atom_alpha
        self.thole  =  atom_thole
        self.penalty=  atom_penalty
        self.comment=  atom_comment
    
class PsfAtom():
    def __init__(self,atom_index,atom_name,atom_type,atom_symbol,atom_mass,atom_charge,
                 atom_resn,atom_resid,atom_segn,atom_chain=None,atom_alpha=None,
                 atom_thole=None,atom_drudetype=None):
        self.index  = atom_index
        self.name   = atom_name 
        self.type   = atom_type 
        self.symbol = atom_symbol 
        self.mass   = atom_mass 
        self.charge = atom_charge 
        self.alpha  = atom_alpha
        self.thole  = atom_thole
        self.dtype  = atom_dtype 
        self.resn   = atom_resn 
        self.resid  = atom_resid 
        self.chain  = atom_chain 
        self.segn   = atom_segn 

class MolAtom():
    def __init__(self,atom_index,atom_name,atom_type,atom_symbol,atom_mass,atom_charge,atom_coord
                 atom_resn=None,atom_resid=1,atom_segn=None,atom_chain=None,atom_occu=None,
                 atom_tfac=None):
        self.index  = atom_index
        self.name   = atom_name 
        self.type   = atom_type 
        self.symbol = atom_symbol 
        self.mass   = atom_mass 
        self.charge = atom_charge 
        self.coord  = atom_coord 
        self.resn   = atom_resn 
        self.resid  = atom_resid 
        self.segn   = atom_segn 
        self.chain  = atom_chain 
        self.occu   = atom_occu 
        self.tfac   = atom_tfac 
