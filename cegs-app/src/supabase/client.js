// ------------------------------------------------------------------
// Arquivo: gofora/cegs-app/src/supabase/client.js
// Descrição: Configuração do Cliente Supabase
// ------------------------------------------------------------------   

import { createClient } from '@supabase/supabase-js'

// A URL do seu novo projeto
const SUPABASE_URL = 'https://qmbpifhbbllurgcshupx.supabase.co' 

// A chave pública (anon key) que você forneceu
const SUPABASE_ANON_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InFtYnBpZmhiYmxsdXJnY3NodXB4Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODM2MTg5OTAsImV4cCI6MjA5OTE5NDk5MH0.vKYo5JX0rnOiH8s9ifm0qA6uMQdTSwzZGq6VZuxuaBQ'

export const supabase = createClient(SUPABASE_URL, SUPABASE_ANON_KEY)