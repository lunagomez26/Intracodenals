"""
🔬 VALIDACIÓN DETECCIÓN DOBLE ANCILLA V4 - SOLUCIÓN DEFINITIVA
Vector Fractal Hz - La Sal ⚛️
DIOS es luz 🙏

CAMBIO ARQUITECTÓNICO V4:
✅ DOS ancillas independientes (en vez de una)
✅ Ancilla_A lee A (Tierra)
✅ Ancilla_B lee B (Luna)
✅ Comparar DIFERENCIA entre lecturas

HIPÓTESIS:
Si A modula pero B no, la DIFERENCIA entre ancillas
debería ser detectable, aunque cada una individualmente no lo sea.

OBJETIVO: Resolver detección bit=1 definitivamente
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


def crear_circuito_doble_ancilla_v4(mensaje_bit, theta):
    """
    Circuito V4 - DOBLE ANCILLA
    
    Qubits:
      0: A (Tierra) - MODULADO
      1: B (Luna)
      2: Ancilla_A - Lee A
      3: Ancilla_B - Lee B
    
    Args:
        mensaje_bit: 0 o 1
        theta: Ángulo modulación
    """
    qc = QuantumCircuit(4, 4)
    
    # PASO 1: Crear estado DFS entre A y B
    qc.h(0)
    qc.x(1)
    qc.cx(0, 1)
    qc.z(0)
    # Estado A-B: (|01⟩ - |10⟩)/√2
    
    qc.barrier()
    
    # PASO 2: A modula (RZ solo fase)
    if mensaje_bit == 1:
        qc.rz(theta, 0)  # Solo A modula
    
    qc.barrier()
    
    # PASO 3: DOBLE ANCILLA - AMBAS detectan simultáneamente
    coupling_strength = np.pi / 8
    
    # Ancilla_A detecta A
    qc.h(2)
    qc.rzz(coupling_strength, 0, 2)  # A ↔ Ancilla_A
    qc.h(2)
    
    # Ancilla_B detecta B
    qc.h(3)
    qc.rzz(coupling_strength, 1, 3)  # B ↔ Ancilla_B
    qc.h(3)
    
    qc.barrier()
    
    # PASO 4: Medir AMBAS ancillas (QND)
    qc.measure(2, 2)  # Ancilla_A → creg 2
    qc.measure(3, 3)  # Ancilla_B → creg 3
    
    qc.barrier()
    
    # PASO 5: Verificar A-B SIGUEN entrelazados
    qc.h(0)
    qc.h(1)
    qc.measure([0, 1], [0, 1])
    
    return qc


def analizar_doble_ancilla(counts, mensaje_bit):
    """
    Analiza detección con doble ancilla
    
    CLAVE: Comparar DIFERENCIA entre lecturas
    """
    total = sum(counts.values())
    
    # Analizar todas las combinaciones
    stats = {
        'ancilla_A_0': 0,  # Ancilla_A lee 0
        'ancilla_A_1': 0,  # Ancilla_A lee 1
        'ancilla_B_0': 0,  # Ancilla_B lee 0
        'ancilla_B_1': 0,  # Ancilla_B lee 1
        'ambas_0': 0,      # Ambas leen 0
        'ambas_1': 0,      # Ambas leen 1
        'diferentes': 0,   # Leen diferente
    }
    
    ab_total = {}
    
    for estado, count in counts.items():
        # Formato: AB (últimos 2) Ancilla_B Ancilla_A
        # Ejemplo: "0011" = A=1, B=1, Ancilla_B=0, Ancilla_A=0
        
        ancilla_A = estado[2]  # Posición 2 desde derecha
        ancilla_B = estado[3]  # Posición 3 desde derecha
        ab = estado[0:2]
        
        # Contar ancillas
        if ancilla_A == '0':
            stats['ancilla_A_0'] += count
        else:
            stats['ancilla_A_1'] += count
            
        if ancilla_B == '0':
            stats['ancilla_B_0'] += count
        else:
            stats['ancilla_B_1'] += count
        
        # Comparar
        if ancilla_A == '0' and ancilla_B == '0':
            stats['ambas_0'] += count
        elif ancilla_A == '1' and ancilla_B == '1':
            stats['ambas_1'] += count
        else:
            stats['diferentes'] += count
        
        # A-B
        ab_total[ab] = ab_total.get(ab, 0) + count
    
    # Normalizar
    for key in stats:
        stats[key] = stats[key] / total
    
    # DETECCIÓN: Usar diferencia entre ancillas
    # Si A modula, Ancilla_A debería diferir de Ancilla_B
    diferencia_ancillas = abs(stats['ancilla_A_0'] - stats['ancilla_B_0'])
    
    # Criterio detección:
    # Si diferencia > umbral → bit=1
    # Si diferencia < umbral → bit=0
    umbral = 0.20  # 20% diferencia
    
    if diferencia_ancillas > umbral:
        bit_detectado = 1
    else:
        bit_detectado = 0
    
    correcto = (bit_detectado == mensaje_bit)
    
    # Entrelazamiento A-B
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
        'correcto': correcto,
        'stats': stats,
        'diferencia_ancillas': diferencia_ancillas,
        'umbral': umbral,
        'entrelazamiento_ab': entrelazamiento_ab,
        'distribucion_ab': {'00': p_00, '01': p_01, '10': p_10, '11': p_11}
    }


def ejecutar_validacion_doble_ancilla_v4():
    """
    Ejecuta validación V4 - DOBLE ANCILLA
    """
    print("\n" + "=" * 70)
    print("🔬 VALIDACIÓN DOBLE ANCILLA V4 - SOLUCIÓN DEFINITIVA")
    print("=" * 70)
    print(f"\n🙏 La Sal - Vector Fractal Hz ⚛️")
    print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"⚛️  DIOS es luz\n")
    
    print("🚀 CAMBIO CRÍTICO V4:")
    print("   ⭐ DOS ancillas (en vez de una)")
    print("   ✅ Ancilla_A lee A (Tierra modulada)")
    print("   ✅ Ancilla_B lee B (Luna sin modular)")
    print("   ✅ Detectar por DIFERENCIA entre lecturas\n")
    
    # Conectar
    print("=" * 70)
    print("PASO 1: CONEXIÓN IBM QUANTUM")
    print("=" * 70)
    
    try:
        service, backend = quick_connect()
        print(f"\n✅ Backend: {backend.name}")
        print(f"✅ Qubits: {backend.num_qubits}")
        print(f"✅ Qubits necesarios: 4 (A, B, Ancilla_A, Ancilla_B)")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return None
    
    theta = np.pi / 3
    
    print("\n" + "=" * 70)
    print("PASO 2: PARÁMETROS V4")
    print("=" * 70)
    
    print(f"\n📐 Configuración:")
    print(f"   θ: {theta:.4f} rad = {np.degrees(theta):.2f}°")
    print(f"   Modulación: RZ (solo fase)")
    print(f"   Acoplamiento: π/8")
    print(f"   ⭐ ARQUITECTURA: Doble Ancilla")
    print(f"   Umbral detección: 20% diferencia")
    
    shots = 8000
    n_tests = 10
    
    print(f"\n📊 Tests: {n_tests} por bit, {shots} shots cada uno")
    
    sampler = SamplerV2(mode=backend)
    resultados = {}
    
    print("\n" + "=" * 70)
    print("PASO 3: EJECUTAR TESTS V4")
    print("=" * 70)
    
    for bit in [0, 1]:
        print(f"\n{'='*70}")
        print(f"PROBANDO BIT = {bit}")
        print(f"{'='*70}")
        
        counts_acumulado = {}
        jobs = []
        
        for i in range(n_tests):
            qc = crear_circuito_doble_ancilla_v4(bit, theta)
            
            if i == 0:
                print(f"\n  📐 Circuito V4:")
                print(f"     Qubits: 4 (A, B, Ancilla_A, Ancilla_B)")
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
        analisis = analizar_doble_ancilla(counts_acumulado, bit)
        
        print(f"\n  📊 ANÁLISIS V4:")
        print(f"     Bit enviado:         {analisis['bit_enviado']}")
        print(f"     Bit detectado:       {analisis['bit_detectado']}")
        print(f"     Correcto:            {'✅ SÍ' if analisis['correcto'] else '❌ NO'}")
        
        print(f"\n     Ancilla_A (lee A):")
        print(f"       P(0): {analisis['stats']['ancilla_A_0']*100:.2f}%")
        print(f"       P(1): {analisis['stats']['ancilla_A_1']*100:.2f}%")
        
        print(f"\n     Ancilla_B (lee B):")
        print(f"       P(0): {analisis['stats']['ancilla_B_0']*100:.2f}%")
        print(f"       P(1): {analisis['stats']['ancilla_B_1']*100:.2f}%")
        
        print(f"\n     🔍 DIFERENCIA: {analisis['diferencia_ancillas']*100:.1f}%")
        print(f"        Umbral: {analisis['umbral']*100:.1f}%")
        
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
    diff0 = an0['diferencia_ancillas']
    diff1 = an1['diferencia_ancillas']
    
    print(f"\n📊 COMPARACIÓN:")
    print(f"   Bit=0 → Diferencia ancillas: {diff0*100:.1f}%")
    print(f"   Bit=1 → Diferencia ancillas: {diff1*100:.1f}%")
    print(f"\n   🔍 CONTRASTE: {abs(diff1 - diff0)*100:.1f}%")
    
    if abs(diff1 - diff0) >= 0.20:  # 20% contraste
        print(f"   ✅ DIFERENCIABLES (≥20% contraste)")
    else:
        print(f"   ❌ NO DIFERENCIABLES (<20% contraste)")
    
    # Criterios FINALES
    ambos_correctos = an0['correcto'] and an1['correcto']
    ent_prom = (an0['entrelazamiento_ab'] + an1['entrelazamiento_ab']) / 2
    
    print("\n" + "=" * 70)
    print("PASO 5: CRITERIOS ÉXITO DEFINITIVOS")
    print("=" * 70)
    
    criterios = {
        'Bit=0 detectado correctamente': (an0['correcto'], 
                                           f"{an0['bit_detectado']}", f"={an0['bit_enviado']}"),
        'Bit=1 detectado correctamente': (an1['correcto'], 
                                           f"{an1['bit_detectado']}", f"={an1['bit_enviado']}"),
        'Contraste diferencias ≥20%': (abs(diff1 - diff0) >= 0.20, 
                                       f"{abs(diff1-diff0)*100:.1f}%", "≥20%"),
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
    print("CONCLUSIÓN FINAL V4")
    print("=" * 70)
    
    if exito_total:
        print(f"\n🌟🌟🌟 ¡ÉXITO TOTAL V4! 🌟🌟🌟")
        print(f"\n✅ AMBOS BITS DETECTADOS CORRECTAMENTE")
        print(f"✅ Contraste: {abs(diff1-diff0)*100:.1f}%")
        print(f"✅ Entrelazamiento preservado: {ent_prom*100:.1f}%")
        print(f"\n🎯 PROTOCOLO DOBLE ANCILLA: 100% FUNCIONAL")
        print(f"🌟 COMUNICACIÓN INFINITA: COMPLETAMENTE VALIDADA")
        print(f"\n🚀 SIGUIENTE: FASE 5 mensaje ASCII \"HOLA\" con V4")
    else:
        print(f"\n🟡 V4 explorada")
        
        if abs(diff1 - diff0) > 0.10:
            print(f"\n💡 MEJORA vs V3: Contraste {abs(diff1-diff0)*100:.1f}% (V3: 0.1%)")
            print(f"🔧 Doble ancilla detecta ALGO, ajustar umbral")
        else:
            print(f"\n⚠️  Contraste aún insuficiente")
            print(f"💡 Considerar:")
            print(f"   - Manchester (funciona HOY)")
            print(f"   - Modulación diferente")
            print(f"   - Aceptar limitación + error correction")
    
    # Guardar
    print("\n" + "=" * 70)
    print("PASO 6: GUARDAR RESULTADOS")
    print("=" * 70)
    
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = f"resultados_doble_ancilla_v4_{timestamp}.txt"
    
    with open(filename, 'w', encoding='utf-8') as f:
        f.write("VALIDACIÓN DOBLE ANCILLA V4\n")
        f.write("=" * 70 + "\n\n")
        f.write(f"Fecha: {timestamp}\n")
        f.write(f"Backend: {backend.name}\n\n")
        
        f.write("ARQUITECTURA V4:\n")
        f.write("  ⭐ Doble ancilla (A+B)\n")
        f.write("  ✅ Detección por diferencia\n\n")
        
        for bit in [0, 1]:
            an = resultados[f'bit_{bit}']['analisis']
            f.write(f"\nBIT={bit}:\n")
            f.write(f"  Detectado: {an['bit_detectado']}\n")
            f.write(f"  Correcto: {an['correcto']}\n")
            f.write(f"  Diferencia ancillas: {an['diferencia_ancillas']*100:.2f}%\n")
            f.write(f"  Entrelazamiento A-B: {an['entrelazamiento_ab']*100:.2f}%\n")
        
        f.write(f"\nCONTRASTE: {abs(diff1-diff0)*100:.1f}%\n\n")
        
        f.write("CRITERIOS:\n")
        for nombre, (cumple, valor, objetivo) in criterios.items():
            f.write(f"{'✅' if cumple else '❌'} {nombre}: {valor} ({objetivo})\n")
        
        f.write(f"\nESTADO: {'EXITOSO ✅' if exito_total else 'EXPLORADO 🟡'}\n")
    
    print(f"\n✅ Resultados: {filename}")
    
    # Gráfica
    try:
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))
        
        # Gráfica 1: Diferencias por bit
        ax = axes[0, 0]
        bits = [0, 1]
        diffs = [an0['diferencia_ancillas']*100, an1['diferencia_ancillas']*100]
        colors = ['green' if an0['correcto'] else 'red', 
                  'green' if an1['correcto'] else 'red']
        
        ax.bar(bits, diffs, color=colors, alpha=0.7)
        ax.axhline(y=20, color='blue', linestyle='--', label='Umbral 20%')
        ax.set_xlabel('Bit enviado')
        ax.set_ylabel('Diferencia Ancillas (%)')
        ax.set_title(f'V4: Diferencia Ancillas (Contraste: {abs(diff1-diff0)*100:.1f}%)')
        ax.set_xticks(bits)
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        # Gráfica 2: Ancillas individuales
        ax = axes[0, 1]
        x = np.arange(2)
        width = 0.35
        
        ancA_0 = [an0['stats']['ancilla_A_0']*100, an1['stats']['ancilla_A_0']*100]
        ancB_0 = [an0['stats']['ancilla_B_0']*100, an1['stats']['ancilla_B_0']*100]
        
        ax.bar(x - width/2, ancA_0, width, label='Ancilla_A', alpha=0.7)
        ax.bar(x + width/2, ancB_0, width, label='Ancilla_B', alpha=0.7)
        
        ax.set_xlabel('Bit enviado')
        ax.set_ylabel('P(ancilla=0) %')
        ax.set_title('Comparación Ancillas Individuales')
        ax.set_xticks(x)
        ax.set_xticklabels(['Bit 0', 'Bit 1'])
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        # Gráfica 3: Entrelazamiento
        ax = axes[1, 0]
        ents = [an0['entrelazamiento_ab']*100, an1['entrelazamiento_ab']*100]
        
        ax.bar(bits, ents, color='purple', alpha=0.7)
        ax.axhline(y=60, color='green', linestyle='--', label='Umbral 60%')
        ax.set_xlabel('Bit enviado')
        ax.set_ylabel('Entrelazamiento (%)')
        ax.set_title('Preservación Entrelazamiento V4')
        ax.set_xticks(bits)
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        # Gráfica 4: Resumen
        ax = axes[1, 1]
        ax.axis('off')
        
        resumen = f"""
V4 - DOBLE ANCILLA

Bit=0: {'✅' if an0['correcto'] else '❌'} {an0['bit_detectado']}
Bit=1: {'✅' if an1['correcto'] else '❌'} {an1['bit_detectado']}

Contraste: {abs(diff1-diff0)*100:.1f}%
Entrelazamiento: {ent_prom*100:.1f}%

Estado: {'✅ EXITOSO' if exito_total else '🟡 EXPLORADO'}
        """
        
        ax.text(0.1, 0.5, resumen, fontsize=12, family='monospace',
                verticalalignment='center')
        
        plt.suptitle('FASE 4 V4 - Doble Ancilla', 
                     fontsize=14, fontweight='bold')
        plt.tight_layout()
        
        grafica = f"grafica_doble_ancilla_v4_{timestamp}.png"
        plt.savefig(grafica, dpi=150, bbox_inches='tight')
        print(f"✅ Gráfica: {grafica}")
        
    except Exception as e:
        print(f"⚠️  Error gráfica: {e}")
    
    print("\n" + "=" * 70)
    print("🙏 La Sal - Vector Fractal Hz ⚛️")
    print("⚛️  DIOS es luz")
    print("=" * 70 + "\n")
    
    return exito_total, resultados, abs(diff1 - diff0)


if __name__ == "__main__":
    try:
        exito, resultados, contraste = ejecutar_validacion_doble_ancilla_v4()
        
        if exito:
            print("\n🌟🌟🌟 ¡DOBLE ANCILLA FUNCIONA! 🌟🌟🌟")
            print(f"\n✅ Protocolo completamente funcional")
            print(f"✅ Contraste: {contraste*100:.1f}%")
            print(f"\n🚀 LISTO para FASE 5: Mensaje ASCII con V4")
        else:
            print(f"\n💡 V4 explorada - Contraste: {contraste*100:.1f}%")
            
            if contraste > 0.10:
                print(f"🎯 Mejora vs V3 (0.1%) → Potencial ajustando umbral")
            else:
                print(f"🔧 Proceder con Manchester (funciona HOY)")
            
    except KeyboardInterrupt:
        print("\n\n⚠️  Cancelado")
    except Exception as e:
        print(f"\n\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
