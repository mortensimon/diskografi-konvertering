# navn format "etternavn, fornavn (rolle);" omdannes til format "fornavn etternavn (rolle),"
def nameformat(namestring):
    fullnames = ""
    names = namestring + ";"
    while names.find(";") > 0:
        semi = names.find(";")

        # finner første navn og sletter dette fra names
        firstname = names[ : semi]

        # sjekker om dette er et navn eller et ensemble
        comma = firstname.find(",")
        if comma > 0:
            surname = firstname[ : comma] # alt før komma
            givenname = firstname[comma + 2 : ] # fornavn inkl rolle
            rolestart = givenname.find("(") # finn rollestart
            if rolestart > 0: # finnes rolle?
                role = givenname[rolestart : ]
                givenname = givenname[ : rolestart - 1]
                fullname = givenname + " " + surname + " " + role + ", "
            else:
                fullname = givenname + " " + surname + ", "
        else:
            fullname = firstname + ", "
            
        # bygger ny navnestreng
        names = names[semi + 2 : ]
        fullnames = fullnames + fullname

    # fjerner siste semikolon
    fullnames = fullnames[ : -2]
    
    if fullnames.isspace() == True:
       fullnames = ""

    return fullnames