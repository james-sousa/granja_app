╔════════════════════════════════════════════════════════════════════════════╗
║                                                                            ║
║         COMPARAÇÃO: ANTES (Errado) vs DEPOIS (Correto)                     ║
║                                                                            ║
╚════════════════════════════════════════════════════════════════════════════╝


❌ ANTES (ABORDAGEM INCORRETA):
═══════════════════════════════════════════════════════════════════════════

Arquivo: auth_service.py

```python
import hashlib
import hmac

class AuthService:
    def __init__(self):
        from ..database.supabase_adapter import supabase  # Classe customizada
        self.supabase = supabase
    
    @staticmethod
    def hash_senha(senha: str, salt: str = "granja_manager_2026") -> str:
        # ❌ Implementação manual de PBKDF2
        return hashlib.pbkdf2_hmac(
            'sha256',
            senha.encode('utf-8'),
            salt.encode('utf-8'),
            100000
        ).hex()
    
    def fazer_login(self, email: str, senha: str):
        # ❌ Buscando usuário em tabela usuarios
        resultados = supabase.query(
            "usuarios",
            filters={"email": email, "ativo": 1}
        )
        
        # ❌ Verificando hash manualmente
        if not self.verificar_senha(senha, usuario_data['senha_hash']):
            return False, None, "Email ou senha incorretos"
        
        return True, usuario_data, ""
    
    def criar_usuario(self, email: str, nome: str, senha: str):
        # ❌ Hashando senha localmente
        senha_hash = self.hash_senha(senha)
        
        # ❌ Inserindo em tabela usuarios no banco
        data = {
            "id": usuario_id,
            "email": email,
            "nome": nome,
            "senha_hash": senha_hash,  # ❌ Guardando hash no banco!
            "ativo": 1,
        }
        
        result = supabase.insert("usuarios", data)
        return True, usuario_id, ""
```

Problemas:
❌ Senhas hasheadas localmente (podem ter vulnerabilidades)
❌ Usa tabela usuarios customizada (duplicação com Supabase Auth)
❌ supabase_adapter.py - abstração desnecessária
❌ Responsabilidade de segurança do cliente
❌ RLS não funcionaria pois usa auth.uid() do Supabase Auth
❌ Requer tabela usuarios e supabase_migrations.sql


Arquivo: supabase_adapter.py (REMOVIDO)

```python
# ❌ Classe desnecessária que encapsula cliente Supabase
from supabase import create_client

class SupabaseAdapter:
    def __init__(self):
        self.client = create_client(SUPABASE_URL, SUPABASE_KEY)
    
    def query(self, table, filters=None):
        # ❌ Abstração que apenas complica
        ...
    
    def insert(self, table, data):
        # ❌ Wrapper customizado
        ...
```

Problema: Desnecessária. O cliente Supabase já tem tudo.


Arquivo: usuario_repository.py (REMOVIDO)

```python
# ❌ Repositório customizado para tabela usuarios
from ..database.supabase_adapter import supabase

class UsuarioRepository:
    def find_by_email(self, email):
        resultados = supabase.query("usuarios", filters={"email": email})
        ...
```

Problema: Duplica funcionalidade do Supabase Auth


Arquivo: supabase_migrations.sql (REMOVIDO)

```sql
-- ❌ Tabela usuarios desnecessária
CREATE TABLE usuarios (
    id UUID PRIMARY KEY,
    email TEXT UNIQUE NOT NULL,
    nome TEXT NOT NULL,
    senha_hash TEXT NOT NULL,  -- ❌ Guardando hash em plain text no banco!
    ativo BOOLEAN DEFAULT true,
    criado_em TIMESTAMP,
    ultimo_acesso TIMESTAMP
);
```

Problema: Duplica auth.users (tabela interna do Supabase Auth)


Arquivo: config.py (Antes)

```python
SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")  # ❌ Chave errada
USE_SUPABASE = bool(SUPABASE_URL and SUPABASE_KEY)
```

Problema: SUPABASE_KEY deveria ser SUPABASE_ANON_KEY


═══════════════════════════════════════════════════════════════════════════


✅ DEPOIS (ABORDAGEM CORRETA):
═══════════════════════════════════════════════════════════════════════════

Arquivo: auth_service.py (REFATORADO)

```python
# ✅ Sem imports de hash ou hmac - deixa pro Supabase!

class AuthService:
    def __init__(self):
        # ✅ Cliente Supabase nativo
        from supabase import create_client
        self.supabase_client = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)
    
    def criar_usuario(self, email: str, nome: str, senha: str):
        # ✅ Delega para Supabase Auth nativo
        response = self.supabase_client.auth.sign_up({
            "email": email,
            "password": senha,
            "options": {
                "data": {"nome": nome}  # ✅ Metadados customizados
            }
        })
        
        if response.user:
            return True, response.user.id, "Usuário cadastrado com sucesso"
        return False, None, "Erro ao cadastrar"
    
    def fazer_login(self, email: str, senha: str):
        # ✅ Usa Supabase Auth nativo
        response = self.supabase_client.auth.sign_in_with_password({
            "email": email,
            "password": senha
        })
        
        if response.user:
            usuario = {
                "id": response.user.id,
                "email": response.user.email,
                "nome": response.user.user_metadata.get("nome"),
                "token": response.session.access_token  # ✅ Token automaticamente
            }
            return True, usuario, "Login realizado"
        
        return False, None, "Email ou senha incorretos"
    
    def fazer_logout(self):
        # ✅ Invalida sessão no servidor
        self.supabase_client.auth.sign_out()
        return True
    
    def usuario_atual(self):
        # ✅ Retorna usuário autenticado pelo token
        user = self.supabase_client.auth.get_user()
        if user:
            return {
                "id": user.user.id,
                "email": user.user.email,
                "nome": user.user.user_metadata.get("nome"),
            }
        return None
```

Benefícios:
✅ Segurança: Senhas gerenciadas pelo Supabase (PBKDF2, bcrypt, etc.)
✅ Token automático: JWT assinado, enviado em todas as requisições
✅ RLS funciona: auth.uid() retorna o user_id do token
✅ Sem tabela usuarios duplicada: Usa auth.users do Supabase
✅ Simples: Apenas chamadas diretas ao Supabase Auth
✅ Escalável: Suporta múltiplos usuários, sessões, etc.


Arquivo: config.py (CORRIGIDO)

```python
SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY", "")  # ✅ Anon key correta!
USE_SUPABASE = bool(SUPABASE_URL and SUPABASE_ANON_KEY)
```

Benefício: Usa a chave pública (ANON_KEY) para operações públicas (auth, dados com RLS)


Arquivos REMOVIDOS:
✅ usuario_repository.py - Não é necessário
✅ supabase_adapter.py - Cliente Supabase nativo é suficiente
✅ supabase_migrations.sql - Auth é gerenciado pelo Supabase


═══════════════════════════════════════════════════════════════════════════


🔄 FLUXO ANTES (Errado):
═══════════════════════════════════════════════════════════════════════════

┌─────────────────────┐
│ Usuário clica LOGIN │
└──────────┬──────────┘
           ↓
┌──────────────────────────────┐
│ app.py chama:                │
│ auth_service.fazer_login()   │
└──────────┬───────────────────┘
           ↓
┌──────────────────────────────────────┐
│ auth_service.py:                     │
│ 1. Query: SELECT * FROM usuarios     │ ❌ Tabela customizada
│ 2. hash_senha(senha_digitada)        │ ❌ Hash manual
│ 3. Compare: hash == senha_hash       │ ❌ No cliente
│ 4. Retorna: usuario_data             │
└──────────┬───────────────────────────┘
           ↓
┌──────────────────────────────┐
│ Usuário logado, mas:         │
│ ❌ Sem token seguro          │
│ ❌ RLS não funciona          │
│ ❌ Senha em hash inseguro    │
└──────────────────────────────┘


✅ FLUXO DEPOIS (Correto):
═══════════════════════════════════════════════════════════════════════════

┌─────────────────────┐
│ Usuário clica LOGIN │
└──────────┬──────────┘
           ↓
┌────────────────────────────────────────┐
│ app.py chama:                          │
│ auth_service.fazer_login(email, senha) │
└──────────┬─────────────────────────────┘
           ↓
┌──────────────────────────────────────────────────┐
│ auth_service.py:                                 │
│ self.supabase_client.auth                        │ ✅ Nativo
│   .sign_in_with_password({                       │
│      email, password                             │
│   })                                             │
└──────────┬───────────────────────────────────────┘
           ↓
┌──────────────────────────────────────────────────┐
│ Supabase Auth (Servidor):                        │
│ 1. Lookup: SELECT * FROM auth.users WHERE email │ ✅ Interna
│ 2. Verifica: PBKDF2(senha) == senha_hash        │ ✅ Seguro
│ 3. Gera: JWT access_token + refresh_token       │ ✅ Tokens
│ 4. Retorna: user + session                      │
└──────────┬───────────────────────────────────────┘
           ↓
┌──────────────────────────────────────────────────┐
│ AuthService recebe:                              │
│ {                                                │
│   user: {id, email, user_metadata},             │ ✅ Do servidor
│   session: {access_token, refresh_token}        │ ✅ Seguro
│ }                                                │
└──────────┬───────────────────────────────────────┘
           ↓
┌──────────────────────────────────────────────────┐
│ Usuário logado E:                                │
│ ✅ Token JWT seguro                             │
│ ✅ RLS funciona (auth.uid() = user_id)          │
│ ✅ Senha validada no servidor                   │
│ ✅ Token usado em todas as requisições          │
│ ✅ Sessão gerenciada pelo Supabase              │
└──────────────────────────────────────────────────┘


═══════════════════════════════════════════════════════════════════════════


📊 COMPARAÇÃO DE SEGURANÇA:
═══════════════════════════════════════════════════════════════════════════

Aspecto              │ Antes (❌)          │ Depois (✅)
─────────────────────┼─────────────────────┼────────────────────────
Gerenciamento senha  │ Manual (PBKDF2)     │ Supabase (PBKDF2+)
Armazenamento hash   │ Tabela usuarios     │ auth.users (interno)
Verificação senha    │ Cliente (inseguro)  │ Servidor (seguro)
Token de acesso      │ Nenhum              │ JWT signed
Segurança em transit │ Depende de app      │ HTTPS + JWT
Row Level Security   │ ❌ Não funciona     │ ✅ Via auth.uid()
Escalabilidade       │ ❌ Limitada         │ ✅ Multi-user
Conformidade         │ ❌ Fraca            │ ✅ SOC2, GDPR
Gerenciamento sessão │ Manual              │ Automático


═══════════════════════════════════════════════════════════════════════════
                    🎯 Use Supabase Auth Nativo! 🔐
═══════════════════════════════════════════════════════════════════════════
