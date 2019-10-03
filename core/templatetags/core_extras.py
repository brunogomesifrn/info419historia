from django import template

register = template.Library()


@register.filter
def index(List, i):
    return List[int(i)]


@register.filter
def trange(end, start=None):
    if start:
        return range(start, end + 1)
    return range(1, end + 1)


@register.filter()
def e_imagem(arquivo):
    ext = arquivo.path[-4:]
    if ext in ['.jpg', '.png', 'jpeg']:
        return True
    else:
        return False


@register.filter()
def beautify(time):
    time = time.split(',')[0]
    if time.startswith('0'):
        time = 'Finalizada'
    return time


@register.filter()
def get_checkbox_meta(form, field):
    return form.get_checkbox_meta(field)


@register.filter()
def masc_fem(genero, letras='o,a'):
    letras = letras.split(',')
    if len(letras) == 1:
        letras += 'a'

    return (letras[0] if genero == 'm'
            else letras[1] if genero == 'f'
            else '')


@register.filter()
def startswith(string, start):
    return string.startswith(start)


@register.filter('breakpoint')
def _breakpoint(data):
    breakpoint()
