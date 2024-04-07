from feynmodel.coupling import Coupling
from feynmodel.coupling_order import CouplingOrder
from feynmodel.decay import Decay
from feynmodel.function import Function
from feynmodel.lorentz import Lorentz
from feynmodel.parameter import Parameter
from feynmodel.particle import Particle
from feynmodel.vertex import Vertex


class FeynModel:
    def __init__(self, name=None):
        self.name = name
        self.particles = []
        self.vertices = []
        self.parameters = []
        self.lorentz = []
        self.couplings = []
        self.orders = []
        self.functions = []
        self.decays = []

    def add_object(self, obj):
        if isinstance(obj, Particle):
            self.add_particle(obj)
        elif isinstance(obj, Decay):
            self.add_decay(obj)
        elif isinstance(obj, Function):
            self.add_function(obj)
        elif isinstance(obj, CouplingOrder):
            self.add_order(obj)
        elif isinstance(obj, Parameter):
            self.add_parameter(obj)
        elif isinstance(obj, Coupling):
            self.add_coupling(obj)
        elif isinstance(obj, Lorentz):
            self.add_lorentz(obj)
        elif isinstance(obj, Vertex):
            self.add_vertex(obj)
        else:
            raise Exception("Unknown object type %s" % obj.__class__.__name__)

    def remove_object(self, obj):
        """
        Remove object from the model

        Contrary to the direct remove functions, this function will also remove
        all references to the object in other objects. For example, if a particle
        is removed, all vertices containing the particle will also be removed.
        """
        if isinstance(obj, Particle):
            self.remove_particle(obj)
            rmv = []
            for v in self.vertices:
                if obj in v.particles:
                    rmv += [v]
            for v in rmv:
                self.remove_vertex(v)
            rmd = []
            for d in self.decays:
                if obj == d.particle:
                    rmd += [d]
            for d in rmd:
                self.remove_decay(d)
        else:
            raise NotImplementedError("remove_object %s" % obj.__class__.__name__)

    ##############################
    # Particle related functions #
    ##############################

    def add_particle(self, particle):
        if particle not in self.particles:
            self.particles.append(particle)
        else:
            raise Exception("Particle %s already exists" % particle)

    def remove_particle(self, particle):
        if particle in self.particles:
            self.particles.remove(particle)
        else:
            raise Exception("Particle %s does not exist" % particle)

    def get_particle(self, name=None, pdg_code=None):
        """Return particle with given name or pdg_code"""
        for particle in self.particles:
            if (name is None or particle.name == name) and (
                pdg_code is None or particle.pdg_code == pdg_code
            ):
                return particle
        return None

    ##############################
    # Decay related functions    #
    ##############################

    def add_decay(self, decay):
        if decay not in self.decays:
            self.decays.append(decay)
        else:
            raise Exception("Decay %s already exists" % decay)

    def remove_decay(self, decay):
        if decay in self.decays:
            self.decays.remove(decay)
        else:
            raise Exception("Decay %s does not exist" % decay)

    ##############################
    # Function related functions #
    ##############################

    def add_function(self, function):
        if function not in self.functions:
            self.functions.append(function)
        else:
            raise Exception("Function %s already exists" % function)

    def remove_function(self, function):
        if function in self.functions:
            self.functions.remove(function)
        else:
            raise Exception("Function %s does not exist" % function)

    ##############################
    # Order related functions    #
    ##############################

    def add_order(self, order):
        if order not in self.orders:
            self.orders.append(order)
        else:
            raise Exception("Order %s already exists" % order)

    def remove_order(self, order):
        if order in self.orders:
            self.orders.remove(order)
        else:
            raise Exception("Order %s does not exist" % order)

    ##############################
    # Parameter related functions#
    ##############################

    def add_parameter(self, parameter):
        if parameter not in self.parameters:
            self.parameters.append(parameter)
        else:
            raise Exception("Parameter %s already exists" % parameter)

    def remove_parameter(self, parameter):
        if parameter in self.parameters:
            self.parameters.remove(parameter)
        else:
            raise Exception("Parameter %s does not exist" % parameter)

    def get_parameter(self, name=None):
        """Return parameter with given name"""
        for parameter in self.parameters:
            if parameter.name == name:
                return parameter
        return None

    ##############################
    # Coupling related functions #
    ##############################

    def add_coupling(self, coupling):
        if coupling not in self.couplings:
            self.couplings.append(coupling)
        else:
            raise Exception("Coupling %s already exists" % coupling)

    def remove_coupling(self, coupling):
        if coupling in self.couplings:
            self.couplings.remove(coupling)
        else:
            raise Exception("Coupling %s does not exist" % coupling)

    def get_coupling(self, name=None):
        """Return coupling with given name"""
        for coupling in self.couplings:
            if coupling.name == name:
                return coupling
        return None

    ##############################
    # Lorentz related functions  #
    ##############################

    def add_lorentz(self, lorentz):
        if lorentz not in self.lorentz:
            self.lorentz.append(lorentz)
        else:
            raise Exception("Lorentz %s already exists" % lorentz)

    def remove_lorentz(self, lorentz):
        if lorentz in self.lorentz:
            self.lorentz.remove(lorentz)
        else:
            raise Exception("Lorentz %s does not exist" % lorentz)

    def get_lorentz(self, name=None):
        """Return lorentz with given name"""
        for lorentz in self.lorentz:
            if lorentz.name == name:
                return lorentz
        return None

    ##############################
    # Vertex related functions   #
    ##############################

    def add_vertex(self, vertex):
        if vertex not in self.vertices:
            self.vertices.append(vertex)
        else:
            raise Exception("Vertex %s already exists" % vertex)

    def remove_vertex(self, vertex):
        if vertex in self.vertices:
            self.vertices.remove(vertex)
        else:
            raise Exception("Vertex %s does not exist" % vertex)

    def get_vertex(self, name=None):
        """Return vertex with given name"""
        for vertex in self.vertices:
            if vertex.name == name:
                return vertex
        return None
