class Function(object):
    def __init__(self, name, arguments, expr):

        # global all_functions
        # all_functions.append(self)

        self.name = name
        self.arguments = arguments
        self.expr = expr

    def __call__(self, *opt):

        for i, arg in enumerate(self.arguments):
            exec("%s = %s" % (arg, opt[i]))

        return eval(self.expr)
