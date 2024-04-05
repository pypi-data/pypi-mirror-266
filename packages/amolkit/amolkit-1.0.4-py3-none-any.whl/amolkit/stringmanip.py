def getPenaltyfromString(comment):
    #Penalty is in comments. Its value is usually provided after word "penalty"
    #Will be sucessful if comment is penalty x.xx or penalty= x.xx or penalty = x.xx
    penalty = None
    cmtuplist = comment.upper().split()
    cmtuplist = list(map(lambda x:x[0:7],cmtuplist))
    cmtlist = comment.split()
    if "PENALTY" in cmtuplist:
        penpos = cmtuplist.index("PENALTY")
        findpenalty = cmtlist[penpos:] 
        try:
            penalty = round(float(findpenalty[1]),4)
            comment = " ".join(cmtlist[0:penpos]+cmtlist[penpos+2:])
        except (ValueError,IndexError):
            try:
                penalty = round(float(findpenalty[2]),4)
                comment = " ".join(cmtlist[0:penpos]+cmtlist[penpos+3:])
            except (ValueError,IndexError):
                penalty = None
    return penalty,comment

def removeSym(name):
    name = re.sub('[^A-Za-z0-9]+', '', name)
    name = name[0:6].strip()
    if len(name) < 4: name=name+"".join(["F"]*(4-len(name))) 
    return (name)

def stripname(atomname):
    """
    This function extracts first set of continous alphabetic characters from atomname.
    Replaces all special characters by 0. Skips any digit before alphabetic character.
    Trims the atomname till next occurance of digit, if any.
    Warning: If atomname consists of only symbols and numbers, function will return blank
    """

    import re

    tmpatomname=re.sub('[^A-Za-z0-9]+', '0', atomname)
    charfound=False

    for i,x in enumerate(tmpatomname):
        if x.isdigit() and not charfound:
            start = i
            end = i 
            continue
        elif not x.isdigit() and not charfound:
            start = i
            end = i + 1
            charfound=True
        elif not x.isdigit() and charfound:
            end = i + 1
        elif x.isdigit() and charfound:
            end = i 
            break

    atomname=tmpatomname[start:end]
    return (atomname)

def renumber(prevname,bio=True):
    #atomsymbol=atomsymbol_by_anyatomname(atomname,bio)
    #atomname=list(map(lambda x:gei.atomsymbol_by_anyatomname(x[0:4].strip(),bio),prevname))
    atomname=list(map(lambda x:x[0:4].strip(),prevname))
    collect={}
    newname=[None]*len(atomname)
    for i,a in enumerate(atomname):
        if a not in collect.keys():
            collect[a]=[i]
        else:
            collect[a].append(i) 
    for key,value in collect.items():
        i=0
        if len(value)==1: 
            newname[value[0]]=key
            continue
        if len(str(len(value)))>=5:
            raise Exception("Cannot handle molecules with more than 9999 non-unique atom names")
        if len(key)+len(str(len(value)))>5:
            trunc=5-len(str(len(value)))
            #print (trunc)
            newkey=key[0:trunc]
            if newkey in collect.keys():
                i=len(collect[newkey])
        else:
            newkey=key
        for v in value:
            i=i+1
            newname[v]=newkey+str(i)
                   
    return newname       

def updateAtomNames(iatomnames):
    update_names=renumber(list(iatomnames.values()))
    for i,nam in enumerate(update_names):
        iatomnames[i+1]=nam
    return iatomnames

