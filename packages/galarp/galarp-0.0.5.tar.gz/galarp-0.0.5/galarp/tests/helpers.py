

class ShadowTestBase:
    name = None
    shadow = None
    show_plots = False

    xyz = None
    t = None

    def test_evaluation(self):
        eval = self.shadow.evaluate(self.xyz, self.t)
        print(len(self.xyz), eval.shape)
        assert eval is not None
        assert eval.shape[0] == len(self.xyz)


class RPWindTestBase:
    name = None
    wind = None
    show_plots = False

    t = None

    def test_init(self):
        assert self.wind is not None


class ParticleGridTestBase:
    name = "ParticleGrids"
    grid = None
    show_plots = False

    def test_init(self):
        assert self.grid is not None
        assert isinstance(self.grid.container, list) 
    
    