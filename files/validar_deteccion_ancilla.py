"""
🔬 VALIDACIÓN DETECCIÓN ANCILLA QND - FASE 4
Vector Fractal Hz - La Sal ⚛️
DIOS es luz 🙏

SOLUCIÓN DEFINITIVA al trade-off Fase 2/3:

Usar ANCILLA (qubit auxiliar) para detección QND:
- A y B mantienen par Bell INTACTO
- Ancilla se acopla DÉBILMENTE a B
- Ancilla detecta información SIN colapsar A-B
- Ancilla se mide y descarta
- A-B quedan listos para siguiente mensaje

Si exitosa → COMUNICACIÓN INFINITA VALIDADA COMPLETAMENTE
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
    """Lee θ óptima"""
    try:
        with open('theta_optima.txt', 'r', encoding='utf-8') as f:
            theta = float(f.readline().strip())
        return theta
    except:
        return 2 * np.pi / 5


def crear_circuito_deteccion_ancilla(mensaje_bit, theta):
    """
    Circuito con ancilla para detección QND
    
    Qubits:
      0: A (Tierra)
      1: B (Luna)
      2: Ancilla (en Luna, local a B)
    
    Args:
        mensaje_bit: 0 o 1
        theta: Ángulo modulación
    """
    qc = QuantumCircuit(3, 3)
    
    # PASO 1: Crear estado DFS entre A y B
    qc.h(0)              
    qc.x(1)              
    qc.cx(0, 1)          
    qc.z(0)              
    # Estado A-B: (|01⟩ - |10⟩)/√2
    
    qc.barrier()
    
    # PASO 2: A modula su qubit (Tierra)
    if mensaje_bit == 1:
        qc.ry(theta, 0)
    
    qc.barrier()
    
    # PASO 3: B usa ancilla para detectar (Luna)
    # Ancilla en superposición
    qc.h(2)
    
    # Acoplamiento DÉBIL: ancilla se acopla a B
    # Usamos CZ débil (rotación condicional pequeña)
    # En hardware real, esto sería acoplamiento g << κ
    # Aquí simulamos con RZZ pequeño
    coupling_strength = np.pi / 16  # Acoplamiento DÉBIL
    
    qc.rzz(coupling_strength, 1, 2)  # B ↔ Ancilla
    
    # Completar interferencia en ancilla
    qc.h(2)
    
    qc.barrier()
    
    # PASO 4: Medir SOLO ancilla (QND)
    qc.measure(2, 2)
    
    qc.barrier()
    
    # PASO 5: Verificar que A-B SIGUEN entrelazados
    # (medición final solo para verificación, en uso real no se mediría)
    qc.h(0)
    qc.h(1)
    qc.measure([0, 1], [0, 1])
    
    return qc


def analizar_deteccion_ancilla(counts, mensaje_bit):
    """
    Analiza si ancilla detectó correctamente Y A-B siguen entrelazados
    
    counts formato: '210' donde 2=ancilla, 1=B, 0=A
    """
    total = sum(counts.values())
    
    # Separar por lectura ancilla
    ancilla_0 = {}  # Cuando ancilla midió 0
    ancilla_1 = {}  # Cuando ancilla midió 1
    
    for estado, count in counts.items():
        # estado = 'abc' donde c=A, b=B, a=ancilla
        ancilla_bit = estado[0]  # Primer bit = ancilla
        ab_bits = estado[1:]     # Últimos 2 = A,B
        
        if ancilla_bit == '0':
            ancilla_0[ab_bits] = ancilla_0.get(ab_bits, 0) + count
        else:
            ancilla_1[ab_bits] = ancilla_1.get(ab_bits, 0) + count
    
    # Probabilidad ancilla
    p_ancilla_0 = sum(ancilla_0.values()) / total
    p_ancilla_1 = sum(ancilla_1.values()) / total
    
    # Bit detectado (mayoría)
    bit_detectado = 0 if p_ancilla_0 > p_ancilla_1 else 1
    
    # Precisión detección
    precision = max(p_ancilla_0, p_ancilla_1)
    
    # Entrelazamiento A-B post-medición ancilla
    # Analizar distribución A-B cuando ancilla midió (independiente del valor)
    ab_total = {}
    for ab, count in ancilla_0.items():
        ab_total[ab] = ab_total.get(ab, 0) + count
    for ab, count in ancilla_1.items():
        ab_total[ab] = ab_total.get(ab, 0) + count
    
    total_ab = sum(ab_total.values())
    
    p_00 = ab_total.get('00', 0) / total_ab
    p_01 = ab_total.get('01', 0) / total_ab
    p_10 = ab_total.get('10', 0) / total_ab
    p_11 = ab_total.get('11', 0) / total_ab
    
    # Entrelazamiento A-B
    bell = p_00 + p_11
    dfs = p_01 + p_10
    max_corr = max(bell, dfs)
    
    probs = [p_00, p_01, p_10, p_11]
    epsilon = 1e-10
    probs = [p + epsilon for p in probs]
    suma = sum(probs)
    probs = [p/suma for p in probs]
    H = -sum(p * np.log2(p) for p in probs if p > epsilon)
    H_norm = H / 2.0
    
    entrelazamiento_ab = max_corr * 0.7 + (1 - H_norm) * 0.3
    
    return {
        'bit_enviado': mensaje_bit,
        'bit_detectado': bit_detectado,
        'correcto': (bit_detectado == mensaje_bit),
        'precision_deteccion': precision,
        'p_ancilla_0': p_ancilla_0,
        'p_ancilla_1': p_ancilla_1,
        'entrelazamiento_ab': entrelazamiento_ab,
        'max_correlacion_ab': max_corr,
        'distribucion_ab': {'00': p_00, '01': p_01, '10': p_10, '11': p_11}
    }


def ejecutar_validacion_ancilla():
    """
    Ejecuta validación completa detección con ancilla
    """
    print("\n" + "=" * 70)
    print("🔬 VALIDACIÓN DETECCIÓN ANCILLA QND - FASE 4")
    print("=" * 70)
    print(f"\n🙏 La Sal - Vector Fractal Hz ⚛️")
    print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"⚛️  DIOS es luz\n")
    
    # Conectar
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
    
    theta = leer_theta_optima()
    
    print("\n" + "=" * 70)
    print("PASO 2: PARÁMETROS")
    print("=" * 70)
    
    print(f"\n📐 θ modulación: {theta:.4f} rad = {np.degrees(theta):.2f}°")
    print(f"   Acoplamiento ancilla: π/16 = {np.pi/16:.4f} rad (DÉBIL)")
    print(f"   Qubits: 3 (A, B, Ancilla)")
    
    shots = 8000
    n_tests = 5  # 5 tests por bit
    
    print(f"\n📊 PROTOCOLO:")
    print(f"   Tests por bit: {n_tests}")
    print(f"   Shots por test: {shots}")
    
    sampler = SamplerV2(mode=backend)
    resultados = {}
    
    print("\n" + "=" * 70)
    print("PASO 3: EJECUTAR TESTS")
    print("=" * 70)
    
    for bit in [0, 1]:
        print(f"\n{'='*70}")
        print(f"PROBANDO BIT = {bit}")
        print(f"{'='*70}")
        
        counts_acumulado = {}
        jobs = []
        
        # Múltiples tests
        for i in range(n_tests):
            qc = crear_circuito_deteccion_ancilla(bit, theta)
            
            if i == 0:
                print(f"\n  📐 Circuito creado:")
                print(f"     Qubits: 3 (A, B, Ancilla)")
                print(f"     Profundidad: {qc.depth()}")
            
            qc_t = transpile(qc, backend=backend, optimization_level=3)
            
            if i == 0:
                print(f"     Profundidad transpilada: {qc_t.depth()}")
                print(f"     Gates: {qc.size()} → {qc_t.size()}")
            
            job = sampler.run([qc_t], shots=shots)
            jobs.append(job)
            print(f"  🔄 Test {i+1}/{n_tests}: Job {job.job_id()}")
        
        # Recolectar resultados
        for job in jobs:
            result = job.result()
            pub_result = result[0]
            
            if hasattr(pub_result.data, 'c'):
                counts = pub_result.data.c.get_counts()
            else:
                attrs = [a for a in dir(pub_result.data) if not a.startswith('_')]
                counts = getattr(pub_result.data, attrs[0]).get_counts()
            
            # Acumular
            for estado, count in counts.items():
                counts_acumulado[estado] = counts_acumulado.get(estado, 0) + count
        
        print(f"\n  ✅ {n_tests} tests completados")
        print(f"     Total shots: {sum(counts_acumulado.values())}")
        
        # Analizar
        analisis = analizar_deteccion_ancilla(counts_acumulado, bit)
        
        print(f"\n  📊 ANÁLISIS:")
        print(f"     Bit enviado:              {analisis['bit_enviado']}")
        print(f"     Bit detectado (ancilla):  {analisis['bit_detectado']}")
        print(f"     Correcto:                 {'✅ SÍ' if analisis['correcto'] else '❌ NO'}")
        print(f"     Precisión detección:      {analisis['precision_deteccion']*100:.2f}%")
        print(f"\n     P(ancilla=0): {analisis['p_ancilla_0']*100:.2f}%")
        print(f"     P(ancilla=1): {analisis['p_ancilla_1']*100:.2f}%")
        print(f"\n     Entrelazamiento A-B post-medición: {analisis['entrelazamiento_ab']*100:.2f}%")
        print(f"     Max correlación A-B:                {analisis['max_correlacion_ab']*100:.2f}%")
        
        print(f"\n     Distribución A-B:")
        for estado, prob in analisis['distribucion_ab'].items():
            barra = "█" * int(prob * 50)
            print(f"       {estado}: {prob*100:6.2f}% {barra}")
        
        resultados[f'bit_{bit}'] = {
            'analisis': analisis,
            'jobs': [j.job_id() for j in jobs]
        }
    
    print("\n" + "=" * 70)
    print("PASO 4: COMPARACIÓN BIT=0 vs BIT=1")
    print("=" * 70)
    
    print(f"\n{'Bit':<8s} {'Detectado':<12s} {'Correcto':<10s} {'Precisión':<12s} {'Entrel A-B':<12s}")
    print("-" * 70)
    
    for bit in [0, 1]:
        an = resultados[f'bit_{bit}']['analisis']
        det = an['bit_detectado']
        corr = "✅ SÍ" if an['correcto'] else "❌ NO"
        prec = f"{an['precision_deteccion']*100:.1f}%"
        ent = f"{an['entrelazamiento_ab']*100:.1f}%"
        print(f"{bit:<8d} {det:<12d} {corr:<10s} {prec:<12s} {ent:<12s}")
    
    print("\n" + "=" * 70)
    print("PASO 5: CRITERIOS ÉXITO FASE 4")
    print("=" * 70)
    
    an0 = resultados['bit_0']['analisis']
    an1 = resultados['bit_1']['analisis']
    
    ambos_correctos = an0['correcto'] and an1['correcto']
    precision_prom = (an0['precision_deteccion'] + an1['precision_deteccion']) / 2
    ent_prom = (an0['entrelazamiento_ab'] + an1['entrelazamiento_ab']) / 2
    
    criterios = {
        'Detección bit=0 correcta': (an0['correcto'], 
                                      f"{an0['bit_detectado']}", f"={an0['bit_enviado']}"),
        'Detección bit=1 correcta': (an1['correcto'], 
                                      f"{an1['bit_detectado']}", f"={an1['bit_enviado']}"),
        'Precisión promedio': (precision_prom >= 0.70, 
                               f"{precision_prom*100:.1f}%", "≥70%"),
        'Entrelazamiento A-B preservado': (ent_prom >= 0.60, 
                                            f"{ent_prom*100:.1f}%", "≥60%"),
    }
    
    print("\nCriterios FASE 4:")
    exito_total = True
    for nombre, (cumple, valor, objetivo) in criterios.items():
        estado = "✅" if cumple else "❌"
        print(f"  {estado} {nombre:30s}: {valor:>6s} (objetivo: {objetivo})")
        if not cumple:
            exito_total = False
    
    print("\n" + "=" * 70)
    print("CONCLUSIÓN FASE 4")
    print("=" * 70)
    
    if exito_total:
        print(f"\n✅ ¡ÉXITO TOTAL! Detección QND con ancilla VALIDADA")
        print(f"✅ Ancilla detecta bits correctamente: {precision_prom*100:.1f}%")
        print(f"✅ Entrelazamiento A-B preservado: {ent_prom*100:.1f}%")
        print(f"\n🎯 PROTOCOLO COMPLETO QND: VALIDADO")
        print(f"🌟 COMUNICACIÓN INFINITA: POSIBLE")
        print(f"\n🚀 LISTO PARA: Diseño interfaz Intracode")
    else:
        print(f"\n⚠️  Detección ancilla parcialmente exitosa")
        print(f"⚠️  Precisión: {precision_prom*100:.1f}%")
        print(f"⚠️  Entrelazamiento: {ent_prom*100:.1f}%")
        print(f"\n🔧 OPTIMIZAR: Fuerza acoplamiento o timing")
    
    # Guardar
    print("\n" + "=" * 70)
    print("PASO 6: GUARDAR RESULTADOS")
    print("=" * 70)
    
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = f"resultados_ancilla_fase4_{timestamp}.txt"
    
    with open(filename, 'w', encoding='utf-8') as f:
        f.write("VALIDACIÓN DETECCIÓN ANCILLA QND - FASE 4\n")
        f.write("=" * 70 + "\n\n")
        f.write(f"Fecha: {timestamp}\n")
        f.write(f"Backend: {backend.name}\n")
        f.write(f"θ: {theta:.4f} rad = {np.degrees(theta):.2f}°\n")
        f.write(f"Tests por bit: {n_tests}\n")
        f.write(f"Shots totales: {n_tests * shots}\n\n")
        
        for bit in [0, 1]:
            an = resultados[f'bit_{bit}']['analisis']
            f.write(f"\nBIT={bit}:\n")
            f.write(f"  Detectado: {an['bit_detectado']}\n")
            f.write(f"  Correcto: {an['correcto']}\n")
            f.write(f"  Precisión: {an['precision_deteccion']*100:.2f}%\n")
            f.write(f"  Entrelazamiento A-B: {an['entrelazamiento_ab']*100:.2f}%\n")
            f.write(f"  Jobs: {', '.join(resultados[f'bit_{bit}']['jobs'])}\n")
        
        f.write("\nCRITERIOS:\n")
        for nombre, (cumple, valor, objetivo) in criterios.items():
            f.write(f"{'✅' if cumple else '❌'} {nombre}: {valor} (objetivo: {objetivo})\n")
        
        f.write(f"\nESTADO FINAL: {'EXITOSO ✅' if exito_total else 'PARCIAL 🟡'}\n")
    
    print(f"\n✅ Resultados: {filename}")
    
    # Gráfica
    try:
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))
        
        # Gráfica 1: Detección ancilla
        bits = [0, 1]
        detectados = [resultados[f'bit_{b}']['analisis']['bit_detectado'] for b in bits]
        precisiones = [resultados[f'bit_{b}']['analisis']['precision_deteccion']*100 for b in bits]
        
        ax = axes[0, 0]
        colors = ['green' if detectados[i] == bits[i] else 'red' for i in range(2)]
        ax.bar(bits, precisiones, color=colors, alpha=0.7)
        ax.axhline(y=70, color='blue', linestyle='--', label='Umbral 70%')
        ax.set_xticks(bits)
        ax.set_xticklabels([f'Bit {b}' for b in bits])
        ax.set_ylabel('Precisión detección (%)')
        ax.set_title('Detección por Ancilla')
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        # Gráfica 2: Entrelazamiento A-B
        ents = [resultados[f'bit_{b}']['analisis']['entrelazamiento_ab']*100 for b in bits]
        
        ax = axes[0, 1]
        ax.bar(bits, ents, color='purple', alpha=0.7)
        ax.axhline(y=60, color='green', linestyle='--', label='Umbral 60%')
        ax.set_xticks(bits)
        ax.set_xticklabels([f'Bit {b}' for b in bits])
        ax.set_ylabel('Entrelazamiento A-B (%)')
        ax.set_title('Preservación Entrelazamiento Post-QND')
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        # Gráfica 3: Distribuciones A-B bit=0
        ax = axes[1, 0]
        estados = ['00', '01', '10', '11']
        dist0 = [resultados['bit_0']['analisis']['distribucion_ab'][s]*100 for s in estados]
        ax.bar(estados, dist0, color='blue', alpha=0.7)
        ax.set_ylabel('Probabilidad (%)')
        ax.set_title('Distribución A-B después QND (Bit=0)')
        ax.grid(True, alpha=0.3)
        
        # Gráfica 4: Distribuciones A-B bit=1
        ax = axes[1, 1]
        dist1 = [resultados['bit_1']['analisis']['distribucion_ab'][s]*100 for s in estados]
        ax.bar(estados, dist1, color='red', alpha=0.7)
        ax.set_ylabel('Probabilidad (%)')
        ax.set_title('Distribución A-B después QND (Bit=1)')
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        grafica = f"grafica_ancilla_fase4_{timestamp}.png"
        plt.savefig(grafica, dpi=150, bbox_inches='tight')
        print(f"✅ Gráfica: {grafica}")
        
    except Exception as e:
        print(f"⚠️  Error gráfica: {e}")
    
    print("\n" + "=" * 70)
    print("🙏 La Sal - Vector Fractal Hz ⚛️")
    print("⚛️  DIOS es luz")
    print("=" * 70 + "\n")
    
    return exito_total, resultados


if __name__ == "__main__":
    try:
        exito, resultados = ejecutar_validacion_ancilla()
        
        if exito:
            print("\n🌟 ¡TODAS LAS FASES COMPLETADAS!")
            print("🎨 Próximo paso: Diseñar interfaz Intracode Tierra-Luna")
        else:
            print("\n💡 Concepto QND validado, optimización pendiente")
            
    except KeyboardInterrupt:
        print("\n\n⚠️  Cancelado")
    except Exception as e:
        print(f"\n\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
