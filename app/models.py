from django.db.models import DateField
from django.db.models import FloatField
from django.db.models import CASCADE
import datetime
from django.db import models
from django.core.mail import send_mail
from reportlab.pdfgen import canvas

# Create your models here

# CLASSES PARA FAZER:
#Orcamento ok
#Pagamento ok
#Produto ok
#Peca ok
#Item_peca ok
#Servico ok
#item_servico ok
#Garantia ok
#OrdemServico ok
#Cliente ok
#Aparelho ok
#Usuário ok
#Técnico ok
#Atendente ok
#Gerente ok
#Venda ok



class Cliente(models.Model):
    nome = models.CharField(max_length=100)
    email = models.EmailField()
    telefone = models.CharField(max_length=15)
    endereco = models.CharField(max_length=200)
    cpf = models.CharField(max_length=11)
    def __str__(self):
        return self.nome
    def ConfirmarOrcamento(self, ordem_servico, aceito):
        if aceito:
            ordem_servico.status = 'ORÇAMENTO ACEITO'
        else:
            ordem_servico.status = 'CANCELADO'
            ordem_servico.data_fechamento = datetime.date.today()
        ordem_servico.save()
        return aceito
    def ChecarStatusOS(self, aparelho):
        os_cliente = OrdemServico.objects.get(cliente=self, aparelho=aparelho)
        return os_cliente.status

    
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
    Preco = models.FloatField()
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
    QtdeS = models.ForeignKey(itemServico, on_delete=models.CASCADE, related_name='orcamentos_qtdes')
    Val_unitarioS = models.ForeignKey(itemServico, on_delete= models.CASCADE, related_name='orcamentos_vals')
    QtdeP = models.ForeignKey(itemPeca, on_delete= models.CASCADE, related_name='orcamentos_qtdep')
    Val_unitarioP = models.ForeignKey(itemPeca, on_delete= models.CASCADE, related_name='orcamentos_valp')
    Imagem = models.BinaryField(null=True, blank=True)
    def calcularpreco(self=None):
        if self is None:
            return 0.0
        return self.QtdeS.QtdeS * self.Val_unitarioS.Val_unitarioS + self.QtdeP.QtdeP * self.Val_unitarioP.Val_unitarioP
    Valor = models.FloatField(default=calcularpreco)

class Usuario(models.Model):
    Nome = models.CharField(max_length= 40)
    Cargo = models.CharField(max_length= 15)

class Atendente(Usuario):
    def CadastrarCliente(self, nome, email, telefone, cpf, endereco):
        novo_cliente = Cliente(nome=nome,email=email,telefone=telefone,endereco=endereco,cpf=cpf)
        novo_cliente.save()
    def CadastrarAparelho(self, nome, marca, modelo, cliente, descricao):
        novo_aparelho = Aparelho(nome=nome, marca=marca, modelo=modelo, cliente=cliente, descricao=descricao)
        novo_aparelho.save()
    def RegistrarVenda(self, valor, data, vendedor):
        nova_venda = venda(Valor=valor, DataVenda= data, Vendedor= vendedor)
        nova_venda.save()
    def FecharOSpagamento(self, valor, parcelas, tipopagamento, OrdemServico):
        registro_pagamento = Pagamento(
            Tipo_pagamento= tipopagamento,
            Parcelas = parcelas,
            Preco_total = valor
        )
        registro_pagamento.save()
        OrdemServico.data_fechamento = datetime.date.today()
        OrdemServico.save()
    def AbrirOS(self, relatocliente, cliente, aparelho):
        data_hoje = datetime.date.today()
        os_nova = OrdemServico(
            cliente = cliente,
            Valor = None,
            data_fechamento = None,
            aparelho = aparelho,
            data_abertura = data_hoje,
            relato_cliente = relatocliente,
        )
        os_nova.save()
        


class venda(models.Model):
    Valor = FloatField()
    DataVenda = DateField()
    Vendedor = models.ForeignKey(Atendente, on_delete= models.CASCADE)

class OrdemServico(models.Model):
    STATUS_CHOICE = (
        ('AGUARDANDO TRIAGEM', 'Aguardando Triagem'),
        ('EM TRIAGEM', 'Em Triagem'),
        ('ORÇAMENTO PRONTO', 'Orçamento Pronto'),
        ('ORÇAMENTO ACEITO', 'Orçamento Aceito'),
        ('EM REPARO', 'Em Reparo'),
        ('TESTE', 'Teste'),
        ('PAGAMENTO FEITO', 'Pagamento Feito'),
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
    data_fechamento = models.DateField(null=True, blank=True)
    relato_cliente = models.TextField()
    Valor = models.ForeignKey(Orcamento, on_delete= models.CASCADE, null=True, blank=True)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICE,
        default = 'AGUARDANDO TRIAGEM'
    )
    def __str__(self):
        return self.numero_os


class Pagamento(models.Model):
    STATUS_PAGAMENTO = (
        ('PENDENTE', 'Pendente'),
        ('PARCIAL', 'Parcialmente Pago (Parcelado)'),
        ('PAGO', 'Pago / Quitado'),
        ('ATRASADO', 'Atrasado'),
        ('CANCELADO', 'Cancelado'),
    )
    Tipo_pagamento = models.CharField(max_length= 100)
    Parcelas = models.IntegerField(default=1)
    Parcelas_pagas = models.IntegerField(default=0)
    Preco_total = models.ForeignKey(Orcamento, on_delete=models.CASCADE)
    status = models.CharField(
        max_length=20,
        choices=STATUS_PAGAMENTO,
        default='PENDENTE'
    )
    def GerarGarantia(self, numero_os):
        data_inicio = datetime.date.today()
        data_fim = data_inicio + datetime.timedelta(days=90)
        termo = f"A garantia do serviço referente à OS {numero_os} é válida de {data_inicio.strftime('%d/%m/%Y')} até o dia {data_fim.strftime('%d/%m/%Y')} (90 dias)."
        nova_garantia = Garantia(
            Termo=termo,
            Data_inicio=data_inicio,
            Data_fim=data_fim
        )
        nova_garantia.save()

        nome_arquivo = f"garantia_{numero_os}.pdf"
        pdf = canvas.Canvas(nome_arquivo)
        pdf.setTitle(f"Termo de Garantia - {numero_os}")
        pdf.drawString(50, 800, "TERMO DE GARANTIA - ASSISTÊNCIA TÉCNICA")
        pdf.drawString(50, 770, termo)
        pdf.save()

        return nova_garantia


class Garantia(models.Model):
    Termo = models.CharField(max_length= 300)
    Data_inicio = models.DateField()
    Data_fim = models.DateField()

class tecnico(Usuario):
    def CadastrarOrcamento(self, itemPeca,itemServico, imagem=None):
        novo_orcamento = Orcamento(QtdeS=itemServico, QtdeP= itemPeca, Val_unitarioS= itemServico, Val_unitarioP= itemPeca)
        novo_orcamento.save()
        return novo_orcamento
    def AtualizarStatus(self, ordem_servico, novo_status):
        ordem_servico.status = novo_status
        ordem_servico.save()

        if novo_status == 'ORÇAMENTO PRONTO':
            send_mail(
                subject=f"Orçamento Pronto - {ordem_servico.numero_os}",
                message=f"Olá, {ordem_servico.cliente.nome}! O orçamento do seu aparelho ({ordem_servico.aparelho.nome}) referente à {ordem_servico.numero_os} já está pronto. Acesse o sistema para aprovar ou recusar.",
                from_email="contato@assistenciatecnica.com",
                recipient_list=[ordem_servico.cliente.email],
                fail_silently=True,
            )
    def RegistrarUsoPeca(self, peca_obj, quantidade, val_unitario):
        peca_obj.Qtde_estoque = peca_obj.Qtde_estoque - quantidade
        peca_obj.save()

        novo_item_peca = itemPeca (Nome= peca_obj, QtdeP= quantidade, Val_unitarioP= val_unitario)
        novo_item_peca.save()


class Gerente(Usuario):
    def AdicionarProduto(self, nome, preco, marca, qtde_estoque, num_serie):
        nova_peca = peca(
            Nome=nome,
            Preco=preco,
            Marca=marca,
            Qtde_estoque=qtde_estoque,
            Num_serie=num_serie
        )
        nova_peca.save()
        return nova_peca

    def AdicionarServico(self, nome, preco, descricao):
        novo_servico = servico(
            Nome=nome,
            Preco=preco,
            Descricao=descricao
        )
        novo_servico.save()
        return novo_servico

    def EditarProduto(self, id_produto, nome, preco, marca, qtde_estoque, num_serie):
        peca_editada = peca.objects.get(id=id_produto)
        peca_editada.Nome = nome
        peca_editada.Preco = preco
        peca_editada.Marca = marca
        peca_editada.Qtde_estoque = qtde_estoque
        peca_editada.Num_serie = num_serie
        peca_editada.save()
        return peca_editada

    def EditarServico(self, id_servico, nome, preco, descricao):
        servico_editado = servico.objects.get(id=id_servico)
        servico_editado.Nome = nome
        servico_editado.Preco = preco
        servico_editado.Descricao = descricao
        servico_editado.save()
        return servico_editado

    def ExcluirProduto(self, id_produto):
        peca_excluir = peca.objects.get(id=id_produto)
        peca_excluir.delete()

    def ExcluirServico(self, id_servico):
        servico_excluir = servico.objects.get(id=id_servico)
        servico_excluir.delete()

    def AdicionarTecnico(self, nome):
        novo_tecnico = tecnico(
            Nome=nome,
            Cargo="Técnico"
        )
        novo_tecnico.save()
        return novo_tecnico

    def AdicionarAtendente(self, nome):
        novo_atendente = Atendente(
            Nome=nome,
            Cargo="Atendente"
        )
        novo_atendente.save()
        return novo_atendente

    def DesligarTecnico(self, id_tecnico):
        tecnico_excluir = tecnico.objects.get(id=id_tecnico)
        tecnico_excluir.delete()

    def DesligarAtendente(self, id_atendente):
        atendente_excluir = Atendente.objects.get(id=id_atendente)
        atendente_excluir.delete()

