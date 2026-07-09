# -------------------------------------------------------------------
# Arquivo: gofora/backend/app/auth.py
# Descrição: Implementa Endpoints de Autenticação
# Autor: Eduardo José
# Data: 28.09.2025 
# Última modificação: 01.10.2025 
# -------------------------------------------------------------------

# ➤ Importações e Routers (FASTAPI)
# ✦ APIRouter     ⟶ Cria Grupo de Rotas de API
# ✦ HTTPException ⟶ Retorno de Erros HTTP
from fastapi import APIRouter, HTTPException 

# ➤ Importações de Instâncias de Cliente
# ✦ Supabase ⟶ Operações como Selecionar, Inserir, Atualizar, Deletar
from app.supabase_client import supabase

# -------------------------------------------------------------------

# ➤ Definição do Router
# ⟶ Define Grupo de Rotas para Autenticação
router = APIRouter()

# -------------------------------------------------------------------

# ➤ Decorador Endpoint REGISTRO de Usuário (Rota POST)

@router.post("/auth/register")

# ➤ Função register_user ⟶ Registro/Validação de Usuário
# ✦ Payload ⟶ Formato JSON com Dados do Usuário de Registro (email, senha, etc.)
def register_user(payload: dict):               # Registro de Usuário:
    email = payload.get("email")                # Email do Usuário (text)
    senha = payload.get("senha")                # Senha do Usuário (text)
    nome  = payload.get("nome")                 # Nome do Usuário (text)
    role  = payload.get("role",                 # Role/Tipo de Usuário (text)
                        "participante")         # ⤷ Valor Padrão Participante

    # ⚠︎ 400 ⟶ Se Email ou Senha for Vazio (400 Bad Request)
    if not email or not senha:
        raise HTTPException(status_code=400, detail="『⚠️』 — Email e Senha são OBRIGATÓRIOS!")

    # ⚠︎ 400 ⟶ Verifica se o Email já Existe
    existing = supabase.table("usuarios").select("id").eq("email", email).execute().data
    if existing:
        raise HTTPException(status_code=400, detail="『⚠️』 — Email JÁ Cadastrado!")

    # ★ usuarios ⟶ Insere Novo Usuário no Banco de Dados
    supabase.table("usuarios").insert({
        "email": email,  # E-Mail Único (text)
        "senha": senha,  # Recomendado: Hash de Senha  (text)
        "nome": nome,    # Nome Completo do Usuário (text)
        "role": role     # Participante ou Organizador (text)
    }).execute()

    # ⟶ Retorno de Mensagem em JSON
    return {"message": "『👤』 — Usuário cadastrado com sucesso"}

# -------------------------------------------------------------------

# ➤ Decorador Endpoint LOGIN de Usuário (Rota POST)

@router.post("/auth/login")

# ✦ Função login_user ⟶ Login/Validação Usuário
# ✦ Payload ⟶ Formato JSON com Dados do Usuário de Registro (email, senha, etc.)
def login_user(payload: dict):             # Login de Usuário
    email = payload.get("email")           # Email do Usuário (text)
    senha = payload.get("senha")           # Senha do Usuário (text)

    # ⚠︎ 400 ⟶ Se E-Mail ou Senha for Vazio (400 Bad Request)
    if not email or not senha:
        raise HTTPException(status_code=400, detail="『⚠️』 — Email e senha são obrigatórios")

    # ★ result ⟶ Busca Usuário com Email e Senha
    result = supabase.table("usuarios").select("*").eq("email", email).eq("senha", senha).execute().data

    # ⚠︎ 401 ⟶ Se a Busca for Incorreta:
    if not result:
        raise HTTPException(status_code=401, detail="『⚠️』 — Credenciais inválidas")

    user = result[0]

    # ★ return ⟶ Retorno Sucesso
    return {
        "message": "『👤』 — Login realizado com sucesso",
        "usuario": {                
            "id": user["id"],       # Id Usuário (uuid) / Default: gen_random_uuid()
            "nome": user["nome"],   # Nome Usuário (text)
            "email": user["email"], # Email Usuário (text)
            "role": user["role"]    # Participante ou Organizador (text)
        }
    }
