from django.test import TestCase

'''
Código para criar os grupos Alunos e Professores com as devidas permissões e usuários para cada grupo
'''
from django.contrib.auth.models import Permission, Group
from django.contrib.contenttypes.models import ContentType
from core.models import Usuario


def get_permissions(model_permissions):
    for model, permissions in model_permissions.items():
        if isinstance(permissions, str):
            permissions = (
                ('add', 'change', 'delete', 'view')
                if permissions == 'all'
                else (permissions,)
            )
        for permission in permissions:
            yield Permission.objects.get(
                content_type=ContentType.objects.get(model=model),
                codename__startswith=permission
            )


professor = {
    'permission': 'all',
    'usuario': 'all',
    'alternativa': 'all',
    'atividade': 'all',
    'documento': 'all',
    'grupo': 'all',
    'questao': 'all',
    'tipodocumento': 'all',
    'turma': 'all',
    'resposta': 'view',
}

aluno = {
    'alternativa': 'view',
    'atividade': 'view',
    'documento': 'view',
    'grupo': 'all',
    'questao': 'view',
    'tipodocumento': 'view',
    'turma': 'view',
    'resposta': 'all',
}

professores = Group.objects.create(name='Professores')
for permissao in get_permissions(professor):
    professores.permissions.add(permissao)

alunos = Group.objects.create(name='Alunos')
for permissao in get_permissions(aluno):
    alunos.permissions.add(permissao)

davi = Usuario.objects.create(
    nome="José Davi",
    sobrenome="Viana Francelino",
    email="josedavifrancelino@gmail.com",
    matricula="20161194010009"
)
davi.set_password("davizinho123.")
davi.groups.add(professores)
davi.save()

lari = Usuario.objects.create(
    nome="Larissa",
    sobrenome="Pereira",
    email="larissaandressaprojetos@gmail.com",
    matricula="20161194010014"
)
lari.set_password("larizinha123.")
lari.groups.add(alunos)
lari.save()

naty = Usuario.objects.create(
    nome="Natália",
    sobrenome="Cristina",
    email="nataliactm@gmail.com",
    matricula="20161194010006"
)
naty.set_password("natyzinha123.")
naty.groups.add(alunos)
naty.save()

milly = Usuario.objects.create(
    nome="Milenna",
    sobrenome="Nunes",
    email="milenna.milly.nunes2716@gmail.com",
    matricula="20161194010010"
)
milly.set_password("millyzinha123.")
milly.groups.add(alunos)
milly.save()

vivi = Usuario.objects.create(
    nome="Vivianny",
    sobrenome="Bezerra",
    email="viviannyfelixvcfb@gmail.com",
    matricula="20161194010021"
)
vivi.set_password("vivizinha123.")
vivi.groups.add(alunos)
vivi.save()

rafa = Usuario.objects.create(
    nome="Rafael",
    sobrenome="Lupito",
    email="laistayany@gmail.com",
    matricula="20161194010017"
)
rafa.set_password("rafazinho123.")
rafa.groups.add(alunos)
rafa.save()

nic = Usuario.objects.create(
    nome="Nícolas",
    sobrenome="Ferreira",
    email="nicolas@gmail.com",
    matricula="20161194010018"
)
nic.set_password("niczinho123.")
nic.groups.add(alunos)
nic.save()

dreyna = Usuario.objects.create(
    nome="Andreyna",
    sobrenome="Patricio",
    email="andreyna@gmail.com",
    matricula="20161194010019"
)
dreyna.set_password("dreynazinha123.")
dreyna.groups.add(alunos)
dreyna.save()

ester = Usuario.objects.create(
    nome="Ester",
    sobrenome="Barroso",
    email="ester@gmail.com",
    matricula="20161194010020"
)
ester.set_password("esterzinha123.")
ester.groups.add(alunos)
ester.save()


'''
Fim
'''
