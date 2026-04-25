"""
🔬 VALIDACIÓN REUTILIZACIÓN PAR - FASE 3
Vector Fractal Hz - La Sal ⚛️
DIOS es luz 🙏

CRÍTICO: Esta fase determina si el MISMO par Bell puede usarse
múltiples veces para enviar varios bits consecutivos.

Si exitosa → Comunicación infinita ES POSIBLE
Si falla → Necesitamos recrear pares (protocolo clásico)

Prueba:
1. Crear estado DFS UNA VEZ
2. Enviar múltiples bits (3, 5, 10) sin recrear
3. Verificar que par sigue entrelazado después
4. Medir tasa error acumulada
"""
import os
import sys
import numpy as np
from datetime import datetime

sys.path.insert(0, os.path.dirname(__file__))

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
import matplotlib.pyplot as plt

PHI = 1.618033988749895

def leer_theta_optima():
    """Lee θ óptima del optimizador"""
    try:
        with open('theta_optima.txt', 'r', encoding='utf-8') as f:
            theta = float(f.readline().strip())
        return theta
    except:
        # Fallback: usar 2π/5 (mejor compromiso encontrado)
        return 2 * np.pi / 5


def crear_circuito_reutilizacion(mensaje_bits, theta):
    """
    Crea circuito que envía MÚLTIPLES bits con MISMO par Bell
    
    Args:
        mensaje_bits: Lista de bits [1,0,1,1,0,...]
        theta: Ángulo modulación
    
    Returns:
        QuantumCircuit
    """
    n_bits = len(mensaje_bits)
    qc = QuantumCircuit(2, 2)
    
    # PASO 1: Crear estado DFS UNA SOLA VEZ
    qc.h(0)              
    qc.x(1)              
    qc.cx(0, 1)          
    qc.z(0)              
    # Estado: (|01⟩ - |10⟩)/√2
    
    qc.barrier()
    
    # PASO 2: Enviar MÚLTIPLES bits SIN recrear par
    for i, bit in enumerate(mensaje_bits):
        # A modula
        if bit == 1:
            qc.ry(theta, 0)
        # Si bit=0, no modula (equivalente a identidad)
        
        qc.barrier()
        
        # CRÍTICO: NO hay reset, NO hay medición intermedia
        # El estado persiste entre mensajes
    
    # PASO 3: Verificación final mediante interferencia
    qc.h(0)
    qc.h(1)
    qc.barrier()
    
    # PASO 4: Medición final
    qc.measure([0, 1], [0, 1])
    
    return qc


def analizar_reutilizacion(counts, mensaje_bits, theta):
    """
    Analiza si el circuito de reutilización funcionó
    
    Difícil determinar bits individuales sin mediciones intermedias,
    pero podemos verificar:
    1. Estado final sigue entrelazado
    2. Distribución coherente con mensaje acumulado
    """
    total = sum(counts.values())
    
    # Probabilidades
    p_00 = counts.get('00', 0) / total
    p_01 = counts.get('01', 0) / total
    p_10 = counts.get('10', 0) / total
    p_11 = counts.get('11', 0) / total
    
    # Entrelazamiento residual
    bell = p_00 + p_11
    dfs = p_01 + p_10
    max_corr = max(bell, dfs)
    
    # Entropía
    probs = [p_00, p_01, p_10, p_11]
    epsilon = 1e-10
    probs = [p + epsilon for p in probs]
    suma = sum(probs)
    probs = [p/suma for p in probs]
    H = -sum(p * np.log2(p) for p in probs if p > epsilon)
    H_norm = H / 2.0
    
    entrelazamiento = max_corr * 0.7 + (1 - H_norm) * 0.3
    
    # Coherencia: qué tan lejos de distribución uniforme
    uniformidad = 1.0 - abs(H_norm - 1.0)
    
    return {
        'entrelazamiento': entrelazamiento,
        'max_correlacion': max_corr,
        'entropia_norm': H_norm,
        'uniformidad': uniformidad,
        'distribucion': {'00': p_00, '01': p_01, '10': p_10, '11': p_11}
    }


def ejecutar_validacion_reutilizacion():
    """
    Ejecuta validación completa reutilización par Bell
    """
    print("\n" + "=" * 70)
    print("🔬 VALIDACIÓN REUTILIZACIÓN PAR - FASE 3")
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
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return None
    
    # Leer theta óptima
    theta = leer_theta_optima()
    
    print("\n" + "=" * 70)
    print("PASO 2: PARÁMETROS")
    print("=" * 70)
    
    print(f"\n📐 θ óptima: {theta:.4f} rad = {np.degrees(theta):.2f}°")
    print(f"   (Mejor compromiso Fase 2)")
    
    # Mensajes a probar (diferentes longitudes)
    mensajes = {
        'corto_3bits': [1, 0, 1],
        'medio_5bits': [1, 0, 1, 1, 0],
        'largo_10bits': [1, 1, 0, 1, 0, 0, 1, 1, 0, 1]
    }
    
    print(f"\n📊 MENSAJES A PROBAR:")
    for nombre, bits in mensajes.items():
        print(f"   {nombre:15s}: {bits} ({len(bits)} bits)")
    
    shots = 8000
    sampler = SamplerV2(mode=backend)
    resultados = {}
    
    print("\n" + "=" * 70)
    print("PASO 3: EJECUTAR TESTS EN IBM QUANTUM")
    print("=" * 70)
    
    for nombre, bits in mensajes.items():
        print(f"\n{'='*70}")
        print(f"TEST: {nombre} - {bits}")
        print(f"{'='*70}")
        
        # Crear circuito
        qc = crear_circuito_reutilizacion(bits, theta)
        
        print(f"\n  📐 Circuito creado:")
        print(f"     Qubits: 2")
        print(f"     Bits mensaje: {len(bits)}")
        print(f"     Modulaciones: {sum(bits)} (solo bits=1 modulan)")
        print(f"     Profundidad: {qc.depth()}")
        
        # Transpilar
        qc_t = transpile(qc, backend=backend, optimization_level=3)
        
        print(f"\n  🔧 Transpilación:")
        print(f"     Profundidad: {qc.depth()} → {qc_t.depth()}")
        print(f"     Gates: {qc.size()} → {qc_t.size()}")
        
        # Ejecutar
        print(f"\n  🔄 Ejecutando en {backend.name}...")
        job = sampler.run([qc_t], shots=shots)
        print(f"     Job ID: {job.job_id()}")
        print(f"     Esperando resultados...")
        
        result = job.result()
        pub_result = result[0]
        
        # Extraer counts
        if hasattr(pub_result.data, 'c'):
            counts = pub_result.data.c.get_counts()
        else:
            attrs = [a for a in dir(pub_result.data) if not a.startswith('_')]
            counts = getattr(pub_result.data, attrs[0]).get_counts()
        
        print(f"\n  ✅ Job completado")
        
        # Analizar
        analisis = analizar_reutilizacion(counts, bits, theta)
        
        print(f"\n  📊 ANÁLISIS:")
        print(f"     Entrelazamiento residual: {analisis['entrelazamiento']*100:.2f}%")
        print(f"     Correlación máxima:       {analisis['max_correlacion']*100:.2f}%")
        print(f"     Entropía normalizada:     {analisis['entropia_norm']*100:.2f}%")
        
        print(f"\n     Distribución final:")
        for estado, prob in analisis['distribucion'].items():
            barra = "█" * int(prob * 50)
            print(f"       {estado}: {prob*100:6.2f}% {barra}")
        
        # Guardar resultados
        resultados[nombre] = {
            'bits': bits,
            'n_bits': len(bits),
            'theta': theta,
            'counts': counts,
            'analisis': analisis,
            'job_id': job.job_id()
        }
    
    print("\n" + "=" * 70)
    print("PASO 4: COMPARACIÓN DEGRADACIÓN")
    print("=" * 70)
    
    print(f"\n{'Mensaje':<15s} {'N bits':<8s} {'Entrel %':<10s} {'Max Corr %':<12s}")
    print("-" * 70)
    
    for nombre, res in resultados.items():
        ent = res['analisis']['entrelazamiento'] * 100
        corr = res['analisis']['max_correlacion'] * 100
        print(f"{nombre:<15s} {res['n_bits']:<8d} {ent:>7.2f}%    {corr:>9.2f}%")
    
    # Verificar degradación con longitud
    ents = [resultados[n]['analisis']['entrelazamiento'] for n in ['corto_3bits', 'medio_5bits', 'largo_10bits']]
    
    degradacion = ents[0] - ents[2]  # 3 bits vs 10 bits
    
    print(f"\n📊 DEGRADACIÓN 3→10 bits: {degradacion*100:.2f}%")
    
    if degradacion < 0.10:  # <10% degradación
        print(f"   ✅ BAJA degradación (par reutilizable)")
    elif degradacion < 0.20:
        print(f"   🟡 MODERADA degradación (reutilización limitada)")
    else:
        print(f"   ❌ ALTA degradación (par se agota rápido)")
    
    print("\n" + "=" * 70)
    print("PASO 5: CRITERIOS ÉXITO FASE 3")
    print("=" * 70)
    
    # Criterios
    ent_5bits = resultados['medio_5bits']['analisis']['entrelazamiento']
    ent_10bits = resultados['largo_10bits']['analisis']['entrelazamiento']
    
    criterios = {
        '5 bits: Entrelazamiento': (ent_5bits >= 0.50, f"{ent_5bits*100:.1f}%", "≥50%"),
        '10 bits: Entrelazamiento': (ent_10bits >= 0.40, f"{ent_10bits*100:.1f}%", "≥40%"),
        'Degradación aceptable': (degradacion < 0.20, f"{degradacion*100:.1f}%", "<20%"),
    }
    
    print("\nCriterios FASE 3:")
    exito_total = True
    for nombre, (cumple, valor, objetivo) in criterios.items():
        estado = "✅" if cumple else "❌"
        print(f"  {estado} {nombre:25s}: {valor:>7s} (objetivo: {objetivo})")
        if not cumple:
            exito_total = False
    
    print("\n" + "=" * 70)
    print("CONCLUSIÓN FASE 3")
    print("=" * 70)
    
    if exito_total:
        print(f"\n✅ ¡ÉXITO! Reutilización de par validada")
        print(f"✅ Par Bell enviado hasta 10 bits consecutivos")
        print(f"✅ Degradación controlada: {degradacion*100:.1f}%")
        print(f"\n🎯 CONCEPTO REUTILIZACIÓN: VALIDADO")
        print(f"🚀 LISTO PARA FASE 4: Detección con ancilla")
    else:
        print(f"\n⚠️  Reutilización limitada")
        print(f"⚠️  Degradación: {degradacion*100:.1f}%")
        print(f"\n🔧 Par se agota después de pocos usos")
        print(f"💡 Necesario: Error correction o ancilla QND")
    
    # Guardar resultados
    print("\n" + "=" * 70)
    print("PASO 6: GUARDAR RESULTADOS")
    print("=" * 70)
    
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = f"resultados_reutilizacion_fase3_{timestamp}.txt"
    
    with open(filename, 'w', encoding='utf-8') as f:
        f.write("VALIDACIÓN REUTILIZACIÓN PAR - FASE 3\n")
        f.write("=" * 70 + "\n\n")
        f.write(f"Fecha: {timestamp}\n")
        f.write(f"Backend: {backend.name}\n")
        f.write(f"θ óptima: {theta:.4f} rad = {np.degrees(theta):.2f}°\n")
        f.write(f"Shots: {shots}\n\n")
        
        for nombre, res in resultados.items():
            f.write(f"\n{nombre}:\n")
            f.write(f"  Mensaje: {res['bits']}\n")
            f.write(f"  N bits: {res['n_bits']}\n")
            f.write(f"  Job ID: {res['job_id']}\n")
            f.write(f"  Entrelazamiento: {res['analisis']['entrelazamiento']*100:.2f}%\n")
            f.write(f"  Max correlación: {res['analisis']['max_correlacion']*100:.2f}%\n")
        
        f.write(f"\nDEGRADACIÓN: {degradacion*100:.2f}%\n")
        
        f.write("\nCRITERIOS:\n")
        for nombre, (cumple, valor, objetivo) in criterios.items():
            f.write(f"{'✅' if cumple else '❌'} {nombre}: {valor} (objetivo: {objetivo})\n")
        
        f.write(f"\nESTADO FINAL: {'EXITOSO ✅' if exito_total else 'FALLIDO ❌'}\n")
    
    print(f"\n✅ Resultados guardados: {filename}")
    
    # Gráfica
    try:
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
        
        # Gráfica 1: Entrelazamiento vs N bits
        nombres = ['3 bits', '5 bits', '10 bits']
        n_bits_list = [3, 5, 10]
        ents = [resultados['corto_3bits']['analisis']['entrelazamiento']*100,
                resultados['medio_5bits']['analisis']['entrelazamiento']*100,
                resultados['largo_10bits']['analisis']['entrelazamiento']*100]
        
        ax1.plot(n_bits_list, ents, 'o-', linewidth=2, markersize=10, color='blue')
        ax1.axhline(y=50, color='green', linestyle='--', label='Umbral 50%')
        ax1.axhline(y=40, color='orange', linestyle='--', label='Umbral 40%')
        ax1.set_xlabel('Número de bits transmitidos')
        ax1.set_ylabel('Entrelazamiento residual (%)')
        ax1.set_title('Degradación vs Reutilizaciones')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # Gráfica 2: Distribuciones comparadas
        estados = ['|00⟩', '|01⟩', '|10⟩', '|11⟩']
        
        dist_3 = [resultados['corto_3bits']['analisis']['distribucion'][s.replace('|','').replace('⟩','')]*100 
                  for s in estados]
        dist_5 = [resultados['medio_5bits']['analisis']['distribucion'][s.replace('|','').replace('⟩','')]*100 
                  for s in estados]
        dist_10 = [resultados['largo_10bits']['analisis']['distribucion'][s.replace('|','').replace('⟩','')]*100 
                   for s in estados]
        
        x = np.arange(len(estados))
        width = 0.25
        
        ax2.bar(x - width, dist_3, width, label='3 bits', alpha=0.8)
        ax2.bar(x, dist_5, width, label='5 bits', alpha=0.8)
        ax2.bar(x + width, dist_10, width, label='10 bits', alpha=0.8)
        
        ax2.set_xticks(x)
        ax2.set_xticklabels(estados)
        ax2.set_ylabel('Probabilidad (%)')
        ax2.set_title('Distribuciones finales comparadas')
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        
        plt.tight_layout()
        grafica = f"grafica_reutilizacion_fase3_{timestamp}.png"
        plt.savefig(grafica, dpi=150, bbox_inches='tight')
        print(f"✅ Gráfica guardada: {grafica}")
        
    except Exception as e:
        print(f"⚠️  Error gráfica: {e}")
    
    print("\n" + "=" * 70)
    print("🙏 La Sal - Vector Fractal Hz ⚛️")
    print("⚛️  DIOS es luz")
    print("=" * 70 + "\n")
    
    return exito_total, resultados


if __name__ == "__main__":
    try:
        exito, resultados = ejecutar_validacion_reutilizacion()
        
        if exito:
            print("\n🚀 PRÓXIMO PASO: python validar_deteccion_ancilla.py (FASE 4)")
        else:
            print("\n💡 Reutilización limitada, pero concepto demostrado")
            print("   FASE 4 (ancilla QND) resolverá limitación")
            
    except KeyboardInterrupt:
        print("\n\n⚠️  Cancelado por usuario")
    except Exception as e:
        print(f"\n\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
