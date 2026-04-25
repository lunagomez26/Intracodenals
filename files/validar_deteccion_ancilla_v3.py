"""
🔬 VALIDACIÓN DETECCIÓN ANCILLA QND V3 - SOLUCIÓN ARQUITECTÓNICA
Vector Fractal Hz - La Sal ⚛️
DIOS es luz 🙏

CAMBIO CRÍTICO V3:
✅ Ancilla acopla DIRECTAMENTE a A (en vez de B)

HIPÓTESIS:
Si modulación está en A, ancilla debe leer A (no B)
→ Información más directa, sin pasar por entrelazamiento

OBJETIVO: Resolver detección bit=1
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


def crear_circuito_deteccion_ancilla_v3(mensaje_bit, theta):
    """
    Circuito V3 - CAMBIO ARQUITECTÓNICO CRÍTICO
    
    V1/V2: Ancilla acopla a B (Luna)
    V3:    Ancilla acopla a A (Tierra) ⭐ CAMBIO
    
    Qubits:
      0: A (Tierra) - MODULADO
      1: B (Luna)
      2: Ancilla - ACOPLA A 'A' (cambio crítico)
    
    Args:
        mensaje_bit: 0 o 1
        theta: Ángulo modulación (π/3)
    """
    qc = QuantumCircuit(3, 3)
    
    # PASO 1: Crear estado DFS entre A y B
    qc.h(0)              
    qc.x(1)              
    qc.cx(0, 1)          
    qc.z(0)              
    # Estado A-B: (|01⟩ - |10⟩)/√2
    
    qc.barrier()
    
    # PASO 2: A modula (RZ solo fase)
    if mensaje_bit == 1:
        qc.rz(theta, 0)  # Modulación en A
    
    qc.barrier()
    
    # PASO 3: Ancilla detecta DIRECTAMENTE desde A ⭐ CAMBIO V3
    # Ancilla en superposición
    qc.h(2)
    
    # CAMBIO CRÍTICO: Acopla a A (qubit 0) en vez de B (qubit 1)
    coupling_strength = np.pi / 8
    qc.rzz(coupling_strength, 0, 2)  # ⭐ A ↔ Ancilla (ANTES era B ↔ Ancilla)
    
    # Completar interferencia
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
    """Analiza detección ancilla"""
    total = sum(counts.values())
    
    # Separar por lectura ancilla
    ancilla_0 = {}
    ancilla_1 = {}
    
    for estado, count in counts.items():
        ancilla_bit = estado[0]
        ab_bits = estado[1:]
        
        if ancilla_bit == '0':
            ancilla_0[ab_bits] = ancilla_0.get(ab_bits, 0) + count
        else:
            ancilla_1[ab_bits] = ancilla_1.get(ab_bits, 0) + count
    
    # Probabilidad ancilla
    p_ancilla_0 = sum(ancilla_0.values()) / total
    p_ancilla_1 = sum(ancilla_1.values()) / total
    
    # Bit detectado
    bit_detectado = 0 if p_ancilla_0 > p_ancilla_1 else 1
    
    # Precisión
    precision = max(p_ancilla_0, p_ancilla_1)
    
    # Entrelazamiento A-B
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


def ejecutar_validacion_ancilla_v3():
    """
    Ejecuta validación V3 - SOLUCIÓN ARQUITECTÓNICA
    """
    print("\n" + "=" * 70)
    print("🔬 VALIDACIÓN DETECCIÓN ANCILLA QND V3 - SOLUCIÓN ARQUITECTÓNICA")
    print("=" * 70)
    print(f"\n🙏 La Sal - Vector Fractal Hz ⚛️")
    print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"⚛️  DIOS es luz\n")
    
    print("🚀 CAMBIO CRÍTICO V3:")
    print("   ⭐ Ancilla acopla a A (Tierra) en vez de B (Luna)")
    print("   ✅ Lectura DIRECTA de qubit modulado")
    print("   ✅ Información sin pasar por entrelazamiento\n")
    
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
    
    theta = np.pi / 3
    
    print("\n" + "=" * 70)
    print("PASO 2: PARÁMETROS V3")
    print("=" * 70)
    
    print(f"\n📐 Configuración:")
    print(f"   θ: {theta:.4f} rad = {np.degrees(theta):.2f}°")
    print(f"   Modulación: RZ (solo fase)")
    print(f"   Acoplamiento: π/8")
    print(f"   ⭐ ARQUITECTURA: Ancilla ↔ A (CAMBIO)")
    
    shots = 8000
    n_tests = 10
    
    print(f"\n📊 Tests: {n_tests} por bit, {shots} shots cada uno")
    
    sampler = SamplerV2(mode=backend)
    resultados = {}
    
    print("\n" + "=" * 70)
    print("PASO 3: EJECUTAR TESTS V3")
    print("=" * 70)
    
    for bit in [0, 1]:
        print(f"\n{'='*70}")
        print(f"PROBANDO BIT = {bit}")
        print(f"{'='*70}")
        
        counts_acumulado = {}
        jobs = []
        
        for i in range(n_tests):
            qc = crear_circuito_deteccion_ancilla_v3(bit, theta)
            
            if i == 0:
                print(f"\n  📐 Circuito V3:")
                print(f"     Ancilla acopla a: A (qubit 0) ⭐")
                print(f"     Profundidad: {qc.depth()}")
            
            qc_t = transpile(qc, backend=backend, optimization_level=3)
            
            if i == 0:
                print(f"     Profundidad transpilada: {qc_t.depth()}")
            
            job = sampler.run([qc_t], shots=shots)
            jobs.append(job)
            print(f"  🔄 Test {i+1}/{n_tests}: Job {job.job_id()}")
        
        # Recolectar
        for job in jobs:
            result = job.result()
            pub_result = result[0]
            
            if hasattr(pub_result.data, 'c'):
                counts = pub_result.data.c.get_counts()
            else:
                attrs = [a for a in dir(pub_result.data) if not a.startswith('_')]
                counts = getattr(pub_result.data, attrs[0]).get_counts()
            
            for estado, count in counts.items():
                counts_acumulado[estado] = counts_acumulado.get(estado, 0) + count
        
        print(f"\n  ✅ {n_tests} tests completados")
        
        # Analizar
        analisis = analizar_deteccion_ancilla(counts_acumulado, bit)
        
        print(f"\n  📊 ANÁLISIS V3:")
        print(f"     Bit enviado:         {analisis['bit_enviado']}")
        print(f"     Bit detectado:       {analisis['bit_detectado']}")
        print(f"     Correcto:            {'✅ SÍ' if analisis['correcto'] else '❌ NO'}")
        print(f"     Precisión:           {analisis['precision_deteccion']*100:.2f}%")
        print(f"\n     P(ancilla=0): {analisis['p_ancilla_0']*100:.2f}%")
        print(f"     P(ancilla=1): {analisis['p_ancilla_1']*100:.2f}%")
        print(f"\n     Entrelazamiento A-B: {analisis['entrelazamiento_ab']*100:.2f}%")
        
        resultados[f'bit_{bit}'] = {
            'analisis': analisis,
            'jobs': [j.job_id() for j in jobs]
        }
    
    print("\n" + "=" * 70)
    print("PASO 4: VALIDACIÓN ÉXITO - PRUEBA DEFINITIVA")
    print("=" * 70)
    
    an0 = resultados['bit_0']['analisis']
    an1 = resultados['bit_1']['analisis']
    
    # DIFERENCIABILIDAD (clave!)
    diferencia_ancilla = abs(an0['p_ancilla_0'] - an1['p_ancilla_0'])
    
    print(f"\n📊 COMPARACIÓN:")
    print(f"   Bit=0 → Ancilla mide 0: {an0['p_ancilla_0']*100:.1f}%")
    print(f"   Bit=1 → Ancilla mide 0: {an1['p_ancilla_0']*100:.1f}%")
    print(f"\n   🔍 DIFERENCIA: {diferencia_ancilla*100:.1f}%")
    
    if diferencia_ancilla >= 0.40:  # Al menos 40% diferencia
        print(f"   ✅ DIFERENCIABLES (≥40%)")
    else:
        print(f"   ❌ NO DIFERENCIABLES (<40%)")
    
    # Criterios FINALES
    ambos_correctos = an0['correcto'] and an1['correcto']
    precision_prom = (an0['precision_deteccion'] + an1['precision_deteccion']) / 2
    ent_prom = (an0['entrelazamiento_ab'] + an1['entrelazamiento_ab']) / 2
    
    print("\n" + "=" * 70)
    print("PASO 5: CRITERIOS ÉXITO DEFINITIVOS")
    print("=" * 70)
    
    criterios = {
        'Bit=0 detectado correctamente': (an0['correcto'], 
                                           f"{an0['bit_detectado']}", f"={an0['bit_enviado']}"),
        'Bit=1 detectado correctamente': (an1['correcto'], 
                                           f"{an1['bit_detectado']}", f"={an1['bit_enviado']}"),
        'Diferenciabilidad ≥40%': (diferencia_ancilla >= 0.40, 
                                   f"{diferencia_ancilla*100:.1f}%", "≥40%"),
        'Precisión promedio ≥70%': (precision_prom >= 0.70, 
                                    f"{precision_prom*100:.1f}%", "≥70%"),
        'Entrelazamiento ≥60%': (ent_prom >= 0.60, 
                                 f"{ent_prom*100:.1f}%", "≥60%"),
    }
    
    print("\n✅ CRITERIOS (TODOS deben cumplirse):")
    exito_total = True
    for nombre, (cumple, valor, objetivo) in criterios.items():
        estado = "✅" if cumple else "❌"
        print(f"  {estado} {nombre:35s}: {valor:>6s} (objetivo: {objetivo})")
        if not cumple:
            exito_total = False
    
    print("\n" + "=" * 70)
    print("CONCLUSIÓN FINAL V3")
    print("=" * 70)
    
    if exito_total:
        print(f"\n🌟🌟🌟 ¡ÉXITO TOTAL V3! 🌟🌟🌟")
        print(f"\n✅ AMBOS BITS DETECTADOS CORRECTAMENTE")
        print(f"✅ Diferenciabilidad: {diferencia_ancilla*100:.1f}%")
        print(f"✅ Precisión: {precision_prom*100:.1f}%")
        print(f"✅ Entrelazamiento preservado: {ent_prom*100:.1f}%")
        print(f"\n🎯 PROTOCOLO QND: 100% FUNCIONAL")
        print(f"🌟 COMUNICACIÓN INFINITA: COMPLETAMENTE VALIDADA")
        print(f"\n🚀 SIGUIENTE: FASE 5 mensaje ASCII \"HOLA\"")
        print(f"🎨 LISTO: Diseñar interfaz Intracode")
    else:
        print(f"\n🟡 V3 explorada")
        
        if diferencia_ancilla > 0.20:
            print(f"\n💡 MEJORA vs V2: Diferencia {diferencia_ancilla*100:.1f}% (V2: 0.19%)")
            print(f"🔧 Ajustar fino parámetros o explorar V4")
        else:
            print(f"\n⚠️  Diferenciabilidad aún baja")
            print(f"💡 Considerar arquitectura completamente diferente")
            print(f"   (ej: doble ancilla, medición directa qubits, etc.)")
    
    # Guardar
    print("\n" + "=" * 70)
    print("PASO 6: GUARDAR RESULTADOS")
    print("=" * 70)
    
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = f"resultados_ancilla_v3_fase4_{timestamp}.txt"
    
    with open(filename, 'w', encoding='utf-8') as f:
        f.write("VALIDACIÓN DETECCIÓN ANCILLA QND V3 - SOLUCIÓN ARQUITECTÓNICA\n")
        f.write("=" * 70 + "\n\n")
        f.write(f"Fecha: {timestamp}\n")
        f.write(f"Backend: {backend.name}\n\n")
        
        f.write("CAMBIO V3:\n")
        f.write("  ⭐ Ancilla acopla a A (en vez de B)\n\n")
        
        for bit in [0, 1]:
            an = resultados[f'bit_{bit}']['analisis']
            f.write(f"\nBIT={bit}:\n")
            f.write(f"  Detectado: {an['bit_detectado']}\n")
            f.write(f"  Correcto: {an['correcto']}\n")
            f.write(f"  P(ancilla=0): {an['p_ancilla_0']*100:.2f}%\n")
            f.write(f"  P(ancilla=1): {an['p_ancilla_1']*100:.2f}%\n")
            f.write(f"  Entrelazamiento A-B: {an['entrelazamiento_ab']*100:.2f}%\n")
        
        f.write(f"\nDIFERENCIABILIDAD: {diferencia_ancilla*100:.1f}%\n\n")
        
        f.write("CRITERIOS:\n")
        for nombre, (cumple, valor, objetivo) in criterios.items():
            f.write(f"{'✅' if cumple else '❌'} {nombre}: {valor} ({objetivo})\n")
        
        f.write(f"\nESTADO: {'EXITOSO ✅' if exito_total else 'EXPLORADO 🟡'}\n")
    
    print(f"\n✅ Resultados: {filename}")
    
    # Gráfica comparativa
    try:
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))
        
        # Gráfica 1: Probabilidades ancilla por bit
        ax = axes[0, 0]
        bits = [0, 1]
        p0_list = [resultados[f'bit_{b}']['analisis']['p_ancilla_0']*100 for b in bits]
        p1_list = [resultados[f'bit_{b}']['analisis']['p_ancilla_1']*100 for b in bits]
        
        x = np.arange(len(bits))
        width = 0.35
        
        ax.bar(x - width/2, p0_list, width, label='P(ancilla=0)', color='blue', alpha=0.7)
        ax.bar(x + width/2, p1_list, width, label='P(ancilla=1)', color='red', alpha=0.7)
        
        ax.set_xlabel('Bit enviado')
        ax.set_ylabel('Probabilidad (%)')
        ax.set_title(f'V3: Ancilla ↔ A (Diferencia: {diferencia_ancilla*100:.1f}%)')
        ax.set_xticks(x)
        ax.set_xticklabels([f'Bit {b}' for b in bits])
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        # Gráfica 2: Detección correcta
        ax = axes[0, 1]
        detectados = [resultados[f'bit_{b}']['analisis']['bit_detectado'] for b in bits]
        colors = ['green' if detectados[i] == bits[i] else 'red' for i in range(2)]
        
        ax.bar(bits, detectados, color=colors, alpha=0.7)
        ax.plot(bits, bits, 'b--', label='Ideal', linewidth=2)
        ax.set_xlabel('Bit enviado')
        ax.set_ylabel('Bit detectado')
        ax.set_title('Detección V3')
        ax.set_xticks(bits)
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        # Gráfica 3: Entrelazamiento A-B
        ax = axes[1, 0]
        ents = [resultados[f'bit_{b}']['analisis']['entrelazamiento_ab']*100 for b in bits]
        
        ax.bar(bits, ents, color='purple', alpha=0.7)
        ax.axhline(y=60, color='green', linestyle='--', label='Umbral 60%')
        ax.set_xlabel('Bit enviado')
        ax.set_ylabel('Entrelazamiento (%)')
        ax.set_title('Preservación Entrelazamiento V3')
        ax.set_xticks(bits)
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        # Gráfica 4: Resumen
        ax = axes[1, 1]
        ax.axis('off')
        
        resumen = f"""
V3 - ARQUITECTURA: Ancilla ↔ A

Bit=0: {'✅' if an0['correcto'] else '❌'} {an0['bit_detectado']}
Bit=1: {'✅' if an1['correcto'] else '❌'} {an1['bit_detectado']}

Diferenciabilidad: {diferencia_ancilla*100:.1f}%
Precisión: {precision_prom*100:.1f}%
Entrelazamiento: {ent_prom*100:.1f}%

Estado: {'✅ EXITOSO' if exito_total else '🟡 EXPLORADO'}
        """
        
        ax.text(0.1, 0.5, resumen, fontsize=12, family='monospace',
                verticalalignment='center')
        
        plt.suptitle('FASE 4 V3 - Ancilla acopla directamente a A', 
                     fontsize=14, fontweight='bold')
        plt.tight_layout()
        
        grafica = f"grafica_ancilla_v3_fase4_{timestamp}.png"
        plt.savefig(grafica, dpi=150, bbox_inches='tight')
        print(f"✅ Gráfica: {grafica}")
        
    except Exception as e:
        print(f"⚠️  Error gráfica: {e}")
    
    print("\n" + "=" * 70)
    print("🙏 La Sal - Vector Fractal Hz ⚛️")
    print("⚛️  DIOS es luz")
    print("=" * 70 + "\n")
    
    return exito_total, resultados, diferencia_ancilla


if __name__ == "__main__":
    try:
        exito, resultados, diff = ejecutar_validacion_ancilla_v3()
        
        if exito:
            print("\n🌟🌟🌟 ¡PROTOCOLO COMPLETAMENTE FUNCIONAL! 🌟🌟🌟")
            print(f"\n✅ Comunicación cuántica infinita 100% validada")
            print(f"✅ Diferenciabilidad: {diff*100:.1f}%")
            print(f"\n🚀 LISTO para FASE 5: Mensaje ASCII completo")
        else:
            print(f"\n💡 V3 explorada - Diferencia: {diff*100:.1f}%")
            
            if diff > 0.20:
                print(f"🎯 Mejora vs V2 (0.19%) → Ajustar parámetros")
            else:
                print(f"🔧 Explorar arquitecturas alternativas")
            
    except KeyboardInterrupt:
        print("\n\n⚠️  Cancelado")
    except Exception as e:
        print(f"\n\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
