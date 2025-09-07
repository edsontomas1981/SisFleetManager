from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from veiculos.service.veiculos_service import VeiculoService
from motoristas.services.motorista_service import MotoristaService

class VeiculosView(APIView):
    permission_classes = [IsAuthenticated] 
    
    def get(self, request, *args, **kwargs):
        return Response({"mensagem": "GET: Você está autenticado!"})

    def post(self, request, *args, **kwargs):
        dados = request.data
        usuario = request.user 
        if usuario.tipo_usuario == 'cliente':
            motorista = MotoristaService.obter_motorista_por_cpf(dados.get("cpf_cnpj"))
            dados["motorista"] = motorista.id if motorista else None
            veiculos = VeiculoService.criar_veiculo(dados, usuario) 
            return Response({"motorista": motorista.to_dict()})
        return Response({"mensagem": f"POST: Dados recebidos: {dados}"})
    
    def put(self, request, *args, **kwargs):
        dados = request.data
        return Response({"mensagem": f"PUT: Dados recebidos: {dados}"})

    def delete(self, request, *args, **kwargs):
        dados = request.data
        return Response({"mensagem": f"DELETE: Dados recebidos: {dados}"})