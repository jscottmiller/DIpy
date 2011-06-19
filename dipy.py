#!/usr/bin/python

from re import compile


class Container(object):
    
    def __init__(self, parent=None, autostub=False):
        super(Container, self).__init__()
        self.parent = parent
        self.registry = {}
        self._autostub = autostub
        self._instances = []
        self._single_instances = {}
    
    def register(self, name, obj, single_instance=False, locally_owned=True):
        """ Register the specified object with the given name.

        Keyword arguments:
        single_instace -- At most one instance is to be created (default False)
        locally_owned -- Instances are owned by the container on which they
        were resolved (default True)
        """
        # If the object is not a type or function, add it to the instance list
        if not isinstance(obj, type) and not type(obj) == type(lambda: 1):
            self._add_instance(obj)
        self.registry.setdefault(name, []).append((obj, single_instance, locally_owned))
    
    def resolve(self, type, *args):
        """ Resolve the component named 'type' from the container. """
        if not isinstance(type, str):
            raise DipyException("Resolve must be passed a string argument")
        return self._resolve_from_str(type, self, *args)
    
    def _resolve_from_str(self, name, request_scope, *args):
        # Validate the requested name
        if name.endswith("_fact_list"):
            raise DipyException(
                "The requested dependency name '%s' is not valid." % name)
                        
        # See if a list of dependencies is requested
        if name.endswith('_list'):
            if name[:-5] not in self.registry:
                raise DipyException(
                    "The requested dependency '%s' could not be located" % name)
            return [(request_scope if locally_owned else self)._create_instance(
                        name[:-5], obj, single_instance, *args)
                    for obj, single_instance, locally_owned in self.registry[name[:-5]]]
        
        # See if a factory is requested
        if name.endswith('_fact'):
            return lambda *args: self._resolve_from_str(name[:-5], request_scope, *args)
        
        # If the dependency is registered in the current container, create the instance
        if name in self.registry:
            obj, single_instance, locally_owned = self.registry[name][0]
            owner = request_scope if locally_owned else self
            return owner._create_instance(name, obj, single_instance, *args)

        # Search through the container heirarchy looking for the dependency
        if self.parent:
            try:
                return self.parent._resolve_from_str(name, request_scope, *args)
            except DipyException:
                pass
        
        # If stubbing is enabled, create a new stub
        if self._autostub:
            return Stub(name)
        
        # If no matching registration is found, raise an exception
        raise DipyException(
            "The requested dependency '%s' could not be located" % name)    

    def _create_instance(self, name, obj, single_instance, *args):
        # If a single instance is required, create and store it
        if single_instance:
            if name not in self._single_instances: 
                self._single_instances[name] = self._create_instance(name, obj, False, *args)
            return self._single_instances[name]
        # If the object is a type, resolve that type
        elif isinstance(obj, type):
            # Create instance based on the named arguments for the constructor
            c = obj.__init__.im_func.func_code
            init_args = c.co_varnames[:c.co_argcount]
            resolved_args = {}
            for arg in list(init_args)[(1 + len(args)):]:
                resolved_args[arg] = self._resolve_from_str(arg, self)
            instance = obj(*args, **resolved_args)
            return self._add_instance(instance)
        # If the object is a function, call it with the container
        elif type(obj) == type(lambda: 1):
            instance = obj(self)
            return self._add_instance(instance)
        # Otherwise, just return the registered instance
        return obj

    def _add_instance(self, obj):
        if hasattr(obj, '__enter__'):
            obj = obj.__enter__()
        self._instances.append(obj)
        return obj
    
    def __enter__(self):
        return self
    
    def __exit__(self, type, value, traceback):
        for instance in self._instances:
            if hasattr(instance, '__exit__'):
                instance.__exit__(type, value, traceback)


class DipyException(Exception):
    
    def __init__(self, value):
        super(DipyException, self).__init__()
        self.value = value
    
    def __str__(self):
        return self.value


def container_resolved(container):
    def wrap(f):
        def call(*args, **kwargs):
            with Container(parent=container) as request:
                c = f.func_code
                func_args = c.co_varnames[:c.co_argcount]
                for name in func_args[len(args):]:
                    if name in kwargs: continue
                    kwargs[name] = request.resolve(name)
                return f(*args, **kwargs)
        return call
    return wrap


class Stub(object):
    
    def __init__(self, name):
        def set_attr(name, value):
            super(Stub, self).__setattr__(name, value)
        set_attr("stub_attrs", {})
        set_attr("stub_name", name)
        set_attr("call_history", [])
        set_attr("call_count", 0)
    
    def __getattr__(self, name):
        if name not in self.stub_attrs:
            self.stub_attrs[name] = Stub(name)
        return self.stub_attrs[name]
    
    def __setattr__(self, name, value):
        self.stub_attrs[name] = value
    
    def __call__(self, *args, **kwargs):
        result = Stub(self.stub_name + "_result")
        
        # Update the function call stats
        def get_attr(name):
            return super(Stub, self).__getattribute__(name)
        def set_attr(name, value):
            super(Stub, self).__setattr__(name, value)
        get_attr("call_history").append((args, kwargs, result))
        set_attr("call_count", get_attr("call_count") + 1)
        
        return result
    
    def __repr__(self):
        return "<Stub instance '%s'>" % self.stub_name


