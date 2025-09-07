# core/serializers.py
from rest_framework import serializers
from .models import CustomUser

class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = [
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "nome_razao_social",
            "cpf_cnpj",
            "telefone",
            "tipo_usuario",
            "is_verified",
            "tipo_plano",
            "endereco_rua",
            "endereco_numero",
            "endereco_complemento",
            "endereco_bairro",
            "endereco_cidade",
            "endereco_estado",
            "endereco_cep",
            "inscricao_estadual",
            "inscricao_municipal",
            "data_nascimento",
            "data_cadastro",
            "atualizado_em",
        ]
        read_only_fields = ["id", "data_cadastro", "atualizado_em"]

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)

    class Meta:
        model = CustomUser
        fields = [
            "username",
            "email",
            "password",
            "nome_razao_social",
            "cpf_cnpj",
            "telefone",
            "tipo_usuario",
            "tipo_plano",
        ]

    def create(self, validated_data):
        password = validated_data.pop("password")
        user = CustomUser(**validated_data)
        user.set_password(password)
        user.save()
        return user

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

