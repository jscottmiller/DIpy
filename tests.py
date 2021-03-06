#!/usr/bin/python

from unittest import TestCase, main
from dipy import Container, Stub, DipyException, container_resolved


#--- Tests and related classes for the IOC container

class ContainerTests(TestCase):
    
    def test_can_resolve_simple_class(self):
        c = Container()
        
        # Register the target class
        c.register("component", ComponentWithNoDependencies)
        
        # Resolve the components
        comp1 = c.resolve("component")
        comp2 = c.resolve("component")
        
        # Verify the correct objects were returned
        self.assertEqual(type(comp1), ComponentWithNoDependencies)
        self.assertEqual(type(comp2), ComponentWithNoDependencies)
        self.assertNotEqual(comp1, comp2)

    def test_can_resolve_from_decorated_func(self):
        c = Container()
        
        # Register the target class
        c.register("component", ComponentWithNoDependencies)

        # Declare a wrapped function with a component dependency
        f = container_resolved(c)(lambda component: component)

        # Resolve the components
        comp1 = f()
        comp2 = f()
        
        # Verify the correct objects were returned
        self.assertEqual(type(comp1), ComponentWithNoDependencies)
        self.assertEqual(type(comp2), ComponentWithNoDependencies)
        self.assertNotEqual(comp1, comp2)

    def test_cannot_resolve_from_type(self):
        c = Container()
        
        # Register the target class
        c.register("component", ComponentWithNoDependencies)
        
        # Resolve the component by type should fail
        self.assertRaises(DipyException, lambda: c.resolve(ComponentWithNoDependencies))
    
    def test_can_exception_format_message(self):
        # Create the exception
        message = "some exception message"
        e = DipyException(message)
        
        # Verify the string representation is the message
        self.assertEqual(str(e), message)
    
    def test_cannot_resolve_nonregistered_name(self):
        c = Container()
        
        # Register a class with a dependency, but not its dependent
        c.register("component", ComponentWithOneDependency)
        
        # Resolving the component should fail
        self.assertRaises(DipyException, lambda: c.resolve("component"))
    
    def test_cannot_resolve_nonregistered_list(self):
        c = Container()
        
        # Register a class with a dependency, but not its dependent
        c.register("component", ComponentWithListDependency)
        
        # Resolving the component should fail
        self.assertRaises(DipyException, lambda: c.resolve("component"))
    
    def test_can_resolve_instance(self):
        c = Container()
        
        # Register the target class
        c.register("component", ComponentWithNoDependencies())
        
        # Resolve the component twice
        comp1 = c.resolve("component")
        comp2 = c.resolve("component")
        
        # Verify the same objects were returned
        self.assertEqual(type(comp1), ComponentWithNoDependencies)
        self.assertEqual(type(comp2), ComponentWithNoDependencies)
        self.assertEqual(comp1, comp2)
    
    def test_can_resolve_single_instance(self):
        c = Container()
        
        # Register a single instance component with one dependency
        c.register("component", ComponentWithOneDependency, single_instance=True)
        c.register("widget", ComponentWithNoDependencies)
        
        # Resolve the component twice
        comp1 = c.resolve("component")
        comp2 = c.resolve("component")
        
        # Verify that the same components were returned and their dependencies are different
        self.assertEqual(comp1, comp2)
        self.assertEqual(type(comp1.widget), ComponentWithNoDependencies)
        self.assertEqual(type(comp2.widget), ComponentWithNoDependencies)
        self.assertEqual(comp1.widget, comp2.widget)
    
    def test_can_resolve_single_instance_list(self):
        c = Container()
        
        # Register a single instance and a component that requires a list
        c.register("component", ComponentWithListDependency)
        c.register("widget", ComponentWithNoDependencies, single_instance=True)
        
        # Resolve the component twice
        comp1 = c.resolve("component")
        comp2 = c.resolve("component")
        
        # Verify that the common dependency is the same instance
        self.assertNotEqual(comp1, comp2)
        self.assertEqual(type(comp1.widget_list), list)
        self.assertEqual(type(comp2.widget_list), list)
        self.assertEqual(len(comp1.widget_list), 1)
        self.assertEqual(len(comp2.widget_list), 1)
        self.assertEqual(comp1.widget_list[0], comp2.widget_list[0])
    
    def test_can_resolve_one_dependency(self):
        c = Container()
        
        # Register a class with a dependency and its dependent
        c.register("component", ComponentWithOneDependency)
        c.register("widget", ComponentWithNoDependencies)
        
        # Resolve the component
        comp1 = c.resolve("component")
        
        # Verify that the component has the correct dependency set
        self.assertNotEqual(comp1.widget, None)
        self.assertEqual(type(comp1.widget), ComponentWithNoDependencies)
    
    def test_can_resolve_list_dependency(self):
        c = Container()
        
        # Register a class with a list dependency as well as some instances
        c.register("component", ComponentWithListDependency)
        c.register("widget", ComponentWithNoDependencies)
        c.register("widget", ComponentWithNoDependencies)
        
        # Resolve the list-dependent class
        comp1 = c.resolve("component")
        
        # Verify that the component has the correct list member set
        self.assertNotEqual(comp1.widget_list, None)
        self.assertEqual(type(comp1.widget_list), list)
        self.assertEqual(len(comp1.widget_list), 2)
        for widget in comp1.widget_list:
            self.assertEqual(type(widget), ComponentWithNoDependencies)
        
    def test_can_resolve_factory_dependency(self):
        c = Container()
        
        # Register a component with a factory dependency
        c.register("component", ComponentWithFactoryDependency)
        c.register("widget", ComponentWithNoDependencies)
        
        # Resolve the component
        comp1 = c.resolve("component")
        
        # Verify the state of the component
        self.assertNotEqual(comp1.widget_fact, None)
        self.assertTrue(hasattr(comp1.widget_fact, '__call__'))
        dep1 = comp1.widget_fact()
        dep2 = comp1.widget_fact()
        self.assertEqual(type(dep1), ComponentWithNoDependencies)
        self.assertEqual(type(dep2), ComponentWithNoDependencies)
        self.assertNotEqual(dep1, dep2)
    
    def test_can_resolve_factory_dependency_with_arg(self):
        c = Container()
        
        # Register a component with a factory dependency
        c.register("component", ComponentWithFactoryDependency)
        c.register("widget", ComponentWithArgument)
        
        # Resolve the component
        comp1 = c.resolve("component")
        
        # Verify that the argements to the factory function are applied
        # to the dependency's constructor
        self.assertNotEqual(comp1.widget_fact, None)
        self.assertTrue(hasattr(comp1.widget_fact, '__call__'))
        result = comp1.widget_fact(1)
        self.assertEqual(type(result), ComponentWithArgument)
        self.assertEqual(result.arg, 1)
    
    def test_can_resolve_func_registration(self):
        c = Container()

        # Register a class with a dependency and its dependent
        c.register("component", ComponentWithOneDependency)
        c.register("widget", lambda c: ComponentWithNoDependencies())

        # Resolve the component
        comp1 = c.resolve("component")

        # Verify that the component has the correct dependency set
        self.assertNotEqual(comp1.widget, None)
        self.assertEqual(type(comp1.widget), ComponentWithNoDependencies)

    def test_can_resolve_owned_registration(self):
        with Container() as c:
            # Register a class with a owned dependency and a dependent with a guard
            c.register("component", ComponentWithOwnedDependency)
            c.register("widget", ComponentWithGaurd)

            # Resolve the component
            comp = c.resolve("component")

            # Verify that the dependent exists and __enter__ was not called
            self.assertNotEqual(comp.widget_owned, None)
            w = comp.widget_owned
            self.assertEqual(type(w), ComponentWithGaurd)
            self.assertEqual(w._enter_calls, 0)
            self.assertEqual(w._exit_calls, 0)

        # Verify that the dependent exists and __exit__ was not called
        self.assertEqual(w._enter_calls, 0)
        self.assertEqual(w._exit_calls, 0)
    
    def test_can_resolve_factory_of_list_dependency(self):
        c = Container()
        
        # Register a component with a factory list dependency
        c.register("component", ComponentWithFactoryOfListDependency)
        c.register("widget", ComponentWithNoDependencies)
        c.register("widget", ComponentWithNoDependencies)
        
        # Resolve the component
        comp1 = c.resolve("component")
        
        # Verify the correct behavior
        self.assertNotEqual(comp1.widget_list_fact, None)
        self.assertTrue(hasattr(comp1.widget_list_fact, "__call__"))
        deps = comp1.widget_list_fact()
        self.assertEqual(type(deps), list)
        self.assertEqual(len(deps), 2)
        for widget in deps:
            self.assertEqual(type(widget), ComponentWithNoDependencies)
        
    def test_cannot_resolve_list_of_factory_dependency(self):
        c = Container()

        # Register a component with a list of factory dependency
        c.register("component", ComponentWithListOfFactoryDependency)
        c.register("widget", ComponentWithNoDependencies)

        # Resolve the component, expect it to fail
        self.assertRaises(DipyException, lambda: c.resolve("component"))
    
    def test_can_resolve_stubed_components(self):
        c = Container(autostub=True)
        
        # Register a class with a dependency, but not the dependency
        c.register("component", ComponentWithOneDependency)
        
        # Resolve the component
        comp1 = c.resolve("component")
        
        # Verify that the dependency was correctly stubed
        self.assertNotEqual(comp1.widget, None)
        self.assertEqual(type(comp1.widget), Stub)
    
    def test_can_child_container_override_parent(self):
        # Create a parent container and register a single instance and another component
        parent = Container()
        dep1 = ComponentWithNoDependencies()
        parent.register("widget", dep1)
        parent.register("component", ComponentWithOneDependency)
        
        # Create a child container, register another single instance dependency
        child = Container(parent=parent)
        dep2 = ComponentWithNoDependencies()
        child.register("widget", dep2)
        
        # Resolve the component and verify that the child's component was injected
        comp1 = child.resolve("component")
        self.assertNotEqual(comp1.widget, None)
        self.assertEqual(type(comp1.widget), ComponentWithNoDependencies)
        self.assertEqual(comp1.widget, dep2)
    
    def test_cannot_resolve_missing_registration_with_parent(self):
        # Create a parent container and register nothing
        parent = Container()
        
        # Create a child container, register another single instance dependency
        child = Container(parent=parent)
        child.register("component", ComponentWithOneDependency)
        
        # Resolve the component and verify that the child's component was injected
        self.assertRaises(DipyException, lambda: child.resolve("component"))
    
    def test_can_resolve_from_parent_with_stubing_child_container(self):
        # Create a parent container and a component
        parent = Container()
        parent.register("widget", ComponentWithNoDependencies)
        
        # Create a stubing child container, register another component
        child = Container(parent=parent, autostub=True)
        child.register("component", ComponentWithOneDependency)
        
        # Resolve the component. It should be the instance from the parent
        comp = child.resolve("component")
        self.assertNotEqual(comp, None)
        self.assertEqual(type(comp), ComponentWithOneDependency)
        self.assertNotEqual(comp.widget, None)
        self.assertEqual(type(comp.widget), ComponentWithNoDependencies)

    def test_can_resolve_stub_from_parent_container(self):
        # Create a parent container with stubing
        parent = Container(autostub=True)

        # Create a child container, register a component with a dependency
        child = Container(parent=parent)
        child.register("component", ComponentWithOneDependency)
        
        # Resolve the component. It should be the instance from the parent
        comp = child.resolve("component")
        self.assertNotEqual(comp, None)
        self.assertEqual(type(comp), ComponentWithOneDependency)
        self.assertNotEqual(comp.widget, None)
        self.assertEqual(type(comp.widget), Stub)

    def test_can_dispose_components(self):
        parent = Container()
        
        # Register one component with gaurd 
        parent.register("component", ComponentWithGaurd)
        
        # Create a new container in a with statement
        with Container(parent=parent) as child:
            # Resolve the component
            comp = child.resolve("component")

            # Verify that enter was called on the dependency
            self.assertEqual(type(comp), ComponentWithGaurd)
            self.assertEqual(comp._enter_calls, 1)
            self.assertEqual(comp._exit_calls, 0)
        
        # Verify exit is called on the dependency
        self.assertEqual(comp._enter_calls, 1)
        self.assertEqual(comp._exit_calls, 1)
    
    def test_can_dispose_single_instance(self):
        parent = Container()
        
        # Register one component with gaurd 
        parent.register("component", ComponentWithGaurd, single_instance=True)
        
        # Create a new container in a with statement
        with Container(parent=parent) as child:
            # Resolve the component
            comp = child.resolve("component")

            # Verify that enter was called on the dependency
            self.assertEqual(type(comp), ComponentWithGaurd)
            self.assertEqual(comp._enter_calls, 1)
            self.assertEqual(comp._exit_calls, 0)
        
        # Verify exit is called on the dependency
        self.assertEqual(comp._enter_calls, 1)
        self.assertEqual(comp._exit_calls, 1)
 
    def test_can_dispose_dependent_components(self):
        parent = Container()
        
        # Register one component with gaurd and another without
        parent.register("component", ComponentWithOneDependency)
        parent.register("widget", ComponentWithGaurd)
        
        # Create a new container in a with statement
        with Container(parent=parent) as child:
            # Resolve the component
            comp = child.resolve("component")

            # Verify that enter was called on the dependency
            self.assertNotEqual(comp.widget, None)
            self.assertEqual(type(comp.widget), ComponentWithGaurd)
            self.assertEqual(comp.widget._enter_calls, 1)
            self.assertEqual(comp.widget._exit_calls, 0)
        
        # Verify exit is called on the dependency
        self.assertEqual(comp.widget._enter_calls, 1)
        self.assertEqual(comp.widget._exit_calls, 1)

    def test_single_instance_owned_by_child(self):
        parent = Container()
        
        # Register one component with gaurd and another without
        parent.register("component", ComponentWithOneDependency)
        parent.register("widget", ComponentWithGaurd, single_instance=True)
        
        # Create a new container in a with statement
        with Container(parent=parent) as child:
            # Resolve the component
            comp = child.resolve("component")

            # Verify that enter was called on the dependency
            self.assertNotEqual(comp.widget, None)
            self.assertEqual(type(comp.widget), ComponentWithGaurd)
            self.assertEqual(comp.widget._enter_calls, 1)
            self.assertEqual(comp.widget._exit_calls, 0)
        
        # Verify exit is called on the dependency
        self.assertEqual(comp.widget._enter_calls, 1)
        self.assertEqual(comp.widget._exit_calls, 1)

        # Resolve a second component instance
        w2 = parent.resolve("widget")

        # Verify the widget is a new instance
        self.assertNotEqual(w2, None)
        self.assertEqual(type(w2), ComponentWithGaurd)
        self.assertNotEqual(w2, comp.widget)

    def test_single_instance_owned_by_parent(self):
        with Container() as parent:
            
            # Register one component with gaurd and another without
            parent.register("component", ComponentWithOneDependency)
            parent.register("widget", ComponentWithGaurd, single_instance=True, locally_owned=False)
            
            # Create a new container in a with statement
            with Container(parent=parent) as child:
                # Resolve the component
                comp = child.resolve("component")

                # Verify that enter was called on the dependency
                self.assertNotEqual(comp.widget, None)
                self.assertEqual(type(comp.widget), ComponentWithGaurd)
                self.assertEqual(comp.widget._enter_calls, 1)
                self.assertEqual(comp.widget._exit_calls, 0)
            
            # Verify exit is not called on the dependency
            self.assertEqual(comp.widget._enter_calls, 1)
            self.assertEqual(comp.widget._exit_calls, 0)

            # Resolve a second component instance
            w2 = parent.resolve("widget")

            # Verify exit is not called on the dependency
            self.assertEqual(w2._enter_calls, 1)
            self.assertEqual(w2._exit_calls, 0)

            # Verify the widget is the same instance
            self.assertNotEqual(w2, None)
            self.assertEqual(type(w2), ComponentWithGaurd)
            self.assertEqual(w2, comp.widget)
        
        # Verify exit is called on the dependency
        self.assertEqual(comp.widget._enter_calls, 1)
        self.assertEqual(comp.widget._exit_calls, 1)



class ComponentWithNoDependencies(object):
    
    def __init__(self):
        super(ComponentWithNoDependencies, self).__init__()


class ComponentWithArgument(object):
    
    def __init__(self, arg):
        super(ComponentWithArgument, self).__init__()
        self.arg = arg


class ComponentWithOneDependency(object):
    
    def __init__(self, widget):
        super(ComponentWithOneDependency, self).__init__()
        self.widget = widget


class ComponentWithListDependency(object):
    
    def __init__(self, widget_list):
        super(ComponentWithListDependency, self).__init__()
        self.widget_list = widget_list


class ComponentWithFactoryDependency(object):
    
    def __init__(self, widget_fact):
        super(ComponentWithFactoryDependency, self).__init__()
        self.widget_fact = widget_fact


class ComponentWithOwnedDependency(object):

    def __init__(self, widget_owned):
        super(ComponentWithOwnedDependency, self).__init__()
        self.widget_owned = widget_owned


class ComponentWithFactoryOfListDependency(object):
    
    def __init__(self, widget_list_fact):
        super(ComponentWithFactoryOfListDependency, self).__init__()
        self.widget_list_fact = widget_list_fact


class ComponentWithListOfFactoryDependency(object):
    
    def __init__(self, widget_fact_list):
        super(ComponentWithListOfFactoryDependency, self).__init__()
        self.widget_fact_list = widget_fact_list


class ComponentWithGaurd(object):
    
    def __init__(self):
        super(ComponentWithGaurd, self).__init__()
        self._enter_calls = 0
        self._exit_calls = 0
    
    def __enter__(self):
        self._enter_calls += 1
        return self
    
    def __exit__(self, type, value, traceback):
        self._exit_calls += 1


#--- Tests for the stubing library

class TestStub(TestCase):
    
    def setUp(self):
        self.stub = Stub("simple_stub")
    
    def test_can_stub_attributes(self):
        m = self.stub
        
        # Create some new attributes
        m.attribute_1 = "value1"
        m.attribute_2 = [1, 2, 3, 4]
        
        # Verify those attributes are set
        self.assertEqual(m.attribute_1, "value1")
        self.assertEqual(m.attribute_2, [1, 2, 3, 4])
    
    def test_stub_repr(self):
        # Make sure the name is included in the repr
        self.assertTrue(self.stub.stub_name in repr(self.stub))
    
    def test_can_stub_consistently(self):
        m = self.stub
        
        # Reference new attributes
        attr_1 = m.attr_1
        attr_2 = m.attr_2
        
        # Verify that the same objects are returned for the same attributes
        self.assertNotEqual(attr_1, attr_2)
        self.assertEqual(attr_1, m.attr_1)
        self.assertEqual(attr_2, m.attr_2)
    
    def test_can_stub_function_calls(self):
        m = self.stub
        
        # Call several stubed functions
        result_1 = m.func_no_args()
        result_2 = m.func_no_args()
        result_3 = m.func_args(1, 2, 3)
        result_4 = m.func_kwargs(kwarg1="arg1", kwarg2="arg2")
        result_5 = m.func_mix_args("one", "two", last="three")
        
        # Verify the call counts of the stubed functions
        self.assertEqual(m.func_no_args.call_count, 2)
        self.assertEqual(m.func_args.call_count, 1)
        self.assertEqual(m.func_kwargs.call_count, 1)
        self.assertEqual(m.func_mix_args.call_count, 1)
        
        # Verify that the arguments and results were captured by the stub
        self.assertEqual(m.func_no_args.call_history[0], ((), {}, result_1))
        self.assertEqual(m.func_no_args.call_history[1], ((), {}, result_2))
        self.assertEqual(m.func_args.call_history[0], ((1, 2, 3), {}, result_3))
        self.assertEqual(
            m.func_kwargs.call_history[0], 
            ((), {"kwarg1":"arg1", "kwarg2":"arg2"}, result_4))
        self.assertEqual(
            m.func_mix_args.call_history[0], 
            (("one", "two"), {"last":"three"}, result_5))


if __name__== '__main__':
    main()
