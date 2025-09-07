from django.db import models
from core.models import CustomUser
from django.conf import settings
from django.utils import timezone
from django.utils import formats
from datetime import datetime

class Motorista(models.Model):
    """
    Modelo para representar informações de Motoristas no sistema.

    Campos:
    - usuario_fk: Chave estrangeira para o usuário associado ao motorista.
    - filiacao_pai: Nome do pai do motorista (pode ser nulo).
    - filiacao_mae: Nome da mãe do motorista (pode ser nulo).
    - cnh_numero: Número da CNH (Carteira Nacional de Habilitação) do motorista (único).
    - cnh_categoria: Categoria da CNH do motorista.
    - cnh_validade: Validade da CNH do motorista (pode ser nula).
    - numero_registro_cnh: Número de registro da CNH do motorista (único).
    - criado_por: Usuário que criou o registro.
    - atualizado_por: Usuário que atualizou o registro pela última vez.
    - created_at: Data e hora de criação do registro.
    - updated_at: Data e hora da última atualização do registro.
    """
    usuario_fk = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='motorista_usuario', null=True)
    responsavel_fk = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='motorista_responsavel', null=True)
    data_nascimento = models.DateField(null=True, blank=True)
    validade_toxicologico = models.DateField(null=True, blank=True)
    pis = models.CharField(max_length=20, blank=True, null=True)
    estado_civil = models.CharField(max_length=20, blank=True, null=True)
    filiacao_pai = models.CharField(max_length=255, blank=True, null=True)
    filiacao_mae = models.CharField(max_length=255, blank=True, null=True)
    cnh_numero = models.CharField(max_length=20, blank=True, null=True)
    cnh_categoria = models.CharField(max_length=5, blank=True, null=True)
    cnh_validade = models.DateField(null=True, blank=True)
    dt_emissao_cnh = models.DateField(null=True, blank=True)
    dt_primeira_cnh = models.DateField(null=True, blank=True)
    numero_registro_cnh = models.CharField(max_length=20, blank=True, null=True)
    criado_por = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, related_name='motorista_criado_por', null=True)
    atualizado_por = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, related_name='motorista_atualizado_por', null=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.usuario_fk.username if self.usuario_fk else ''

    def to_dict(self):
        return {
            'usuario_fk': self.usuario_fk.to_dict() if self.usuario_fk else None,
            'data_nascimento': self.formatar_data(self.data_nascimento) if self.data_nascimento else None,
            'validade_toxicologico': self.formatar_data(self.validade_toxicologico) if self.validade_toxicologico else None,
            'pis':self.pis,
            'estado_civil':self.estado_civil,
            'filiacao_pai': self.filiacao_pai,
            'filiacao_mae': self.filiacao_mae,  
            'cnh_numero': self.cnh_numero,
            'cnh_categoria': self.cnh_categoria,
            'cnh_validade': self.formatar_data(self.cnh_validade) if self.cnh_validade else None,
            'dt_emissao_cnh': self.formatar_data(self.dt_emissao_cnh) if self.dt_emissao_cnh else None,
            'dt_primeira_cnh': self.formatar_data(self.dt_primeira_cnh) if self.dt_primeira_cnh else None,
            'numero_registro_cnh': self.numero_registro_cnh,
            'criado_por': self.criado_por.username if self.criado_por else None,
            'atualizado_por': self.atualizado_por.username if self.atualizado_por else None,
            'created_at': self.formatar_data(self.created_at),
            'updated_at': self.formatar_data(self.updated_at),
        }
    
    def formatar_data(self, data):
        if data and isinstance(data, str):
            # Se for uma string, converte para datetime
            data = datetime.strptime(data, "%Y-%m-%d")
        return data.strftime("%Y-%m-%d %H:%M:%S") if data else None
