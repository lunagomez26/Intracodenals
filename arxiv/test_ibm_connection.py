"""
🧪 TEST CONEXIÓN IBM QUANTUM
La Sal - Vector Fractal Hz ⚛️
DIOS es luz 🙏

Script para verificar conexión con IBM Quantum Cloud.
"""

import sys
from config_ibm_secure import IBMQuantumSecureConfig


def test_connection():
    """Test completo de conexión"""
    
    print("\n" + "=" * 70)
    print("🧪 TEST CONEXIÓN IBM QUANTUM CLOUD")
    print("=" * 70)
    print("\n🙏 DIOS es luz - La Sal - Vector Fractal Hz ⚛️\n")
    
    try:
        # Conectar
        config = IBMQuantumSecureConfig()
        service, backend = config.connect_ibm_quantum()
        
        # Verificar conexión
        print("\n📊 INFORMACIÓN DETALLADA:\n")
        
        info = config.get_backend_info()
        
        print(f"Backend: {info['name']}")
        print(f"Qubits: {info['num_qubits']}")
        print(f"Estado: {'✅ Operacional' if info['operational'] else '❌ No operacional'}")
        print(f"Jobs en cola: {info['pending_jobs']}")
        
        if 'properties' in info:
            print(f"T₁ promedio: {info['properties']['t1_avg']*1e6:.1f} µs")
            print(f"T₂ promedio: {info['properties']['t2_avg']*1e6:.1f} µs")
        
        # Verificar capacidad para Quantum Walk
        print("\n✅ VERIFICACIÓN QUANTUM WALK:\n")
        
        min_qubits = 4  # 3 position + 1 coin
        if info['num_qubits'] >= min_qubits:
            print(f"✅ Qubits suficientes: {info['num_qubits']} >= {min_qubits}")
        else:
            print(f"❌ Qubits insuficientes: {info['num_qubits']} < {min_qubits}")
        
        if info['operational']:
            print("✅ Backend operacional")
        else:
            print("❌ Backend NO operacional")
        
        if info['pending_jobs'] < 50:
            print(f"✅ Cola razonable: {info['pending_jobs']} jobs")
        else:
            print(f"⚠️  Cola larga: {info['pending_jobs']} jobs (espera posible)")
        
        # Resultado final
        print("\n" + "=" * 70)
        print("✅ TEST EXITOSO - CONEXIÓN IBM QUANTUM VERIFICADA")
        print("=" * 70)
        
        print("\n🚀 PRÓXIMOS PASOS:\n")
        print("1. Ejecutar Quantum Walk en simulador local:")
        print("   python quantum_walk_ibm.py --mode=simulator\n")
        print("2. Ejecutar Quantum Walk en hardware REAL:")
        print("   python quantum_walk_ibm.py --mode=real\n")
        print("3. Integrar con V4:")
        print("   python quantum_carrier_search_v4.py\n")
        
        print("🙏 DIOS es luz - La Sal - Vector Fractal Hz ⚛️\n")
        
        return True
        
    except FileNotFoundError:
        print("\n❌ ERROR: Credenciales no configuradas\n")
        print("⚠️  Primero ejecuta:")
        print("   python setup_credentials.py\n")
        return False
        
    except ValueError:
        print("\n❌ ERROR: Password incorrecto\n")
        print("⚠️  Intenta nuevamente con el password correcto\n")
        return False
        
    except Exception as e:
        print("\n❌ ERROR DE CONEXIÓN:\n")
        print(f"   {str(e)}\n")
        print("⚠️  Verifica:")
        print("   • Credenciales correctas")
        print("   • Conexión a internet")
        print("   • Cuenta IBM Quantum activa")
        print("   • API Key válida\n")
        return False


if __name__ == '__main__':
    success = test_connection()
    
    if not success:
        sys.exit(1)
    
    sys.exit(0)
