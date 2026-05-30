╔════════════════════════════════════════════════════════════════════════════╗
║                                                                            ║
║              ✅ AUTENTICAÇÃO COM SUPABASE AUTH NATIVO                       ║
║                      (Versão Corrigida - Mai 2026)                        ║
║                                                                            ║
╚════════════════════════════════════════════════════════════════════════════╝


🔄 O QUE FOI REFATORADO:
═══════════════════════════════════════════════════════════════════════════

REMOVIDO (Abordagem Incorreta):
❌ usuario_repository.py - Não é mais necessário
❌ supabase_adapter.py - Substituído por cliente Supabase nativo
❌ Hash de senha manual (PBKDF2-SHA256) - Supabase gerencia isto
❌ Tabela usuarios no banco de dados - Supabase Auth gerencia identidades
❌ supabase_migrations.sql - Não necessário para Auth

IMPLEMENTADO (Abordagem Correta):
✅ Supabase Auth nativo via supabase.auth.*
✅ Single client instance em config.py
✅ Tokens de sessão automáticos do Supabase
✅ RLS habilitado com row level security
✅ Senhas gerenciadas seguramente pelo Supabase


🎯 COMO FUNCIONA AGORA:
═══════════════════════════════════════════════════════════════════════════

1. CADASTRO (sign_up)
   ─────────────────────
   
   auth_service.criar_usuario(email, nome, senha)
                    ↓
   supabase.auth.sign_up({
       "email": email,
       "password": senha,
       "options": {"data": {"nome": nome}}
   })
   
   • Email e senha gerenciados pelo Supabase Auth
   • Metadados (nome) armazenados em user_metadata
   • Confirmação de email enviada automaticamente
   • Usuário criado em auth.users (tabela interna)


2. LOGIN (sign_in_with_password)
   ──────────────────────────────
   
   auth_service.fazer_login(email, senha)
                    ↓
   supabase.auth.sign_in_with_password({
       "email": email,
       "password": senha
   })
                    ↓
   Retorna:
   • user object (id, email, user_metadata)
   • session object (access_token, refresh_token)
   
   O access_token é automaticamente usado em todas as
   chamadas subsequentes ao banco.


3. LOGOUT (sign_out)
   ──────────────────
   
   auth_service.fazer_logout()
                    ↓
   supabase.auth.sign_out()
   
   • Token de sessão invalidado no servidor
   • Cliente local limpo


4. USUÁRIO ATUAL (get_user)
   ────────────────────────
   
   auth_service.usuario_atual()
                    ↓
   supabase.auth.get_user()
   
   Retorna dados do usuário autenticado


📋 ESTRUTURA DO AUTHSERVICE:
═══════════════════════════════════════════════════════════════════════════

```python
class AuthService:
    def __init__(self):
        # Uma única instância do cliente Supabase
        from config import USE_SUPABASE, SUPABASE_URL, SUPABASE_ANON_KEY
        
        if USE_SUPABASE:
            from supabase import create_client
            self.supabase_client = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)
    
    def criar_usuario(email, nome, senha):
        # Retorna (sucesso, usuario_id, mensagem)
        response = self.supabase_client.auth.sign_up({...})
    
    def fazer_login(email, senha):
        # Retorna (sucesso, usuario_dict, mensagem)
        response = self.supabase_client.auth.sign_in_with_password({...})
        # usuario_dict contém: id, email, nome, token
    
    def fazer_logout():
        # Invalida sessão
        self.supabase_client.auth.sign_out()
    
    def usuario_atual():
        # Retorna dados do usuário logado
        return self.supabase_client.auth.get_user()
```


🔐 SEGURANÇA:
═══════════════════════════════════════════════════════════════════════════

✅ Senhas:
   • Criptografadas pelo Supabase (PBKDF2)
   • Nunca são visíveis para o cliente
   • Verificação segura via Supabase Auth

✅ Tokens:
   • JWT access tokens assinados pelo Supabase
   • Enviados em Authorization header automaticamente
   • Verificados em cada requisição ao banco

✅ RLS (Row Level Security):
   • Políticas de acesso baseadas no user_id do token
   • Dados isolados por usuário automaticamente
   • Supabase valida permissões antes de retornar dados

✅ Sessão:
   • Gerenciada pelo Supabase
   • Token expira em 1 hora
   • Refresh token válido por 1 semana


🚀 COMO USAR:
═══════════════════════════════════════════════════════════════════════════

1. CONFIGURAR .env
   ────────────────
   
   Criar arquivo .env na raiz do projeto (mesmo nível que run.py):
   
   ```
   SUPABASE_URL=https://seu-projeto.supabase.co
   SUPABASE_ANON_KEY=seu_anon_key_aqui
   ```
   
   Obter credenciais em: https://app.supabase.com → Project → Settings → API


2. INICIAR APLICAÇÃO
   ──────────────────
   
   ```bash
   python run.py
   ```
   
   • Se .env não tiver Supabase: usa SQLite localmente
   • Se .env tiver Supabase: conecta automaticamente
   • Ambos suportam auth, mas Supabase é para produção


3. CADASTRAR USUÁRIO
   ──────────────────
   
   Na tela de login:
   1. Clique em "Cadastre-se aqui"
   2. Preencha: Nome, Email, Senha
   3. Clique em "Cadastrar"
   
   • Email é verificado (pode precisar confirmar)
   • Se erro "Email já cadastrado": tente outro email


4. FAZER LOGIN
   ────────────
   
   Na tela de login:
   1. Digite email e senha
   2. Clique em "Entrar"
   
   • Se sucesso: acesso ao dashboard
   • Se erro: mensagem de "Email ou senha incorretos"


5. USAR TOKEN NAS REQUISIÇÕES
   ───────────────────────────
   
   O token é automaticamente incluído em:
   
   ```python
   # Em qualquer repositório:
   supabase.from_('tabela').select('*').execute()
   # O token é enviado automaticamente no header Authorization
   ```


⚙️ VARIÁVEIS EM CONFIG.PY:
═══════════════════════════════════════════════════════════════════════════

```python
# Antes (incorreto):
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
USE_SUPABASE = bool(SUPABASE_URL and SUPABASE_KEY)

# Agora (correto):
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY")
USE_SUPABASE = bool(SUPABASE_URL and SUPABASE_ANON_KEY)
```


📦 DEPENDÊNCIAS:
═══════════════════════════════════════════════════════════════════════════

Adicionar ao requirements.txt:

```
supabase==2.0.3
python-dotenv>=1.0.0
requests>=2.31.0
```

Instalar:
```bash
pip install -r requirements.txt
```


🔗 INTEGRANDO COM BANCO DE DADOS:
═══════════════════════════════════════════════════════════════════════════

Exemplo: Acessar dados com proteção de RLS

```python
# Em um repositório:
class ProdutoRepository:
    def __init__(self):
        from config import USE_SUPABASE
        from supabase import create_client
        
        if USE_SUPABASE:
            self.supabase = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)
    
    def listar_meus_produtos(self):
        # O token é automaticamente incluído
        # RLS verifica: WHERE user_id = auth.uid()
        response = self.supabase.from_('produtos').select('*').execute()
        return response.data
```


⚠️ IMPORTANTE - Sem Modo Offline:
═══════════════════════════════════════════════════════════════════════════

A nova versão REQUER Supabase para autenticação.

Para desenvolvimento local SEM Supabase:
• Será necessário criptografar senhas localmente (PBKDF2)
• Ou usar SQLite com auth manual
• Isto será implementado em futuras versões

Por enquanto: Configure Supabase no .env


📚 ARQUIVO .env.example ATUALIZADO:
═══════════════════════════════════════════════════════════════════════════

Ver arquivo: .env.example


❓ PRÓXIMAS ETAPAS:
═══════════════════════════════════════════════════════════════════════════

1. ✅ FEITO: Remover hash manual de senhas
2. ✅ FEITO: Usar Supabase Auth nativo
3. ⏳ TODO: Adaptar repositórios para RLS
4. ⏳ TODO: Implementar confirmação de email
5. ⏳ TODO: Adicionar recuperação de senha
6. ⏳ TODO: Suporte a 2FA
7. ⏳ TODO: Modo offline com SQLite + hash local


🐛 PROBLEMAS COMUNS:
═══════════════════════════════════════════════════════════════════════════

Problema: "Sistema de autenticação não configurado"
Solução: Crie arquivo .env com SUPABASE_URL e SUPABASE_ANON_KEY

Problema: "Email já cadastrado"
Solução: Use outro email (cada email é único no Supabase Auth)

Problema: "Erro ao fazer login"
Solução: Verifique credenciais do .env (URL e ANON_KEY corretos)

Problema: Sessão expires
Solução: Será implementado refresh token automático


════════════════════════════════════════════════════════════════════════════
            Autenticação segura com Supabase Auth nativo! 🔐
════════════════════════════════════════════════════════════════════════════
