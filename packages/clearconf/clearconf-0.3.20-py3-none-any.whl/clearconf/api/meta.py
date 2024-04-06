from .node import Node

class MetaBaseConfig(type):
    def __init__(cls, name, bases, clsdict):
        '''This executes after the configuration subclassing baseconfig
           is defined and it adds BaseConfig as a super class of all nested
           configurations'''
        super(MetaBaseConfig, cls).__init__(name, bases, clsdict)
        
        if len(cls.mro()) > 2:
            cls.__visit()
    
    def __visit(cls):
        from clearconf.api._utils.misc import (expand_name, add_parent, resolve_eval, subclass)
        from clearconf.api._utils.pickle_reduce import add_pickle_reduce

        cls._initialized = False
        
        cls._name = expand_name(cls)
        nodes = [Node(name, parent=cls) for name in dir(cls)]
        cls._nodes = nodes

        for node in nodes:
            subclass(node)
            add_parent(node) # if you add the parent before subclass an infinite loop happens somehow
            resolve_eval(node)
            # add_pickle_reduce(node)

        cls._initialized = True

    def __setattr__(cls, key, value):
        from clearconf.api._utils.misc import add_parent
        super().__setattr__(key, value)
        
        # This will let you add a baseconfig as an attribute of another while maintaining the tree
        if isinstance(value, MetaBaseConfig) and value._initialized and cls._initialized:
            node = Node(key, parent=cls, value=value)
            cls._nodes.append(node)
            add_parent(node)
