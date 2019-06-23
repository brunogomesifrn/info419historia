from django import template

register = template.Library()

@register.filter
def index(List, i):
	return List[int(i)]

@register.filter
def trange(end, start=None):
	if start:
		return range(start, end+1)
	return range(1, end+1)