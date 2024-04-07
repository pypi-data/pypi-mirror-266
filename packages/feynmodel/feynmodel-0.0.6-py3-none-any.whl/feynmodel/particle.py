from feynmodel.ufo_base_class import UFOBaseClass


class Particle(UFOBaseClass):
    """A standard Particle"""

    require_args = [
        "pdg_code",
        "name",
        "antiname",
        "spin",
        "color",
        "mass",
        "width",
        "texname",
        "antitexname",
        "charge",
    ]

    require_args_all = [
        "pdg_code",
        "name",
        "antiname",
        "spin",
        "color",
        "mass",
        "width",
        "texname",
        "antitexname",
        "charge",
        "line",
        "propagating",
        "goldstoneboson",
    ]

    def __init__(
        self,
        pdg_code=None,
        name=None,
        antiname=None,
        spin=-99999999999,
        color=None,
        mass=None,
        width=None,
        texname=None,
        antitexname=None,
        charge=-99999999999999999,
        line=None,
        propagating=True,
        goldstoneboson=False,
        **options
    ):

        args = (
            pdg_code,
            name,
            antiname,
            spin,
            color,
            mass,
            width,
            texname,
            antitexname,
            float(charge),
        )

        UFOBaseClass.__init__(self, *args, **options)

        # global all_particles
        # all_particles.append(self)

        self.propagating = propagating
        self.goldstoneboson = goldstoneboson

        self.selfconjugate = name == antiname
        if 1:  # not line:
            self.line = self.find_line_type()
        else:
            self.line = line

    def __eq__(self, other):
        return (self.pdg_code == other.pdg_code) and (self.name == other.name)

    def find_line_type(self):
        """find how we draw a line if not defined
        valid output: dashed/straight/wavy/curly/double/swavy/scurly
        """

        spin = self.spin
        color = self.color

        # use default
        if spin == 1:
            return "dashed"
        elif spin == 2:
            if not self.selfconjugate:
                return "straight"
            elif color == 1:
                return "swavy"
            else:
                return "scurly"
        elif spin == 3:
            if color == 1:
                return "wavy"

            else:
                return "curly"
        elif spin == 5:
            return "double"
        elif spin == -1:
            return "dotted"
        else:
            return "dashed"  # not supported yet

    def anti(self):
        if self.selfconjugate:
            raise Exception("%s has no anti particle." % self.name)
        outdic = {}
        for k, v in self.__dict__.items():
            if k not in self.require_args_all:
                outdic[k] = -v
        if self.color in [1, 8]:
            newcolor = self.color
        else:
            newcolor = -self.color

        return Particle(
            -self.pdg_code,
            self.antiname,
            self.name,
            self.spin,
            newcolor,
            self.mass,
            self.width,
            self.antitexname,
            self.texname,
            -self.charge,
            self.line,
            self.propagating,
            self.goldstoneboson,
            **outdic
        )
