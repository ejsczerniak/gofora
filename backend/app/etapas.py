# -----------------------------------------------------------------------
# Arquivo: gofora/backend/app/etapas.py
# Descrição: Implementa Endpoints para Atualização de Etapas dos CEGs
# Data: 28.09.2025 
# Última modificação: 28.09.2025 
# -----------------------------------------------------------------------

# ➤ Importações e Routers
# ✦ APIRouter     ⟶ Cria Grupo de Rotas de API
# ✦ HTTPException ⟶ Retorno de Erros HTTP
from fastapi import APIRouter, HTTPException

# ➤ Importações de Instâncias de Cliente
# ✦ Supabase ⟶ Operações como Selecionar, Inserir, Atualizar, Deleta
# ✦ Datetime ⟶ Módulo Padrão Python para Manipulação de Datas e Horários
from app.supabase_client import supabase
from datetime import date

# -------------------------------------------------------------------

# ➤ Definição do Router
# ⟶ Define Grupo de Rotas para Etapas
router = APIRouter()

# -------------------------------------------------------------------

# ➤ Decorador Endpoint ATUALIZAÇÃO DE ETAPAS (Rota Patch)
@router.patch("/cegs/{id}/etapa")

# ➤ Função atualizar_etapa ⟶ Atualização/Modificação de Nova Etapa
# ✦ Id ⟶ Id da CEG (Compra em Grupo)
# ✦ Payload ⟶ Dicionário com Dados da Etapa (Etapa, Id, Data...)
def atualizar_etapa(id: str, payload: dict):

    # ✦ nova_etapa ⟶ Próxima Etapa Selecionada por Usuário
    nova_etapa = payload.get("etapa_atual") # Default Value: 'Aberto para Inscrições'::text

    # ⚠︎ 400 ⟶ Nova Etapa Vazia
    if not nova_etapa:
        raise HTTPException(status_code=400, detail="『⚠️』— Nova Etapa Não Informada")

    # ★ campos_data⟶ Mapeia Campos de Data com Descrições
    campos_data = {
        "Pagamento do Envio Internacional": "data_envio_internacional", # Data Envio Internacional (date)
        "Divisão de Tributos e Taxas": "data_divisao_tributos",         # Data Divisão Tributos (date)
        "Pagamento de Frete Nacional": "data_frete_nacional",           # Data Frete Nacional (date)
        "Entrega Concluída": "data_entrega_concluida"                   # Data Entrega Concluída (date)
    }

    # ★ update_data ⟶ Atualização de Etapa 
    update_data = {"etapa_atual": nova_etapa}

    # ★ ⟶ Atualização com Descrição para Hoje
    if nova_etapa in campos_data:
        update_data[campos_data[nova_etapa]] = str(date.today())

    # ★ result⟶ Atualização no Banco de Dados
    result = supabase.table("cegs").update(update_data).eq("id", id).execute()

    # ⚠︎ 404 ⟶ Tratamento de Erro para Atualização Falha
    if not result.data:
        raise HTTPException(status_code=404, detail="『❌』 — Grupo não encontrado")

    # ★ return ⟶ Retorno de Sucesso
    return {"message": "Etapa atualizada com sucesso"}
