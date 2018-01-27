def jsonListFind( l, k, v, exact=True ):
    # l - list of json objects
    # k - key, must be in json object
    # v - value to find
    # exact match or just contains
    r = {}
    for i in l:
        #print( "I ", i, k)
        #print( dir( i ) )
        #print( "DN2 ", getattr( i, k ) )
        if getattr( i, k ) == v or (not exact and getattr( i, k ).find( v ) != -1) :
            r = i
            break
    return r

def jsonListFind2( l, k, v ):
    # l - list of json objects
    # k - key, must be in json object
    # v - value to find
    r = [ i for i in l if getattr( i, k ) == v ]
    if len( r ) > 0:
        return r[ 0 ]
    else:
        return {}

def jsonListFindAll( l, k, v ):
    # l - list of json objects
    # k - key, must be in json object
    # v - value to find
    r = []
    for i in l:
        if getattr( i, k ) == v:
            r.append( i )
    return r
