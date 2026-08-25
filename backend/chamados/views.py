from rest_framework import generics
from rest_framework.exceptions import ValidationError

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