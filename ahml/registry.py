registry = {}

def add(name, c):
	registry[name] = c

def call(cmd, state, args):
	c = cmd.plugin
	if (c):
		return c.render(state, args)
	return 'Unknown plugin.'

def produce(name, cmd):
	c = registry.get(name, None)
	if (c):
		i = c(cmd)
		cmd.plugin = i
	else:
		cmd.plugin = None

def exists(name):
	return (name in registry)