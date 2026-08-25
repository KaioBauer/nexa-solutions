from rest_framework import generics, status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Chamado
from .serializers import ChamadoSerializer


class ChamadoListCreateView(generics.ListCreateAPIView):
    """
    Lista e cria chamados.

    A listagem aceita o parâmetro de consulta `status` para retornar
    somente os chamados com o status informado, ex.: `?status=ABERTO`.
    """

    serializer_class = ChamadoSerializer

    def get_queryset(self):
        queryset = Chamado.objects.all().order_by("-criado_em")
        status_param = self.request.query_params.get("status")

        if status_param:
            valores_validos = Chamado.Status.values
            if status_param not in valores_validos:
                raise ValidationError(
                    {
                        "status": (
                            f"Status inválido: '{status_param}'. "
                            f"Valores aceitos: {', '.join(valores_validos)}."
                        )
                    }
                )
            queryset = queryset.filter(status=status_param)

        return queryset


class ChamadoDetailView(generics.RetrieveUpdateAPIView):
    queryset = Chamado.objects.all()
    serializer_class = ChamadoSerializer


class IndicadoresView(APIView):
    """
    Retorna o volume total de chamados e a quantidade em cada status.
    """

    def get(self, request):
        queryset = Chamado.objects.all()

        dados = {
            "total": queryset.count(),
            "abertos": queryset.filter(status=Chamado.Status.ABERTO).count(),
            "em_andamento": queryset.filter(status=Chamado.Status.EM_ANDAMENTO).count(),
            "concluidos": queryset.filter(status=Chamado.Status.CONCLUIDO).count(),
        }

        return Response(dados, status=status.HTTP_200_OK)