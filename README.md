# Sistema de Chamados — Nexa Solutions

API REST para abertura, acompanhamento e indicadores de chamados de suporte, desenvolvida em Django + Django REST Framework, com PostgreSQL containerizado via Docker Compose.

## Tecnologias

- Python 3.12
- Django 5
- Django REST Framework
- PostgreSQL 16
- Docker / Docker Compose
- python-dotenv (variáveis de ambiente)

## Estrutura do projeto

```text
nexa-solutions/
├── backend/
│   ├── config/            # settings, urls, wsgi/asgi
│   ├── chamados/          # app: models, serializers, views, tests
│   └── requirements.txt
├── docker/
│   └── entrypoint.sh       # aguarda o banco e aplica migrations
├── frontend/
│   └── index.html          # interface HTML simples (consome a API)
├── docs/
│   └── issues.md            # demandas formais da empresa
├── .env.example
├── Dockerfile
├── docker-compose.yml
└── README.md
```

## Como executar

### Pré-requisitos

- Docker e Docker Compose instalados.

### Passo a passo

1. Clone o repositório e entre na pasta do projeto.
2. Crie o arquivo `.env` a partir do exemplo:

   ```bash
   cp .env.example .env
   ```

   Os valores de exemplo já funcionam para rodar localmente. Em um ambiente real, troque `DJANGO_SECRET_KEY` e `POSTGRES_PASSWORD` por valores próprios — o `.env` nunca deve ser versionado (ele já está no `.gitignore`).

3. Suba os containers:

   ```bash
   docker compose up --build
   ```

   O `docker compose` sobe dois serviços:
   - **db**: PostgreSQL 16, com volume próprio para persistir os dados entre reinicializações.
   - **api**: aplicação Django. Antes de iniciar o servidor, o container aguarda o `db` responder e aplica as migrations automaticamente (veja `docker/entrypoint.sh`).

4. A API estará disponível em `http://localhost:8000/api/`.

### Variáveis de ambiente (`.env`)

| Variável             | Descrição                                          |
|----------------------|-----------------------------------------------------|
| `DJANGO_SECRET_KEY`  | Chave secreta do Django. Obrigatória, sem valor padrão. |
| `DEBUG`              | `True` ou `False`. Padrão: `False`.                 |
| `ALLOWED_HOSTS`      | Hosts permitidos, separados por vírgula.            |
| `POSTGRES_DB`        | Nome do banco. Obrigatória.                         |
| `POSTGRES_USER`      | Usuário do banco. Obrigatória.                      |
| `POSTGRES_PASSWORD`  | Senha do banco. Obrigatória.                        |
| `POSTGRES_HOST`      | Host do banco (`db` dentro do Docker Compose). Obrigatória. |
| `POSTGRES_PORT`      | Porta do banco (`5432`). Obrigatória.               |

As variáveis marcadas como obrigatórias não têm valor padrão no código: se estiverem faltando no `.env`, a aplicação falha imediatamente ao subir, com uma mensagem indicando qual variável configurar — em vez de rodar silenciosamente com um segredo mascarado.

### Frontend

`frontend/index.html` é uma página HTML simples e independente que consome a API. Ela não é servida pelos containers — abra o arquivo diretamente no navegador (duplo clique, ou `start frontend/index.html` no Windows). A página espera a API rodando em `http://localhost:8000`.

## Endpoints

Base: `http://localhost:8000/api/`

### `GET /api/chamados/`

Lista os chamados cadastrados, ordenados do mais recente para o mais antigo.

Aceita o parâmetro opcional `status` para filtrar:

```text
GET /api/chamados/?status=ABERTO
```

Valores aceitos: `ABERTO`, `EM_ANDAMENTO`, `CONCLUIDO`. Um valor fora dessa lista retorna `400 Bad Request` com uma mensagem explicando os valores aceitos.

### `POST /api/chamados/`

Cria um novo chamado.

```json
{
  "titulo": "Impressora com defeito",
  "descricao": "Não imprime desde ontem",
  "status": "ABERTO"
}
```

- `titulo` é **obrigatório** (não pode ser vazio ou conter só espaços). Sem ele, a API responde `400 Bad Request` com `{"titulo": ["O título é obrigatório."]}` — nunca um erro 500.
- `descricao` é opcional.
- `status` é opcional; o padrão é `ABERTO`.

### `GET /api/chamados/<id>/` e `PUT/PATCH /api/chamados/<id>/`

Consulta e atualiza um chamado específico.

### `GET /api/indicadores/`

Retorna a contagem de chamados por status:

```json
{
  "total": 10,
  "abertos": 4,
  "em_andamento": 3,
  "concluidos": 3
}
```

## Testes automatizados

Os testes cobrem os cenários críticos: criação válida, criação sem título, filtro por status e indicadores.

Com os containers no ar (`docker compose up`), rode em outro terminal:

```bash
docker compose exec api python manage.py test chamados
```

## Decisões técnicas

- **PostgreSQL em vez de SQLite**: o repositório-base usava SQLite local; trocamos para Postgres containerizado para refletir um ambiente reproduzível e mais próximo de produção.
- **Sem fallback para segredos**: `SECRET_KEY` e as credenciais do banco não têm valor padrão no código — a aplicação falha alto (`ImproperlyConfigured`) se o `.env` não estiver configurado, em vez de mascarar a ausência de configuração.
- **Entrypoint com espera ativa pelo banco**: o `docker/entrypoint.sh` verifica se a porta do Postgres está respondendo antes de aplicar migrations e subir o servidor, evitando falhas de inicialização por condição de corrida entre os containers.
- **Validação de título via serializer**: em vez de depender só da constraint do modelo, o `ChamadoSerializer` valida e remove espaços em branco, retornando sempre `400` com mensagem clara.
