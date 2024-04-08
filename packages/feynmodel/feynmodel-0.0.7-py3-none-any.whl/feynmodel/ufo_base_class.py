class UFOBaseClass(object):
    """The class from which all FeynRules classes are derived."""

    require_args = []

    def __init__(self, *args, **options):
        assert len(self.require_args) == len(args)
        for i, name in enumerate(self.require_args):
            setattr(self, name, args[i])

        for (option, value) in options.items():
            setattr(self, option, value)

    def get(self, name):
        return getattr(self, name)

    def set(self, name, value):
        setattr(self, name, value)

    def get_all(self):
        """Return a dictionary containing all the information of the object"""
        return self.__dict__

    def __str__(self):
        return self.name

    def nice_string(self):
        """return string with the full information"""
        return "\n".join(
            ["%s \t: %s" % (name, value) for name, value in self.__dict__.items()]
        )

    def __repr__(self):
        replacements = [
            ("+", "__plus__"),
            ("-", "__minus__"),
            ("@", "__at__"),
            ("!", "__exclam__"),
            ("?", "__quest__"),
            ("*", "__star__"),
            ("~", "__tilde__"),
        ]
        text = self.name
        for orig, sub in replacements:
            text = text.replace(orig, sub)
        return text
