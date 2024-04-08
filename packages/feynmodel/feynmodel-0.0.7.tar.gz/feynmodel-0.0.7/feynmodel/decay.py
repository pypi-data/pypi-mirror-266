from feynmodel.ufo_base_class import UFOBaseClass


class Decay(UFOBaseClass):
    require_args = ["particle", "partial_widths"]

    def __init__(self, particle, partial_widths, **opt):
        args = (particle, partial_widths)
        UFOBaseClass.__init__(self, *args, **opt)

        # global all_decays
        # all_decays.append(self)

        # Add the information directly to the particle
        particle.partial_widths = partial_widths
