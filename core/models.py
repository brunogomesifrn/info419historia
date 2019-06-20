from django.db import models


class Usuario(models.Model):
	nome = models.CharField('Nome', max_length=100)
	matricula = models.CharField('Matrícula', max_length=14)
	email = models.EmailField('Email')
	professor = models.BooleanField('Professor')


class Turma(models.Model):
	nome = models.CharField('Nome', max_length=50)
	usuarios = models.ManyToManyField(Usuario)


class Atividade(models.Model):
	peso = models.IntegerField('Peso')
	inicio = models.DateField('Data de Início')
	fim = models.DateField('Data de Fim')
	turmas = models.ManyToManyField(Turma)


class Grupo(models.Model):
	nota = models.IntegerField('Nota')
	usuarios = models.ManyToManyField(Usuario, limit_choices_to={'professor': False})
	atividade = models.ForeignKey(Atividade, on_delete=models.CASCADE)


class Questao(models.Model):
	comando = models.CharField('Comando', max_length=500)
	peso = models.IntegerField('Peso')


class Alternativa(models.Model):
	texto = models.CharField('Texto', max_length=500)
	peso = models.IntegerField('Peso')


class Documento(models.Model):
	texto = models.CharField('Texto', max_length=10000)
	arquivo = models.FileField('Arquivo', upload_to='documentos', null=True, blank=True)
