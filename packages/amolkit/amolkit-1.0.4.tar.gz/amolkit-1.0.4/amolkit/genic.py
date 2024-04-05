import numpy as np
from operator import sub
from collections import OrderedDict

class ICs():
    """
    Get Molecular Graph and Internal Coordinate List
    """
    @staticmethod
    def getBondDict(iatomname,bondlist,onlyatoms=True):
        """
        Generate Dict with atomname as keys and bonded atoms as values
        Arguments:
            iatomname: Dictionary of atom indices containing atomnames
            bondlist: List of list of bonds obtained from reading mol2 format
            onlyatoms: If true, output dictionary will not have lone pair names as keys
        Returns:
            aBond: Dictionary of atomnames with bonded atomnames as values
        """

        def patch_dict(anolpbond_dict,alpbond_dict):
            abond_dict=OrderedDict()
            for key,value in anolpbond_dict.items():
                abond_dict[key]=value
            if alpbond_dict != None:            
                for key,value in alpbond_dict.items():
                    chkval=anolpbond_dict.get(key)
                    if not chkval:
                        abond_dict.update({key:value})
                    else:
                        newvalue=chkval+value
                        abond_dict.update({key:newvalue})
            return (abond_dict)    

        anolpbond_dict=OrderedDict()
        alpbond_dict=OrderedDict()

        for field in bondlist:
            ba = iatomname[int(field[0])]
            bb = iatomname[int(field[-1])]
            if 'LP' not in [ba[0:2], bb[0:2]]:
                try:
                    anolpbond_dict[ba].append(bb)
                except KeyError:
                    anolpbond_dict[ba]=[bb]
                try:
                    anolpbond_dict[bb].append(ba)
                except KeyError:
                    anolpbond_dict[bb]=[ba]
            else:
                if onlyatoms:
                    if ba[0:2]=="LP":
                        lpa=ba
                        hatm=bb
                    else:
                        lpa=bb
                        hatm=ba
                    try:
                        alpbond_dict[hatm].append(lpa)
                    except KeyError:
                        alpbond_dict[hatm]=[lpa]
                else:
                    try:
                        alpbond_dict[ba].append(bb)
                    except KeyError:
                        alpbond_dict[ba]=[bb]
                    try:
                        alpbond_dict[bb].append(ba)
                    except KeyError:
                        alpbond_dict[bb]=[ba]

        if alpbond_dict != None:
            abond_dict=patch_dict(anolpbond_dict,alpbond_dict)
            return({"aBond":abond_dict,"aNoLPBond":anolpbond_dict,"aLPBond":alpbond_dict})
        else:
            abond_dict=anolpbond_dict
            return({"aBond":abond_dict})

    @staticmethod
    def getBonds(aatomname,bond_dict):
        """
        Make a list of list of bond pairs with atomnames and atomindices
        Arguments:
            aatomname: Dictionary of atom names containing atomindices
            bond_dict: BondDict obtained from getBondDict
        Returns:
            abondlist: list of list of bond pairs with atomnames
            ibondlist: list of list of bond pairs with atomindices
        """
        abondlist = []
        ibondlist = []
        for key,value in list(bond_dict.items()):
            for val in value:
                if [val,key] not in abondlist:
                    abondlist.append([key,val])
                    ibondlist.append([int(aatomname[key]),int(aatomname[val])])
        return(abondlist,ibondlist)

    @staticmethod
    def getAngles(aatomname,bond_dict):
        """Make a list of list of angle triplets with atomnames and atomindices"""
        aanglelist = []
        ianglelist = []
        for k0,v0 in list(bond_dict.items()):
            if len(v0) > 1:
                for i in range(0,(len(v0)-1)):
                    ang2 = k0
                    ang1 = v0[i]
                    for j in range(i+1,len(v0)):
                        ang3 = v0[j]
                        aanglelist.append([ang1,ang2,ang3])
                        ianglelist.append([int(aatomname[ang1]),int(aatomname[ang2]),int(aatomname[ang3])])
        return(aanglelist,ianglelist)

    @staticmethod
    def getDihedrals(aatomname,bond_dict):
        """Make a list of list of dihedral quads with atomnames and atomindices"""
        adihedrallist = []
        idihedrallist = []
        for k0,v0 in list(bond_dict.items()):
            dih0 = k0
            for k1 in v0:
                if bond_dict.get(k1) and len(bond_dict[k1]) != 1:
                    dih1 = k1
                    for k2 in bond_dict[k1]:
                        if bond_dict.get(k2) and len(bond_dict[k2]) != 1 and k2 != dih0:
                            dih2 = k2
                            for k3 in bond_dict[k2]:
                                if k3 != dih1 and k3 != dih0:
                                    dih3 = k3
                                    if [dih3,dih2,dih1,dih0] not in adihedrallist:
                                        adihedrallist.append([dih0,dih1,dih2,dih3])
                                        idihedrallist.append([int(aatomname[dih0]),int(aatomname[dih1]),int(aatomname[dih2]),int(aatomname[dih3])])
        return(adihedrallist,idihedrallist)

    @staticmethod
    def getOnefives(aatomname,bond_dict):
        """Make a list of list of onefives 5 entries with atomnames and atomindices"""
        aonefivelist = []
        ionefivelist = []
        for k0,v0 in list(bond_dict.items()):
            skip=[k0,*v0]
            of0 = k0
            for k1 in v0:
                if len(bond_dict[k1]) != 1 and bond_dict.get(k1):
                    of1 = k1
                    for k2 in bond_dict[k1]:
                        if len(bond_dict[k2]) != 1 and k2 != of0:
                            of2 = k2
                            for k3 in bond_dict[k2]:
                                if len(bond_dict[k3]) != 1 and k3 != of1 and k3 != of0:
                                    of3 = k3
                                    for k4 in bond_dict[k3]:
                                        if k4 != of2 and k4 != of1 and k4 != of0:
                                            of4 = k4
                                            if [of4,of3,of2,of1,of0] not in aonefivelist:
                                                aonefivelist.append([of0,of1,of2,of3,of4])
                                                ionefivelist.append([int(aatomname[of0]),int(aatomname[of1]),int(aatomname[of2]),int(aatomname[of3]),int(aatomname[of4])])
        return(aonefivelist,ionefivelist)
    
    @staticmethod
    def getImpropers(aatomname,bond_dict):
        aimplist=[]
        iimplist=[]
        for key,val in list(bond_dict.items()):
            if len(val)==3:
                aimplist.append([key,*val])
                iimplist.append([int(aatomname[key]),int(aatomname[val[0]]),int(aatomname[val[1]]),int(aatomname[val[2]])])
        return (aimplist,iimplist)

class ICValue():
    """
    Get Distance, Angle and Dihedral Value by provides a set of 2/3/4 coordinates
    """
    @staticmethod
    def getBondValue(coord1,coord2):
        coord1=np.array(coord1,dtype='float32')
        coord2=np.array(coord2,dtype='float32')
    
        xyz = np.array(list(map(sub,coord1,coord2)))
        distance = np.linalg.norm(xyz)
        distance = round(distance,4)
        return distance
    
    @staticmethod
    def getAngleValue(coord1,coord2,coord3):
        coord1=np.array(coord1,dtype='float32')
        coord2=np.array(coord2,dtype='float32')
        coord3=np.array(coord3,dtype='float32')
    
        bav = coord1 - coord2 
        bcv = coord3 - coord2 
        cosine_angle = np.dot(bav, bcv) / (np.linalg.norm(bav) * np.linalg.norm(bcv))
        angle = np.arccos(cosine_angle)
        angle = np.degrees(angle)
        angle = round(angle,3)
        return angle
    
    @staticmethod
    def getDihedralValue(coord1,coord2,coord3,coord4):
        coord1=np.array(coord1,dtype='float32')
        coord2=np.array(coord2,dtype='float32')
        coord3=np.array(coord3,dtype='float32')
        coord4=np.array(coord4,dtype='float32')
        b0 = -1.0*(coord2 - coord1)
        b1 = coord3 - coord2 
        b2 = coord4 - coord3 
        b0xb1 = np.cross(b0, b1)
        b1xb2 = np.cross(b2, b1)
        b0xb1_x_b1xb2 = np.cross(b0xb1, b1xb2)
        y = np.dot(b0xb1_x_b1xb2, b1)*(1.0/np.linalg.norm(b1))
        x = np.dot(b0xb1, b1xb2)
        dihedral = np.arctan2(y, x)
        dihedral = np.degrees(dihedral)
        dihedral = round(dihedral,3)
        return dihedral
    
def getICValue(coord1=[],coord2=[],coord3=[],coord4=[]):
    if coord1 and coord2 and not coord3 and not coord4: return ICValue.getBondValue(coord1,coord2)
    if coord1 and coord2 and coord3 and not coord4: return ICValue.getAngleValue(coord1,coord2,coord3)
    if coord1 and coord2 and coord3 and coord4: return ICValue.getDihedralValue(coord1,coord2,coord3,coord4)


