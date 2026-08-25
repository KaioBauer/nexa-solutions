from django.urls import path

from .views import ChamadoDetailView, ChamadoListCreateView, IndicadoresView

urlpatterns = [
    path(
        "chamados/",
        ChamadoListCreateView.as_view(),
        name="chamado-list-create",
    ),
    path(
        "chamados/<int:pk>/",
        ChamadoDetailView.as_view(),
        name="chamado-detail",
    ),
    path(
        "indicadores/",
        IndicadoresView.as_view(),
        name="indicadores",
    ),
]