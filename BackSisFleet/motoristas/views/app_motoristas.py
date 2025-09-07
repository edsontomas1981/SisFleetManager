from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from motoristas.services.motorista_service import MotoristaService
from core.service.usuarios_service import UserService
from datetime import datetime
from common.utils.processar_data import processar_datas
from veiculos.service.veiculos_service import VeiculoService

class AppMotoristasView(APIView):

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
        print(usuario.to_dict())
        if usuario.tipo_usuario == 'motorista':
            motorista = MotoristaService.obter_motorista_por_cpf(usuario.cpf_cnpj)
            veiculo = VeiculoService.obter_veiculos_por_motorista(motorista.id)
            return Response({"motorista": motorista.to_dict(), "veiculo": veiculo})

        return Response({"mensagem": "Você não tem acesso a esta funcionalidade."}, status=403)

    def post(self, request, *args, **kwargs):
        return Response({"mensagem": "Motorista criado com sucesso", "motorista":" motorista.to_dict()"})

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
