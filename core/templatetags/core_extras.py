from django import template

register = template.Library()


@register.filter
def get(_dict, i):
    try:
        return _dict[i]
    except (IndexError):
        return None


@register.filter('range')
def _range(end, start=None):
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


@register.filter()
def endswith(string, end):
    return string.endswith(end)


@register.filter()
def participacao(user, atividade):
    return user.get_participacao(atividade)

# @register.filter()
# def nota(grupo):
#     grupo = user.get_grupo(atividade)
#     if not grupo or not grupo.nota:
#         return False
#     return grupo.nota


@register.simple_tag(name='breakpoint', takes_context=True)
def _breakpoint(context, *args, **kwargs):
    breakpoint()


# deprecated
@register.filter
def check(nota):
    if not nota and nota != 0:
        return ''
    if nota >= 80:
        return ' border-success'
    if nota >= 60:
        return ' border-info'
    if nota >= 20:
        return ' border-warning'
    return ' border-danger'
