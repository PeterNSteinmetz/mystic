#! /usr/bin/env python
"""
Classes for Dirac measure data objects.
Includes point, dirac_measure, and product_measure classes.
"""
# Adapted from seesaw2d.py in branches/UQ/math/examples2/ 
# For usage example, see seesaw2d_inf_example.py .

from mystic.math.measures import impose_mean, impose_expectation
from mystic.math.measures import impose_spread, impose_variance
from mystic.math.measures import impose_weight_norm

class point(object):
  """ 1-d object with weight and position """

  def __init__(self, position, weight):
    self.weight = weight
    self.position = position
    return

  def __repr__(self):
    return "(%s @%s)" % (self.weight, self.position)

  pass


class dirac_measure(list):  #FIXME: meant to only accept points...
  """ a 1-d collection of points forming a 'discrete_measure'
  s = dirac_measure([point1, point2, ..., pointN])  
    where a point has weight and position

 queries:
  s.weights   --  returns list of weights
  s.coords  --  returns list of positions
  s.npts  --  returns the number of points
  s.mass  --  calculates sum of weights
  s.mean  --  calculates sum of weights*positions
  s.range  --  calculates |max - min| for positions
  s.var  --  calculates mean( |positions - mean(positions)|**2 )

 settings:
  s.weights = [w1, w2, ..., wn]  --  set weights
  s.coords = [x1, x2, ..., xn]  --  set positions
  s.normalize()  --  normalizes the weights to 1.0
  s.mean(R)  --  set the mean
  s.range(R)  --  set the range
  s.var(R)  --  set the variance

 notes:
  - constraints should impose that sum(weights) should be 1.0
  - assumes that s.n = len(s.coords) == len(s.weights)
"""

  def __weights(self):
    return [i.weight for i in self]

  def __positions(self):
    return [i.position for i in self]

  def __n(self):
    return len(self)

  def __mass(self):
    return sum(self.weights)
    #from mystic.math.measures import norm
    #return norm(self.weights)  # normalized by self.npts

  def __mean(self):
    from mystic.math.measures import mean
    return mean(self.coords, self.weights)

  def __range(self):
    from mystic.math.measures import spread
    return spread(self.coords)

  def __variance(self):
    from mystic.math.measures import variance
    return variance(self.coords, self.weights)

  def __set_weights(self, weights):
    for i in range(len(weights)):
      self[i].weight = weights[i]
    return

  def __set_positions(self, positions):
    for i in range(len(positions)):
      self[i].position = positions[i]
    return

  def normalize(self):
    self.coords, self.weights = impose_weight_norm(self.coords, self.weights)
    return

  def __set_mean(self, m):
    self.coords = impose_mean(m, self.coords, self.weights)
    return

  def __set_range(self, r):
    self.coords = impose_spread(r, self.coords, self.weights)
    return

  def __set_variance(self, v):
    self.coords = impose_variance(v, self.coords, self.weights)
    return

  # interface
  weights = property(__weights, __set_weights)
  coords = property(__positions, __set_positions)
  ###XXX: why not use 'points' also/instead?
  npts = property(__n )
  mass = property(__mass )
  range = property(__range, __set_range)
  mean = property(__mean, __set_mean)
  var = property(__variance, __set_variance)
  pass

class product_measure(list):  #FIXME: meant to only accept sets...
  """ a N-d product measure, a collection of dirac measures
  c = product_measure([measure1, measure2, ..., measureN])  
    where all measures are orthogonal

 queries:
  c.npts  --  returns total number of points
  c.weights   --  returns list of weights
  c.coords  --  returns list of position tuples
  c.mass  --  returns list of weight norms

 settings:
  c.coords = [(x1,y1,z1),...]  --  set positions (propagates to each set member)

 methods:
  c.pof(f)  --  calculate the probability of failure
  c.get_expect(f)  --  calculate the expectation
  c.set_expect((center,delta), f)  --  impose expectation by adjusting positions

 notes:
  - constraints impose expect (center - delta) <= E <= (center + delta)
  - constraints impose sum(weights) == 1.0 for each set
  - assumes that c.npts = len(c.coords) == len(c.weights)
  - weight wxi should be same for each (yj,zk) at xi; similarly for wyi & wzi
"""

  def __n(self):
    npts = 1
    for i in self:
      npts *= i.npts
    return npts

  def __weights(self):
    from mystic.math.measures import _pack
    weights = [i.weights for i in self]
    weights = _pack(weights)
    _weights = []
    for wts in weights:
      weight = 1.0
      for w in wts:
        weight *= w
      _weights.append(weight)
    return _weights

  def __positions(self):
    from mystic.math.measures import _pack
    coords = [i.coords for i in self]
    coords = _pack(coords)
    return coords

  def __set_positions(self, coords):
    from mystic.math.measures import _unpack
    npts = [i.npts for i in self]
    coords = _unpack(coords,npts)
    for i in range(len(coords)):
      self[i].coords = coords[i]
    return

 #def __get_center(self):
 #  return self.__center

 #def __get_delta(self):
 #  return self.__delta

  def __mass(self):
    return [self[i].mass for i in range(len(self))]

  def get_expect(self, f):
    """calculate the expectation for a given function

Inputs:
    f -- a function that takes a list and returns a number
"""
    from mystic.math.measures import expectation
    return expectation(f, self.coords, self.weights)

  def set_expect(self, (m,D), f, bounds=None, constraints=None):
    """impose a expectation on a product measure

Inputs:
    (m,D) -- tuple of expectation m and acceptable deviation D
    f -- a function that takes a list and returns a number
    bounds -- tuple of lists of bounds  (lower_bounds, upper_bounds)
    constraints -- a function that takes a nested list of N x 1D discrete
        measure positions and weights   x' = constraints(x, w)
"""
   #self.__center = m
   #self.__delta = D
    npts = [i.npts for i in self]
    self.coords = impose_expectation((m,D), f, npts, bounds, self.weights, \
                                                     constraints=constraints) 
    return

  def pof(self, f):
    """calculate probability of failure over a given function, f,
where f takes a list of (product_measure) positions and returns a single value

Inputs:
    f -- a function that returns True for 'success' and False for 'failure'
"""
    u = 0
    set = zip(self.coords, self.weights)
    for x in set:
      if f(x[0]) <= 0.0:
        u += x[1]
    return u
  # for i in range(self.npts):
  #   #if f(self.coords[i]) > 0.0:  #NOTE: f(x) > 0.0 yields prob of success
  #   if f(self.coords[i]) <= 0.0:  #NOTE: f(x) <= 0.0 yields prob of failure
  #     u += self.weights[i]
  # return u  #XXX: does this need to be normalized?
    
  def sampled_pof(self, f, npts=10000):
    """calculate probability of failure over a given function, f,
where f takes a list of (product_measure) positions and returns a single value

Inputs:
    f -- a function that returns True for 'success' and False for 'failure'
    npts -- number of points sampled from the underlying discrete measures
"""
    from mystic.math.samples import _pof_given_samples
    pts = self.support(npts)
    return _pof_given_samples(f, pts)

  def support(self, npts=10000):
    """randomly select support points from the underlying discrete measures

Inputs:
    npts -- number of points sampled from the underlying discrete measures

Returns:
    pts -- a nested list of len(prod_measure) lists, each of len(npts)
"""
    from mystic.math.measures import weighted_select as _select
    pts = []
    for i in range(npts):
      # for a single trial, select coords from all sets
      pts.append( [_select(set.coords, set.weights) for set in self] )

    # convert pts to len(prod_meas) lists, each of len(npts)
    from numpy import transpose
    return transpose(pts)  #XXX: assumes 'coords' is a list of floats

 #__center = None
 #__delta = None

  # interface
  npts = property(__n )
  weights = property(__weights )
  coords = property(__positions, __set_positions )
 #center = property(__get_center ) #FIXME: remove c.center and c.delta... or
 #delta = property(__get_delta )   #       replace with c._params (e.g. (m,D))
 #expect = property(__expect, __set_expect )
  mass = property(__mass )
  pass


#---------------------------------------------
# creators and destructors from parameter list

def _mimic(samples, weights):
  """Generate a product_measure object from a list N product measure
positions and a list of N weights. The resulting product measure will
mimic the original product measure's statistics, but be larger in size.

For example:
    >>> smp = [[-6,3,6],[-2,4],[1]]
    >>> wts = [[.4,.2,.4],[.5,.5],[1.]]
    >>> c = compose(samples, weights)
    >>> d = _mimic(c.coords, c.weights)
    >>> c[0].mean == d[0].mean
    True
    >>> c[1].range == d[1].range
    True
    >>> c.npts == d.npts
    False
    >>> c.npts == d[0].npts
    True
"""
  x = zip(*samples)                     # 'mimic' to a nested list
  w = [weights for i in range(len(x))]  # 'mimic' to a nested list
  return compose(x,w)


def compose(samples, weights):
  """Generate a product_measure object from a nested list of N x 1D
discrete measure positions and a nested list of N x 1D weights."""
  total = []
  for i in range(len(samples)):
    next = dirac_measure()
    for j in range(len(samples[i])):
      next.append(point( samples[i][j], weights[i][j] ))
    total.append(next)
  c = product_measure(total)
  return c


def decompose(c):
  """Decomposes a product_measure object into a nested list of
N x 1D discrete measure positions and a nested list of N x 1D weights."""
  from mystic.math.measures import _nested_split
  npts = [set.npts for set in c]
  w, x = _nested_split(flatten(c), npts)
  return x, w


def unflatten(params, npts):
  """Map a list of random variables to N x 1D discrete measures
in a product_measure object."""
  from mystic.math.measures import _nested_split
  w, x = _nested_split(params, npts)
  return compose(x, w)


def flatten(c):
  """Flattens a product_measure object into a list."""
  rv = []
  for i in range(len(c)):
    rv.append(c[i].weights)
    rv.append(c[i].coords)
  # now flatten list of lists into just a list
  from itertools import chain
  rv = list(chain(*rv))
  return rv


# EOF