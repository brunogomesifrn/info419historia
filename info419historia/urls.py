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
from core.views import *


urlpatterns = [
    path('admin/',
         admin.site.urls),
    path('login/',
         auth_views.LoginView.as_view(),
         name='login'),
    path("logout/",
         auth_views.LogoutView.as_view(),
         name="logout"),
    path('',
         perfil,
         name='perfil'),
    path('usuarios/',
         usuarios,
         name='usuarios'),
    path('usuarios/cadastrar/',
         registro,
         name='registro'),
    path('usuarios/editar/<int:id>/',
         usuario_edicao,
         name='usuario_edicao'),
    path('usuarios/apagar/<int:id>/',
         usuario_remocao,
         name='usuario_remocao'),
    # path('turmas/cadastrar/',
    #      turma_cadastro,
    #      name='turma_cadastro'),
    path('turmas/<int:id>',
         turma,
         name='turma'),
    path('turmas/<int:id>/editar',
         turma_edicao,
         name='turma_edicao'),
    path('turmas/<int:id>/remover',
         turma_remocao,
         name='turma_remocao'),
    path('atividades/<int:id>/',
         atividade,
         name='atividade'),
    path('atividades/<int:atividade_id>/grupos/',
         grupos,
         name='grupos'),
    path('atividades/<int:atividade_id>/grupos/cadastrar/',
         grupo_cadastro,
         name='grupo_cadastro'),
    path('atividades/<int:atividade_id>/notas',
         gerar_notas,
         name='gerar_notas'),
    path('grupos/<int:id>/editar/',
         grupo_edicao,
         name='grupo_edicao'),
    path('grupos/<int:id>/ápagar/',
         grupo_remocao,
         name='grupo_remocao'),
    path('atividades/cadastrar/',
         atividade_cadastro,
         name='atividade_cadastro'),
    path('atividades/<int:id>/editar/',
         atividade_edicao,
         name='atividade_edicao'),
    path('atividades/<int:id>/remover',
         atividade_remocao,
         name='atividade_remocao'),
    path('documentos/',
         documentos,
         name='documentos'),
    # path('documentos/cadastrar/',
    #      documento_cadastro,
    #      name='documento_cadastro'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
