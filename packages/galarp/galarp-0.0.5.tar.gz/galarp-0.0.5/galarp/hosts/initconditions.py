

class InitConditions:
    """ Container for a satellite's initial conditions."""
    def __init__(self, pos=None, vel=None):
        self.pos = pos
        self.vel = vel

    def __repr__(self):
        return f"InitConditions(pos={self.pos}, vel={self.vel})"

