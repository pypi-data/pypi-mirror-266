class CouplingOrder(object):
    def __init__(self, name, expansion_order, hierarchy, perturbative_expansion=0):

        # global all_orders
        # all_orders.append(self)

        self.name = name
        self.expansion_order = expansion_order
        self.hierarchy = hierarchy
