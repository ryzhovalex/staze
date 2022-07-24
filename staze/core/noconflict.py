"""Module for resolving metaclasses conflicts.

Refs:
    http://www.phyast.pitt.edu/~micheles/python/metatype.html
"""

metadic={}

def _generatemetaclass(bases,metas,priority):
    trivial=lambda m: sum([issubclass(M,m) for M in metas],m is type)
    # hackish!! m is trivial if it is 'type' or, in the case explicit
    # metaclasses are given, if it is a superclass of at least one of them
    metabs=tuple([mb for mb in map(type,bases) if not trivial(mb)])
    metabases=(metabs+metas, metas+metabs)[priority]
    if metabases in metadic: # already generated metaclass
        return metadic[metabases]
    elif not metabases: # trivial metabase
        meta=type
    elif len(metabases)==1: # single metabase
        meta=metabases[0]
    else: # multiple metabases
        metaname="_"+''.join([m.__name__ for m in metabases])
        meta=makecls()(metaname,metabases,{})
    return metadic.setdefault(metabases,meta)

def makecls(*metas,**options):
    """Class factory avoiding metatype conflicts. The invocation syntax is
    makecls(M1,M2,..,priority=1)(name,bases,dic). If the base classes have
    metaclasses conflicting within themselves or with the given metaclasses,
    it automatically generates a compatible metaclass and instantiate it.
    If priority is True, the given metaclasses have priority over the
    bases' metaclasses"""

    priority=options.get('priority',False) # default, no priority
    return lambda n,b,d: _generatemetaclass(b,metas,priority)(n,b,d)