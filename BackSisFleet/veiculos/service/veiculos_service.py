# veiculo_service.py
from django.db import IntegrityError
from django.utils import timezone
from core.models import CustomUser
from motoristas.models.motoristas import Motorista
from veiculos.models.veiculos import Veiculo
from django.db.models import Q


class VeiculoError(Exception):
    """Exceção base para erros relacionados ao veículo."""


class BadRequestError(VeiculoError):
    """Exceção para erros de solicitação inválida (código HTTP 400)."""


class NotFoundError(VeiculoError):
    """Exceção para erros de recurso não encontrado (código HTTP 404)."""


class InternalServerError(VeiculoError):
    """Exceção para erros internos do servidor (código HTTP 500)."""


class VeiculoService:
    
    @classmethod
    def _carregar_dados_comuns(cls, data):
        """Carrega os dados comuns para criação/atualização de veículo"""
        return {
            "motorista": data.get("motorista"),
            "placa": data.get("placa"),
            "renavam": data.get("renavam"),
            "chassi": data.get("chassi"),
            "marca": data.get("marca"),
            "modelo": data.get("modelo"),
            "ano_fabricacao": data.get("ano_fabricacao"),
            "ano_modelo": data.get("ano_modelo"),
            "cor": data.get("cor"),
            "tipo_combustivel": data.get("tipo_combustivel"),
        }

    @classmethod
    def criar_veiculo(cls, data, usuario_criador):
        try:
            # Resolver motorista
            motorista = data.get("motorista")
            if isinstance(motorista, int):
                motorista = Motorista.objects.get(id=motorista)

            dados = cls._carregar_dados_comuns(data)
            dados["motorista"] = motorista
            dados["criado_por"] = usuario_criador
            dados["atualizado_por"] = usuario_criador
            dados["created_at"] = timezone.now()
            dados["updated_at"] = timezone.now()

            veiculo = Veiculo.objects.create(**dados)
            return veiculo

        except IntegrityError as e:
            if "placa" in str(e):
                raise BadRequestError("Já existe um veículo com esta placa")
            elif "renavam" in str(e):
                raise BadRequestError("Já existe um veículo com este Renavam")
            elif "chassi" in str(e):
                raise BadRequestError("Já existe um veículo com este chassi")
            raise InternalServerError(f"Erro de integridade ao criar veículo: {str(e)}")
        except Exception as e:
            raise InternalServerError(f"Erro ao criar veículo: {str(e)}")
        
    @classmethod
    def obter_veiculos_por_motorista(cls, motorista_id):
        """
        Obtém todos os veículos associados a um motorista específico.

        Args:
            motorista_id (int): ID do motorista.

        Returns:
            list: Lista de dicionários representando os veículos.

        Raises:
            NotFoundError: Se nenhum veículo for encontrado para o motorista.
        """
        try:
            veiculos = Veiculo.objects.filter(motorista_id=motorista_id).select_related(
                "motorista", "criado_por", "atualizado_por"
            )

            if not veiculos.exists():
                raise NotFoundError(f"Nenhum veículo encontrado para o motorista ID {motorista_id}")

            return [cls.to_dict(veiculo) for veiculo in veiculos]

        except Exception as e:
            raise InternalServerError(f"Erro ao obter veículos do motorista: {str(e)}")

    @classmethod
    def atualizar_veiculo(cls, veiculo_id, data, usuario_atualizador):
        try:
            veiculo = cls.obter_veiculo_por_id(veiculo_id)
            dados = cls._carregar_dados_comuns(data)

            if "motorista" in data and data["motorista"]:
                motorista = data["motorista"]
                if isinstance(motorista, int):
                    motorista = Motorista.objects.get(id=motorista)
                dados["motorista"] = motorista

            for field, value in dados.items():
                if value is not None:
                    setattr(veiculo, field, value)

            veiculo.atualizado_por = usuario_atualizador
            veiculo.updated_at = timezone.now()
            veiculo.save()

            return veiculo

        except IntegrityError as e:
            if "placa" in str(e):
                raise BadRequestError("Já existe um veículo com esta placa")
            elif "renavam" in str(e):
                raise BadRequestError("Já existe um veículo com este Renavam")
            elif "chassi" in str(e):
                raise BadRequestError("Já existe um veículo com este chassi")
            raise InternalServerError(f"Erro de integridade ao atualizar veículo: {str(e)}")
        except Exception as e:
            raise InternalServerError(f"Erro ao atualizar veículo: {str(e)}")

    @classmethod
    def obter_veiculo_por_id(cls, veiculo_id):
        try:
            return Veiculo.objects.get(id=veiculo_id)
        except Veiculo.DoesNotExist:
            raise NotFoundError(f"Veículo com ID {veiculo_id} não encontrado")

    @classmethod
    def obter_veiculo_por_placa(cls, placa):
        try:
            return Veiculo.objects.get(placa=placa)
        except Veiculo.DoesNotExist:
            return None

    @classmethod
    def listar_veiculos(cls, filtros=None):
        queryset = Veiculo.objects.all()

        if filtros:
            if "placa" in filtros and filtros["placa"]:
                queryset = queryset.filter(placa__icontains=filtros["placa"])

            if "marca" in filtros and filtros["marca"]:
                queryset = queryset.filter(marca__icontains=filtros["marca"])

            if "modelo" in filtros and filtros["modelo"]:
                queryset = queryset.filter(modelo__icontains=filtros["modelo"])

            if "ano_fabricacao" in filtros and filtros["ano_fabricacao"]:
                queryset = queryset.filter(ano_fabricacao=filtros["ano_fabricacao"])

            if "motorista_id" in filtros and filtros["motorista_id"]:
                queryset = queryset.filter(motorista_id=filtros["motorista_id"])

        return queryset.select_related("motorista", "criado_por", "atualizado_por")

    @classmethod
    def listar_veiculos_por_motorista(cls, motorista_id):
        veiculos = Veiculo.objects.filter(motorista_id=motorista_id).select_related(
            "motorista", "criado_por", "atualizado_por"
        )
        return [cls.to_dict(veiculo) for veiculo in veiculos]

    @classmethod
    def deletar_veiculo(cls, veiculo_id):
        try:
            veiculo = cls.obter_veiculo_por_id(veiculo_id)
            veiculo.delete()
        except Veiculo.DoesNotExist:
            raise NotFoundError(f"Veículo com ID {veiculo_id} não encontrado")

    @classmethod
    def to_dict(cls, veiculo):
        return veiculo.to_dict() if hasattr(veiculo, "to_dict") else {
            "id": veiculo.id,
            "motorista": veiculo.motorista.id if veiculo.motorista else None,
            "motorista_info": {
                "username": veiculo.motorista.usuario_fk.username if veiculo.motorista and veiculo.motorista.usuario_fk else None,
                "cpf": veiculo.motorista.usuario_fk.cpf_cnpj if veiculo.motorista and veiculo.motorista.usuario_fk else None,
            } if veiculo.motorista else None,
            "placa": veiculo.placa,
            "renavam": veiculo.renavam,
            "chassi": veiculo.chassi,
            "marca": veiculo.marca,
            "modelo": veiculo.modelo,
            "ano_fabricacao": veiculo.ano_fabricacao,
            "ano_modelo": veiculo.ano_modelo,
            "cor": veiculo.cor,
            "tipo_combustivel": veiculo.tipo_combustivel,
            "criado_por": veiculo.criado_por.username if veiculo.criado_por else None,
            "atualizado_por": veiculo.atualizado_por.username if veiculo.atualizado_por else None,
            "created_at": veiculo.created_at.isoformat() if veiculo.created_at else None,
            "updated_at": veiculo.updated_at.isoformat() if veiculo.updated_at else None,
        }
