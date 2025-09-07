# motorista_manager.py
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseNotFound
from django.db import IntegrityError
from django.utils import timezone
from core.models import CustomUser
from motoristas.models.motoristas import Motorista
from django.db.models import Q

class MotoristaError(Exception):
    """Exceção base para erros relacionados ao motorista."""

class BadRequestError(MotoristaError):
    """Exceção para erros de solicitação inválida (código HTTP 400)."""

class NotFoundError(MotoristaError):
    """Exceção para erros de recurso não encontrado (código HTTP 404)."""

class InternalServerError(MotoristaError):
    """Exceção para erros internos do servidor (código HTTP 500)."""

class MotoristaService:
    
    @classmethod
    def _carregar_dados_comuns(cls, data):
        """Carrega os dados comuns para criação/atualização de motorista"""
        return {
            'usuario_fk': data.get('usuario_fk'),
            'responsavel_fk': data.get('responsavel_fk'),
            'data_nascimento': data.get('data_nascimento'),
            'validade_toxicologico': data.get('validade_toxicologico'),
            'pis': data.get('pis'),
            'estado_civil': data.get('estado_civil'),
            'filiacao_pai': data.get('filiacao_pai'),
            'filiacao_mae': data.get('filiacao_mae'),
            'cnh_numero': data.get('cnh_numero'),
            'cnh_categoria': data.get('cnh_categoria'),
            'cnh_validade': data.get('cnh_validade'),
            'dt_emissao_cnh': data.get('dt_emissao_cnh'),
            'dt_primeira_cnh': data.get('dt_primeira_cnh'),
            'numero_registro_cnh': data.get('numero_registro_cnh'),
        }
    
    @classmethod
    def criar_motorista(cls, data, usuario_criador):
        try:
            # Resolver usuario_fk
            usuario_fk = data.get("usuario_fk")
            if isinstance(usuario_fk, int):
                usuario_fk = CustomUser.objects.get(id=usuario_fk)
            elif isinstance(usuario_fk, str):  # caso receba CPF direto
                usuario_fk = CustomUser.objects.get(cpf=usuario_fk)
            
            if usuario_fk and usuario_fk.tipo_usuario != 'motorista':
                raise BadRequestError("O usuário associado deve ser do tipo 'motorista'")

            # Resolver responsavel_fk
            responsavel_fk = data.get("responsavel_fk")
            if isinstance(responsavel_fk, int):
                responsavel_fk = CustomUser.objects.get(id=responsavel_fk)

            dados_comuns = cls._carregar_dados_comuns(data)
            dados_comuns['usuario_fk'] = usuario_fk
            dados_comuns['responsavel_fk'] = responsavel_fk
            dados_comuns['criado_por'] = usuario_criador
            dados_comuns['atualizado_por'] = usuario_criador
            dados_comuns['created_at'] = timezone.now()
            dados_comuns['updated_at'] = timezone.now()

            # Validações
            if dados_comuns['cnh_validade'] and dados_comuns['cnh_validade'] < timezone.now().date():
                raise BadRequestError("A validade da CNH não pode ser uma data passada")

            motorista = Motorista.objects.create(**dados_comuns)
            return motorista

        except IntegrityError as e:
            if 'cnh_numero' in str(e):
                raise BadRequestError("Já existe um motorista com este número de CNH")
            elif 'numero_registro_cnh' in str(e):
                raise BadRequestError("Já existe um motorista com este número de registro de CNH")
            raise InternalServerError(f"Erro de integridade ao criar motorista: {str(e)}")
        except Exception as e:
            raise InternalServerError(f"Erro ao criar motorista: {str(e)}")

    
    @classmethod
    def atualizar_motorista(cls, motorista_id, data, usuario_atualizador):
        """
        Atualiza um motorista existente
        
        Args:
            motorista_id (int): ID do motorista a ser atualizado
            data (dict): Dados a serem atualizados
            usuario_atualizador (User): Usuário que está atualizando o registro
            
        Returns:
            Motorista: Objeto do motorista atualizado
        """
        try:
            motorista = cls.obter_motorista_por_id(motorista_id)
            dados_comuns = cls._carregar_dados_comuns(data)
            
            # Validações específicas
            if 'usuario_fk' in data and data['usuario_fk'] and data['usuario_fk'].tipo_usuario != 'motorista':
                raise BadRequestError("O usuário associado deve ser do tipo 'motorista'")
            
            if 'cnh_validade' in data and data['cnh_validade'] and data['cnh_validade'] < timezone.now().date():
                raise BadRequestError("A validade da CNH não pode ser uma data passada")
            
            for field, value in dados_comuns.items():
                if value is not None:  # Permite atualizar apenas os campos fornecidos
                    setattr(motorista, field, value)
            
            motorista.atualizado_por = usuario_atualizador
            motorista.updated_at = timezone.now()
            motorista.save()
            
            return motorista
            
        except IntegrityError as e:
            if 'cnh_numero' in str(e):
                raise BadRequestError("Já existe um motorista com este número de CNH")
            elif 'numero_registro_cnh' in str(e):
                raise BadRequestError("Já existe um motorista com este número de registro de CNH")
            raise InternalServerError(f"Erro de integridade ao atualizar motorista: {str(e)}")
        except Exception as e:
            raise InternalServerError(f"Erro ao atualizar motorista: {str(e)}")
    
    @classmethod
    def obter_motorista_por_id(cls, motorista_id):
        """
        Obtém um motorista pelo ID
        
        Args:
            motorista_id (int): ID do motorista
            
        Returns:
            Motorista: Objeto do motorista
            
        Raises:
            NotFoundError: Se o motorista não for encontrado
        """
        try:
            motorista = Motorista.objects.get(id=motorista_id)
            return motorista
        except Motorista.DoesNotExist:
            raise NotFoundError(f"Motorista com ID {motorista_id} não encontrado")
    
    @classmethod
    def obter_motorista_por_usuario(cls, usuario_id):
        """
        Obtém um motorista pelo ID do usuário associado
        
        Args:
            usuario_id (int): ID do usuário
            
        Returns:
            Motorista: Objeto do motorista ou None se não encontrado
        """
        try:
            return Motorista.objects.get(usuario_fk_id=usuario_id)
        except Motorista.DoesNotExist:
            return None
    
    @classmethod
    def obter_motorista_por_cnh(cls, cnh_numero):
        """
        Obtém um motorista pelo número da CNH
        
        Args:
            cnh_numero (str): Número da CNH
            
        Returns:
            Motorista: Objeto do motorista ou None se não encontrado
        """
        try:
            return Motorista.objects.get(cnh_numero=cnh_numero)
        except Motorista.DoesNotExist:
            return None
    
    @classmethod
    def obter_motorista_por_cpf(cls, cpf):
        """
        Obtém um motorista pelo CPF (através do usuário associado)

        Args:
            cpf (str): CPF do motorista

        Returns:
            Motorista: Objeto do motorista ou None se não encontrado
        """
        try:
            # Busca o usuário pelo CPF
            usuario = CustomUser.objects.filter(cpf_cnpj=cpf, tipo_usuario='motorista').first()
            if not usuario:
                return None
            
            # Busca o motorista associado a esse usuário
            return Motorista.objects.filter(usuario_fk=usuario).first()
        
        except Exception:
            return None

    
    @classmethod
    def listar_motoristas(cls, filtros=None):
        """
        Lista motoristas com filtros opcionais
        
        Args:
            filtros (dict): Dicionário com filtros de busca
            
        Returns:
            QuerySet: QuerySet com os motoristas encontrados
        """
        queryset = Motorista.objects.all()
        
        if filtros:
            # Filtro por nome (busca no usuário associado)
            if 'nome' in filtros and filtros['nome']:
                queryset = queryset.filter(
                    Q(usuario_fk__first_name__icontains=filtros['nome']) |
                    Q(usuario_fk__last_name__icontains=filtros['nome'])
                )
            
            # Filtro por CPF (busca no usuário associado)
            if 'cpf' in filtros and filtros['cpf']:
                queryset = queryset.filter(usuario_fk__cpf__icontains=filtros['cpf'])
            
            # Filtro por número de CNH
            if 'cnh_numero' in filtros and filtros['cnh_numero']:
                queryset = queryset.filter(cnh_numero__icontains=filtros['cnh_numero'])
            
            # Filtro por categoria de CNH
            if 'cnh_categoria' in filtros and filtros['cnh_categoria']:
                queryset = queryset.filter(cnh_categoria=filtros['cnh_categoria'])
            
            # Filtro por validade de CNH
            if 'cnh_valida' in filtros:
                from django.utils import timezone
                if filtros['cnh_valida']:
                    queryset = queryset.filter(cnh_validade__gte=timezone.now().date())
                else:
                    queryset = queryset.filter(cnh_validade__lt=timezone.now().date())
            
            # Filtro por validade do toxicológico
            if 'toxicologico_valido' in filtros:
                from django.utils import timezone
                if filtros['toxicologico_valido']:
                    queryset = queryset.filter(validade_toxicologico__gte=timezone.now().date())
                else:
                    queryset = queryset.filter(validade_toxicologico__lt=timezone.now().date())
        
        return queryset.select_related('usuario_fk', 'responsavel_fk', 'criado_por', 'atualizado_por')
    
    @classmethod
    def listar_motoristas_por_responsavel(cls, responsavel_id):
        """
        Lista todos os motoristas de um determinado responsável.

        Args:
            responsavel_id (int): ID do usuário responsável.

        Returns:
            QuerySet: QuerySet contendo os motoristas vinculados ao responsável.
        """

        motoristas = Motorista.objects.filter(responsavel_fk_id=responsavel_id).select_related(
            'usuario_fk', 'responsavel_fk', 'criado_por', 'atualizado_por'
        )

        motoristas = [cls.to_dict(motorista) for motorista in motoristas]
        return motoristas

    @classmethod
    def deletar_motorista(cls, motorista_id):
        """
        Exclui um motorista
        
        Args:
            motorista_id (int): ID do motorista a ser excluído
            
        Raises:
            NotFoundError: Se o motorista não for encontrado
        """
        try:
            motorista = cls.obter_motorista_por_id(motorista_id)
            motorista.delete()
        except Motorista.DoesNotExist:
            raise NotFoundError(f"Motorista com ID {motorista_id} não encontrado")
    
    @classmethod
    def verificar_cnh_valida(cls, motorista_id):
        """
        Verifica se a CNH do motorista está válida
        
        Args:
            motorista_id (int): ID do motorista
            
        Returns:
            bool: True se a CNH estiver válida, False caso contrário
        """
        try:
            motorista = cls.obter_motorista_por_id(motorista_id)
            return motorista.cnh_validade >= timezone.now().date() if motorista.cnh_validade else False
        except NotFoundError:
            return False
    
    @classmethod
    def verificar_toxicologico_valido(cls, motorista_id):
        """
        Verifica se o exame toxicológico do motorista está válido
        
        Args:
            motorista_id (int): ID do motorista
            
        Returns:
            bool: True se o toxicológico estiver válido, False caso contrário
        """
        try:
            motorista = cls.obter_motorista_por_id(motorista_id)
            return motorista.validade_toxicologico >= timezone.now().date() if motorista.validade_toxicologico else False
        except NotFoundError:
            return False
    
    @classmethod
    def to_dict(cls, motorista):
        """
        Converte um objeto Motorista para dicionário
        
        Args:
            motorista (Motorista): Objeto do motorista
            
        Returns:
            dict: Representação em dicionário do motorista
        """
        return motorista.to_dict() if hasattr(motorista, 'to_dict') else {
            'id': motorista.id,
            'usuario_fk': motorista.usuario_fk.id if motorista.usuario_fk else None,
            'usuario_info': {
                'username': motorista.usuario_fk.username if motorista.usuario_fk else None,
                'email': motorista.usuario_fk.email if motorista.usuario_fk else None,
                'first_name': motorista.usuario_fk.first_name if motorista.usuario_fk else None,
                'last_name': motorista.usuario_fk.last_name if motorista.usuario_fk else None,
                'cpf': motorista.usuario_fk.cpf if motorista.usuario_fk else None,
            } if motorista.usuario_fk else None,
            'responsavel_fk': motorista.responsavel_fk.id if motorista.responsavel_fk else None,
            'responsavel_info': {
                'username': motorista.responsavel_fk.username if motorista.responsavel_fk else None,
                'email': motorista.responsavel_fk.email if motorista.responsavel_fk else None,
                'first_name': motorista.responsavel_fk.first_name if motorista.responsavel_fk else None,
                'last_name': motorista.responsavel_fk.last_name if motorista.responsavel_fk else None,
            } if motorista.responsavel_fk else None,
            'data_nascimento': motorista.data_nascimento.isoformat() if motorista.data_nascimento else None,
            'validade_toxicologico': motorista.validade_toxicologico.isoformat() if motorista.validade_toxicologico else None,
            'pis': motorista.pis,
            'estado_civil': motorista.estado_civil,
            'filiacao_pai': motorista.filiacao_pai,
            'filiacao_mae': motorista.filiacao_mae,
            'cnh_numero': motorista.cnh_numero,
            'cnh_categoria': motorista.cnh_categoria,
            'cnh_validade': motorista.cnh_validade.isoformat() if motorista.cnh_validade else None,
            'dt_emissao_cnh': motorista.dt_emissao_cnh.isoformat() if motorista.dt_emissao_cnh else None,
            'dt_primeira_cnh': motorista.dt_primeira_cnh.isoformat() if motorista.dt_primeira_cnh else None,
            'numero_registro_cnh': motorista.numero_registro_cnh,
            'criado_por': motorista.criado_por.id if motorista.criado_por else None,
            'criado_por_info': {
                'username': motorista.criado_por.username if motorista.criado_por else None,
            } if motorista.criado_por else None,
            'atualizado_por': motorista.atualizado_por.id if motorista.atualizado_por else None,
            'atualizado_por_info': {
                'username': motorista.atualizado_por.username if motorista.atualizado_por else None,
            } if motorista.atualizado_por else None,
            'created_at': motorista.created_at.isoformat() if motorista.created_at else None,
            'updated_at': motorista.updated_at.isoformat() if motorista.updated_at else None,
            'cnh_valida': motorista.cnh_validade >= timezone.now().date() if motorista.cnh_validade else False,
            'toxicologico_valido': motorista.validade_toxicologico >= timezone.now().date() if motorista.validade_toxicologico else False,
        }