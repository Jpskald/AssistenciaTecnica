import datetime
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, redirect
from .models import (
    Cliente,
    Aparelho,
    OrdemServico,
    Atendente,
    Pagamento,
    peca,
    servico,
    itemPeca,
    itemServico,
    tecnico,
    Gerente,
)


@never_cache
@csrf_exempt
def fazer_login(request):
    """Login exclusivo para Clientes (usando Nº da OS e senha)."""
    erro = None
    if request.method == 'GET' and request.user.is_authenticated:
        logout(request)

    if request.method == 'POST':
        username = request.POST.get('username')
        senha = request.POST.get('password')
        user = authenticate(request, username=username, password=senha)

        if user is not None:
            if hasattr(user, 'cliente'):
                login(request, user)
                return redirect('painel_cliente')
            else:
                erro = "Esta página é exclusiva para Clientes. Utilize o link de Acesso de Funcionários abaixo."
        else:
            erro = "Número da OS ou senha incorretos."

    return render(request, 'login.html', {'erro': erro})


@never_cache
@csrf_exempt
def login_usuarios(request):
    """Login exclusivo para Funcionários (Atendente, Técnico, Gerente) e Admin."""
    erro = None
    if request.method == 'GET' and request.user.is_authenticated:
        logout(request)

    if request.method == 'POST':
        username = request.POST.get('username')
        senha = request.POST.get('password')
        user = authenticate(request, username=username, password=senha)

        if user is not None:
            if hasattr(user, 'usuario'):
                login(request, user)
                cargo = user.usuario.Cargo
                if cargo == 'Atendente':
                    return redirect('painel_atendente')
                elif cargo == 'Técnico':
                    return redirect('painel_tecnico')
                elif cargo == 'Gerente':
                    return redirect('painel_gerente')
            elif user.is_superuser or user.is_staff:
                login(request, user)
                return redirect('/admin/')
            else:
                erro = "Acesso restrito a funcionários. Clientes devem usar o Portal do Cliente."
        else:
            erro = "Usuário ou senha incorretos."

    return render(request, 'login_usuarios.html', {'erro': erro})


def painel_atendente(request):
    mensagem = None
    # Pega o atendente logado ou o primeiro atendente cadastrado para chamar os métodos:
    atendente_obj = Atendente.objects.first()
    if not atendente_obj:
        atendente_obj = Atendente.objects.create(Nome="Atendente Padrão", Cargo="Atendente")

    if request.method == 'POST':
        acao = request.POST.get('acao')

        if acao == 'cadastrar_cliente':
            atendente_obj.CadastrarCliente(
                nome=request.POST.get('nome'),
                email=request.POST.get('email'),
                telefone=request.POST.get('telefone'),
                cpf=request.POST.get('cpf'),
                endereco=request.POST.get('endereco'),
            )
            mensagem = "Cliente cadastrado com sucesso!"

        elif acao == 'cadastrar_aparelho':
            cliente_obj = Cliente.objects.get(id=request.POST.get('cliente_id'))
            atendente_obj.CadastrarAparelho(
                nome=request.POST.get('nome'),
                marca=request.POST.get('marca'),
                modelo=request.POST.get('modelo'),
                cliente=cliente_obj,
                descricao=request.POST.get('descricao'),
            )
            mensagem = "Aparelho cadastrado com sucesso!"

        elif acao == 'abrir_os':
            cliente_obj = Cliente.objects.get(id=request.POST.get('cliente_id'))
            aparelho_obj = Aparelho.objects.get(id=request.POST.get('aparelho_id'))
            os_criada = atendente_obj.AbrirOS(
                relatocliente=request.POST.get('relato_cliente'),
                cliente=cliente_obj,
                aparelho=aparelho_obj,
            )
            mensagem = f"OS {os_criada.numero_os} aberta! Senha gerada para o cliente: {cliente_obj.senha_acesso}"

        elif acao == 'registrar_venda':
            peca_obj = peca.objects.get(id=request.POST.get('peca_id'))
            quantidade = int(request.POST.get('quantidade', 1))
            data_venda = request.POST.get('data_venda') or datetime.date.today()
            venda_criada = atendente_obj.RegistrarVenda(
                peca_obj=peca_obj,
                quantidade=quantidade,
                data=data_venda,
                vendedor=atendente_obj,
            )
            mensagem = f"Venda de {quantidade}x {peca_obj.Nome} (R$ {venda_criada.Valor:.2f}) registrada e estoque atualizado!"

        elif acao == 'fechar_os_pagamento':
            os_obj = OrdemServico.objects.get(id=request.POST.get('os_id'))
            parcelas = int(request.POST.get('parcelas', 1))
            tipo_pagamento = request.POST.get('tipo_pagamento')
            if os_obj.Valor:
                atendente_obj.FecharOSpagamento(
                    valor=os_obj.Valor,
                    parcelas=parcelas,
                    tipopagamento=tipo_pagamento,
                    OrdemServico=os_obj,
                )
                os_obj.status = 'PAGAMENTO FEITO'
                os_obj.save()
                mensagem = f"Pagamento registrado e OS {os_obj.numero_os} fechada!"
            else:
                mensagem = f"A OS {os_obj.numero_os} ainda não possui um orçamento vinculado."

    contexto = {
        'clientes': Cliente.objects.all(),
        'aparelhos': Aparelho.objects.all(),
        'pecas': peca.objects.all(),
        'ordens': OrdemServico.objects.all().order_by('-id'),
        'mensagem': mensagem,
    }
    return render(request, 'painel_atendente.html', contexto)


def painel_cliente(request):
    mensagem = None
    cliente_obj = None

    if request.user.is_authenticated and hasattr(request.user, 'cliente'):
        cliente_obj = request.user.cliente
    else:
        cliente_obj = Cliente.objects.first()

    if request.method == 'POST' and cliente_obj:
        os_id = request.POST.get('os_id')
        decisao = request.POST.get('decisao')
        os_obj = OrdemServico.objects.get(id=os_id, cliente=cliente_obj)

        if decisao == 'aceitar':
            cliente_obj.ConfirmarOrcamento(ordem_servico=os_obj, aceito=True)
            mensagem = f"Orçamento da {os_obj.numero_os} aprovado com sucesso!"
        elif decisao == 'recusar':
            cliente_obj.ConfirmarOrcamento(ordem_servico=os_obj, aceito=False)
            mensagem = f"Orçamento recusado. A {os_obj.numero_os} foi cancelada."

    ordens = OrdemServico.objects.filter(cliente=cliente_obj).order_by('-id') if cliente_obj else []

    contexto = {
        'cliente': cliente_obj,
        'ordens': ordens,
        'mensagem': mensagem,
    }
    return render(request, 'painel_cliente.html', contexto)


def painel_tecnico(request):
    mensagem = None
    tecnico_obj = tecnico.objects.first()
    if not tecnico_obj:
        tecnico_obj = tecnico.objects.create(Nome="Técnico Padrão", Cargo="Técnico")

    if request.method == 'POST':
        acao = request.POST.get('acao')

        if acao == 'registrar_uso_peca':
            peca_obj = peca.objects.get(id=request.POST.get('peca_id'))
            quantidade = int(request.POST.get('quantidade', 1))
            tecnico_obj.RegistrarUsoPeca(
                peca_obj=peca_obj,
                quantidade=quantidade,
                val_unitario=peca_obj.Preco,
            )
            mensagem = f"Uso de {quantidade}x {peca_obj.Nome} registrado e estoque atualizado!"

        elif acao == 'cadastrar_orcamento':
            os_obj = OrdemServico.objects.get(id=request.POST.get('os_id'))
            item_peca_obj = itemPeca.objects.get(id=request.POST.get('item_peca_id'))
            servico_obj = servico.objects.get(id=request.POST.get('servico_id'))
            qtde_servico = int(request.POST.get('qtde_servico', 1))

            arquivo_imagem = request.FILES.get('imagem')
            imagem_bytes = arquivo_imagem.read() if arquivo_imagem else None

            item_servico_obj = itemServico.objects.create(
                Nome=servico_obj,
                QtdeS=qtde_servico,
                Val_unitarioS=servico_obj.Preco,
            )
            orcamento_criado = tecnico_obj.CadastrarOrcamento(
                itemPeca=item_peca_obj,
                itemServico=item_servico_obj,
                imagem=imagem_bytes,
            )
            os_obj.Valor = orcamento_criado
            os_obj.save()
            mensagem = f"Orçamento de R$ {orcamento_criado.Valor:.2f} cadastrado na {os_obj.numero_os}!"

        elif acao == 'atualizar_status':
            os_obj = OrdemServico.objects.get(id=request.POST.get('os_id'))
            novo_status = request.POST.get('novo_status')
            tecnico_obj.AtualizarStatus(ordem_servico=os_obj, novo_status=novo_status)
            mensagem = f"Status da {os_obj.numero_os} atualizado para '{novo_status}'!"

    contexto = {
        'ordens': OrdemServico.objects.all().order_by('-id'),
        'pecas': peca.objects.all(),
        'servicos': servico.objects.all(),
        'itens_peca': itemPeca.objects.all().order_by('-id'),
        'mensagem': mensagem,
    }
    return render(request, 'painel_tecnico.html', contexto)


def painel_gerente(request):
    mensagem = None
    gerente_obj = Gerente.objects.first()
    if not gerente_obj:
        gerente_obj = Gerente.objects.create(Nome="Gerente Padrão", Cargo="Gerente")

    if request.method == 'POST':
        acao = request.POST.get('acao')

        if acao == 'adicionar_produto':
            gerente_obj.AdicionarProduto(
                nome=request.POST.get('nome'),
                preco=float(request.POST.get('preco')),
                marca=request.POST.get('marca'),
                qtde_estoque=int(request.POST.get('qtde_estoque')),
                num_serie=request.POST.get('num_serie'),
            )
            mensagem = "Peça adicionada ao estoque com sucesso!"

        elif acao == 'editar_produto':
            gerente_obj.EditarProduto(
                id_produto=request.POST.get('id_produto'),
                nome=request.POST.get('nome'),
                preco=float(request.POST.get('preco')),
                marca=request.POST.get('marca'),
                qtde_estoque=int(request.POST.get('qtde_estoque')),
                num_serie=request.POST.get('num_serie'),
            )
            mensagem = "Dados da peça atualizados com sucesso!"

        elif acao == 'excluir_produto':
            gerente_obj.ExcluirProduto(id_produto=request.POST.get('id_produto'))
            mensagem = "Peça removida do banco de dados!"

        elif acao == 'adicionar_servico':
            gerente_obj.AdicionarServico(
                nome=request.POST.get('nome'),
                preco=float(request.POST.get('preco')),
                descricao=request.POST.get('descricao'),
            )
            mensagem = "Serviço adicionado com sucesso!"

        elif acao == 'editar_servico':
            gerente_obj.EditarServico(
                id_servico=request.POST.get('id_servico'),
                nome=request.POST.get('nome'),
                preco=float(request.POST.get('preco')),
                descricao=request.POST.get('descricao'),
            )
            mensagem = "Serviço atualizado com sucesso!"

        elif acao == 'excluir_servico':
            gerente_obj.ExcluirServico(id_servico=request.POST.get('id_servico'))
            mensagem = "Serviço removido do banco de dados!"

        elif acao == 'adicionar_tecnico':
            novo_tec = gerente_obj.AdicionarTecnico(nome=request.POST.get('nome'))
            username = request.POST.get('username')
            password = request.POST.get('password')
            if username and password:
                user_tec = User.objects.create_user(username=username, password=password)
                novo_tec.user = user_tec
                novo_tec.save()
            mensagem = f"Técnico '{novo_tec.Nome}' contratado com sucesso!"

        elif acao == 'adicionar_atendente':
            novo_atend = gerente_obj.AdicionarAtendente(nome=request.POST.get('nome'))
            username = request.POST.get('username')
            password = request.POST.get('password')
            if username and password:
                user_atend = User.objects.create_user(username=username, password=password)
                novo_atend.user = user_atend
                novo_atend.save()
            mensagem = f"Atendente '{novo_atend.Nome}' contratado com sucesso!"

        elif acao == 'desligar_tecnico':
            gerente_obj.DesligarTecnico(id_tecnico=request.POST.get('id_tecnico'))
            mensagem = "Técnico desligado e removido do sistema!"

        elif acao == 'desligar_atendente':
            gerente_obj.DesligarAtendente(id_atendente=request.POST.get('id_atendente'))
            mensagem = "Atendente desligado e removido do sistema!"

    contexto = {
        'pecas': peca.objects.all(),
        'servicos': servico.objects.all(),
        'tecnicos': tecnico.objects.all(),
        'atendentes': Atendente.objects.all(),
        'mensagem': mensagem,
    }
    return render(request, 'painel_gerente.html', contexto)





