# core/services/user_service.py
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseNotFound
from django.db import IntegrityError
from django.utils import timezone
from django.contrib.auth.hashers import make_password
from django.core.exceptions import ValidationError
from django.db.models import Q
from ..models import CustomUser

class UserError(Exception):
    """Exceção base para erros relacionados ao usuário."""

class BadRequestError(UserError):
    """Exceção para erros de solicitação inválida (código HTTP 400)."""

class NotFoundError(UserError):
    """Exceção para erros de recurso não encontrado (código HTTP 404)."""

class InternalServerError(UserError):
    """Exceção para erros internos do servidor (código HTTP 500)."""

class UserService:
    """
    Service class para operações de negócio com CustomUser
    """
    
    @classmethod
    def _validar_dados_usuario(cls, data):
        """Valida dados básicos do usuário"""
        errors = {}
        
        # Validação de CPF/CNPJ único
        if 'cpf_cnpj' in data and data['cpf_cnpj']:
            if CustomUser.objects.filter(cpf_cnpj=data['cpf_cnpj']).exclude(id=data.get('id')).exists():
                errors['cpf_cnpj'] = "CPF/CNPJ já cadastrado"
        
        # Validação de email único
        if 'email' in data and data['email']:
            if CustomUser.objects.filter(email=data['email']).exclude(id=data.get('id')).exists():
                errors['email'] = "Email já cadastrado"
        
        # Validação de username único
        if 'username' in data and data['username']:
            if CustomUser.objects.filter(username=data['username']).exclude(id=data.get('id')).exists():
                errors['username'] = "Username já cadastrado"
        
        if errors:
            raise BadRequestError(errors)
    
    @classmethod
    def criar_usuario(cls, data):
        """
        Cria um novo usuário no sistema
        
        Args:
            data (dict): Dados do usuário
            
        Returns:
            CustomUser: Objeto do usuário criado
        """
        try:
            # Valida dados
            cls._validar_dados_usuario(data)
            
            # Prepara dados para criação
            user_data = {
                'username': data.get('username'),
                'email': data.get('email'),
                'first_name': data.get('first_name', ''),
                'last_name': data.get('last_name', ''),
                'nome_razao_social': data.get('nome_razao_social'),
                'cpf_cnpj': data.get('cpf_cnpj'),
                'telefone': data.get('telefone'),
                'tipo_usuario': data.get('tipo_usuario', 'cliente'),
                'tipo_plano': data.get('tipo_plano', 'gratis'),
                'endereco_rua': data.get('endereco_rua'),
                'endereco_numero': data.get('endereco_numero'),
                'endereco_complemento': data.get('endereco_complemento'),
                'endereco_bairro': data.get('endereco_bairro'),
                'endereco_cidade': data.get('endereco_cidade'),
                'endereco_estado': data.get('endereco_estado'),
                'endereco_cep': data.get('endereco_cep'),
                'inscricao_estadual': data.get('inscricao_estadual'),
                'inscricao_municipal': data.get('inscricao_municipal'),
                'data_nascimento': data.get('data_nascimento'),
                'is_verified': data.get('is_verified', False),
            }
            
            # Cria usuário
            usuario = CustomUser.objects.create(**user_data)
            
            # Define password se fornecido
            if 'password' in data and data['password']:
                usuario.set_password(data['password'])
                usuario.save()
            
            return usuario
            
        except IntegrityError as e:
            if 'username' in str(e):
                raise BadRequestError("Username já existe")
            elif 'email' in str(e):
                raise BadRequestError("Email já existe")
            elif 'cpf_cnpj' in str(e):
                raise BadRequestError("CPF/CNPJ já existe")
            raise InternalServerError(f"Erro de integridade ao criar usuário: {str(e)}")
        except Exception as e:
            raise InternalServerError(f"Erro ao criar usuário: {str(e)}")
    
    @classmethod
    def atualizar_usuario(cls, usuario_id, data):
        """
        Atualiza um usuário existente
        
        Args:
            usuario_id (int): ID do usuário a ser atualizado
            data (dict): Dados a serem atualizados
            
        Returns:
            CustomUser: Objeto do usuário atualizado
        """
        try:
            usuario = cls.obter_usuario_por_id(usuario_id)
            
            # Valida dados
            data['id'] = usuario_id  # Para validação de unicidade
            cls._validar_dados_usuario(data)
            
            # Atualiza campos
            campos_permitidos = [
                'first_name', 'last_name', 'nome_razao_social', 'cpf_cnpj',
                'telefone', 'tipo_usuario', 'tipo_plano', 'endereco_rua',
                'endereco_numero', 'endereco_complemento', 'endereco_bairro',
                'endereco_cidade', 'endereco_estado', 'endereco_cep',
                'inscricao_estadual', 'inscricao_municipal', 'data_nascimento',
                'is_verified'
            ]
            
            for campo in campos_permitidos:
                if campo in data:
                    setattr(usuario, campo, data[campo])
            
            # Atualiza password se fornecido
            if 'password' in data and data['password']:
                usuario.set_password(data['password'])
            
            usuario.save()
            return usuario
            
        except IntegrityError as e:
            raise InternalServerError(f"Erro de integridade ao atualizar usuário: {str(e)}")
        except Exception as e:
            raise InternalServerError(f"Erro ao atualizar usuário: {str(e)}")
    
    @classmethod
    def obter_usuario_por_id(cls, usuario_id):
        """
        Obtém um usuário pelo ID
        
        Args:
            usuario_id (int): ID do usuário
            
        Returns:
            CustomUser: Objeto do usuário
            
        Raises:
            NotFoundError: Se o usuário não for encontrado
        """
        try:
            return CustomUser.objects.get(id=usuario_id)
        except CustomUser.DoesNotExist:
            raise NotFoundError(f"Usuário com ID {usuario_id} não encontrado")
    
    @classmethod
    def obter_usuario_por_email(cls, email):
        """
        Obtém um usuário pelo email
        
        Args:
            email (str): Email do usuário
            
        Returns:
            CustomUser: Objeto do usuário ou None se não encontrado
        """
        try:
            return CustomUser.objects.get(email=email)
        except CustomUser.DoesNotExist:
            return None
    
    @classmethod
    def obter_usuario_por_cpf_cnpj(cls, cpf_cnpj):
        """
        Obtém um usuário pelo CPF/CNPJ
        
        Args:
            cpf_cnpj (str): CPF ou CNPJ do usuário
            
        Returns:
            CustomUser: Objeto do usuário ou None se não encontrado
        """
        try:
            return CustomUser.objects.get(cpf_cnpj=cpf_cnpj)
        except CustomUser.DoesNotExist:
            return None
    
    @classmethod
    def obter_usuario_por_username(cls, username):
        """
        Obtém um usuário pelo username
        
        Args:
            username (str): Username do usuário
            
        Returns:
            CustomUser: Objeto do usuário ou None se não encontrado
        """
        try:
            return CustomUser.objects.get(username=username)
        except CustomUser.DoesNotExist:
            return None
    
    @classmethod
    def listar_usuarios(cls, filtros=None):
        """
        Lista usuários com filtros opcionais
        
        Args:
            filtros (dict): Dicionário com filtros de busca
            
        Returns:
            QuerySet: QuerySet com os usuários encontrados
        """
        queryset = CustomUser.objects.all()
        
        if filtros:
            # Filtro por nome/razão social
            if 'nome' in filtros and filtros['nome']:
                queryset = queryset.filter(
                    Q(nome_razao_social__icontains=filtros['nome']) |
                    Q(first_name__icontains=filtros['nome']) |
                    Q(last_name__icontains=filtros['nome'])
                )
            
            # Filtro por tipo de usuário
            if 'tipo_usuario' in filtros and filtros['tipo_usuario']:
                queryset = queryset.filter(tipo_usuario=filtros['tipo_usuario'])
            
            # Filtro por tipo de plano
            if 'tipo_plano' in filtros and filtros['tipo_plano']:
                queryset = queryset.filter(tipo_plano=filtros['tipo_plano'])
            
            # Filtro por CPF/CNPJ
            if 'cpf_cnpj' in filtros and filtros['cpf_cnpj']:
                queryset = queryset.filter(cpf_cnpj__icontains=filtros['cpf_cnpj'])
            
            # Filtro por email
            if 'email' in filtros and filtros['email']:
                queryset = queryset.filter(email__icontains=filtros['email'])
            
            # Filtro por verificação
            if 'is_verified' in filtros and filtros['is_verified'] is not None:
                queryset = queryset.filter(is_verified=filtros['is_verified'])
        
        return queryset.order_by('-data_cadastro')
    
    @classmethod
    def deletar_usuario(cls, usuario_id):
        """
        Exclui um usuário
        
        Args:
            usuario_id (int): ID do usuário a ser excluído
            
        Raises:
            NotFoundError: Se o usuário não for encontrado
        """
        try:
            usuario = cls.obter_usuario_por_id(usuario_id)
            usuario.delete()
        except CustomUser.DoesNotExist:
            raise NotFoundError(f"Usuário com ID {usuario_id} não encontrado")
    
    @classmethod
    def verificar_usuario(cls, usuario_id):
        """
        Marca um usuário como verificado
        
        Args:
            usuario_id (int): ID do usuário a ser verificado
            
        Returns:
            CustomUser: Objeto do usuário atualizado
        """
        try:
            usuario = cls.obter_usuario_por_id(usuario_id)
            usuario.is_verified = True
            usuario.save()
            return usuario
        except CustomUser.DoesNotExist:
            raise NotFoundError(f"Usuário com ID {usuario_id} não encontrado")
    
    @classmethod
    def alterar_plano(cls, usuario_id, novo_plano):
        """
        Altera o plano de um usuário
        
        Args:
            usuario_id (int): ID do usuário
            novo_plano (str): Novo plano ('gratis' ou 'premium')
            
        Returns:
            CustomUser: Objeto do usuário atualizado
        """
        try:
            usuario = cls.obter_usuario_por_id(usuario_id)
            usuario.tipo_plano = novo_plano
            usuario.save()
            return usuario
        except CustomUser.DoesNotExist:
            raise NotFoundError(f"Usuário com ID {usuario_id} não encontrado")
    
    @classmethod
    def to_dict(cls, usuario):
        """
        Converte um objeto CustomUser para dicionário
        
        Args:
            usuario (CustomUser): Objeto do usuário
            
        Returns:
            dict: Representação em dicionário do usuário
        """
        return usuario.to_dict() if hasattr(usuario, 'to_dict') else {
            'id': usuario.id,
            'username': usuario.username,
            'email': usuario.email,
            'first_name': usuario.first_name,
            'last_name': usuario.last_name,
            'nome_razao_social': usuario.nome_razao_social,
            'cpf_cnpj': usuario.cpf_cnpj,
            'telefone': usuario.telefone,
            'tipo_usuario': usuario.tipo_usuario,
            'is_verified': usuario.is_verified,
            'tipo_plano': usuario.tipo_plano,
            'endereco_rua': usuario.endereco_rua,
            'endereco_numero': usuario.endereco_numero,
            'endereco_complemento': usuario.endereco_complemento,
            'endereco_bairro': usuario.endereco_bairro,
            'endereco_cidade': usuario.endereco_cidade,
            'endereco_estado': usuario.endereco_estado,
            'endereco_cep': usuario.endereco_cep,
            'inscricao_estadual': usuario.inscricao_estadual,
            'inscricao_municipal': usuario.inscricao_municipal,
            'data_nascimento': usuario.data_nascimento.isoformat() if usuario.data_nascimento else None,
            'data_cadastro': usuario.data_cadastro.isoformat() if usuario.data_cadastro else None,
            'atualizado_em': usuario.atualizado_em.isoformat() if usuario.atualizado_em else None,
        }
    
    @classmethod
    def estatisticas_usuarios(cls):
        """
        Retorna estatísticas sobre os usuários
        
        Returns:
            dict: Estatísticas dos usuários
        """
        total_usuarios = CustomUser.objects.count()
        total_motoristas = CustomUser.objects.filter(tipo_usuario='motorista').count()
        total_clientes = CustomUser.objects.filter(tipo_usuario='cliente').count()
        total_admins = CustomUser.objects.filter(tipo_usuario='admin').count()
        total_verificados = CustomUser.objects.filter(is_verified=True).count()
        total_premium = CustomUser.objects.filter(tipo_plano='premium').count()
        
        return {
            'total_usuarios': total_usuarios,
            'total_motoristas': total_motoristas,
            'total_clientes': total_clientes,
            'total_admins': total_admins,
            'total_verificados': total_verificados,
            'total_premium': total_premium,
        }