import logging
try:
    from rdkit import Chem
    from rdkit.Chem import AllChem
except ImportError:
    logging.warning('RDKit not found!')
import numpy as np
from collections import OrderedDict

class MolTransform():
    __transformtypes={2:'bond',3:'angle',4:'dihedral'}
    def __init__(self,m,resname,rescharge,coor,atomnames,atomnrmap,bondnames,changetype,atomlist,targetvalue=None,targetrange=None,returns=None,pathfilebase=None,writepdb=False,writepy=False,multiplicity=1):
        self.m=m
        self.resname=resname
        self.rescharge=rescharge
        self.multiplicity=multiplicity
        self.atomnames=atomnames
        self.atomnrmap= atomnrmap
        self.bonds=bondnames
        self.coor=coor
        self.changetype=changetype
        self.scanatomnames=atomlist
        self.scanatomnr=[self.atomnrmap[i][0] for i in self.scanatomnames]
        self.targetvalue=targetvalue
        self.targetrange=targetrange
        self.returns=returns
        self.pfbase=pathfilebase
        self.writepy=writepy
        self.writepdb=writepdb

        if not self.__ctrl_changetype():
            return(None)
        if not self.__ctrl_bonds():
            return(None)
        if not self.__ctrl_length():
            return(None)
        if not self.__ctrl_coor():
            return(None)
        if not self.targetvalue:
            if not self.__ctrl_range():
                return(None)
        elif self.targetvalue:
            if type(self.targetvalue) not in [str,int,float]:
                logging.error('Target value keyword excepts a single value')
                return(None)
            else:
                try:
                    self.targetvalue=float(self.targetvalue)
                except ValueError:
                    logging.error("Cannot convert target value to float")
                    return(None)
        else:
            logging.error('Provide either target value or target range not both.')
            return(None)

        if not self.returns:
            if not self.pfbase:
                logging.error('Either provide a base filename (prepended with the path) or request to return the generated coordinate objects.')
        self.__transform()

    def __ctrl_changetype(self):
        #Sanity check
        typefromlist=self.__transformtypes[len(self.scanatomnr)]
        if typefromlist != self.changetype:
            logging.error('The transformation type %s requies % atoms.' %(self.changetype,len(self.scanatomnr)))
            return(None)
        if self.changetype not in self.__transformtypes.values():
            logging.error('Transformation type %s is not supported, Please choose from:%'%(self.changetype,','.join(self.__transformtypes.values())))
            return(None)
        return(True)

    def __ctrl_bonds(self):
        natom={'bond':2,'angle':3,'dihedral':4}
        bonded_groups=[self.scanatomnames[0:2]]
        if self.changetype == 'angle':
            bonded_groups+=[self.scanatomnames[1:3]]
        elif self.changetype == 'dihedral':
            bonded_groups+=[self.scanatomnames[1:3]]
            bonded_groups+=[self.scanatomnames[2:]]
        for bonded in bonded_groups:
            if len(bonded) != 2:
                logging.error("The atomlist should contain %s atoms for transformation type %s" %(natom[self.changetype],self.changetype))
                return False
            if bonded not in self.bonds:
                if [bonded[1],bonded[0]] not in self.bonds:
                    logging.error("%s %s atoms are not bonded. Cannot carry on with the transformation."%(bonded[0],bonded[1]))
                    return False
        return True

    def __ctrl_length(self):
        if len(self.atomnames) != len(self.coor):
            logging.error('Topology has %s atoms, but %s coordinates is passed.' %(len(self.atomnames),len(self.coor)))
            return False
        return True

    def __ctrl_coor(self):
        if not isinstance(self.coor,np.ndarray):
            self.coor=np.array(self.coor)
        nrs,names=self.coor[:,0:1],self.coor[:,1:2]
        try:
            [float(i) for i in names]
        except ValueError:
            return True
        else:
            logging.error('Please pass the coordinates in this format: [[Nr, AtName,x,y,z],[],[]]')
            return False
        return True

    def __ctrl_range(self):
        if self.targetrange is None:
            logging.error('Either provide a single target value or provide a range using the keyword arugments targetvalue or targetrange.')
            return False
        if len(self.targetrange) != 3:
            logging.error('The target range must have 3 elements, start, end , increment')
            return False
        try:
            self.targetrange=[float(i) for i in self.targetrange]
        except ValueError:
            logging.error('The target range contains characters. Please pass only numbers.')
            return False
        return True

    def __transformcore(self,m,coor,changetype,atomlist,value):
        #RDKit mols are C++ objects, pointers to that object created. So we either do a deepy copy or create another molecule to work with temporarily, otherwise the original molecule is modified.
        nrname=coor[:,0:2]
        tmp=Chem.Mol(m)
        tmp.RemoveAllConformers()
        AllChem.EmbedMultipleConfs(tmp,1)
        funcs={'bond':Chem.rdMolTransforms.SetBondLength,'angle':Chem.rdMolTransforms.SetAngleDeg,'dihedral':Chem.rdMolTransforms.SetDihedralDeg}
        #RDKit numbers start from 0
        atomlist=[int(i)-1 for i in atomlist]
        value=float(value)
        conf=tmp.GetConformer()
        for i in range(tmp.GetNumAtoms()):
            conf.SetAtomPosition(i,[float(coor[i][2]),float(coor[i][3]),float(coor[i][4])])
        funcs[changetype](conf,*atomlist,value)
        a=conf.GetPositions()
        a=np.hstack((nrname,a))
        return(a)

    def __transform(self):
        if self.targetvalue:
            values=[self.targetvalue]
        elif self.targetrange:
            values=mc.frange(self.targetrange,rdigit=3,step=True)
        returncoor={}
        if self.writepy:
            pyoutn=self.pfbase+'_xyz.py'
            pyout=open(pyoutn,'w')
            objname='scan_'
            pyout.write('basename="%s" \n' %objname)
            pyout.write('scanrange=[')
            pyvalues=[]
            for i in values:
                i='_'.join(str(i).split('.'))
                if '-' in i:
                    i='n'.join(str(i).split('-'))
                pyvalues.append(i)
                pyout.write('"%s",' %i)
            pyout.write(']\n')
        elif self.writepdb:
            pdbns=[]
        for val in range(len(values)):
            mol=Chem.Mol(self.m)
            newcoor=self.__transformcore(mol,self.coor,self.changetype,self.scanatomnr,values[val])
            if self.returns:
                returncoor.update({pyvalues[val]:newcoor})
            else:
                if self.writepdb:
                    pdbn=self.pfbase+'_'+str(values[val])+'.pdb'
                    pdbns.append(pdbn)
                    with open(pdbn,'w') as pdbout:
                        for coor in newcoor:
                            pdbout.write(cw.crdline(coor,returntype='pdb'))
                if self.writepy:
                    pyout.write("%s%s='''\n"%(objname,pyvalues[val]))
                    pyout.write("%d %d \n" %(self.rescharge,self.multiplicity))
                    #Only underscore within objectnames
                    for coor in newcoor:
                        #The crdline returns with a new line
                        pyout.write(cw.crdline(coor,returntype='xyz'))
                    pyout.write('\nnoreorient\nnocom\n')
                    pyout.write("'''\n")
                    pyout.write("\n")
        if self.returns:
            return(returncoor)
        if self.writepy:
            pyout.close()
            return(pyoutn)
        if self.writepdb:
            return(pdbns)

def align(positions,center=False):
    positions = positions - positions.min(axis=0)
    if center:
        origin = np.array([0.,0.,0.],dtype='float32')
        origin = sum(positions)/len(positions)
        positions = positions - origin
    return positions
