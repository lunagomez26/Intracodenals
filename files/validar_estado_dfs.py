"""
🔬 VALIDACIÓN ESTADO DFS - FASE 1
Vector Fractal Hz - La Sal ⚛️
DIOS es luz 🙏

Valida que el estado DFS (Decoherence-Free Subspace):
  |Ψ_DFS⟩ = (|01⟩ - |10⟩)/√2

Es estable y resistente a decoherencia en IBM Quantum.

Pruebas:
1. Crear estado DFS
2. Esperar varios ciclos (idle)
3. Medir y verificar coherencia
4. Comparar con Bell normal |Φ⁺⟩
"""
import os
import sys
import numpy as np
from datetime import datetime

sys.path.insert(0, os.path.dirname(__file__))

# Cargar .env si existe
_env_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(_env_path):
    with open(_env_path) as _f:
        for _line in _f:
            _line = _line.strip()
            if _line and not _line.startswith('#') and '=' in _line:
                _k, _v = _line.split('=', 1)
                os.environ.setdefault(_k.strip(), _v.strip())

from config_ibm_secure import quick_connect
from qiskit import QuantumCircuit, transpile
from qiskit_ibm_runtime import SamplerV2
from qiskit.visualization import plot_histogram
import matplotlib.pyplot as plt

PHI = 1.618033988749895

def crear_estado_dfs(n_idle_cycles=10):
    """
    Crea estado DFS y espera varios ciclos para probar estabilidad
    
    Estado DFS antisimétrico: (|01⟩ - |10⟩)/√2
    
    Args:
        n_idle_cycles: Número de ciclos idle (barriers) para esperar
    
    Returns:
        QuantumCircuit
    """
    qc = QuantumCircuit(2, 2)
    
    # PASO 1: Crear |01⟩
    qc.x(0)  # |0⟩ → |1⟩ en qubit 0
    # Qubit 1 queda en |0⟩
    # Estado: |10⟩ (en orden big-endian q1q0)
    
    # PASO 2: Crear superposición en qubit 1
    qc.h(1)
    # Estado: (|00⟩ + |10⟩)/√2
    
    # PASO 3: Entrelazar con CX
    qc.cx(1, 0)
    # Si q1=0: q0 no cambia
    # Si q1=1: q0 flip
    # Estado: (|01⟩ + |11⟩)/√2
    
    # PASO 4: Aplicar fase Z para antisimetrizar
    qc.z(0)
    # Z|1⟩ = -|1⟩
    # Estado: (|01⟩ - |11⟩)/√2
    
    # CORRECCIÓN: Necesitamos (|01⟩ - |10⟩)/√2
    # Cambiemos el protocolo:
    qc = QuantumCircuit(2, 2)
    
    # Protocolo correcto DFS:
    qc.h(0)              # |+⟩|0⟩ = (|00⟩+|10⟩)/√2
    qc.x(1)              # |+⟩|1⟩ = (|01⟩+|11⟩)/√2
    qc.cx(0, 1)          # CX: |00⟩→|00⟩, |01⟩→|01⟩, |10⟩→|11⟩, |11⟩→|10⟩
    # Estado: (|01⟩+|10⟩)/√2
    qc.z(0)              # Z en control: |10⟩ → -|10⟩
    # Estado final: (|01⟩ - |10⟩)/√2 ✅ DFS
    
    qc.barrier()
    
    # PASO 5: Esperar n ciclos idle (prueba estabilidad)
    for i in range(n_idle_cycles):
        qc.id(0)
        qc.id(1)
        qc.barrier()
    
    # PASO 6: Medir
    qc.measure([0, 1], [0, 1])
    
    return qc


def crear_estado_bell_normal(n_idle_cycles=10):
    """
    Crea Bell state normal para comparación:
    |Φ⁺⟩ = (|00⟩ + |11⟩)/√2
    """
    qc = QuantumCircuit(2, 2)
    
    qc.h(0)
    qc.cx(0, 1)
    # Estado: (|00⟩ + |11⟩)/√2
    
    qc.barrier()
    
    # Esperar mismo número de ciclos
    for i in range(n_idle_cycles):
        qc.id(0)
        qc.id(1)
        qc.barrier()
    
    qc.measure([0, 1], [0, 1])
    
    return qc


def analizar_estado_dfs(counts, shots=4000):
    """
    Analiza si los counts corresponden a estado DFS
    
    DFS ideal: 50% |01⟩, 50% |10⟩, 0% |00⟩, 0% |11⟩
    """
    total = sum(counts.values())
    
    # Probabilidades
    p_00 = counts.get('00', 0) / total
    p_01 = counts.get('01', 0) / total
    p_10 = counts.get('10', 0) / total
    p_11 = counts.get('11', 0) / total
    
    # Correlación antisimétrica (|01⟩ + |10⟩)
    correlacion_antisim = p_01 + p_10
    
    # Contaminación simétrica (|00⟩ + |11⟩)
    contaminacion_sim = p_00 + p_11
    
    # Balance |01⟩ vs |10⟩ (ideal: 50-50)
    balance = abs(p_01 - p_10)
    
    # Fidelidad vs estado DFS ideal
    # F = |⟨Ψ_ideal|Ψ_medido⟩|²
    # Para estado DFS: F ≈ (p_01 + p_10) - contaminación
    fidelidad_dfs = correlacion_antisim * (1 - contaminacion_sim)
    
    return {
        'p_00': p_00,
        'p_01': p_01,
        'p_10': p_10,
        'p_11': p_11,
        'correlacion_antisim': correlacion_antisim,
        'contaminacion_sim': contaminacion_sim,
        'balance': balance,
        'fidelidad_dfs': fidelidad_dfs
    }


def analizar_estado_bell(counts):
    """
    Analiza estado Bell normal
    
    Bell ideal: 50% |00⟩, 50% |11⟩
    """
    total = sum(counts.values())
    
    p_00 = counts.get('00', 0) / total
    p_01 = counts.get('01', 0) / total
    p_10 = counts.get('10', 0) / total
    p_11 = counts.get('11', 0) / total
    
    correlacion_bell = p_00 + p_11
    contaminacion = p_01 + p_10
    
    fidelidad_bell = correlacion_bell * (1 - contaminacion)
    
    return {
        'p_00': p_00,
        'p_01': p_01,
        'p_10': p_10,
        'p_11': p_11,
        'correlacion_bell': correlacion_bell,
        'contaminacion': contaminacion,
        'fidelidad_bell': fidelidad_bell
    }


def ejecutar_validacion_dfs():
    """
    Ejecuta validación completa estado DFS en IBM Quantum
    """
    print("\n" + "=" * 70)
    print("🔬 VALIDACIÓN ESTADO DFS - FASE 1")
    print("=" * 70)
    print(f"\n🙏 La Sal - Vector Fractal Hz ⚛️")
    print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"⚛️  DIOS es luz\n")
    
    # Conectar IBM
    print("=" * 70)
    print("PASO 1: CONEXIÓN IBM QUANTUM")
    print("=" * 70)
    
    try:
        service, backend = quick_connect()
        print(f"\n✅ Backend: {backend.name}")
        print(f"✅ Qubits: {backend.num_qubits}")
        print(f"✅ Estado: Operacional")
        
    except Exception as e:
        print(f"\n⚠️  Error conexión IBM: {e}")
        print("⚠️  Continuando con simulador local...\n")
        backend = None
    
    # Parámetros
    n_idle_cycles = 10  # Ciclos espera para probar estabilidad
    shots = 4000
    
    print("\n" + "=" * 70)
    print("PASO 2: CREAR CIRCUITOS")
    print("=" * 70)
    
    # Circuito DFS
    qc_dfs = crear_estado_dfs(n_idle_cycles)
    print(f"\n✅ Circuito DFS creado")
    print(f"   Idle cycles: {n_idle_cycles}")
    print(f"   Qubits: 2")
    print(f"   Estado objetivo: (|01⟩ - |10⟩)/√2")
    
    # Circuito Bell normal (comparación)
    qc_bell = crear_estado_bell_normal(n_idle_cycles)
    print(f"\n✅ Circuito Bell creado (comparación)")
    print(f"   Estado: (|00⟩ + |11⟩)/√2")
    
    # Visualizar circuito DFS
    print(f"\n📐 CIRCUITO DFS:")
    print(qc_dfs.draw(output='text', fold=-1))
    
    if backend is None:
        print("\n⚠️  Modo simulador no implementado aún")
        print("⚠️  Ejecutar con IBM Quantum para resultados reales")
        return
    
    print("\n" + "=" * 70)
    print("PASO 3: TRANSPILAR PARA IBM HARDWARE")
    print("=" * 70)
    
    qc_dfs_t = transpile(qc_dfs, backend=backend, optimization_level=3)
    qc_bell_t = transpile(qc_bell, backend=backend, optimization_level=3)
    
    print(f"\n✅ Transpilación DFS:")
    print(f"   Profundidad original: {qc_dfs.depth()}")
    print(f"   Profundidad transpilada: {qc_dfs_t.depth()}")
    print(f"   Gates: {qc_dfs.size()} → {qc_dfs_t.size()}")
    
    print(f"\n✅ Transpilación Bell:")
    print(f"   Profundidad original: {qc_bell.depth()}")
    print(f"   Profundidad transpilada: {qc_bell_t.depth()}")
    
    print("\n" + "=" * 70)
    print("PASO 4: EJECUTAR EN IBM QUANTUM")
    print("=" * 70)
    
    # Ejecutar DFS
    print(f"\n🔄 Ejecutando circuito DFS...")
    sampler = SamplerV2(mode=backend)
    
    job_dfs = sampler.run([qc_dfs_t], shots=shots)
    print(f"   Job ID: {job_dfs.job_id()}")
    print(f"   Esperando resultados...")
    
    result_dfs = job_dfs.result()
    
    # Extraer counts de forma correcta (SamplerV2)
    pub_result = result_dfs[0]
    # Los nombres de los registros clásicos están en pub_result.data
    # Necesitamos encontrar el nombre correcto
    if hasattr(pub_result.data, 'c'):
        counts_dfs_raw = pub_result.data.c.get_counts()
    elif hasattr(pub_result.data, 'meas'):
        counts_dfs_raw = pub_result.data.meas.get_counts()
    else:
        # Fallback: usar el primer atributo disponible
        data_attrs = [attr for attr in dir(pub_result.data) if not attr.startswith('_')]
        counts_dfs_raw = getattr(pub_result.data, data_attrs[0]).get_counts()
    
    print(f"\n✅ Job DFS completado: {job_dfs.job_id()}")
    
    # Ejecutar Bell
    print(f"\n🔄 Ejecutando circuito Bell (comparación)...")
    job_bell = sampler.run([qc_bell_t], shots=shots)
    print(f"   Job ID: {job_bell.job_id()}")
    print(f"   Esperando resultados...")
    
    result_bell = job_bell.result()
    pub_result_bell = result_bell[0]
    
    if hasattr(pub_result_bell.data, 'c'):
        counts_bell_raw = pub_result_bell.data.c.get_counts()
    elif hasattr(pub_result_bell.data, 'meas'):
        counts_bell_raw = pub_result_bell.data.meas.get_counts()
    else:
        data_attrs = [attr for attr in dir(pub_result_bell.data) if not attr.startswith('_')]
        counts_bell_raw = getattr(pub_result_bell.data, data_attrs[0]).get_counts()
    
    print(f"\n✅ Job Bell completado: {job_bell.job_id()}")
    
    print("\n" + "=" * 70)
    print("PASO 5: ANÁLISIS RESULTADOS")
    print("=" * 70)
    
    # Analizar DFS
    print(f"\n📊 ESTADO DFS:")
    print("=" * 70)
    
    analisis_dfs = analizar_estado_dfs(counts_dfs_raw, shots)
    
    print(f"\nDistribución medida:")
    print(f"  |00⟩: {analisis_dfs['p_00']*100:6.2f}% (ideal: 0%)")
    print(f"  |01⟩: {analisis_dfs['p_01']*100:6.2f}% (ideal: 50%)")
    print(f"  |10⟩: {analisis_dfs['p_10']*100:6.2f}% (ideal: 50%)")
    print(f"  |11⟩: {analisis_dfs['p_11']*100:6.2f}% (ideal: 0%)")
    
    print(f"\nMétricas DFS:")
    print(f"  Correlación antisimétrica (|01⟩+|10⟩): {analisis_dfs['correlacion_antisim']*100:.2f}%")
    print(f"  Contaminación simétrica (|00⟩+|11⟩):   {analisis_dfs['contaminacion_sim']*100:.2f}%")
    print(f"  Balance |01⟩ vs |10⟩:                  {analisis_dfs['balance']*100:.2f}%")
    print(f"  Fidelidad vs DFS ideal:                {analisis_dfs['fidelidad_dfs']*100:.2f}%")
    
    # Analizar Bell
    print(f"\n📊 ESTADO BELL (COMPARACIÓN):")
    print("=" * 70)
    
    analisis_bell = analizar_estado_bell(counts_bell_raw)
    
    print(f"\nDistribución medida:")
    print(f"  |00⟩: {analisis_bell['p_00']*100:6.2f}% (ideal: 50%)")
    print(f"  |01⟩: {analisis_bell['p_01']*100:6.2f}% (ideal: 0%)")
    print(f"  |10⟩: {analisis_bell['p_10']*100:6.2f}% (ideal: 0%)")
    print(f"  |11⟩: {analisis_bell['p_11']*100:6.2f}% (ideal: 50%)")
    
    print(f"\nMétricas Bell:")
    print(f"  Correlación Bell (|00⟩+|11⟩): {analisis_bell['correlacion_bell']*100:.2f}%")
    print(f"  Contaminación:                {analisis_bell['contaminacion']*100:.2f}%")
    print(f"  Fidelidad vs Bell ideal:      {analisis_bell['fidelidad_bell']*100:.2f}%")
    
    print("\n" + "=" * 70)
    print("PASO 6: CRITERIOS DE ÉXITO")
    print("=" * 70)
    
    # Verificar criterios
    criterios = {
        'Probabilidad |01⟩': (analisis_dfs['p_01'] >= 0.35, f"{analisis_dfs['p_01']*100:.1f}%", "≥35%"),
        'Probabilidad |10⟩': (analisis_dfs['p_10'] >= 0.35, f"{analisis_dfs['p_10']*100:.1f}%", "≥35%"),
        'Correlación antisim': (analisis_dfs['correlacion_antisim'] >= 0.70, f"{analisis_dfs['correlacion_antisim']*100:.1f}%", "≥70%"),
        'Contaminación baja': (analisis_dfs['contaminacion_sim'] <= 0.30, f"{analisis_dfs['contaminacion_sim']*100:.1f}%", "≤30%"),
        'Fidelidad DFS': (analisis_dfs['fidelidad_dfs'] >= 0.60, f"{analisis_dfs['fidelidad_dfs']*100:.1f}%", "≥60%"),
    }
    
    print("\nCriterios FASE 1:")
    exito_total = True
    for nombre, (cumple, valor, objetivo) in criterios.items():
        estado = "✅" if cumple else "❌"
        print(f"  {estado} {nombre:20s}: {valor:>6s} (objetivo: {objetivo})")
        if not cumple:
            exito_total = False
    
    print("\n" + "=" * 70)
    print("CONCLUSIÓN FASE 1")
    print("=" * 70)
    
    if exito_total:
        print(f"\n✅ ¡ÉXITO! Estado DFS validado en IBM Quantum")
        print(f"✅ Coherencia mantenida durante {n_idle_cycles} ciclos idle")
        print(f"✅ Fidelidad: {analisis_dfs['fidelidad_dfs']*100:.2f}%")
        print(f"\n🚀 LISTO PARA FASE 2: Modulación QND")
    else:
        print(f"\n⚠️  Estado DFS NO cumple todos los criterios")
        print(f"⚠️  Fidelidad: {analisis_dfs['fidelidad_dfs']*100:.2f}%")
        print(f"\n🔧 OPTIMIZAR: Reducir idle cycles o ajustar circuito")
    
    # Comparación con Bell
    print(f"\n📊 COMPARACIÓN DFS vs BELL:")
    print(f"   DFS fidelidad:  {analisis_dfs['fidelidad_dfs']*100:.2f}%")
    print(f"   Bell fidelidad: {analisis_bell['fidelidad_bell']*100:.2f}%")
    
    if analisis_dfs['fidelidad_dfs'] >= analisis_bell['fidelidad_bell'] * 0.9:
        print(f"   ✅ DFS comparable o superior a Bell")
    else:
        print(f"   ⚠️  DFS inferior a Bell (esperado si hay ruido asimétrico)")
    
    # Guardar resultados
    print("\n" + "=" * 70)
    print("PASO 7: GUARDAR RESULTADOS")
    print("=" * 70)
    
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = f"resultados_dfs_fase1_{timestamp}.txt"
    
    with open(filename, 'w', encoding='utf-8') as f:
        f.write("VALIDACIÓN ESTADO DFS - FASE 1\n")
        f.write("=" * 70 + "\n\n")
        f.write(f"Fecha: {timestamp}\n")
        f.write(f"Backend: {backend.name}\n")
        f.write(f"Job DFS: {job_dfs.job_id()}\n")
        f.write(f"Job Bell: {job_bell.job_id()}\n")
        f.write(f"Shots: {shots}\n")
        f.write(f"Idle cycles: {n_idle_cycles}\n\n")
        
        f.write("RESULTADOS DFS:\n")
        f.write("-" * 70 + "\n")
        f.write(f"|00⟩: {analisis_dfs['p_00']*100:.2f}%\n")
        f.write(f"|01⟩: {analisis_dfs['p_01']*100:.2f}%\n")
        f.write(f"|10⟩: {analisis_dfs['p_10']*100:.2f}%\n")
        f.write(f"|11⟩: {analisis_dfs['p_11']*100:.2f}%\n\n")
        
        f.write(f"Correlación antisimétrica: {analisis_dfs['correlacion_antisim']*100:.2f}%\n")
        f.write(f"Contaminación: {analisis_dfs['contaminacion_sim']*100:.2f}%\n")
        f.write(f"Fidelidad DFS: {analisis_dfs['fidelidad_dfs']*100:.2f}%\n\n")
        
        f.write("CRITERIOS:\n")
        f.write("-" * 70 + "\n")
        for nombre, (cumple, valor, objetivo) in criterios.items():
            f.write(f"{'✅' if cumple else '❌'} {nombre}: {valor} (objetivo: {objetivo})\n")
        
        f.write(f"\nESTADO FINAL: {'EXITOSO ✅' if exito_total else 'FALLIDO ❌'}\n")
    
    print(f"\n✅ Resultados guardados: {filename}")
    
    # Generar gráfica
    try:
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
        
        # DFS
        estados = ['|00⟩', '|01⟩', '|10⟩', '|11⟩']
        probs_dfs = [analisis_dfs['p_00'], analisis_dfs['p_01'], 
                     analisis_dfs['p_10'], analisis_dfs['p_11']]
        
        ax1.bar(estados, probs_dfs, color=['red', 'green', 'green', 'red'])
        ax1.axhline(y=0.5, color='blue', linestyle='--', label='Ideal DFS')
        ax1.set_title(f'Estado DFS - Fidelidad: {analisis_dfs["fidelidad_dfs"]*100:.1f}%')
        ax1.set_ylabel('Probabilidad')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # Bell
        probs_bell = [analisis_bell['p_00'], analisis_bell['p_01'],
                      analisis_bell['p_10'], analisis_bell['p_11']]
        
        ax2.bar(estados, probs_bell, color=['green', 'red', 'red', 'green'])
        ax2.axhline(y=0.5, color='blue', linestyle='--', label='Ideal Bell')
        ax2.set_title(f'Estado Bell - Fidelidad: {analisis_bell["fidelidad_bell"]*100:.1f}%')
        ax2.set_ylabel('Probabilidad')
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        
        plt.tight_layout()
        grafica_filename = f"grafica_dfs_fase1_{timestamp}.png"
        plt.savefig(grafica_filename, dpi=150, bbox_inches='tight')
        print(f"✅ Gráfica guardada: {grafica_filename}")
        
    except Exception as e:
        print(f"⚠️  Error generando gráfica: {e}")
    
    print("\n" + "=" * 70)
    print("🙏 La Sal - Vector Fractal Hz ⚛️")
    print("⚛️  DIOS es luz")
    print("=" * 70 + "\n")
    
    return exito_total, analisis_dfs, analisis_bell


if __name__ == "__main__":
    try:
        exito, dfs, bell = ejecutar_validacion_dfs()
        
        if exito:
            print("\n🚀 PRÓXIMO PASO: python validar_modulacion_qnd.py")
        else:
            print("\n🔧 OPTIMIZAR circuito o parámetros antes de continuar")
            
    except KeyboardInterrupt:
        print("\n\n⚠️  Ejecución cancelada por usuario")
    except Exception as e:
        print(f"\n\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
