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
from core.views import home, usuarios, turmas, atividades, atividade_cadastro, questao_cadastro, alternativa_cadastro, atividade, grupos, documentos, documento_cadastro


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home),
    path('usuarios/', usuarios, name='usuarios'),
    path('turmas/', turmas, name='turmas'),
    path('atividades/', atividades, name='atividades'),
    path('atividades/<int:id>/', atividade, name='atividade'),
    path('atividades/cadastrar/', atividade_cadastro, name='atividade_cadastro'),
    path('atividades/cadastrar/questao', questao_cadastro, name='questao_cadastro'),
    path('atividades/cadastrar/questao/alternativa', alternativa_cadastro, name='alternativa_cadastro'),
    path('grupos/', grupos, name='grupos'),
    path('documentos/', documentos, name='documentos'),
    path('documentos/cadastrar/', documento_cadastro, name='documento_cadastro'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
