#!/usr/bin/env python
#
# Author: Patrick Hung (patrickh @caltech)
# Copyright (c) 1997-2016 California Institute of Technology.
# Copyright (c) 2016-2017 The Uncertainty Quantification Foundation.
# License: 3-clause BSD.  The full license text is available at:
#  - http://trac.mystic.cacr.caltech.edu/project/mystic/browser/mystic/LICENSE
"""
Testing the Corana parabola in 1D. Requires sam.
"""

import sam, numpy, mystic
#from test_corana import *
from mystic.solvers import fmin
from mystic.tools import getch

from mystic.models.corana import corana1d as Corana1

x = numpy.arange(-2., 2., 0.01)
y = [Corana1([c]) for c in x]

sam.put('x', x)
sam.put('y', y)
sam.eval("plot(x,y,'LineWidth',1); hold on")


for xinit in numpy.arange(0.1,2,0.1):
    sol = fmin(Corana1, [xinit], full_output=1, retall=1)
    xx = mystic.flatten_array(sol[-1])
    yy = [Corana1([c]) for c in xx]
    sam.put('xx', xx)
    sam.put('yy', yy)
    sam.eval("plot(xx,yy,'r-',xx,yy,'ko','LineWidth',2)")

sam.eval("axis([0 2 0 4])")
getch('press any key to exit')

# end of file
