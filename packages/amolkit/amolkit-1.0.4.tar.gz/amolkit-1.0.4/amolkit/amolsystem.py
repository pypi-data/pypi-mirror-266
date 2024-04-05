import math
from collections import OrderedDict
from amolkit import genic
from amolkit import getEleInfo as gei 
from amolkit.topology import Topology
from amolkit.molecule import Molecule

class MolSystem(Topology):
    """
    Create molecule object using topology, parameters and coordinate file
    """
    def __init__(self): 
        """
        """
        super().__init__()

    def loadTopology(self,resname,resitopfile):
        '''
        Load the features of the residue based on topology file.
        '''

        self.loadCharmmTopology(resname,resitopfile)

    def loadParameters(self,parfiles,autogenangdih=True):
        """
        Load parameters into molecule's internal coordinates by reading parameter file/s.
        Arguments:
            parfiles: Can be a list of parameter containing files or single file.
        Attributes:
            self.bondparam: List of parameters with bond ICs [[C1,H1,kval,eqdist,penalty],...]
            self.angleparam: List of parameters with angle ICs [[H1,C1,C2,kval,eqangle,penalty],...]
            self.dihedralparam: List of parameters with dihedral ICs [[C1,C2,C3,C4,mult,kval,phase,penalty],...]
                                Note that position of multiplicity has changed compared to charmm parameter format
                                This helps in management of the list. 
            self.superdihparam: Each dihedral IC has 6 entries with 6 different multiplicties.
                                If there is no dihedral value corresponding to a particular multiplicity in
                                charmm parameter file, it will just store None against it.
                                This helps when one wants to optimize parameters.
        Note:
            Have to add improper also. Haven't added because I dont have function to generate impropers in a molecule.
            Thus have to rely on impropers in topology file. self.impropers are stored in terms of numbers.
        """

        from copy import deepcopy
        from amolkit.parameter import Parameter

        param = Parameter()
        param.loadCharmmParameter(parfiles)
        #param.charmmParameter: Collection of all parameters obtained from parfiles.
        
        if not self.bonds:
            print ("Charmm Parameters obtained, but not loaded on molecular ics. You should load topology prior to loading parameters")
            return
        
        # Get list of bond angle and dihedral
        bondindices=[]
        for ba,bb in self.bonds:
            bondindices.append([self.atomindex_byId[ba],self.atomindex_byId[bb]])
        bondgraph = genic.ICs.getBondDict(self.atomname_byIdx,bondindices)["aNoLPBond"]
        bondnames,_ = genic.ICs.getBonds(self.atomindex_byId,bondgraph)
        if autogenangdih:
            anglenames,_ = genic.ICs.getAngles(self.atomindex_byId,bondgraph)
            dihedralnames,_ = genic.ICs.getDihedrals(self.atomindex_byId,bondgraph)
        else:
            anglenames = deepcopy(self.angles)
            dihedralnames = deepcopy(self.dihedrals)
            
        # Assign parameters to bond, angle and dihedral
        # Initialize parameter lists
        self.bondparam = deepcopy(bondnames)
        self.angleparam = deepcopy(anglenames)
        self.superdihparam = [None]*6*(len(dihedralnames))

        for i,bp in enumerate(self.bondparam):
            self.bondparam[i].append(None)
            self.bondparam[i].append(None) 
            self.bondparam[i].append(None) 

        # Will not assume Urey Bradley terms here, should be appended if exists
        for i,ap in enumerate(self.angleparam):
            self.angleparam[i].append(None)   
            self.angleparam[i].append(None) 
            self.angleparam[i].append(None) 
         
        # Each dihedral will have 6 copies with 6 different multiplicities 
        nd = 0    
        for i,dp in enumerate(dihedralnames):
            for j in range(6):
                self.superdihparam[nd] = deepcopy(dp) 
                self.superdihparam[nd].append(j+1) 
                self.superdihparam[nd].append(None) 
                self.superdihparam[nd].append(None) 
                self.superdihparam[nd].append(None) 
                nd=nd+1
                
        # Assign now
        for i,bl in enumerate(bondnames):
            parainq = [self.atomtype_byId[bl[0]], self.atomtype_byId[bl[1]]]
            for j, listele in enumerate(param.charmmParameter['BONDS']):
                listf = listele[0:2]
                listb = listele[0:2][::-1]
                if parainq == listf or parainq == listb:
                    self.bondparam[i][2] = listele[2] 
                    self.bondparam[i][3] = listele[3]
                    self.bondparam[i][4] = listele[4]

        for i,al in enumerate(anglenames):
            parainq = [self.atomtype_byId[al[0]], self.atomtype_byId[al[1]],self.atomtype_byId[al[2]]]
            for j, listele in enumerate(param.charmmParameter['ANGLES']):
                listf = listele[0:3]
                listb = listele[0:3][::-1]
                if parainq == listf or parainq == listb:
                    if len(listele) == 7:
                        self.angleparam[i][3] = listele[3]
                        self.angleparam[i][4] = listele[4]
                        self.angleparam[i][5] = listele[5]
                    elif len(listele) == 9:
                        self.angleparam[i][3] = listele[3]
                        self.angleparam[i][4] = listele[4]
                        self.angleparam[i][5] = listele[5]
                        self.angleparam[i].append(listele[6])
                        self.angleparam[i].append(listele[7])

        for i,dl in enumerate(dihedralnames):
            parainq = [self.atomtype_byId[dl[0]], self.atomtype_byId[dl[1]],self.atomtype_byId[dl[2]],self.atomtype_byId[dl[3]]]
            for j, listele in enumerate(param.charmmParameter['DIHEDRALS']):
                listf = listele[0:4]
                listb = listele[0:4][::-1]
                if parainq == listf or parainq == listb:
                    #listele[5] is multiplicity
                    index = i*6 + (int(listele[5])-1)
                    self.superdihparam[index][5] = listele[4] 
                    self.superdihparam[index][6] = listele[6] 
                    self.superdihparam[index][7] = listele[7] 
        
        # Get dihedral IC with same multiplicities as obtained in charmm parameter files
        # ==> But this also removes those entries for which no parameter is found.
        self.dihedralparam=[]
        for ent in self.superdihparam:
            if ent[5] != None:
                self.dihedralparam.append(ent)

    def _checkCompatibility(self):
        # sanity check
        namecompatible=False
        ordercompatible=False
        ordercompatible_nolpdx=False

        topnames = list(map(lambda x:x.upper(),self.atomnames)) 
        molnames = list(map(lambda x:x.upper(),self.molecule.atomname_byIdx.values()))

        # Ideal scenario 
        # All atomnames in topology and molecule instance are same and in order.
        if topnames == molnames:
            namecompatible = True

        if not namecompatible:    
            topnames = sorted(topnames)
            molnames = sorted(molnames)
            if topnames == molnames:
               namecompatible = True
        if not namecompatible:       
            topnames_nolpd = [v for v in topnames if v[0:2].upper() != "LP" and v[0].upper() != "D"]
            molnames_nolpd = [v for v in molnames if v[0:2].upper() != "LP" and v[0].upper() != "D"]
            if topnames_nolpd == molnames_nolpd:
                namecompatible = True
        if not namecompatible:    
            topnames_nolpd = sorted(topnames_nolpd)
            molnames_nolpd = sorted(molnames_nolpd)
            if topnames_nolpd == molnames_nolpd:
               namecompatible = True

        if not namecompatible:    
            topelements = list(map(lambda x:x.upper(),self.atomele_byId.values())) 
            molelements = list(map(lambda x:x.upper(),self.molecule.atomele_byIdx.values()))
            if topelements == molelements:
                ordercompatible = True

        if not namecompatible and not ordercompatible:    
            topelements_nolpdx = [v for v in topelements if v[0:2].upper() != "LP" and v[0].upper() != "D" and v[0].upper() != "X"]
            molelements_nolpdx = [v for v in molelements if v[0:2].upper() != "LP" and v[0].upper() != "D" and v[0].upper() != "X"]

            if topelements_nolpdx == molelements_nolpdx:
                ordercompatible_nolpdx = True
        return (namecompatible,ordercompatible,ordercompatible_nolpdx)        

    def loadGeometry(self,molecule,update=""):
        """
        This method expects to receive Molecule object with preloaded coordinate file.
        It uses the coordinates to assign atomcoord to molsystem object.
        Before assigning atomcoord, it checks if molecule coordinates are compatible with
        atomnames in topology object. Else raises ValueError

        Arguments:
            molecule: Molecule object with preloaded coordinate file
        Attributes:
            self.atomcoord: OrderedDict containing coordinates with respect atom name in topology object
        """

        self.molecule = molecule 
        self.nmolatoms = self.molecule.nmolatoms
        self.atomcoord_byId  = OrderedDict() 
        self.atomcoord_byIdx = OrderedDict() 
        self.atomele_byIdx   = OrderedDict() 
        self.atomserial_byIdx= OrderedDict() 
        self.atomresn_byIdx  = OrderedDict() 
        self.atomresid_byIdx = OrderedDict() 
        self.atomsegn_byIdx  = OrderedDict() 
        self.atomchain_byIdx = OrderedDict()
        self.atomoccu_byIdx  = OrderedDict()
        self.atomtfac_byIdx  = OrderedDict()
        self.atomcharge_byIdx= OrderedDict()

        namecompatible,ordercompatible,ordercompatible_nolpdx = self._checkCompatibility() # sanity check

        if namecompatible: 
            for key,value in self.atomindex_byId.items():
                try:
                    self.atomcoord_byId[key] = self.molecule.atomcoord_byIdx[self.molecule.atomindex_byId[key]]
                except KeyError:
                    self.atomcoord_byId[key]=[9999.999,9999.999,9999.999]
        
        elif ordercompatible:    
            for key,value in self.atomname_byIdx.items():
                try:
                    self.atomcoord_byId[value] = self.molecule.atomcoord_byIdx[key]
                except KeyError:
                    self.atomcoord_byId[value] = [9999.999,9999.999,9999.999]

        elif ordercompatible_nolpdx:    
            key = 0
            atomcoord_byIdx_nolpdx=OrderedDict() 
            for i in range(self.molecule.nmolatoms):
                checkatom = molecule.atomele_byIdx[i+1].upper() 
                if checkatom[0:2] == "LP" or checkatom[0] == "D" or checkatom[0] =="X": 
                    continue 
                else:
                    key = key + 1
                    atomcoord_byIdx_nolpdx[key] = self.molecule.atomcoord_byIdx[i+1] 

            key = 0
            for i in range(self.ntopatoms):
                value = self.atomname_byIdx[i+1]
                if value[0:2] == "LP" or value[0] == "D" or value[0] =="X": 
                    self.atomcoord_byId[value] = [9999.999,9999.999,9999.999]
                else:
                    key = key + 1
                    self.atomcoord_byId[value] = atomcoord_byIdx_nolpdx[key] 

        else:
            raise ValueError ("Neither the name nor the order of elements in molecule are compatible with topology")

        for key,value in self.atomcoord_byId.items(): 
            self.atomcoord_byIdx[self.atomindex_byId[key]]= value 
            self.atomserial_byIdx[self.atomindex_byId[key]]= self.atomindex_byId[key]
            self.atomele_byIdx[self.atomindex_byId[key]]= self.atomele_byId[key]
            self.atomresn_byIdx[self.atomindex_byId[key]]= self.resname 
            self.atomresid_byIdx[self.atomindex_byId[key]]= 1 
            self.atomsegn_byIdx[self.atomindex_byId[key]]=self.resname 
