from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import RegisterSerializer
from .models import CustomUser
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import AccessToken
from datetime import timedelta
from django.contrib.auth import get_user_model

User = get_user_model()

class HelloView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        
        return Response({"message": f"Olá, {request.user.username}! API protegida ok."})

class RegisterView(generics.CreateAPIView):
    queryset = CustomUser.objects.all()  
    permission_classes = [permissions.AllowAny]  
    serializer_class = RegisterSerializer


class SolicitarRecuperacaoSenhaView(APIView):
    """
    Solicita a recuperação de senha por email ou cpf_cnpj.
    Retorna um token JWT temporário (30 minutos).
    """
    def post(self, request):
        email = request.data.get("email")
        cpf_cnpj = request.data.get("cpf_cnpj")

        try:
            if email:
                usuario = User.objects.get(email=email)
            elif cpf_cnpj:
                usuario = User.objects.get(cpf_cnpj=cpf_cnpj)
            else:
                return Response({"erro": "Informe email ou cpf_cnpj"}, status=status.HTTP_400_BAD_REQUEST)

        except User.DoesNotExist:
            return Response({"erro": "Usuário não encontrado"}, status=status.HTTP_404_NOT_FOUND)

        # Gera token temporário
        token = AccessToken.for_user(usuario)
        token.set_exp(lifetime=timedelta(minutes=30))  # expira em 30 minutos

        # Para testes via Insomnia vamos retornar direto o token
        return Response({
            "mensagem": "Token de recuperação gerado com sucesso",
            "token_recuperacao": str(token),
            "usuario": usuario.to_dict()
        })


class RedefinirSenhaView(APIView):
    """
    Redefine a senha do usuário a partir de um token JWT válido.
    """
    def post(self, request):
        token_recuperacao = request.data.get("token")
        nova_senha = request.data.get("nova_senha")

        if not token_recuperacao or not nova_senha:
            return Response({"erro": "Token e nova_senha são obrigatórios"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            token = AccessToken(token_recuperacao)
            usuario = User.objects.get(id=token["user_id"])
        except Exception as e:
            return Response({"erro": f"Token inválido ou expirado: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)

        usuario.set_password(nova_senha)
        usuario.save()

        return Response({"mensagem": "Senha alterada com sucesso!"}, status=status.HTTP_200_OK)
