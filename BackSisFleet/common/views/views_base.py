# common/views_base.py
from django.views import View
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.http import JsonResponse, HttpResponseBadRequest, HttpResponseServerError
import json

class ViewBase(View):  # <- agora herda de View
    """
    Classe base para lidar com views que exigem autenticação e retornam respostas JSON.
    Suporta os métodos HTTP GET, POST, PUT, DELETE.
    """

    # @method_decorator(login_required(logsin_url='/auth/entrar/'))
    def dispatch(self, request, *args, **kwargs):
        # chama o dispatch original da View
        return super().dispatch(request, *args, **kwargs)

    def process_request_data(self, request, require_body=True):
        if require_body:
            if not request.body:
                return HttpResponseBadRequest("Corpo da requisição vazio.")
            try:
                dados = json.loads(request.body.decode('utf-8'))
                return dados
            except json.JSONDecodeError:
                return HttpResponseBadRequest("JSON inválido.")
        else:
            return {}

    def post(self, request, *args, **kwargs):
        return JsonResponse({"mensagem": "Método POST padrão"}, status=200)

    def get(self, request, *args, **kwargs):
        return JsonResponse({"mensagem": "Método GET padrão"}, status=200)

    def put(self, request, *args, **kwargs):
        return JsonResponse({"mensagem": "Método PUT padrão"}, status=200)

    def delete(self, request, *args, **kwargs):
        return JsonResponse({"mensagem": "Método DELETE padrão"}, status=200)

    def handle_error(self, e):
        return HttpResponseServerError(f"Erro no servidor: {str(e)}")
