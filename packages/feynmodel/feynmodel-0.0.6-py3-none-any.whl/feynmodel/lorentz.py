from feynmodel.ufo_base_class import UFOBaseClass


class Lorentz(UFOBaseClass):

    require_args = ["name", "spins", "structure"]

    def __init__(self, name, spins, structure="external", **opt):
        args = (name, spins, structure)
        UFOBaseClass.__init__(self, *args, **opt)

        # global all_lorentz
        # all_lorentz.append(self)
