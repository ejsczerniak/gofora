# ------------------------------------------------------------------ 
# Arquivo: gofora/backend/app/main.py
# Descrição: Ponto de Entrada da Aplicação FastAPI
# Data: 28.09.2025 
# Última modificação: 28.09.2025 
# -------------------------------------------------------------------

# ➤ Importações e Routers (FASTAPI)
# ✦ APIRouter      ⟶ Cria Grupo de Rotas de API
# ✦ HTTPException  ⟶ Retorno de Erros HTTP
# ✦ CORSMiddleware ⟶  Cross-Origin Resource Sharing (React Acessa API)
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

# ➤ Importações de Instâncias de Cliente
# ✦ Supabase ⟶ Operações como Selecionar, Inserir, Atualizar, Deletar
# ✦ Auth     ⟶ Autenticação Registro/Login
# ✦ Etapas   ⟶ Etapas de CEG (Compras em Grupo)
from app.supabase_client import supabase
from app import auth
from app import etapas

# -------------------------------------------------------------------

# ➤ Instância Principal Aplicação
app = FastAPI()

# -------------------------------------------------------------------

# ➤ Libera Requisições do FrontEnd
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permissão Qualquer Site Acessar API
    allow_methods=["*"],  # Permissão de TODOS Métodos (GET ,POST, PATCH, DELETE...)
    allow_headers=["*"]   # Permissão de TODOS Cabeçalhos HTTP
)

# ➤ Rota de Autenticação (Registro/Login e Etapas de Compra)
app.include_router(auth.router)    # @router.post("/auth/login") e @router.post("/auth/register")
app.include_router(etapas.router)  # @router.patch("/cegs/{id}/etapa")

# -------------------------------------------------------------------

# ➤ Decorador Endpoint Base de TESTE (Rota GET)
@app.get("/")

# ✦ Função read_root ⟶ http://localhost:8001/ API ONLINE!
def read_root():
    return {"message": "API rodando com sucesso!"}

# -------------------------------------------------------------------

# ➤ Decorador Endpoint Listagem de CEGs Existentes (Rota GET)
@app.get("/cegs")

# ✦ Função listar_cegs ⟶ Lista das CEGs do Banco de Dados
def listar_cegs():

    # ✦ res ⟶ Resultado Lista CEGs
    res = supabase.table("cegs").select("*").execute()
    return res.data

# -------------------------------------------------------------------

# ➤ Decorador Endpoint Lista de CEGs do Usuário Organizador (Rota GET)
@app.get("/cegs/mine")

# ✦ Função listar_grupos_do_organizador ⟶ Exemplo: /cegs/mine?usuario_id=abc123
def listar_grupos_do_organizador(usuario_id: str = Query(...)):

    # ⚠︎ ⟶  Usuário ID NÃO Inserido
    if not usuario_id:
        raise HTTPException(status_code=400, detail="『⚠️』— ID do usuário é obrigatório")

    # ✦ grupos ⟶ Tabela CEGS
    grupos = supabase.table("cegs").select("*").eq("organizador_id", usuario_id).execute()

    return grupos.data

# -------------------------------------------------------------------

# ➤ Decorador Endpoint Inserção Novo CEG (Rota POST)
@app.post("/cegs")

# ➤ Função criar_ceg ⟶ Criação de Compra de Grupo
# ✦ Payload ⟶  Dicionário com Dados da CEG ou Produtos
def criar_ceg(payload: dict):

    # ✦ ceg_data ⟶ JSON Dados Registro CEG (Nome, Loja, País...) para Busca
    ceg_data = {
        "nome": payload.get("nome"),                    # Nome (text) / Default:'sem_nome'::text
        "loja": payload.get("loja"),                    # Loja (text)
        "pais": payload.get("pais"),                    # País (text)
        "status": payload.get("status", "Aberta"),      # Status (text)
        "organizador_id": payload.get("organizador_id") # Organizador ID (uuid)
    }

    # ✦ ceg ⟶ Tabela CEG para Inserção
    ceg = supabase.table("cegs").insert(ceg_data).execute().data[0]

    # ✦ ceg_id ⟶ CEG ID (Recebe Valor)
    ceg_id = ceg["id"] # CEG ID (UUID) / Default: gen_random_uuid()

    # ✦ produtos ⟶ Produtos para CEGs (Nome, Preço, CEG) para Inserção
    produtos = payload.get("produtos", [])
    for p in produtos:
        supabase.table("produtos").insert({
            "nome": p["nome"],           # Nome Produto (text)
            "preco": float(p["preco"]),  # Preço (numeric)
            "ceg_id": ceg_id             # CEG ID (Foreign Key) / Default: gen_random_uuid()
        }).execute()

    return ceg

# -------------------------------------------------------------------

# ➤ Decorador Endpoint Listafem de Participantes Existentes (Rota GET)
@app.get("/cegs/{id}/participantes")

# ➤ Função listar_participantes ⟶ Lista de Participantes de um CEG 
def listar_participantes(id: str):

    # ✦ participantes ⟶ Tabela Participantes
    participantes = supabase.table("participantes").select("*").eq("ceg_id", id).execute()
    return participantes.data

# -------------------------------------------------------------------

# ➤ Decorador Endpoint Adição Novo Participante CEG (Rota POST)
@app.post("/participantes")

# ➤ Função adicionar_participante ⟶ Adição de Novo Participante a um CEG
# ✦ Payload ⟶  Dicionário de Dados de Participantes (Nome, CEG, Produtos)
def adicionar_participante(payload: dict):
    nome = payload.get("nome")
    ceg_id = payload.get("ceg_id")
    produtos = payload.get("produtos", [])  # lista: [{ produto_id, quantidade }]

    # ⚠︎ 400 ⟶ Se Nome ou Produtos NÃO forem Informados
    if not nome or not produtos:
        raise HTTPException(status_code=400, detail="『⚠️』— Nome e produtos são obrigatórios")

    # ✦ participante ⟶ Cria o participante da Tabela 'participantes'
    participantes = supabase.table("participantes").insert({
        "nome": nome,       # Nome Participante (text) / Default 'sem_nome'::text
        "ceg_id": ceg_id,   # CEG ID (Foreign Key)     / Default gen_random_uuid()
        "total": 0          # Total (numeric)          / Default 0
    }).execute().data[0]

    # ✦ participante_id ⟶ Recebe Id 
    participante_id = participantes["id"] # Participante ID (int8)

    # ✦ total_geral ⟶ Total Geral Produtos
    total_geral = 0 # Default 0

    # ✦ item ⟶ Busca Tabela 'produtos'
    for item in produtos:
        produto_id = item.get("produto_id")    # ID Produto (uuid) / Default gen_random_uuid()
        quantidade = item.get("quantidade", 1) # Quantidade        / Default 1

        # ✦ Produto ID ou Quantidade VAZIO ⟶ IGNORADO
        if not produto_id or quantidade <= 0:
            continue

        # ✦ produto ⟶ Busca de Preço
        produto = supabase.table("produtos").select("preco").eq("id", produto_id).execute().data
        if not produto:
            continue

        # ✦ preco_unitario ⟶ Conversão para Float por Unidade
        preco_unitario = float(produto[0]["preco"])
        # ✦ total_item ⟶ Cálculo Preço Item por Unidade
        total_item = preco_unitario * quantidade
        # ✦ total_geral ⟶  Soma Total do Participante Acumulado
        total_geral += total_item

        # ✦ participante_produtos ⟶ Salva Relação no Banco de Dados
        supabase.table("participante_produtos").insert({
            "participante_id": participante_id, # Participante ID (Foreign Key int8)
            "produto_id": produto_id,           # Produto ID (Foreign Key uuid)
            "quantidade": quantidade,           # Quantidade (int4)
            "valor_unitario": preco_unitario    # Valor Unitário (numeric)
        }).execute()

    # ✦ participantes ⟶ Atualiza Total Final no Banco de Dados 
    supabase.table("participantes").update({"total": total_geral}).eq("id", participante_id).execute()

    # ✦ return ⟶ Adição Sucesso
    return {"message": "Participante adicionado com sucesso"}

