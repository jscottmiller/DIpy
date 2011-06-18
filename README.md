DIpy
====

Introduction
------------

DIpy is a simple, pure-python inversion of control container whose design is heavily inspired by [Autofac](http://code.google.com/p/autofac/ "Autofac Homepage"). 

DIpy features:

1. Flexible component resolution and registration.
2. Simple component lifetime management.
3. Higher-order component resolution.
4. Ability to stub missing dependencies.

Usage
-----

The IOC container is provided by the Container class:

	con = dipy.Container()
	
Components are identified by a string name and registered directly against a container instance:

	con.register("widget", SimpleWidget)
	
Components can then be resolved from the container:

	widget = con.resolve("widget")

When a component is registered via a type, resolving that component always returns a new instance:

	widget1 = con.resolve("widget")
	widget2 = con.resolve("widget")
	
	return widget1 is widget2 # returns False

Dependencies are injected based on constructor parameters:

	class ComplexWidget(object):
		def __init__(self, simple_widget)
			self._simple_widget = simple_widget
	
	con = dipy.Container()
	
	con.register("complex_widget", ComplexWidget)
	con.register("simple_widget", SimpleWidget)
	
	 # widget.simple_widget will be a new instance of SimpleWidget
	widget = con.resolve("complex_widget")
	
An instance of a class may be registered directly. Each time that component is resolved, the same instance will be returned:

	con.register("widget", SimpleWidget())
	
	widget1 = con.resolve("widget")
	widget2 = con.resolve("widget")
	
	return widget1 is widget2 # returns True

It is also possible to indicate that only single instance of a component should be created per container:

	con.register("widget", SimpleWidget, single_instance=True)

	widget1 = con.resolve("widget")
	widget2 = con.resolve("widget")

	return widget1 is widget2 # returns True

Components can request higher-order dependencies that are derived based on dependency names. Appending "_list" to the end of a component name will inject a list of all components with that name:

	class Machine(object):
		def __init__(self, widget_list):
			self.widgets = widget_list
	
	con = dipy.Container()
	con.register("widget", BlueWidget)
	con.register("widget", GoldWidget)
	con.register("widget", RedWidget)
	con.register("machine", Machine)
	
	# machine.widgets will contain a list of 3 elements, one for each widget type
	machine = con.resolve("machine")

Adding "_fact" to a dependency name will inject a factory function that can be used to create instances of that dependency at runtime. Additional parameters required by the dependency can be passed to this function.

	class ReportGenerator(object):
		def __init__(self, session_fact):
			self.session_fact = session_fact

		def do_it(self):
			sess = self.session_fact()
			sess.do_some_work()

DIpy provides simple lifetime management of all registered components. When a component is resolved, its \_\_enter\_\_ method is called, if applicable. When the container's \_\_exit\_\_ method is called for all components.

Finally, DIpy encourages proper unit testing of components by providing a built-in means of stubing components that have not been registered with the container:

	class UserControl:
		def __init__(self, third_party_component_x):
			self.component = third_party_component_x
	
	con = dipy.Container(autostub=True)
	con.register("control", UserControl)
	
	# control.component will be an instance of dipy.Stub
	control = con.resolve("control")

