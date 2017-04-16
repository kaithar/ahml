from ahml import registry

class testdummy(object):
	def __init__(self, cmd):
		pass

	def render(self, state, args):
		return "Foo"

registry.add("testdummy", testdummy)
