

class _NestedClassGetter(object):
    # https://stackoverflow.com/questions/1947904/how-can-i-pickle-a-dynamically-created-nested-class-in-python/11493777#11493777
    # I can't reproduce the reason why this is required easily. However using torchdata with multiple workers can trigger it
    """
    When called with the containing class as the first argument, 
    and the name of the nested class as the second argument,
    returns an instance of the nested class.
    """
    def __call__(self, containing_class, class_name):
        nested_class = getattr(containing_class, class_name)

        # make an instance of a simple object (this one will do), for which we can change the
        # __class__ later on.
        nested_instance = _NestedClassGetter()

        # set the class of the instance, the __init__ will never be called on the class
        # but the original state will be set later on by pickle.
        nested_instance.__class__ = nested_class
        return nested_instance


def add_pickle_reduce(node):
    if not node.is_config or node.is_visited or node.is_hidden or node.is_private:
        return
    
    def _pickle_reduce(self):
        # return a class which can return this class when called with the 
        # appropriate tuple of arguments
        state = self.__dict__.copy()
        return (_NestedClassGetter(), (node.parent, self.__class__.__name__, ), state)
    setattr(node.value, '__reduce__', _pickle_reduce)