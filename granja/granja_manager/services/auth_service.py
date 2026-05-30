"""Serviço de Autenticação com Supabase Auth Nativo"""

import logging
from typing import Optional, Tuple

logger = logging.getLogger(__name__)


class AuthService:
    """Autenticação usando Supabase Auth nativo (sem hash local)."""

    def __init__(self):
        """Inicializa cliente Supabase para autenticação."""
        self.supabase_client = None
        self.usuario_logado: Optional[dict] = None
        
        try:
            from config import SUPABASE_URL, SUPABASE_ANON_KEY
            
            if SUPABASE_URL and SUPABASE_ANON_KEY:
                from supabase import create_client
                self.supabase_client = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)
                logger.info("✅ Supabase Auth inicializado")
            else:
                logger.error("❌ SUPABASE_URL ou SUPABASE_ANON_KEY não configurados")
                
        except Exception as e:
            logger.error(f"❌ Erro ao inicializar Supabase: {e}")

    def _validar_email(self, email: str) -> bool:
        """Valida formato de email."""
        if not email or "@" not in email:
            return False
        return True

    def _validar_senha(self, senha: str) -> Tuple[bool, str]:
        """Valida força mínima da senha."""
        if len(senha) < 6:
            return False, "Mínimo 6 caracteres"
        return True, ""

    def cadastrar(self, email: str, nome: str, senha: str) -> Tuple[bool, Optional[str], str]:
        """Cadastra novo usuário no Supabase Auth.
        
        Args:
            email: Email do usuário
            nome: Nome completo
            senha: Senha (Supabase valida força)
            
        Returns:
            (sucesso, usuario_id, mensagem)
        """
        try:
            if not self.supabase_client:
                return False, None, "Autenticação não configurada"
            
            email = email.strip().lower()
            if not self._validar_email(email):
                return False, None, "Email inválido"
            
            if not nome or len(nome) < 3:
                return False, None, "Nome inválido (mín. 3 caracteres)"
            
            valido, msg = self._validar_senha(senha)
            if not valido:
                return False, None, f"Senha: {msg}"
            
            # Cadastrar no Supabase Auth
            response = self.supabase_client.auth.sign_up({
                "email": email,
                "password": senha,
                "options": {"data": {"nome": nome}}
            })
            
            if response.user:
                logger.info(f"✅ Usuário cadastrado: {email}")
                return True, response.user.id, "Cadastro realizado"
            
            return False, None, "Erro ao cadastrar"
            
        except Exception as e:
            msg = str(e).lower()
            if "already registered" in msg:
                return False, None, "Email já cadastrado"
            if "weak password" in msg:
                return False, None, "Senha muito fraca"
            logger.error(f"❌ Erro ao cadastrar: {e}")
            return False, None, str(e)

    def login(self, email: str, senha: str) -> Tuple[bool, Optional[dict], str]:
        """Faz login com email e senha no Supabase Auth.
        
        Args:
            email: Email do usuário
            senha: Senha
            
        Returns:
            (sucesso, dados_usuario, mensagem)
        """
        try:
            if not self.supabase_client:
                return False, None, "Autenticação não configurada"
            
            email = email.strip().lower()
            if not self._validar_email(email):
                return False, None, "Email inválido"
            
            # Login via Supabase Auth
            response = self.supabase_client.auth.sign_in_with_password({
                "email": email,
                "password": senha
            })
            
            if response.user and response.session:
                # Extrair dados do usuário com fallback robusto
                nome = (response.user.user_metadata.get('nome') or 
                        response.user.user_metadata.get('full_name') or 
                        response.user.email.split('@')[0])
                
                self.usuario_logado = {
                    "id": response.user.id,
                    "email": response.user.email,
                    "nome": nome,
                    "token": response.session.access_token
                }
                logger.info(f"✅ Login: {email}")
                return True, self.usuario_logado, "Login realizado"
            
            logger.warning(f"❌ Login falhou: {email}")
            return False, None, "Email ou senha incorretos"
            
        except Exception as e:
            msg = str(e).lower()
            if "invalid login credentials" in msg:
                return False, None, "Email ou senha incorretos"
            if "email not confirmed" in msg:
                return False, None, "Email não confirmado"
            logger.error(f"❌ Erro login: {e}")
            return False, None, str(e)

    def logout(self) -> bool:
        """Faz logout no Supabase Auth."""
        try:
            if not self.supabase_client:
                return False
            
            self.supabase_client.auth.sign_out()
            self.usuario_logado = None
            logger.info("✅ Logout realizado")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro logout: {e}")
            return False

    def usuario_atual(self) -> Optional[dict]:
        """Retorna dados do usuário logado."""
        try:
            if not self.supabase_client:
                return None
            
            user = self.supabase_client.auth.get_user()
            if user:
                return {
                    "id": user.user.id,
                    "email": user.user.email,
                    "nome": user.user.user_metadata.get("nome", user.user.email.split("@")[0])
                }
            return None
            
        except Exception as e:
            logger.warning(f"⚠️  Erro ao obter usuário: {e}")
            return None

    def obter_usuario_logado(self) -> Optional[dict]:
        """Retorna usuário armazenado em memória."""
        return self.usuario_logado

    def esta_logado(self) -> bool:
        """Verifica se há sessão ativa."""
        return self.usuario_logado is not None

    def recuperar_senha(self, email: str) -> Tuple[bool, str]:
        """Envia email para recuperação de senha.
        
        Args:
            email: Email do usuário
            
        Returns:
            (sucesso, mensagem)
        """
        try:
            if not self.supabase_client:
                return False, "Autenticação não configurada"
            
            email = email.strip().lower()
            if not self._validar_email(email):
                return False, "Email inválido"
            
            # Usar API REST do Supabase para reset de senha
            from config import SUPABASE_URL, SUPABASE_ANON_KEY
            import requests
            
            url = f"{SUPABASE_URL}/auth/v1/recover"
            headers = {
                "apikey": SUPABASE_ANON_KEY,
                "Content-Type": "application/json"
            }
            payload = {
                "email": email,
                "gotrue_meta_security": {}
            }
            
            response = requests.post(url, json=payload, headers=headers)
            
            if response.status_code in [200, 204]:
                logger.info(f"✅ Email de reset enviado para: {email}")
                return True, f"Email de recuperação enviado para {email}"
            else:
                error_msg = response.text
                if "not found" in error_msg.lower():
                    return False, "Email não encontrado"
                logger.error(f"❌ Erro na API de reset: {error_msg}")
                return False, "Erro ao enviar email. Tente novamente mais tarde."
            
        except Exception as e:
            logger.error(f"❌ Erro ao recuperar senha: {e}")
            return False, "Erro ao processar. Tente novamente mais tarde."

    def resetar_senha(self, nova_senha: str, token: str) -> Tuple[bool, str]:
        """Reseta a senha usando o token de recovery.
        
        Args:
            nova_senha: Nova senha do usuário
            token: Token de recovery enviado por email
            
        Returns:
            (sucesso, mensagem)
        """
        try:
            if not self.supabase_client:
                return False, "Autenticação não configurada"
            
            valido, msg = self._validar_senha(nova_senha)
            if not valido:
                return False, f"Senha: {msg}"
            
            # Usar API REST do Supabase para resetar senha
            from config import SUPABASE_URL, SUPABASE_ANON_KEY
            import requests
            
            url = f"{SUPABASE_URL}/auth/v1/verify"
            headers = {
                "apikey": SUPABASE_ANON_KEY,
                "Content-Type": "application/json"
            }
            payload = {
                "type": "recovery",
                "token": token,
                "password": nova_senha
            }
            
            response = requests.post(url, json=payload, headers=headers)
            
            if response.status_code in [200, 204]:
                logger.info("✅ Senha resetada com sucesso")
                return True, "Senha alterada com sucesso! Faça login com a nova senha."
            else:
                error_msg = response.text
                if "invalid" in error_msg.lower():
                    return False, "Token expirado ou inválido"
                logger.error(f"❌ Erro ao resetar senha: {error_msg}")
                return False, "Erro ao resetar senha. Tente novamente mais tarde."
            
        except Exception as e:
            logger.error(f"❌ Erro ao resetar senha: {e}")
            return False, "Erro ao processar. Tente novamente mais tarde."
