class instantiate(type):
    def __new__(cls, clsname, bases, attrs):
        return type.__new__(cls, clsname, bases, attrs)('[eval]cfg')

class Root(str, metaclass=instantiate):
    
    def __new__(cls, string):
        instance = super().__new__(cls, string)
        return instance
    
    def __getattr__(self, name):
        return type(Root)(self + '.' + name)