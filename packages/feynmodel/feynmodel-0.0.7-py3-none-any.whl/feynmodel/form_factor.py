from feynmodel.ufo_base_class import UFOBaseClass


class FormFactor(UFOBaseClass):
    require_args = ["name", "type", "value"]

    def __init__(self, name, type, value, **opt):
        args = (name, type, value)
        UFOBaseClass.__init__(self, *args, **opt)

        # global all_form_factors
        # all_form_factors.append(self)
