"""info419historia URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from core import views


urlpatterns = [
    path('admin/', admin.site.urls),
    path('login/', auth_views.LoginView.as_view(), name='login'),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path('', views.perfil, name='perfil'),
    path('usuarios/', views.usuarios, name='usuarios'),
    path('usuarios/cadastrar/', views.registro, name='registro'),
    path(
        'usuarios/editar/<int:id>/',
        views.usuario_edicao,
        name='usuario_edicao'
    ),
    path(
        'usuarios/apagar/<int:id>/',
        views.usuario_remocao,
        name='usuario_remocao'
    ),
    path('turmas/cadastrar/', views.turma_cadastro, name='turma_cadastro'),
    path('turmas/<int:id>', views.turma, name='turma'),
    path('turmas/<int:id>/editar', views.turma_edicao, name='turma_edicao'),
    path('turmas/<int:id>/remover', views.turma_remocao, name='turma_remocao'),
    path('atividades/<int:id>/', views.atividade, name='atividade'),
    path('atividades/<int:atividade_id>/grupos/', views.grupos, name='grupos'),
    path(
        'atividades/<int:atividade_id>/grupos/cadastrar/',
        views.grupo_cadastro,
        name='grupo_cadastro'
    ),
    path(
        'atividades/<int:atividade_id>/notas',
        views.gerar_notas,
        name='gerar_notas'
    ),
    path('grupos/<int:id>/entrar/', views.entrar_grupo, name='entrar_grupo'),
    path('grupos/<int:id>/sair/', views.sair_grupo, name='sair_grupo'),
    path('grupos/<int:id>/editar/', views.grupo_edicao, name='grupo_edicao'),
    path('grupos/<int:id>/apagar/', views.grupo_remocao, name='grupo_remocao'),
    path(
        'grupos/<int:grupo_id>/aceitar/<int:aluno_id>/',
        views.grupo_aceitar,
        name='grupo_aceitar'
    ),
    path(
        'grupos/<int:grupo_id>/rejeitar/<int:aluno_id>/',
        views.grupo_rejeitar,
        name='grupo_rejeitar'
    ),
    path(
        'atividades/cadastrar/',
        views.atividade_cadastro,
        name='atividade_cadastro'
    ),
    path(
        'atividades/<int:id>/editar/',
        views.atividade_edicao,
        name='atividade_edicao'
    ),
    path(
        'atividades/<int:id>/remover',
        views.atividade_remocao,
        name='atividade_remocao'
    ),
    path(
        'documentos/',
        views.documentos,
        name='documentos'
    ),
    path(
        'documentos/cadastrar/',
        views.documento_cadastro,
        name='documento_cadastro'
    ),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
