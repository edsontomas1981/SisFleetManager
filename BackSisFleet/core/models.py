# core/models.py
from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    # Dados pessoais/empresa
    nome_razao_social = models.CharField(max_length=150, blank=True, null=True, verbose_name="Nome/Razão Social")
    cpf_cnpj = models.CharField(max_length=18, blank=True, null=True, unique=True, verbose_name="CPF/CNPJ")
    telefone = models.CharField(max_length=20, blank=True, null=True, verbose_name="Telefone")

    tipo_usuario = models.CharField(
        max_length=20,
        choices=[('motorista', 'Motorista'), ('cliente', 'Cliente'), ('admin', 'Administrador')],
        default='cliente'
    )
    is_verified = models.BooleanField(default=False)

    # Tipo de plano
    tipo_plano = models.CharField(
        max_length=20,
        choices=[('gratis', 'Grátis'), ('premium', 'Premium')],
        default='gratis'
    )

    # Endereço
    endereco_rua = models.CharField(max_length=255, blank=True, null=True, verbose_name="Rua")
    endereco_numero = models.CharField(max_length=10, blank=True, null=True, verbose_name="Número")
    endereco_complemento = models.CharField(max_length=50, blank=True, null=True, verbose_name="Complemento")
    endereco_bairro = models.CharField(max_length=100, blank=True, null=True, verbose_name="Bairro")
    endereco_cidade = models.CharField(max_length=100, blank=True, null=True, verbose_name="Cidade")
    endereco_estado = models.CharField(max_length=2, blank=True, null=True, verbose_name="UF")
    endereco_cep = models.CharField(max_length=10, blank=True, null=True, verbose_name="CEP")

    # Empresa
    inscricao_estadual = models.CharField(max_length=20, blank=True, null=True, verbose_name="Inscrição Estadual")
    inscricao_municipal = models.CharField(max_length=20, blank=True, null=True, verbose_name="Inscrição Municipal")

    # Controle
    data_nascimento = models.DateField(blank=True, null=True, verbose_name="Data de Nascimento")
    data_cadastro = models.DateTimeField(auto_now_add=True, verbose_name="Data de Cadastro")
    atualizado_em = models.DateTimeField(auto_now=True, verbose_name="Atualizado em")

    class Meta:
        verbose_name = "Usuário"
        verbose_name_plural = "Usuários"

    def __str__(self):
        return self.username or self.email

    def to_dict(self):
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "nome_razao_social": self.nome_razao_social,
            "cpf_cnpj": self.cpf_cnpj,
            "telefone": self.telefone,
            "tipo_usuario": self.tipo_usuario,
            "is_verified": self.is_verified,
            "tipo_plano": self.tipo_plano,
            "endereco_rua": self.endereco_rua,
            "endereco_numero": self.endereco_numero,
            "endereco_complemento": self.endereco_complemento,
            "endereco_bairro": self.endereco_bairro,
            "endereco_cidade": self.endereco_cidade,
            "endereco_estado": self.endereco_estado,
            "endereco_cep": self.endereco_cep,
            "inscricao_estadual": self.inscricao_estadual,
            "inscricao_municipal": self.inscricao_municipal,
            "data_nascimento": self.data_nascimento,
            "data_cadastro": self.data_cadastro,
            "atualizado_em": self.atualizado_em,
        }

