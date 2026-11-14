from django.db.models import CASCADE
import datetime
from django.db import models

# Create your models here


class Cliente(models.Model):
    nome = models.CharField(max_length=100)
    email = models.EmailField()
    telefone = models.CharField(max_length=15)
    endereco = models.CharField(max_length=200)
    cpf = models.CharField(max_length=11)
    def __str__(self):
        return self.nome



class Aparelho(models.Model):
    nome = models.CharField(max_length=100)
    marca = models.CharField(max_length=100)
    modelo = models.CharField(max_length=100)
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    descricao = models.TextField()
    def __str__(self):
        return self.nome








class produto(models.Model):
    Nome = models.CharField(max_length=100)
    class Meta:
        verbose_name = "Produto"
        verbose_name_plural = "Produtos"
    def __str__(self):
        return self.Nome

class peca(produto):
    Marca = models.CharField(max_length=50)
    Qtde_estoque = models.IntegerField()
    Num_serie = models.CharField(max_length=50)
    class Meta:
        verbose_name = "Peça"
        verbose_name_plural = "Peças"
    def __str__(self):
        return f"{self.Nome}, {self.Num_serie}"

class servico(produto):
    Descricao = models.TextField()
    class Meta:
        verbose_name = "Serviço"
        verbose_name_plural = "Serviços"

class usuario(models.Model):
    nome = models.CharField(max_length=100)
    cargo = models.CharField(max_length=15)

class itemPeca(models.Model):
    Nome = models.ForeignKey(peca, on_delete=models.CASCADE)
    QtdeP = models.IntegerField()
    Val_unitarioP = models.FloatField()
    def __str__(self):
        return self.Nome

class itemServico(models.Model):
    Nome = models.ForeignKey(servico, on_delete=models.CASCADE)
    QtdeS = models.IntegerField()
    Val_unitarioS = models.FloatField()
    def __str__(self):
        return self.Nome

class Orcamento(models.Model):
    QtdeS = models.ForeignKey(itemServico, on_delete=models.CASCADE)
    Val_unitarioS = models.ForeignKey(itemServico, on_delete= models.CASCADE)
    QtdeP = models.ForeignKey(itemPeca, on_delete= models.CASCADE)
    Val_unitarioP = models.ForeignKey(itemPeca, on_delete= models.CASCADE)
    def calcularpreco():
        return self.QtdeS * self.Val_unitarioS + self.QtdeP * self.Val_unitarioP      
    Valor = models.FloatField(default= Orcamento.calcularpreco)

class OrdemServico(models.Model):
    STATUS_CHOICE = (
        ('AGUARDANDO TRIAGEM', 'Aguardando Triagem'),
        ('EM TRIAGEM', 'Em Triagem'),
        ('ORÇAMENTO PRONTO', 'Orçamento Pronto'),
        ('ORÇAMENTO ACEITO', 'Orçamento Aceito'),
        ('ORÇAMENTO RECUSADO', 'Orçamento Recusado'),
        ('EM REPARO', 'Em Reparo'),
        ('TESTE', 'Teste'),
        ('ENTREGUE', 'Entregue'),
        ('CANCELADO', 'Cancelado'),
    )
    def gerarNumeroOS():
        ano = datetime.date.today().year
        numero = OrdemServico.objects.filter(data_abertura__year=ano).count() + 1
        return f'OS-{ano}-{numero:03d}'
    numero_os = models.CharField(max_length=13, default=gerarNumeroOS)
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    aparelho = models.ForeignKey(Aparelho, on_delete=models.CASCADE)
    data_abertura = models.DateField()
    data_fechamento = models.DateField()
    relato_cliente = models.TextField()
    Valor = models.ForeignKey(Orcamento, on_delete= models.CASCADE)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICE
    )
    def __str__(self):
        return self.numero_os


#    def CalcularPreco():

#class tecnico(usuario):


