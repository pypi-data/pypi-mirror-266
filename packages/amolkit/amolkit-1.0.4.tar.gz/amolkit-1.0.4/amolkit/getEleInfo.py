import numpy as np
from amolkit import EleInfo as ei
from amolkit.stringmanip import stripname


cpatomlist=list(map(lambda x:x.upper(), ei.AtomOrder))
cpbiolist=list(ei.BioNametoAtomName.keys())
elementname = {v: k for k, v in ei.AtomicNumber.items()}

def bioname_to_atomname(atomname):
    bioname=ei.BioNametoAtomName.get(atomname.upper())
    return bioname

def getindex(atomlist:list,atomname):
    index=None
    try:
       index=atomlist.index(atomname[0:3].strip())
       atomname=atomname[0:3]
    except ValueError:
       try:
          index=atomlist.index(atomname[0:2].strip())
          atomname=atomname[0:2]
       except ValueError:
          try:
              index=atomlist.index(atomname[0:1].strip())
              atomname=atomname[0:1]
          except ValueError:
              index=None
              atomname=None
    return index,atomname

def atomsymbol_by_anyatomname(atomname,bio=True):
    inname=atomname
    atomname=stripname(atomname) 
    atomname=atomname.upper()
    if bio: 
        bioindex,bioname=getindex(cpbiolist,atomname)
        if bioindex:        
            atomname=ei.BioNametoAtomName.get(bioname)
            return atomname
    
    index,name=getindex(cpatomlist,atomname)
    atomname=ei.AtomOrder[index] if index else name
    if not atomname: raise NameError('Could not determine correct atomsymbol for %s'%(inname))
    return atomname

def atomicnumber_by_anyatomname(atomname,bio=True):
    atomsymbol=atomsymbol_by_anyatomname(atomname,bio)
    atomicnumber=ei.AtomicNumber.get(atomsymbol)
    return atomicnumber

def atomicmass_by_anyatomname(atomname,bio=True):
    atomsymbol=atomsymbol_by_anyatomname(atomname,bio)
    atomicmass=ei.AtomicMass.get(atomsymbol)
    return atomicmass

def atomicnumber_by_atomtype(atomtype):
    eleName=ei.AtomTypetoAtomName.get(atomtype.upper())
    if eleName:
       eleNumber=ei.AtomicNumber[eleName]
       return eleNumber
    else:  
       raise NameError("Could not find any element associated with " + atomtype) 

def atomicmass_by_atomtype(atomtype):
    eleName=ei.AtomTypetoAtomName.get(atomtype.upper())
    if eleName:
       eleMass=ei.AtomicMass[eleName]
       return (eleMass)
    else:
       raise NameError("Could not find any element associated with " + atomtype) 

def covrad_by_atomsymbol(atomname): 
    radius=ei.CovalentRadius[atomname]
    return radius

def color_by_atomsymbol(atomname): 
    color=ei.AtomColor[atomname]
    return color

def atomsymbol_by_atomicnumber(atomicnumber): #:int):
    atomsymbol=elementname[int(atomicnumber)]
    return atomsymbol

class ElementProp():
   def __init__(self, Z, radius, max_bonds, r, g, b):
      self.Z = Z
      self.radius = radius
      self.max_bonds = max_bonds
      self.color = np.array([r,g,b], dtype='float32')
   def __str__(self):
      format_string = ' '.join(['{:4d}','{:9f}','{:4d}','{:9f}'*3])
      return format_string.format(self.Z, self.radius, self.max_bonds, *self.color)

class AssignElementProp(ElementProp):
   def __init__(self): 
      self.PSE = {}
      self.ATSYM = {}
      for atsym in ei.AtomOrder:
         self.PSE[atsym.upper()] = ElementProp(ei.AtomicNumber[atsym],ei.CovalentRadius[atsym],ei.BondOrder[atsym],*ei.AtomColor[atsym])
         self.ATSYM[ei.AtomicNumber[atsym]] = atsym
