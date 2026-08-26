from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from .models import Chamado


class CriacaoChamadoTests(APITestCase):
    def test_criacao_valida_de_chamado(self):
        url = reverse("chamado-list-create")
        dados = {
            "titulo": "Impressora com defeito",
            "descricao": "Não imprime desde ontem",
            "status": Chamado.Status.ABERTO,
        }

        resposta = self.client.post(url, dados, format="json")

        self.assertEqual(resposta.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Chamado.objects.count(), 1)
        chamado = Chamado.objects.get()
        self.assertEqual(chamado.titulo, "Impressora com defeito")
        self.assertEqual(chamado.status, Chamado.Status.ABERTO)

    def test_criacao_sem_titulo_retorna_400(self):
        url = reverse("chamado-list-create")
        dados = {"descricao": "Chamado sem título"}

        resposta = self.client.post(url, dados, format="json")

        self.assertEqual(resposta.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("titulo", resposta.data)
        self.assertEqual(Chamado.objects.count(), 0)

    def test_criacao_com_titulo_em_branco_retorna_400(self):
        url = reverse("chamado-list-create")
        dados = {"titulo": "   ", "descricao": "Chamado com título em branco"}

        resposta = self.client.post(url, dados, format="json")

        self.assertEqual(resposta.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("titulo", resposta.data)
        self.assertEqual(Chamado.objects.count(), 0)


class FiltroStatusChamadoTests(APITestCase):
    def setUp(self):
        Chamado.objects.create(titulo="Chamado aberto", status=Chamado.Status.ABERTO)
        Chamado.objects.create(titulo="Chamado em andamento", status=Chamado.Status.EM_ANDAMENTO)
        Chamado.objects.create(titulo="Chamado concluído", status=Chamado.Status.CONCLUIDO)

    def test_lista_todos_os_chamados_sem_filtro(self):
        url = reverse("chamado-list-create")

        resposta = self.client.get(url)

        self.assertEqual(resposta.status_code, status.HTTP_200_OK)
        self.assertEqual(len(resposta.data), 3)

    def test_filtra_chamados_por_status(self):
        url = reverse("chamado-list-create")

        resposta = self.client.get(url, {"status": Chamado.Status.ABERTO})

        self.assertEqual(resposta.status_code, status.HTTP_200_OK)
        self.assertEqual(len(resposta.data), 1)
        self.assertEqual(resposta.data[0]["status"], Chamado.Status.ABERTO)

    def test_filtro_com_status_invalido_retorna_400(self):
        url = reverse("chamado-list-create")

        resposta = self.client.get(url, {"status": "INEXISTENTE"})

        self.assertEqual(resposta.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("status", resposta.data)


class IndicadoresChamadoTests(APITestCase):
    def test_indicadores_contam_chamados_por_status(self):
        Chamado.objects.create(titulo="Aberto 1", status=Chamado.Status.ABERTO)
        Chamado.objects.create(titulo="Aberto 2", status=Chamado.Status.ABERTO)
        Chamado.objects.create(titulo="Em andamento", status=Chamado.Status.EM_ANDAMENTO)
        Chamado.objects.create(titulo="Concluído", status=Chamado.Status.CONCLUIDO)

        url = reverse("indicadores")
        resposta = self.client.get(url)

        self.assertEqual(resposta.status_code, status.HTTP_200_OK)
        self.assertEqual(resposta.data["total"], 4)
        self.assertEqual(resposta.data["abertos"], 2)
        self.assertEqual(resposta.data["em_andamento"], 1)
        self.assertEqual(resposta.data["concluidos"], 1)

    def test_indicadores_sem_chamados_cadastrados(self):
        url = reverse("indicadores")

        resposta = self.client.get(url)

        self.assertEqual(resposta.status_code, status.HTTP_200_OK)
        self.assertEqual(resposta.data["total"], 0)
        self.assertEqual(resposta.data["abertos"], 0)
        self.assertEqual(resposta.data["em_andamento"], 0)
        self.assertEqual(resposta.data["concluidos"], 0)
