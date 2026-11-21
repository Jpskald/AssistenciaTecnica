from app.models import venda
from app.models import Gerente
from app.models import Atendente
from app.models import tecnico
from app.models import servico
from app.models import peca
from app.models import Aparelho
from app.models import Garantia
from app.models import Pagamento
from app.models import Cliente
from app.models import OrdemServico, Orcamento
from django.contrib import admin
from .models import *

# Register your models here.

admin.site.register(Orcamento)
admin.site.register(OrdemServico)
admin.site.register(Cliente)
admin.site.register(Pagamento)
admin.site.register(Garantia)
admin.site.register(Aparelho)
admin.site.register(peca)
admin.site.register(servico)
admin.site.register(tecnico)
admin.site.register(Atendente)
admin.site.register(Gerente)
admin.site.register(venda)

