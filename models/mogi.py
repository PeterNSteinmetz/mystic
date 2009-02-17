#!/usr/bin/env python

"""
References:

[3] Mogi, K. Relations between the eruptions of various
volcanoes and the deformations of the ground surfaces around them, 
Bull. Earthquake. Res. Inst., 36, 99-134, 1958.
"""
from poly import AbstractModel

from numpy import sum as numpysum
from numpy import array, pi

class Mogi(AbstractModel):
    """
Computes surface displacements Ux, Uy, Uz in meters from a point spherical
pressure source in an elastic half space [3].
    """

    def __init__(self,name='mogi',metric=lambda x: numpysum(x*x),sigma=1.0):
        AbstractModel.__init__(self,name,metric,sigma)
        return

    def evaluate(self,coeffs,evalpts):
        """evaluate a single Mogi peak over a 2D (2 by N) numpy array of evalpts
coeffs = (x0,y0,z0,dV)"""
        x0,y0,z0,dV = coeffs
        dx = evalpts[0,:] - x0
        dy = evalpts[1,:] - y0
        dz = 0 - z0
        c = dV * 3. / 4. * pi
        # or equivalently c= (3/4) a^3 dP / rigidity
        # where a = sphere radius, dP = delta Pressure
        r2 = dx*dx + dy*dy + dz*dz
        C = c / pow(r2, 1.5)
        return array((C*dx,C*dy,C*dz))

    def ForwardFactory(self,coeffs):
        """generates a mogi source instance from a list of coefficients"""
        x0,y0,z0,dV = coeffs
        def forward_mogi(evalpts):
            """a single Mogi peak over a 2D (2 by N) numpy array
with (x0,y0,z0,dV) = (%s,%s,%s,%s)""" % (x0,y0,z0,dV)
            return self.evaluate((x0,y0,z0,dV),evalpts)
        return forward_mogi

    #FIXME: continue refactoring from test_mogi*.py...
    def CostFactory(self,target,pts):
        """generates a cost function instance from lists of coefficients & evaluation points"""
        raise NotImplementedError, "cost function not implemented"

    #FIXME: continue refactoring from test_mogi*.py...
    def CostFactory2(self,pts,datapts,nparams):
        """generates a cost function instance from datapoints & evaluation points"""
        raise NotImplementedError, "cost function not implemented"

    pass
 

# prepared instances
mogi = Mogi()

# End of file
