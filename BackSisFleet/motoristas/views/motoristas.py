from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from motoristas.services.motorista_service import MotoristaService
from core.service.usuarios_service import UserService
from datetime import datetime
from common.utils.processar_data import processar_datas

class MotoristasView(APIView):
    """
    API View para gerenciar motoristas vinculados a um usuário responsável.

    Permissões:
        - Somente usuários autenticados podem acessar esta view.
    
    Métodos disponíveis:
        - GET: Lista todos os motoristas de um determinado responsável.
        - POST: Cria um novo motorista vinculado ao usuário responsável.
        - PATCH: Recebe dados para atualização parcial (não implementado).
        - PUT: Recebe dados para atualização completa (não implementado).
        - DELETE: Recebe dados para exclusão (não implementado).
    """
    permission_classes = [IsAuthenticated] 
    
    def get(self, request, *args, **kwargs):
        """
        Lista motoristas vinculados ao usuário responsável.

        Regras:
            - Apenas usuários do tipo 'cliente' podem listar motoristas.

        Args:
            request (Request): Objeto de requisição HTTP.

        Returns:
            Response: JSON com a lista de motoristas ou mensagem de erro caso não permitido.
        """
        usuario = request.user 
        if usuario.tipo_usuario == 'cliente':
            motoristas = MotoristaService.listar_motoristas_por_responsavel(usuario.id)
            return Response({"motoristas": motoristas})

        return Response({"mensagem": "Você não tem acesso a esta funcionalidade."}, status=403)

    def post(self, request, *args, **kwargs):
        """
        Cria um novo motorista vinculado ao usuário responsável.

        Regras:
            - Usuários do tipo 'motorista' não podem criar outros motoristas.
            - Campos de data devem estar no formato 'YYYY-MM-DD'.

        Args:
            request (Request): Objeto de requisição HTTP contendo dados do motorista.

        Retorna:
            Response: JSON com mensagem de sucesso e dados do motorista criado ou erro de validação.
        """
        dados = request.data.copy()  # Faz uma cópia para manipular

        usuario = request.user
        if usuario.tipo_usuario == 'motorista':
            return Response({"mensagem": "Não Autorizado"}, status=403)

        user_motorista = UserService.obter_usuario_por_cpf_cnpj(dados.get('cpf_usuario'))

        # Converte campos de data (se existirem)
        campos_data = [
            "data_nascimento", 
            "validade_toxicologico", 
            "cnh_validade", 
            "dt_emissao_cnh", 
            "dt_primeira_cnh"
        ]

        dados_processados, erro = processar_datas(dados, campos_data)
        if erro:
            return Response({"erro": erro}, status=400)

        dados = dados_processados

        dados['usuario_fk'] = user_motorista
        dados['responsavel_fk'] = usuario.id

        motorista = MotoristaService.criar_motorista(dados, usuario)
        return Response({"mensagem": "Motorista criado com sucesso", "motorista": motorista.to_dict()})

    def patch(self, request, *args, **kwargs):
        """
        Recebe dados para atualização parcial de motorista.
        Atualmente apenas retorna os dados recebidos.

        Args:
            request (Request): Objeto de requisição HTTP.

        Returns:
            Response: JSON com dados recebidos.
        """
        dados = request.data
        return Response({"mensagem": f"PATCH: Dados recebidos: {dados}"})

    def put(self, request, *args, **kwargs):
        """
        Recebe dados para atualização completa de motorista.
        Atualmente apenas retorna os dados recebidos.

        Args:
            request (Request): Objeto de requisição HTTP.

        Returns:
            Response: JSON com dados recebidos.
        """
        dados = request.data
        return Response({"mensagem": f"PUT: Dados recebidos: {dados}"})

    def delete(self, request, *args, **kwargs):
        """
        Recebe dados para exclusão de motorista.
        Atualmente apenas retorna os dados recebidos.

        Args:
            request (Request): Objeto de requisição HTTP.

        Returns:
            Response: JSON com dados recebidos.
        """
        dados = request.data
        return Response({"mensagem": f"DELETE: Dados recebidos: {dados}"})

