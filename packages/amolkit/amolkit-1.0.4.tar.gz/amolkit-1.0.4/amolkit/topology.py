import sys
import math
import argparse
from collections import OrderedDict
from amolkit import genic
from amolkit import getEleInfo as gei 
from amolkit.stringmanip import getPenaltyfromString

class Topology():
    def __init__(self): 
        """
        Constructor for the Topology class.
        """
    
    @staticmethod
    def readCharmmTopology(resname,resitopfile,bio=True):
        '''
        Load the features of the residue based on topology file.
    
        Note::
        field[1] is atomname
        field[2] is atomtype
        if bio is True then utilize gei.atomicmass_by_anyatomname upon atomtype
        to get atomicmass or symbol. This way I am not limited to predefined atomtypes in EleInfo.
    
        atommass_byId[field[1]] = gei.atomicmass_by_anyatomname(field[2],bio)
        atomele_byId[field[1]] = gei.atomsymbol_by_anyatomname(field[2],bio)
    
        But if it false, then I should ideally get atomicmass by atomtype
        and in case an atomtype is missing, I should allow user to supply new atomtype and its correspondence.
    
        # Give some thought if bio is False. In that case, atomtype = MAG will not be converted to Mg
        # Thus it would not find Mg
        '''
    
        topology = {}
        topology["resname"]            = resname
        topology["fftype"]             = 'additive' 
        topology["rescharge"]          = None 
        topology['ntopatoms']          = None
        topology['natoms']             = None
        topology['first_byId']         = None
        topology['last_byId']          = None
        topology['atomindex_byId']     = OrderedDict() 
        topology['atomname_byIdx']     = OrderedDict()
        topology['atomtype_byId']      = OrderedDict()
        topology['atomcharge_byId']    = OrderedDict()
        topology['atompenalty_byId']   = OrderedDict()
        topology['atommass_byId']      = OrderedDict()
        topology['atomele_byId']       = OrderedDict()
        topology['atomalpha_byId']     = OrderedDict()
        topology['atomthole_byId']     = OrderedDict()
        topology['atomdrudetype_byId'] = OrderedDict()
        topology['atomsinring']        = OrderedDict()
        topology['groups']             = []  
        topology['atomnames']          = []    
        topology['bonds']              = []
        topology['lpbonds']            = []
        topology['angles']             = []
        topology['dihedrals']          = []
        topology['impropers']          = []
        topology['lpics']              = []
        topology['anisotropies']       = []
        topology['donors']             = []
        topology['acceptors']          = []
        topology['cmaps']              = []
        topology['atomcharges']        = []
    
        try:
            filein=open(resitopfile, "r")
        except IOError:
            raise IOError('Could not access the ' + resitopfile + ' topology file')
    
        found=False
        ring = 0
        nat = 0
    
        for nl,line in enumerate(filein):
            #Strip the line, remove the comment lines, and split using whitespace
            field = line.strip().split("!")[0].split()
            
            fieldup = list(map(lambda x:x.upper(),field))
    
            comment = "!".join(line.strip().split("!")[1:]) 
    
            if len(fieldup) >= 1:
                ftype = fieldup[0][0:4]
                if found and ftype == "END": break
                if ftype in ["RESI","PRES"] and fieldup[1] !=  topology['resname'].upper():
                    if found:
                        break
                    else:
                       found = False
                elif ftype in ["RESI","PRES"] and fieldup[1] ==  topology['resname'].upper():
                    found = True
                    try:
                        topology["rescharge"]=round(float(field[2]),3)
                    except (ValueError,IndexError):
                        raise ValueError('Beware:: Error in detecting residue charge of '+topology['resname']+'.')
    
            if found and len(fieldup) > 0:
                ftype = fieldup[0][0:4]
                if ftype not in ["RING","GROU","ATOM","BOND","DOUB","TRIP","ANGL","DIHE","IMPR","DONO","ACCE","CMAP","LONE","ANIS"]: continue
                if ftype == "RING":
                    ring=ring+1
                    #topology['atomsinring'][ring]=field[1:]
                    topology['atomsinring'][ring]=fieldup[1:]
                    continue
                elif ftype == "GROU":
                    topology['groups'].append([nat,0,0])
                    continue
                elif ftype == "ATOM" and len(fieldup) > 3: 
                    nat = nat + 1
                    topology['atomindex_byId'][fieldup[1]] = nat
                    topology['atomname_byIdx'][nat] = fieldup[1]    # Atomname stored as in str
                    topology['atomtype_byId'][fieldup[1]] = fieldup[2]  # Atomtype capitalized before storing
                    topology['atomcharge_byId'][fieldup[1]] = float(field[3])
                    # Using atomicmass_by_anyatomname, but supplying atomtype
                    # Because atomicmass_by_anyatomtype does a fixed conversion
                    topology['atommass_byId'][fieldup[1]] = gei.atomicmass_by_anyatomname(field[2],bio)
                    topology['atomele_byId'][fieldup[1]] = gei.atomsymbol_by_anyatomname(field[2],bio)
                    topology['atomcharges'].append(float(field[3]))
                    topology['atompenalty_byId'][fieldup[1]],_ = getPenaltyfromString(comment)
    
                    if topology['atomnames'] and fieldup[1] in topology['atomnames']:
                        raise ValueError("Topology contains repeated atomname %s. Unable to load."%(field[1]))
                    else:
                        topology['atomnames'].append(fieldup[1]) 
                    
                    if any(list(map(lambda x:x in fieldup, ["ALPHA","THOLE","TYPE"]))): 
                        topology['atomalpha_byId'][fieldup[1]]=None
                        topology['atomthole_byId'][fieldup[1]]=None
                        topology['atomdrudetype_byId'][fieldup[1]]='DRUD'
                        topology["fftype"] = "drude"
    
                    if "ALPHA" in fieldup:
                        topology['atomalpha_byId'][fieldup[1]]=float(field[fieldup.index("ALPHA")+1])
                    if "THOLE" in fieldup:
                        topology['atomthole_byId'][fieldup[1]]=float(field[fieldup.index("THOLE")+1])
                    if "TYPE" in fieldup:
                        topology['atomdrudetype_byId'][fieldup[1]]=fieldup[fieldup.index("TYPE")+1]
    
                    continue
    
                #Bond list dictionary of each atom is populated.
                elif ftype in ["BOND","DOUB","TRIP"] and (len(fieldup)-1) % 2 == 0:
                    for i in range(1,len(fieldup),2):
                        ba = fieldup[i].strip("+-")
                        bb = fieldup[i+1].strip("+-")
                        topology['bonds'].append([ba,bb])
    
                        if ba.startswith('+'): topology['first_byId'] = ba
                        if bb.startswith('+'): topology['first_byId'] = bb
                        if ba.startswith('-'): topology['last_byId'] = ba
                        if bb.startswith('-'): topology['last_byId'] = bb
    
                        if 'LP' in [ba[0:2], bb[0:2]]:
                            topology['lpbonds'].append([ba,bb])
    
                elif ftype in ["BOND","DOUB","TRIP"] and (len(fieldup)-1) % 2 != 0:
                     raise ValueError('Topology file BOND line has the wrong format. It should be multiples of two! BOND At1 At2 At2 At3 At1 At3 etc.')
    
                #Angle list dictionary.
                elif ftype == "ANGL" and (len(fieldup)-1) % 3 == 0:
                    for i in range(1,len(fieldup),3):
                        aa = fieldup[i].strip("+-")
                        ab = fieldup[i+1].strip("+-")
                        ac = fieldup[i+2].strip("+-")
                        topology['angles'].append([aa,ab,ac])
                    continue
                elif ftype == "ANGL" and (len(fieldup)-1) % 3 != 0:
                    raise ValueError('Topology file ANGLE line has the wrong format. Ignored reading.')
                    continue
    
                #Dihedral list dictionary.
                elif ftype == "DIHE" and (len(fieldup)-1) % 4 == 0:
                    for i in range(1,len(fieldup),4):
                        da = fieldup[i].strip("+-")
                        db = fieldup[i+1].strip("+-")
                        dc = fieldup[i+2].strip("+-")
                        dd = fieldup[i+3].strip("+-")
                        topology['dihedrals'].append([da,db,dc,dd])
    
                elif ftype == "DIHE" and (len(fieldup)-1) % 4 != 0:
                    raise ValueError('Topology file DIHEDRAL line has the wrong format. Ignored reading.')
    
                #Improper list dictionary.
                elif ftype == "IMPR" and (len(fieldup)-1) % 4 == 0:
                    for i in range(1,len(fieldup),4):
                        ima = fieldup[i].strip("+-")
                        imb = fieldup[i+1].strip("+-")
                        imc = fieldup[i+2].strip("+-")
                        imd = fieldup[i+3].strip("+-")
                        topology['impropers'].append([ima,imb,imc,imd])
                elif ftype == "IMPR" and (len(fieldup)-1) % 4 != 0:
                    raise ValueError('Topology file IMPROPER line has the wrong format. Ignored reading.')
    
                #Donor list dictionary.
                elif ftype == "DONO" and (len(fieldup)-1) % 2 == 0:
                    for i in range(1,len(fieldup),2):
                        topology['donors'].append([fieldup[i+1],fieldup[i]])
    
                elif ftype == "DONO" and (len(fieldup)-1) % 2 != 0:
                    raise ValueError('Topology file DONOR line has the wrong format. Ignored reading.')
    
                #Acceptor list dictionary.
                elif ftype == "ACCE" and (len(fieldup)-1) % 2 == 0:
                    for i in range(1,len(fieldup),2):
                        topology['acceptors'].append([fieldup[i],fieldup[i+1]])
    
                elif ftype == "ACCE" and (len(fieldup)-1) == 1:
                    topology['acceptors'].append([fieldup[-1],""])
    
                elif ftype == "ACCE" and (len(fieldup)-1) != 1 or ftype == "ACCE" and (len(fieldup)-1) % 2 != 0:
                    raise ValueError('Topology file ACCEPTOR line has the wrong format. Ignored reading.')
    
                elif ftype == "CMAP" and (len(fieldup)-1) % 8 == 0:
                    for i in range(1,len(fieldup),8):
                        ca = fieldup[i].strip("+-")
                        cb = fieldup[i+1].strip("+-")
                        cc = fieldup[i+2].strip("+-")
                        cd = fieldup[i+3].strip("+-")
                        ce = fieldup[i+4].strip("+-")
                        cf = fieldup[i+5].strip("+-")
                        cg = fieldup[i+6].strip("+-")
                        ch = fieldup[i+7].strip("+-")
                        topology['cmaps'].append([ca,cb,cc,cd,ce,cf,cg,ch])
    
                elif ftype == "CMAP" and (len(fieldup)-1) % 8 != 0:
                    raise ValueError('Topology file CMAP line has the wrong format. Ignored reading.')
                
                # topology['atomindex_byId'] will change later according to inclusion of 
                # Lone pair list dictionary
                elif ftype == "LONE": 
                    if fieldup[1][0:4] in ["RELA","BISE"]:
                        try:
                            hlist = fieldup[2:6]
                            vlist = []
                            for ilp in range(len(fieldup)): 
                                if fieldup[ilp][0:4] == "DIST" and fieldup[1][0:4] == "RELA":
                                    vlist.append(float(fieldup[ilp+1]))
                                if fieldup[ilp][0:4] == "DIST" and fieldup[1][0:4] == "BISE":
                                    vlist.append(-(float(fieldup[ilp+1])))
                                if fieldup[ilp][0:4] == "ANGL":
                                    vlist.append(float(fieldup[ilp+1]))
                                if fieldup[ilp][0:4] == "DIHE":
                                    vlist.append(float(fieldup[ilp+1]))
                            topology['lpics'].append([fieldup[1][0:4],hlist,vlist])
                        except (IndexError, ValueError,KeyError):    
                            raise ValueError('Topology file LONEPAIR line has the wrong format. Ignored reading.')
                    elif fieldup[1][0:4] == "COLI": 
                        try:
                            hlist =fieldup[2:5]
                            vlist = []
                            for ilp in range(len(fieldup)): 
                                if fieldup[ilp][0:4] == "DIST":
                                    vlist.append(float(fieldup[ilp+1]))
                                if fieldup[ilp][0:4] == "SCAL":
                                    vlist.append(float(fieldup[ilp+1]))
                            vlist.append(float(0.0))
                            topology['lpics'].append([fieldup[1][0:4],hlist,vlist])
                        except (IndexError, ValueError):    
                            raise ValueError('Topology file LONEPAIR line has the wrong format. Ignored reading.')
                    elif fieldup[1][0:4] == "FIXE":
                        try:
                            topology['lpics'].append([[fieldup[1][0:4]],[],list(map(float,fieldup[2:5]))]) 
                        except (IndexError, ValueError):    
                            raise ValueError('Topology file LONEPAIR line has the wrong format. Ignored reading.')
                    elif fieldup[1][0:4] == "CENT":
                        try:
                            topology['lpics'].append([fieldup[1][0:4],fieldup[2:],[]])
                        except (IndexError, ValueError):    
                            raise ValueError('Topology file LONEPAIR line has the wrong format. Ignored reading.')
    
                # Anisotropy list dictionary
                elif ftype == "ANIS": 
                    try:
                        hlist = field[1:5]
                        for ilp in range(len(fieldup)): 
                            if fieldup[ilp][0:3] == "A11":
                                a11 =  float(fieldup[ilp+1])
                            if fieldup[ilp][0:3] == "A22":
                                a22 =  float(fieldup[ilp+1])
                        if a11 == 0.0 or a22 == 0.0:
                            raise ValueError('0.0 is invalid force constant. Correct the anisotropy line.')
                        vlist = [a11,a22] 
                        topology['anisotropies'].append([hlist,vlist])
                    except (IndexError, ValueError,KeyError):    
                        raise ValueError('Topology file Anisotropy line has the wrong format. Ignored reading.')
        #### Reading done ###
    
        if found:
            onlyatomsnlps = [at for at in topology['atomindex_byId'].keys() if at[0].upper() != "D"]
            onlyatoms     = [at for at in onlyatomsnlps if at[0:2].upper() != "LP" ]
            topology['ntopatoms']     = len(topology['atomindex_byId'].keys())
            topology['natoms']        = len(onlyatoms)
    
            #Check for residue total charge
            if abs( sum(topology['atomcharges']) - topology['rescharge'] ) > 0.00001:
                print('Warning: Your total charge does not match the sum of partial charges.')
    
        elif not found:
            print ('Could not find the residue name: '+topology['resname']+' in the provided topology file.')
        filein.close()
        return topology

    def loadCharmmTopology(self,resname,resitopfile,bio=True): 
        """
        Load topology information using CHARMM force field and store it as attributes.
        
        Args:
            resname (str): Name of the residue.
            resitopfile (str): Path to the CHARMM topology file.
        """

        topology = self.readCharmmTopology(resname,resitopfile,bio)
        for key,value in topology.items():
            self._assignattr(key,value)
    
    def _assignattr(self, key, value):
        """
        Private method to assign attributes to the class instance.

        Args:
            key: The attribute name.
            value: The value to assign to the attribute.
        """
        setattr(self, key, value)  

class WriteCharmmTopology():
    @staticmethod
    def rtf_header(header):
        text="* %s\n* Written by: amolkit\n*\n"%(header)
        return text
    
    @staticmethod
    def rtf_ioformat(extended=True):
        if extended: text="ioformat extended"
        return text
    
    @staticmethod
    def rtf_readinstruct(append=True):
        if append:
            text="read rtf card append"
        else:
            text="read rtf card"
        return text
    
    @staticmethod
    def rtf_version(version):
        return str(version)
    
    @staticmethod
    def rtf_autogenangdih(drude=True):
        if drude: 
            text = "AUTO ANGL DIHE DRUD"
        else:    
            text = "AUTO ANGL DIHE"
        return text    
    
    @staticmethod
    def rtf_comment(comment):
        return comment
    
    @staticmethod
    def rtf_end():
        return "END\n\n"
