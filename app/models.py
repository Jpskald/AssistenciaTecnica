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



class OrdemServico(models.Model):
    STATUS_CHOICE = (
        ('AGUARDANDO TRIAGEM', 'EM TRIAGEM',
         'ORÇAMENTO PRONTO',
         'ORÇAMENTO ACEITO',
         'ORÇAMENTO RECUSADO',
         'EM REPARO',
         'TESTE',
         'ENTREGUE',
         'CANCELADO',
        )
    )
    def gerarNumeroOS():
        ano = datetime.date.today().year
        numero = OrdemServico.objects.filter(ano=ano).count() + 1
        return f'OS-{ano}-{numero:03d}'
    numero_os = models.CharField(max_length=13, default=gerarNumeroOS)
    
    
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    aparelho = models.ForeignKey(Aparelho, on_delete=models.CASCADE)
    data_abertura = models.DateField()
    data_fechamento = models.DateField()
    relato_cliente = models.TextField()
    status = models.CharField(max_length = 20)
    def __str__(self):
        return self.numero_os