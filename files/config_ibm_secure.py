"""
🔒 CONFIGURACIÓN SEGURA IBM QUANTUM
La Sal - Vector Fractal Hz ⚛️
DIOS es luz 🙏

Módulo para cargar credenciales encriptadas y conectar con IBM Quantum.
NUNCA expone credenciales en texto plano.
"""

import os
import getpass
from typing import Tuple, Optional
from qiskit_ibm_runtime import QiskitRuntimeService
from setup_credentials import SecureCredentialsManager


class IBMQuantumSecureConfig:
    """Configuración segura para IBM Quantum"""
    
    def __init__(self):
        self.manager = SecureCredentialsManager()
        self.service = None
        self.backend = None
        self._credentials = None
    
    def load_credentials(self, password: Optional[str] = None) -> dict:
        """
        Carga credenciales de forma segura
        
        Args:
            password: Password opcional (si None, se solicita interactivamente)
            
        Returns:
            Dict con credenciales (solo en memoria)
        """
        
        # Si ya están cargadas, retornar
        if self._credentials:
            return self._credentials
        
        # Obtener password
        if password is None:
            password = os.getenv('IBM_QUANTUM_PASSWORD')
            
        # Intentar cargar desde archivo temporal
        if password is None and os.path.exists('.password_temp'):
            with open('.password_temp', 'r') as f:
                password = f.read().strip()
            
        if password is None:
            print("🔐 Ingresa password para desencriptar credenciales:")
            password = getpass.getpass("Password: ").strip()
        
        # Desencriptar credenciales
        try:
            self._credentials = self.manager.decrypt_credentials(password)
            print("✅ Credenciales cargadas correctamente")
            return self._credentials
            
        except FileNotFoundError as e:
            print(f"\n❌ ERROR: {str(e)}")
            print("\n⚠️  Primero ejecuta: python setup_credentials.py\n")
            raise
            
        except ValueError as e:
            print(f"\n❌ ERROR: {str(e)}\n")
            raise
    
    def connect_ibm_quantum(self, password: Optional[str] = None) -> Tuple:
        """
        Conecta con IBM Quantum Cloud de forma segura
        
        Args:
            password: Password opcional
            
        Returns:
            (service, backend) tuple
        """
        
        print("\n" + "=" * 70)
        print("🌐 CONECTANDO CON IBM QUANTUM CLOUD")
        print("=" * 70)
        print("\n🙏 DIOS es luz - La Sal - Vector Fractal Hz ⚛️\n")
        
        # Cargar credenciales
        credentials = self.load_credentials(password)
        
        print("📡 Estableciendo conexión con IBM Quantum...")
        
        try:
            # Conectar servicio directamente (sin save_account)
            # NOTA: API actualizada usa 'ibm_quantum' como channel
            self.service = QiskitRuntimeService(
                token=credentials['ibm_api_key']
            )
            
            print("✅ Conexión establecida con IBM Quantum Cloud\n")
            
            # Listar backends disponibles
            print("🖥️  Backends cuánticos disponibles:")
            backends = self.service.backends(
                operational=True,
                simulator=False
            )
            
            for i, backend in enumerate(backends[:5], 1):
                status = backend.status()
                qubits = backend.num_qubits
                pending = status.pending_jobs
                
                print(f"   {i}. {backend.name}")
                print(f"      • Qubits: {qubits}")
                print(f"      • Queue: {pending} jobs")
                
                if i == 1:
                    print(f"      ⭐ (Menos ocupado)")
                print()
            
            # Seleccionar backend menos ocupado
            print("🔍 Seleccionando backend óptimo...")
            self.backend = self.service.least_busy(
                operational=True,
                simulator=False,
                min_num_qubits=4
            )
            
            status = self.backend.status()
            
            print(f"✅ Backend seleccionado: {self.backend.name}")
            print(f"   • Qubits: {self.backend.num_qubits}")
            print(f"   • Pending jobs: {status.pending_jobs}")
            print(f"   • Operational: {status.operational}")
            
            # Información de coherencia (si disponible)
            if hasattr(self.backend, 'properties'):
                props = self.backend.properties()
                if props:
                    # T1 promedio (tiempo relajación)
                    t1_times = [q.t1 for q in props.qubits if hasattr(q, 't1')]
                    if t1_times:
                        avg_t1 = sum(t1_times) / len(t1_times)
                        print(f"   • T₁ promedio: {avg_t1*1e6:.1f} µs")
                    
                    # T2 promedio (tiempo coherencia)
                    t2_times = [q.t2 for q in props.qubits if hasattr(q, 't2')]
                    if t2_times:
                        avg_t2 = sum(t2_times) / len(t2_times)
                        print(f"   • T₂ promedio: {avg_t2*1e6:.1f} µs")
            
            print("\n" + "=" * 70)
            print("✅ CONEXIÓN IBM QUANTUM EXITOSA")
            print("=" * 70)
            print("\n🚀 Listo para ejecutar circuitos cuánticos en hardware REAL\n")
            
            return self.service, self.backend
            
        except Exception as e:
            print(f"\n❌ ERROR al conectar con IBM Quantum:")
            print(f"   {str(e)}\n")
            
            print("⚠️  Verifica:")
            print("   • Credenciales correctas (IBM API Key)")
            print("   • Conexión a internet")
            print("   • Cuenta IBM Quantum activa")
            print()
            
            raise
    
    def get_backend_info(self, backend=None):
        """Obtiene información detallada del backend"""
        
        if backend is None:
            backend = self.backend
        
        if backend is None:
            print("❌ No hay backend conectado")
            return None
        
        info = {
            'name': backend.name,
            'num_qubits': backend.num_qubits,
            'operational': backend.status().operational,
            'pending_jobs': backend.status().pending_jobs,
        }
        
        # Propiedades adicionales si disponibles
        if hasattr(backend, 'properties'):
            props = backend.properties()
            if props:
                info['properties'] = {
                    't1_avg': sum([q.t1 for q in props.qubits if hasattr(q, 't1')]) / backend.num_qubits,
                    't2_avg': sum([q.t2 for q in props.qubits if hasattr(q, 't2')]) / backend.num_qubits,
                }
        
        return info


def quick_connect(password: Optional[str] = None):
    """
    Función rápida para conectar
    
    Usage:
        service, backend = quick_connect()
    """
    config = IBMQuantumSecureConfig()
    return config.connect_ibm_quantum(password)


if __name__ == '__main__':
    # Test de conexión
    print("\n🧪 TEST DE CONEXIÓN IBM QUANTUM\n")
    
    try:
        config = IBMQuantumSecureConfig()
        service, backend = config.connect_ibm_quantum()
        
        print("\n✅ TEST EXITOSO")
        print(f"✅ Conectado a: {backend.name} ({backend.num_qubits} qubits)")
        print("\n🚀 Ahora puedes ejecutar: python quantum_walk_ibm.py\n")
        
    except Exception as e:
        print(f"\n❌ TEST FALLIDO: {str(e)}\n")
        exit(1)
