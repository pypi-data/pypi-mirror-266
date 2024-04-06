import inspect
import typing

from clearconf.api.hidden import Hidden


class Node:
    
    def __init__(self, name, parent=None, value=None) -> None:
        self._name = name
        self._alias = name
        
        if parent is None:
            parent = type('parent', (), {})
            setattr(parent, name, value)
        
        self.parent = parent
        
    @property
    def value(self):
        return getattr(self.parent, self._name)
        
    @value.setter
    def value(self, new):
        setattr(self.parent, self._name, new)
        
    @property
    def name(self):
        return self._alias
    
    @name.setter
    def name(self, alias):
        self._alias = alias
        
    @property
    def is_private(self):
        return self.name.startswith('_') or '._' in self.name

    @property
    def is_hidden(self):
        from clearconf.api.base_config import BaseConfig
        return (self.name in dir(BaseConfig) or 
                self.parent.__dict__.get('__annotations__', {}).get(self.name, None) == Hidden)
    @property      
    def is_visited(self):
        from clearconf.api.base_config import BaseConfig
        return issubclass(self.value, BaseConfig)
    
    @property
    def is_config(self):
        from clearconf.api.base_config import BaseConfig
        from clearconf.api._utils.misc import find_root
        # Attr is a class who has either been defined in the same module we are considering or is a
        # subclass of BaseConfig
        return (inspect.isclass(self.value) and 
            (find_root(self.value).__module__ == self.parent.__module__ or issubclass(self.value, BaseConfig)))
        
    def __repr__(self):
        return f'clearconf.Node({self.name})'

    # def __str__(self):
    #     sel
