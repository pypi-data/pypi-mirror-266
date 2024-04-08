from feynmodel.ufo_base_class import UFOBaseClass


class Vertex(UFOBaseClass):

    require_args = ["name", "particles", "color", "lorentz", "couplings"]

    def __init__(
        self, name, particles, color=None, lorentz=None, couplings=None, **opt
    ):

        args = (name, particles, color, lorentz, couplings)

        UFOBaseClass.__init__(self, *args, **opt)

        args = (particles, color, lorentz, couplings)

        # global all_vertices
        # all_vertices.append(self)

    def __eq__(self, other):
        return self.name == other.name
