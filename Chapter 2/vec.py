# Copyright 2013 Philip N. Klein
#Includes all code for the functions, i.e. solution to part of hw01

def getitem(v,k):
    """
    Return the value of entry d in v.
    Be sure getitem(v,d) returns 0 if d is not represented in v.f.

    >>> v = Vec({'a','b','c', 'd'},{'a':2,'c':1,'d':3})
    >>> v['d']
    3
    >>> v['b']
    0
    """
    pass

def setitem(v,k,val):
    """
    Set the element of v with label d to be val.
    setitem(v,d,val) should set the value for key d even if d
    is not previously represented in v.f.

    >>> v = Vec({'a', 'b', 'c'}, {'b':0})
    >>> v['b'] = 5
    >>> v['b']
    5
    >>> v['a'] = 1
    >>> v['a']
    1
    """
    pass

def equal(u,v):
    """
    Return true iff u is equal to v.
    Because of sparse representation, it is not enough to compare dictionaries

    >>> Vec({'a', 'b', 'c'}, {'a':0}) == Vec({'a', 'b', 'c'}, {'b':0})
    True

    Be sure that equal(u, v) check equalities for all keys from u.f and v.f even if
    some keys in u.f do not exist in v.f (or vice versa)

    >>> Vec({'x','y','z'},{'y':1,'x':2}) == Vec({'x','y','z'},{'y':1,'z':0})
    False
    >>> Vec({'a','b','c'}, {'a':0,'c':1}) == Vec({'a','b','c'}, {'a':0,'c':1,'b':4})
    False
    >>> Vec({'a','b','c'}, {'a':0,'c':1,'b':4}) == Vec({'a','b','c'}, {'a':0,'c':1})
    False

    The keys matter:
    >>> Vec({'a','b'},{'a':1}) == Vec({'a','b'},{'b':1})
    False

    The values matter:
    >>> Vec({'a','b'},{'a':1}) == Vec({'a','b'},{'a':2})
    False

    """
    assert u.D == v.D
    pass

def add(u,v):
    """
    Returns the sum of the two vectors.
    Make sure to add together values for all keys from u.f and v.f even if some keys in u.f do not
    exist in v.f (or vice versa)

    >>> a = Vec({'a','e','i','o','u'}, {'a':0,'e':1,'i':2})
    >>> b = Vec({'a','e','i','o','u'}, {'o':4,'u':7})
    >>> c = Vec({'a','e','i','o','u'}, {'a':0,'e':1,'i':2,'o':4,'u':7})
    >>> a + b == c
    True
    >>> d = Vec({'x','y','z'}, {'x':2,'y':1})
    >>> e = Vec({'x','y','z'}, {'z':4,'y':-1})
    >>> f = Vec({'x','y','z'}, {'x':2,'y':0,'z':4})
    >>> d + e == f
    True
    >>> b + Vec({'a','e','i','o','u'}, {}) == b
    True
    """
    assert u.D == v.D
    pass

def dot(u,v):
    """
    Returns the dot product of the two vectors.

    >>> u1 = Vec({'a','b'}, {'a':1, 'b':2})
    >>> u2 = Vec({'a','b'}, {'b':2, 'a':1})
    >>> u1*u2
    5
    >>> v1 = Vec({'p','q','r','s'}, {'p':2,'s':3,'q':-1,'r':0})
    >>> v2 = Vec({'p','q','r','s'}, {'p':-2,'r':5})
    >>> v1*v2
    -4
    >>> w1 = Vec({'a','b','c'}, {'a':2,'b':3,'c':4})
    >>> w2 = Vec({'a','b','c'}, {'a':12,'b':8,'c':6})
    >>> w1*w2
    72

    The pairwise products should not be collected in a set before summing
    because a set eliminates duplicates
    >>> v1 = Vec({1, 2}, {1 : 3, 2 : 6})
    >>> v2 = Vec({1, 2}, {1 : 2, 2 : 1})
    >>> v1 * v2
    12
    """
    assert u.D == v.D
    pass

def scalar_mul(v, alpha):
    """
   Returns the scalar-vector product alpha times v.

   >>> zero = Vec({'x','y','z','w'}, {})
   >>> u = Vec({'x','y','z','w'},{'x':1,'y':2,'z':3,'w':4})
   >>> 0*u == zero
   True
   >>> 1*u == u
   True
   >>> 0.5*u == Vec({'x','y','z','w'},{'x':0.5,'y':1,'z':1.5,'w':2})
   True
    """
    pass

def neg(v):
    """
    Returns the negation of a vector.

    >>> u = Vec({2,4,6,8},{2:1,4:2,6:3,8:4})
    >>> neg(u)
    Vec({8, 2, 4, 6},{8: -4, 2: -1, 4: -2, 6: -3})
    """
    pass

###############################################################################################################################

class Vec:
    """
    A vector has two fields:
    D - the domain (a set)
    f - a dictionary mapping (some) domain elements to field elements
        elements of D not appearing in f are implicitly mapped to zero
    """
    def __init__(self, labels = set(), function = {}):
        self.D = labels
        self.f = function

    __getitem__ = getitem
    __setitem__ = setitem
    __neg__ = neg
    __rmul__ = scalar_mul #if left arg of * is primitive, assume it's a scalar

    def __mul__(self,other):
        #If other is a vector, returns the dot product of self and other
        if isinstance(other, Vec):
            return dot(self,other)
        else:
            return NotImplemented  #  Will cause other.__rmul__(self) to be invoked

    def __truediv__(self,other):  # Scalar division
        return (1/other)*self

    __add__ = add

    def __radd__(self, other):
        "Hack to allow sum(...) to work with vectors"
        if other == 0:
            return self

    def __sub__(a,b):
        "Returns a vector which is the difference of a and b."
        return a+(-b)

    __eq__ = equal

    def __str__(v):
        "pretty-printing"
        D_list = sorted(v.D, key=repr)
        numdec = 3
        wd = dict([(k,(1+max(len(str(k)), len('{0:.{1}G}'.format(v[k], numdec))))) if isinstance(v[k], int) or isinstance(v[k], float) else (k,(1+max(len(str(k)), len(str(v[k]))))) for k in D_list])
        # w = 1+max([len(str(k)) for k in D_list]+[len('{0:.{1}G}'.format(value,numdec)) for value in v.f.values()])
        s1 = ''.join(['{0:>{1}}'.format(k,wd[k]) for k in D_list])
        s2 = ''.join(['{0:>{1}.{2}G}'.format(v[k],wd[k],numdec) if isinstance(v[k], int) or isinstance(v[k], float) else '{0:>{1}}'.format(v[k], wd[k]) for k in D_list])
        return "\n" + s1 + "\n" + '-'*sum(wd.values()) +"\n" + s2

    def __repr__(self):
        return "Vec(" + str(self.D) + "," + str(self.f) + ")"

    def copy(self):
        "Don't make a new copy of the domain D"
        return Vec(self.D, self.f.copy())
