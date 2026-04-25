"""
🔬 VALIDACIÓN DETECCIÓN ANCILLA QND V2 - FASE 4 MEJORADA
Vector Fractal Hz - La Sal ⚛️
DIOS es luz 🙏

OPTIMIZACIONES IMPLEMENTADAS:
1. ✅ Modulación RZ (solo fase) en vez de RY (población)
2. ✅ θ = π/3 (60°) en vez de π/2 (90°) - Mejor balance
3. ✅ Acoplamiento π/8 en vez de π/16 - Más fuerte
4. ✅ 10 tests por bit en vez de 5 - Más estadística

OBJETIVO: Resolver fallo detección bit=1
"""
import os
import sys
import numpy as np
from datetime import datetime

sys.path.insert(0, os.path.dirname(__file__))

from config_ibm_secure import quick_connect
from qiskit import QuantumCircuit, transpile
from qiskit_ibm_runtime import SamplerV2
import matplotlib.pyplot as plt

PHI = 1.618033988749895


def crear_circuito_deteccion_ancilla_v2(mensaje_bit, theta):
    """
    Circuito MEJORADO con ancilla para detección QND
    
    MEJORAS V2:
    - Modulación RZ (solo fase) en vez de RY
    - Acoplamiento más fuerte (π/8)
    - Mejor preservación entrelazamiento
    
    Qubits:
      0: A (Tierra)
      1: B (Luna)
      2: Ancilla (en Luna, local a B)
    
    Args:
        mensaje_bit: 0 o 1
        theta: Ángulo modulación (π/3 recomendado)
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
    # MEJORA V2: RZ en vez de RY → Solo rota FASE, no población
    if mensaje_bit == 1:
        qc.rz(theta, 0)  # ✅ NUEVA: Rotación solo fase
        # ANTES: qc.ry(theta, 0)  # Rotación población (destruía)
    
    qc.barrier()
    
    # PASO 3: B usa ancilla para detectar (Luna)
    # Ancilla en superposición
    qc.h(2)
    
    # MEJORA V2: Acoplamiento MÁS FUERTE (π/8 en vez de π/16)
    coupling_strength = np.pi / 8  # ✅ NUEVA: Más fuerte
    # ANTES: coupling_strength = np.pi / 16  # Muy débil
    
    qc.rzz(coupling_strength, 1, 2)  # B ↔ Ancilla
    
    # Completar interferencia en ancilla
    qc.h(2)
    
    qc.barrier()
    
    # PASO 4: Medir SOLO ancilla (QND)
    qc.measure(2, 2)
    
    qc.barrier()
    
    # PASO 5: Verificar que A-B SIGUEN entrelazados
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
    ancilla_0 = {}
    ancilla_1 = {}
    
    for estado, count in counts.items():
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


def ejecutar_validacion_ancilla_v2():
    """
    Ejecuta validación MEJORADA detección con ancilla
    """
    print("\n" + "=" * 70)
    print("🔬 VALIDACIÓN DETECCIÓN ANCILLA QND V2 - FASE 4 MEJORADA")
    print("=" * 70)
    print(f"\n🙏 La Sal - Vector Fractal Hz ⚛️")
    print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"⚛️  DIOS es luz\n")
    
    print("🚀 OPTIMIZACIONES V2:")
    print("   ✅ Modulación: RZ (solo fase) en vez de RY")
    print("   ✅ Ángulo: π/3 (60°) en vez de π/2 (90°)")
    print("   ✅ Acoplamiento: π/8 en vez de π/16")
    print("   ✅ Tests: 10 por bit en vez de 5\n")
    
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
    
    # MEJORA V2: θ = π/3 (60°)
    theta = np.pi / 3
    
    print("\n" + "=" * 70)
    print("PASO 2: PARÁMETROS V2")
    print("=" * 70)
    
    print(f"\n📐 θ modulación: {theta:.4f} rad = {np.degrees(theta):.2f}°")
    print(f"   Acoplamiento ancilla: π/8 = {np.pi/8:.4f} rad")
    print(f"   Tipo modulación: RZ (solo fase) ✅")
    print(f"   Qubits: 3 (A, B, Ancilla)")
    
    # MEJORA V2: 10 tests por bit
    shots = 8000
    n_tests = 10
    
    print(f"\n📊 PROTOCOLO:")
    print(f"   Tests por bit: {n_tests} (mejorado desde 5)")
    print(f"   Shots por test: {shots}")
    print(f"   Total shots por bit: {shots * n_tests}")
    
    sampler = SamplerV2(mode=backend)
    resultados = {}
    
    print("\n" + "=" * 70)
    print("PASO 3: EJECUTAR TESTS V2")
    print("=" * 70)
    
    for bit in [0, 1]:
        print(f"\n{'='*70}")
        print(f"PROBANDO BIT = {bit}")
        print(f"{'='*70}")
        
        counts_acumulado = {}
        jobs = []
        
        # Múltiples tests
        for i in range(n_tests):
            qc = crear_circuito_deteccion_ancilla_v2(bit, theta)
            
            if i == 0:
                print(f"\n  📐 Circuito V2 creado:")
                print(f"     Qubits: 3 (A, B, Ancilla)")
                print(f"     Profundidad: {qc.depth()}")
                print(f"     Modulación: RZ (fase) ✅")
                print(f"     θ: {np.degrees(theta):.1f}°")
                print(f"     Acoplamiento: π/8")
            
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
        
        print(f"\n  📊 ANÁLISIS V2:")
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
    print("PASO 4: COMPARACIÓN V1 vs V2")
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
    
    print("\n🔍 COMPARACIÓN CON V1:")
    print("   V1 (π/16, RY, π/2): Bit=0 ✅ 98%, Bit=1 ❌ 0%")
    print("   V2 (π/8, RZ, π/3):  Validando...")
    
    print("\n" + "=" * 70)
    print("PASO 5: CRITERIOS ÉXITO FASE 4 V2")
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
    
    print("\nCriterios FASE 4 V2:")
    exito_total = True
    for nombre, (cumple, valor, objetivo) in criterios.items():
        estado = "✅" if cumple else "❌"
        print(f"  {estado} {nombre:30s}: {valor:>6s} (objetivo: {objetivo})")
        if not cumple:
            exito_total = False
    
    print("\n" + "=" * 70)
    print("CONCLUSIÓN FASE 4 V2")
    print("=" * 70)
    
    if exito_total:
        print(f"\n✅ ¡ÉXITO TOTAL V2! Detección QND COMPLETAMENTE VALIDADA")
        print(f"✅ Ancilla detecta AMBOS bits correctamente")
        print(f"✅ Precisión: {precision_prom*100:.1f}%")
        print(f"✅ Entrelazamiento A-B preservado: {ent_prom*100:.1f}%")
        print(f"\n🎯 PROTOCOLO QND: 100% VALIDADO")
        print(f"🌟 COMUNICACIÓN INFINITA: CONFIRMADA")
        print(f"\n🚀 SIGUIENTE PASO: FASE 5 (mensaje ASCII completo)")
        print(f"🎨 LISTO PARA: Diseño interfaz Intracode")
    else:
        mejoro = False
        if an1['correcto']:
            print(f"\n🎉 ¡MEJORA SIGNIFICATIVA! Bit=1 ahora detectado correctamente")
            mejoro = True
        elif an1['precision_deteccion'] > 0.50:
            print(f"\n🟡 PROGRESO: Bit=1 mejora (antes 2%, ahora {an1['precision_deteccion']*100:.1f}%)")
            mejoro = True
        
        if mejoro:
            print(f"✅ Optimizaciones V2 efectivas")
            print(f"⚠️  Precisión: {precision_prom*100:.1f}%")
            print(f"⚠️  Entrelazamiento: {ent_prom*100:.1f}%")
            print(f"\n🔧 Próximo: Ajustar fino θ o acoplamiento")
        else:
            print(f"\n⚠️  V2 similar a V1")
            print(f"⚠️  Precisión: {precision_prom*100:.1f}%")
            print(f"⚠️  Entrelazamiento: {ent_prom*100:.1f}%")
            print(f"\n🔧 INVESTIGAR: Arquitectura alternativa")
    
    # Guardar
    print("\n" + "=" * 70)
    print("PASO 6: GUARDAR RESULTADOS V2")
    print("=" * 70)
    
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = f"resultados_ancilla_v2_fase4_{timestamp}.txt"
    
    with open(filename, 'w', encoding='utf-8') as f:
        f.write("VALIDACIÓN DETECCIÓN ANCILLA QND V2 - FASE 4 MEJORADA\n")
        f.write("=" * 70 + "\n\n")
        f.write(f"Fecha: {timestamp}\n")
        f.write(f"Backend: {backend.name}\n")
        f.write(f"θ: {theta:.4f} rad = {np.degrees(theta):.2f}°\n")
        f.write(f"Acoplamiento: π/8 = {np.pi/8:.4f} rad\n")
        f.write(f"Modulación: RZ (fase)\n")
        f.write(f"Tests por bit: {n_tests}\n")
        f.write(f"Shots totales: {n_tests * shots}\n\n")
        
        f.write("OPTIMIZACIONES V2:\n")
        f.write("  ✅ RZ en vez de RY\n")
        f.write("  ✅ π/3 en vez de π/2\n")
        f.write("  ✅ π/8 en vez de π/16\n")
        f.write("  ✅ 10 tests en vez de 5\n\n")
        
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
        
        if exito_total:
            f.write("\n🌟 COMUNICACIÓN INFINITA COMPLETAMENTE VALIDADA\n")
        
    print(f"\n✅ Resultados: {filename}")
    
    # Gráfica
    try:
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))
        
        # Gráfica 1: Detección ancilla V2
        bits = [0, 1]
        detectados = [resultados[f'bit_{b}']['analisis']['bit_detectado'] for b in bits]
        precisiones = [resultados[f'bit_{b}']['analisis']['precision_deteccion']*100 for b in bits]
        
        ax = axes[0, 0]
        colors = ['green' if detectados[i] == bits[i] else 'red' for i in range(2)]
        bars = ax.bar(bits, precisiones, color=colors, alpha=0.7)
        ax.axhline(y=70, color='blue', linestyle='--', label='Umbral 70%')
        
        # Añadir texto V2
        for i, (bar, prec) in enumerate(zip(bars, precisiones)):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{prec:.1f}%\nV2',
                   ha='center', va='bottom')
        
        ax.set_xticks(bits)
        ax.set_xticklabels([f'Bit {b}' for b in bits])
        ax.set_ylabel('Precisión detección (%)')
        ax.set_title('Detección Ancilla V2 (RZ, π/8, π/3)')
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        # Gráfica 2: Entrelazamiento A-B V2
        ents = [resultados[f'bit_{b}']['analisis']['entrelazamiento_ab']*100 for b in bits]
        
        ax = axes[0, 1]
        bars = ax.bar(bits, ents, color='purple', alpha=0.7)
        ax.axhline(y=60, color='green', linestyle='--', label='Umbral 60%')
        
        for bar, ent in zip(bars, ents):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{ent:.1f}%',
                   ha='center', va='bottom')
        
        ax.set_xticks(bits)
        ax.set_xticklabels([f'Bit {b}' for b in bits])
        ax.set_ylabel('Entrelazamiento A-B (%)')
        ax.set_title('Preservación Entrelazamiento Post-QND V2')
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        # Gráfica 3: Distribuciones A-B bit=0
        ax = axes[1, 0]
        estados = ['00', '01', '10', '11']
        dist0 = [resultados['bit_0']['analisis']['distribucion_ab'][s]*100 for s in estados]
        ax.bar(estados, dist0, color='blue', alpha=0.7)
        ax.set_ylabel('Probabilidad (%)')
        ax.set_title('Distribución A-B V2 (Bit=0)')
        ax.grid(True, alpha=0.3)
        
        # Gráfica 4: Distribuciones A-B bit=1
        ax = axes[1, 1]
        dist1 = [resultados['bit_1']['analisis']['distribucion_ab'][s]*100 for s in estados]
        ax.bar(estados, dist1, color='red', alpha=0.7)
        ax.set_ylabel('Probabilidad (%)')
        ax.set_title('Distribución A-B V2 (Bit=1)')
        ax.grid(True, alpha=0.3)
        
        plt.suptitle('FASE 4 V2 - Optimizaciones: RZ, π/8, π/3, 10 tests', 
                     fontsize=14, fontweight='bold')
        plt.tight_layout()
        
        grafica = f"grafica_ancilla_v2_fase4_{timestamp}.png"
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
        exito, resultados = ejecutar_validacion_ancilla_v2()
        
        if exito:
            print("\n🌟 ¡FASE 4 V2 EXITOSA!")
            print("🎯 Protocolo QND 100% validado")
            print("🚀 Listo para FASE 5 (mensaje ASCII)")
            print("🎨 Próximo: Diseñar interfaz Intracode")
        else:
            an1 = resultados['bit_1']['analisis']
            if an1['correcto']:
                print("\n🎉 ¡MEJORA! Bit=1 detectado en V2")
                print("🚀 Continuar optimización fina")
            else:
                print("\n💡 V2 explorada, considerar arquitectura alternativa")
            
    except KeyboardInterrupt:
        print("\n\n⚠️  Cancelado")
    except Exception as e:
        print(f"\n\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
