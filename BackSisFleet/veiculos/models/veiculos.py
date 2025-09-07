from django.db import models
from django.conf import settings
from django.utils import timezone
from datetime import datetime
from motoristas.models.motoristas import Motorista


class Veiculo(models.Model):
    """
    Modelo para representar informações de Veículos no sistema.

    Campos:
    - motorista: Chave estrangeira para o motorista responsável pelo veículo.
    - placa: Placa do veículo (única).
    - renavam: Número do Renavam do veículo (único).
    - chassi: Número do chassi do veículo (único).
    - marca: Marca do veículo.
    - modelo: Modelo do veículo.
    - ano_fabricacao: Ano de fabricação.
    - ano_modelo: Ano do modelo.
    - cor: Cor do veículo.
    - tipo_combustivel: Tipo de combustível utilizado.
    - criado_por: Usuário que criou o registro.
    - atualizado_por: Usuário que atualizou o registro pela última vez.
    - created_at: Data e hora de criação do registro.
    - updated_at: Data e hora da última atualização do registro.
    """

    motorista = models.ForeignKey(
        Motorista,
        on_delete=models.SET_NULL,
        related_name="veiculos",
        null=True,
        blank=True,
        help_text="Motorista responsável pelo veículo"
    )
    placa = models.CharField(max_length=10, unique=True)
    renavam = models.CharField(max_length=20, unique=True, null=True, blank=True)
    chassi = models.CharField(max_length=30, unique=True, null=True, blank=True)
    marca = models.CharField(max_length=50)
    modelo = models.CharField(max_length=50)
    ano_fabricacao = models.IntegerField(null=True, blank=True)
    ano_modelo = models.IntegerField(null=True, blank=True)
    cor = models.CharField(max_length=30, null=True, blank=True)
    tipo_combustivel = models.CharField(max_length=20, null=True, blank=True)

    criado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="veiculo_criado_por",
        null=True
    )
    atualizado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="veiculo_atualizado_por",
        null=True
    )
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.placa} - {self.modelo}/{self.marca}"

    def to_dict(self):
        return {
            "motorista": self.motorista.usuario_fk.username if self.motorista and self.motorista.usuario_fk else None,
            "placa": self.placa,
            "renavam": self.renavam,
            "chassi": self.chassi,
            "marca": self.marca,
            "modelo": self.modelo,
            "ano_fabricacao": self.ano_fabricacao,
            "ano_modelo": self.ano_modelo,
            "cor": self.cor,
            "tipo_combustivel": self.tipo_combustivel,
            "criado_por": self.criado_por.username if self.criado_por else None,
            "atualizado_por": self.atualizado_por.username if self.atualizado_por else None,
            "created_at": self.formatar_data(self.created_at),
            "updated_at": self.formatar_data(self.updated_at),
        }

    def formatar_data(self, data):
        if data and isinstance(data, str):
            data = datetime.strptime(data, "%Y-%m-%d")
        return data.strftime("%Y-%m-%d %H:%M:%S") if data else None
