"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
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
from django.contrib import admin
from django.urls import path
from app import views


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.fazer_login, name = 'login'),
    path('atendente/', views.painel_atendente, name = 'painel_atendente'),
    path('cliente/', views.painel_cliente, name = 'painel_cliente'),
    path('tecnico/', views.painel_tecnico, name = 'painel_tecnico'),
    path('gerente/', views.painel_gerente, name = 'painel_gerente'),
]
