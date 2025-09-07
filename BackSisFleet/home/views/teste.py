from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

class TesteView(APIView):
    permission_classes = [IsAuthenticated]  # 🔑 aqui você exige autenticação JWT

    def get(self, request, *args, **kwargs):
        return Response({"mensagem": "GET: Você está autenticado!"})

    def post(self, request, *args, **kwargs):
        dados = request.data
        return Response({"mensagem": f"POST: Dados recebidos: {dados}"})
    
    def put(self, request, *args, **kwargs):
        dados = request.data
        return Response({"mensagem": f"PUT: Dados recebidos: {dados}"})

    def delete(self, request, *args, **kwargs):
        dados = request.data
        return Response({"mensagem": f"DELETE: Dados recebidos: {dados}"})
    
    def patch(self, request, *args, **kwargs):
        dados = request.data
        return Response({"mensagem": f"PATCH: Dados recebidos: {dados}"})
    
    