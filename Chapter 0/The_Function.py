# version code 0d1e4db3d840
# Please fill out this stencil and submit using the provided submission script.





## 1: (Problem 0.8.3) Tuple Sum
def tuple_sum(A, B):
    '''
    Input:
      -A: a list of tuples
      -B: a list of tuples
    Output:
      -list of pairs (x,y) in which the first element of the
      ith pair is the sum of the first element of the ith pair in
      A and the first element of the ith pair in B
    Examples:
    >>> tuple_sum([(1,2), (10,20)],[(3,4), (30,40)])
    [(4,6), (40,60)]
    '''
    return [(A[i][0]+B[i][0],A[i][1]+B[i][1]) for i in range(len(A))]



## 2: (Problem 0.8.4) Inverse Dictionary
def inv_dict(d):
    '''
    Input:
      -d: dictionary representing an invertible function f
    Output:
      -dictionary representing the inverse of f, the returned dictionary's
       keys are the values of d and its values are the keys of d
    Examples:
    >>> inv_dict({'thank you': 'merci', 'goodbye':  'au revoir'})
    {'merci':'thank you', 'au revoir':'goodbye'}]
    '''
    return {d[key]:key for key in d}


## 3: (Problem 0.8.5) Nested Comprehension
def row(p, n):
    '''
    Input:
      -p: a number
      -n: a number
    Output:
      - n-element list such that element i is p+i
    Examples:
    >>> row(10,4)
    [10, 11, 12, 13]
    '''
    return list(range(p,p+n))

comprehension_with_row = [row(i,20) for i in range(15)]

comprehension_without_row = [list(range(i,i+20)) for i in range(15)]
#Jared:What's wrong here??

#(0.8.6) Yes, 1-1 and onto
#(0.8.7) No, not onto.  It can be made invertible by expanding the domain.

## 4: (Problem 0.8.10) Probability_1
# f(x)=x+1, Domain={1,2,3,4,5,6}
# pr(1)=.5
# pr(2)=.2
# pr(3)=pr(5)=pr(6)=.1

Pr_f_is_even = .5+.1+.1
Pr_f_is_odd  = .2+.1



## 5: (Problem 0.8.11) Probability_2
# {1,4,7} -> 1
# {2,5} -> 2
# {3,6} -> 3
# pr(1)=pr(2)=pr(3)=.2
# pr(4)=pr(5)=pr(6)=pr(7)=.1

Pr_g_is_1    = .2+.1+.1
Pr_g_is_0or2 = 1 - Pr_g_is_1

