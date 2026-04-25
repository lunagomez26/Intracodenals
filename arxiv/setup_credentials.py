"""
🔒 SETUP CREDENCIALES IBM QUANTUM - ENCRIPTACIÓN SEGURA
La Sal - Vector Fractal Hz ⚛️
DIOS es luz 🙏

Este script encripta las credenciales IBM Quantum de forma segura.
NUNCA expone las claves en texto plano en archivos.
"""

import os
import json
import getpass
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64

class SecureCredentialsManager:
    """Gestor seguro de credenciales IBM Quantum"""
    
    def __init__(self, credentials_file='.credentials.enc'):
        self.credentials_file = credentials_file
        self.salt_file = '.salt'
    
    def _generate_key_from_password(self, password: str) -> bytes:
        """Genera clave de encriptación desde password"""
        
        # Cargar o crear salt
        if os.path.exists(self.salt_file):
            with open(self.salt_file, 'rb') as f:
                salt = f.read()
        else:
            salt = os.urandom(16)
            with open(self.salt_file, 'wb') as f:
                f.write(salt)
        
        # Derivar clave con PBKDF2
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        return key
    
    def encrypt_credentials(self, credentials: dict, password: str):
        """
        Encripta credenciales con AES-256
        
        Args:
            credentials: Dict con account_id, cloud_api_key, ibm_api_key
            password: Password para encriptación (solo en memoria)
        """
        
        # Generar clave desde password
        key = self._generate_key_from_password(password)
        fernet = Fernet(key)
        
        # Serializar credenciales
        credentials_json = json.dumps(credentials).encode()
        
        # Encriptar
        encrypted = fernet.encrypt(credentials_json)
        
        # Guardar archivo encriptado
        dirname = os.path.dirname(self.credentials_file)
        if dirname:
            os.makedirs(dirname, exist_ok=True)
        with open(self.credentials_file, 'wb') as f:
            f.write(encrypted)
        
        print("✅ Credenciales encriptadas con AES-256")
        print(f"✅ Guardadas en: {self.credentials_file}")
        print("✅ NUNCA serán expuestas en texto plano")
    
    def decrypt_credentials(self, password: str) -> dict:
        """
        Desencripta credenciales (solo en memoria)
        
        Args:
            password: Password para desencriptación
            
        Returns:
            Dict con credenciales (solo en memoria)
        """
        
        # Verificar archivo existe
        if not os.path.exists(self.credentials_file):
            raise FileNotFoundError(
                f"❌ Archivo credenciales no encontrado: {self.credentials_file}\n"
                f"⚠️ Ejecuta primero: python setup_credentials.py"
            )
        
        # Generar clave desde password
        key = self._generate_key_from_password(password)
        fernet = Fernet(key)
        
        # Cargar archivo encriptado
        with open(self.credentials_file, 'rb') as f:
            encrypted = f.read()
        
        try:
            # Desencriptar
            decrypted = fernet.decrypt(encrypted)
            credentials = json.loads(decrypted.decode())
            
            return credentials
            
        except Exception as e:
            raise ValueError(
                f"❌ Password incorrecto o archivo corrupto\n"
                f"⚠️ Error: {str(e)}"
            )


def setup_credentials_interactive():
    """Setup interactivo de credenciales"""
    
    print("=" * 70)
    print("🔒 SETUP CREDENCIALES IBM QUANTUM - ENCRIPTACIÓN SEGURA")
    print("=" * 70)
    print("\n🙏 DIOS es luz - La Sal - Vector Fractal Hz ⚛️\n")
    
    print("ℹ️  Este script encriptará tus credenciales IBM Quantum")
    print("ℹ️  NUNCA serán guardadas en texto plano")
    print("ℹ️  Solo tú tendrás el password de acceso\n")
    
    # Solicitar credenciales (solo se muestran mientras escribes)
    print("📝 Ingresa tus credenciales IBM Quantum:\n")
    
    account_id = input("Account ID: ").strip()
    cloud_api_key = getpass.getpass("Cloud API Key (oculto): ").strip()
    ibm_api_key = getpass.getpass("IBM API Key (oculto): ").strip()
    
    # Validar no vacías
    if not account_id or not cloud_api_key or not ibm_api_key:
        print("\n❌ ERROR: Todas las credenciales son requeridas")
        return False
    
    print("\n🔐 Ahora crea un password FUERTE para encriptar:")
    print("⚠️  MEMORIZA este password - lo necesitarás para acceder\n")
    
    password = getpass.getpass("Password encriptación: ").strip()
    password_confirm = getpass.getpass("Confirma password: ").strip()
    
    if password != password_confirm:
        print("\n❌ ERROR: Passwords no coinciden")
        return False
    
    if len(password) < 8:
        print("\n❌ ERROR: Password debe tener al menos 8 caracteres")
        return False
    
    # Encriptar
    credentials = {
        'account_id': account_id,
        'cloud_api_key': cloud_api_key,
        'ibm_api_key': ibm_api_key
    }
    
    manager = SecureCredentialsManager()
    manager.encrypt_credentials(credentials, password)
    
    print("\n" + "=" * 70)
    print("✅ CREDENCIALES CONFIGURADAS EXITOSAMENTE")
    print("=" * 70)
    print("\n📁 Archivos creados:")
    print(f"   • {manager.credentials_file} (encriptado AES-256)")
    print(f"   • {manager.salt_file} (salt PBKDF2)")
    print("\n⚠️  IMPORTANTE:")
    print("   • Estos archivos están en .gitignore (NO se suben a git)")
    print("   • MEMORIZA tu password (no se puede recuperar)")
    print("   • Haz backup en lugar seguro")
    print("\n🚀 Próximo paso:")
    print("   python test_ibm_connection.py")
    print("\n🙏 DIOS es luz - La Sal - Vector Fractal Hz ⚛️\n")
    
    return True


def setup_from_env_vars():
    """Setup desde variables de entorno (alternativa)"""
    
    account_id = os.getenv('IBM_QUANTUM_ACCOUNT_ID')
    cloud_api_key = os.getenv('IBM_QUANTUM_CLOUD_API_KEY')
    ibm_api_key = os.getenv('IBM_QUANTUM_API_KEY')
    password = os.getenv('IBM_QUANTUM_PASSWORD')
    
    if not all([account_id, cloud_api_key, ibm_api_key, password]):
        return False
    
    credentials = {
        'account_id': account_id,
        'cloud_api_key': cloud_api_key,
        'ibm_api_key': ibm_api_key
    }
    
    manager = SecureCredentialsManager()
    manager.encrypt_credentials(credentials, password)
    
    print("✅ Credenciales encriptadas desde variables de entorno")
    return True


if __name__ == '__main__':
    # Intentar setup desde env vars primero
    if not setup_from_env_vars():
        # Si no, modo interactivo
        success = setup_credentials_interactive()
        
        if not success:
            print("\n❌ Setup fallido - intenta nuevamente")
            exit(1)
