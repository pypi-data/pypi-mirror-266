def getExtension(filein):
    extension = filein.split('.')[-1].lower()
    return extension

def FileStatus(filein): 
    status = True
    if not os.path.exists(filein): status=False
    if os.stat(filein).st_size==0: status=False
    if os.stat(filein).st_size/(1024 * 1024)>50: status=False
    return status
