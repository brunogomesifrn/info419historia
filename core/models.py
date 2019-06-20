from django.db import models


class Usuario(models.Model):
	nome = models.CharField('Nome', max_length=100)
	matricula = models.CharField('Matrícula', max_length=14)
	email = models.EmailField('Email')
	professor = models.BooleanField('Professor')

	def __str__(self):
		return self.nome


class Turma(models.Model):
	nome = models.CharField('Nome', max_length=50)
	membros = models.ManyToManyField(Usuario)

	def __str__(self):
		return self.nome


class Atividade(models.Model):
	peso = models.IntegerField('Peso')
	inicio = models.DateField('Data de Início')
	fim = models.DateField('Data de Fim')
	turmas = models.ManyToManyField(Turma)

	def __str__(self):
		return "Atividade %d" % self.id


class Grupo(models.Model):
	nota = models.IntegerField('Nota')
	membros = models.ManyToManyField(Usuario, limit_choices_to={'professor': False})
	atividade = models.ForeignKey(Atividade, on_delete=models.CASCADE)


class Documento(models.Model):
	texto = models.TextField('Texto')
	arquivo = models.FileField('Arquivo', upload_to='documentos', null=True, blank=True)

	def __str__(self):
		return "Documento " + self.id


class Questao(models.Model):
	comando = models.TextField('Comando')
	peso = models.IntegerField('Peso')
	atividade = models.ForeignKey(Atividade, on_delete=models.CASCADE, null=True)
	documentos = models.ManyToManyField(Documento)


class Alternativa(models.Model):
	texto = models.TextField('Texto')
	peso = models.IntegerField('Peso')
	questao = models.ForeignKey(Questao, on_delete=models.CASCADE, null=True)
