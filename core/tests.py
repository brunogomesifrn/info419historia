from django.test import TestCase

'''
Código para criar os grupos ALunos e Professores com as devidas permissõess
'''
from django.contrib.auth.models import Permission, Group
from django.contrib.contenttypes.models import ContentType


def get_permissions(model_permissions):
    for model, permissions in model_permissions.items():
        if isinstance(permissions, str):
            permissions = (('add', 'change', 'delete', 'view')
                           if permissions == 'all'
                           else (permissions,))
        for permission in permissions:
            yield Permission.objects.get(
                content_type=ContentType.objects.get(model=model),
                codename__startswith=permission)


professor = {
    'permission': 'all',
    'usuario': 'all',
    'alternativa': 'all',
    'atividade': 'all',
    'documento': 'all',
    'grupo': 'all',
    'questao': 'all',
    'tipo': 'all',
    'turma': 'all',
    'resposta': 'view',
}

aluno = {
    'alternativa': 'view',
    'atividade': 'view',
    'documento': 'view',
    'grupo': 'all',
    'questao': 'view',
    'tipo': 'view',
    'turma': 'view',
    'resposta': 'all',
}

professores = Group.objects.create(name='Professores')
for permissao in get_permissions(professor):
    professores.permissions.add(permissao)

alunos = Group.objects.create(name='Alunos')
for permissao in get_permissions(aluno):
    alunos.permissions.add(permissao)

'''
Fim
'''
