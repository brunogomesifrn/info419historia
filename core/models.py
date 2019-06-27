from django.db import models
from django.contrib.auth.models import User


class Usuario(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    nome = models.CharField('Nome', max_length=100)
    matricula = models.CharField('Matrícula', max_length=14)
    email = models.EmailField('Email')
    professor = models.BooleanField('Professor')


class Turma(models.Model):
    nome = models.CharField('Nome', max_length=50)
    membros = models.ManyToManyField(User)

    def __str__(self):
        return self.nome


class Atividade(models.Model):
    assunto = models.CharField('Assunto', max_length=50)
    peso = models.IntegerField('Peso')
    inicio = models.DateTimeField('Início')
    fim = models.DateTimeField('Fim')
    turmas = models.ManyToManyField(Turma)

    def __str__(self):
        return "Atividade - %s" % self.assunto


class Grupo(models.Model):
    nota = models.IntegerField('Nota')
    membros = models.ManyToManyField(
        User, limit_choices_to={'professor': False})
    atividade = models.ForeignKey(Atividade, on_delete=models.CASCADE)


class Tipo(models.Model):
    nome = models.CharField('Tipo', max_length=50, unique=True)

    def __str__(self):
        return self.nome


class Documento(models.Model):
    titulo = models.CharField('Título', max_length=100)
    origem = models.TextField('Origem')
    creditos = models.CharField('Créditos', max_length=100)
    texto = models.TextField('Texto', blank=True, null=True)
    arquivo = models.FileField(
        'Arquivo', upload_to='documentos', blank=True, null=True)
    tipo = models.ForeignKey(Tipo, on_delete=models.PROTECT)

    def __str__(self):
        return self.titulo


class Questao(models.Model):
    comando = models.TextField('Comando')
    peso = models.IntegerField('Peso')
    atividade = models.ForeignKey(Atividade, on_delete=models.CASCADE)
    documentos = models.ManyToManyField(Documento)


class Alternativa(models.Model):
    texto = models.TextField('Texto')
    peso = models.IntegerField('Peso')
    questao = models.ForeignKey(Questao, on_delete=models.CASCADE)
