from feynmodel.ufo_base_class import UFOBaseClass


class Coupling(UFOBaseClass):

    require_args = ["name", "value", "order"]

    def __init__(self, name, value, order, **opt):

        args = (name, value, order)
        UFOBaseClass.__init__(self, *args, **opt)
        # global all_couplings
        # all_couplings.append(self)
