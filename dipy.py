#!/usr/bin/python

import re


class Container(object):
    
    def __init__(self, parent=None, automock=False):
        super(Container, self).__init__()
        self.parent = parent
        self.registry = {}
        self._automock = automock
        self._instances = []
        self._single_instances = {}
        self._invalid_names = [
            re.compile(r"_fact_list"), # Don't allow lists of factories
        ]
    
    def register(self, name, obj, single_instance=False):
        # If the object is not a type or function, add it to the instance list
        if not isinstance(obj, type) and not hasattr(obj, '__call__'):
            self._instances.append(obj)
        self.registry[name] = \
            self.registry.get(name, []) + [(obj, single_instance)]
    
    def resolve(self, type, *args):    
        # If asked for a string, resolve based on the name
        if isinstance(type, str):
            return self._create_from_str(type, *args)
        
        # Otherwise, resolve based on the named arguments for the constructor
        init_args = type.__init__.im_func.func_code.co_varnames
        resolved_args = {}
        for arg in list(init_args)[(1 + len(args)):]:
            resolved_args[arg] = self.resolve(arg)
        
        # Create, save, and return the new instance
        result = type(*args, **resolved_args)
        if hasattr(result, '__enter__'):
            result = result.__enter__()
        self._instances.append(result)
        return result
    
    def _create_from_str(self, name, *args):
        def create_helper(name, obj, single_instance):
            # If a single instance is required, create and store it
            if single_instance:
                if name not in self._single_instances: 
                    self._single_instances[name] = create_helper(name, obj, False)
                return self._single_instances[name]
            # If the object is a type, resolve that type
            elif isinstance(obj, type):
                return self.resolve(obj, *args)
            # If the object is callable, call it with the container
            elif hasattr(obj, '__call__'):
                return obj(self)
            # Otherwise, just return the registered instance
            return obj
        
        # Validate the requested name
        if not self._is_valid_name(name):
            raise DipyException(
                "The requested dependency name '%s' is not valid." % name)
                        
        # See if a list of dependencies is requested
        if name.endswith('_list'):
            if name[:-5] not in self.registry:
                raise DipyException(
                    "The requested dependency '%s' could not be located" % name)
            return [create_helper(name[:-5], obj, single_instance) 
                    for obj, single_instance in self.registry[name[:-5]]]
        
        # See if a factory is requested
        if name.endswith('_fact'):
            return lambda *args: self.resolve(name[:-5], *args)
        
        # Search through the container heirarchy looking for the dependency
        container = self
        while container:
            if name in container.registry:
                obj, is_single = container.registry[name][0]
                return create_helper(name, obj, is_single)
            container = container.parent
        
        # If mocking is enabled, create a new mock
        if self._automock:
            return Mock(name)
        
        # If no matching registration is found, raise an exception
        raise DipyException(
            "The requested dependency '%s' could not be located" % name)    
    
    def _is_valid_name(self, name):
        for regex in self._invalid_names:
            if regex.findall(name): 
                return False
        return True
    
    def __enter__(self):
        return self
    
    def __exit__(self, type, value, traceback):
        for instance in self._single_instances.values() + self._instances:
            if hasattr(instance, '__exit__'):
                instance.__exit__(type, value, traceback)


class DipyException(Exception):
    
    def __init__(self, value):
        super(DipyException, self).__init__()
        self.value = value
    
    def __str__(self):
        return self.value


class Mock(object):
    
    def __init__(self, name):
        def set_attr(name, value):
            super(Mock, self).__setattr__(name, value)
        set_attr("attrs", {})
        set_attr("name", name)
        set_attr("call_history", [])
        set_attr("call_count", 0)
    
    def __getattr__(self, name):
        if name not in self.attrs:
            self.attrs[name] = Mock(name)
        return self.attrs[name]
    
    def __setattr__(self, name, value):
        self.attrs[name] = value
    
    def __call__(self, *args, **kwargs):
        result = Mock(self.name + "_result")
        
        # Update the function call stats
        def get_attr(name):
            return super(Mock, self).__getattribute__(name)
        def set_attr(name, value):
            super(Mock, self).__setattr__(name, value)
        get_attr("call_history").append((args, kwargs, result))
        set_attr("call_count", get_attr("call_count") + 1)
        
        return result
    
    def __repr__(self):
        return "<Mock instance '%s'>" % self.name


