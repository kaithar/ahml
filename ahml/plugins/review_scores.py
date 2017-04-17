from ahml import registry

score_key = {
	0: 'Beyond Appalling',
	1: 'Appalling',
	2: 'Horrible',
	3: 'Very Bad',
	4: 'Bad',
	5: 'Average',
	6: 'Fine',
	7: 'Good',
	8: 'Very Good',
	9: 'Great',
	10: 'Masterpiece',
	11: 'Spinal Tap',
	9001: 'Memetastic'
}

class scores(object):
	def __init__(self, cmd):
		cmd.eat_nl = True

	def render(self, state, args):
		varname = args[0][1].strip('\'" ')
		data = {}
		for k,v in state['variables'].get(varname,{}).items():
			data[k.lower()] = v
		# Start row...
		r1,r2,r3 = '', '', ''
		for i in ('Story', 'Art', 'Sound', 'Character', 'Enjoyment', 'Overall'):
			score = data.get(i.lower(),None)
			if score:
				desc = '({})'.format(score_key.get(score,''))
			else:
				score = '?'
				desc = ''
			r1 += '<th>{}</th>'.format(i)
			r2 += '<td>{}/10</td>'.format(score)
			r3 += '<td>{}</td>'.format(desc)
		return '<table class="review_scores"><tr>{}</tr><tr>{}</tr><tr>{}</tr></table>'.format(r1, r2, r3)

registry.add("scores", scores)
