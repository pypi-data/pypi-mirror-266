import numpy as np

from .helpers import ShadowTestBase
from .. import shadows 

class TestUniformShadow(ShadowTestBase):
    shadow = shadows.UniformShadow()
    xyz = np.array([[0, 0, 0], [1, 1, 1], [2, 2, 2]])
    t = 0

class TestExponentialShadow(ShadowTestBase):
    shadow = shadows.ExponentialShadow()
    xyz = np.array([[0, 0, 0], [1, 1, 1], [2, 2, 2]])
    t = 0

class TestEdgeOnShadow(ShadowTestBase):
    shadow = shadows.EdgeOnShadow()
    xyz = np.array([[0, 0, 0], [1, 1, 1], [2, 2, 2]])
    t = 0
    