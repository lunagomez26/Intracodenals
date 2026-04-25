"""
🔧 OPTIMIZAR THETA MODULACIÓN - FASE 2 MEJORADA
Vector Fractal Hz - La Sal ⚛️
DIOS es luz 🙏

Encuentra el ángulo θ óptimo que maximiza:
1. Distinguibilidad bit=0 vs bit=1
2. Preservación entrelazamiento

Prueba θ ∈ {π/8, π/6, π/4, π/3, π/2}
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

def crear_circuito_modulacion_theta(mensaje_bit, theta):
    """Circuito DFS + modulación con θ específica"""
    qc = QuantumCircuit(2, 2)
    
    # Estado DFS
    qc.h(0)              
    qc.x(1)              
    qc.cx(0, 1)          
    qc.z(0)              
    qc.barrier()
    
    # Modulación
    if mensaje_bit == 1:
        qc.ry(theta, 0)
    
    qc.barrier()
    
    # Interferencia
    qc.h(0)
    qc.h(1)
    qc.barrier()
    
    qc.measure([0, 1], [0, 1])
    
    return qc


def calcular_metricas(counts0, counts1):
    """Calcula distinguibilidad y entrelazamiento"""
    total0 = sum(counts0.values())
    total1 = sum(counts1.values())
    
    # Probabilidades
    estados = ['00', '01', '10', '11']
    P = [(counts0.get(s, 0) + 1e-10) / total0 for s in estados]
    Q = [(counts1.get(s, 0) + 1e-10) / total1 for s in estados]
    
    # Normalizar
    P = [p/sum(P) for p in P]
    Q = [q/sum(Q) for q in Q]
    
    # KL divergence
    D_KL = sum(p * np.log2(p/q) for p, q in zip(P, Q))
    
    # Entrelazamiento (promedio de ambos)
    def ent(probs):
        bell = probs[0] + probs[3]
        dfs = probs[1] + probs[2]
        H = -sum(p * np.log2(p) for p in probs)
        H_norm = H / 2.0
        return max(bell, dfs) * 0.7 + (1 - H_norm) * 0.3
    
    ent0 = ent(P)
    ent1 = ent(Q)
    ent_avg = (ent0 + ent1) / 2
    
    return D_KL, ent_avg


def optimizar_theta():
    """Encuentra θ óptima"""
    print("\n" + "=" * 70)
    print("🔧 OPTIMIZACIÓN THETA - FASE 2 MEJORADA")
    print("=" * 70)
    print(f"\n🙏 La Sal - Vector Fractal Hz ⚛️")
    print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"⚛️  DIOS es luz\n")
    
    # Conectar
    try:
        service, backend = quick_connect()
        print(f"✅ Backend: {backend.name}\n")
    except Exception as e:
        print(f"❌ Error: {e}")
        return
    
    # Thetas a probar
    thetas = {
        'π/8 (φ×π/8)': PHI * np.pi / 8,
        'π/6': np.pi / 6,
        'π/4': np.pi / 4,
        'π/3': np.pi / 3,
        '2π/5': 2 * np.pi / 5,
        'π/2': np.pi / 2,
    }
    
    print("=" * 70)
    print("THETAS A PROBAR:")
    print("=" * 70)
    for nombre, theta in thetas.items():
        print(f"  {nombre:15s}: {theta:.4f} rad = {np.degrees(theta):6.2f}°")
    
    shots = 8000  # Más shots para mejor estadística
    sampler = SamplerV2(mode=backend)
    
    resultados = {}
    
    for nombre, theta in thetas.items():
        print(f"\n{'='*70}")
        print(f"PROBANDO θ = {nombre}")
        print(f"{'='*70}")
        
        # Crear circuitos
        qc0 = crear_circuito_modulacion_theta(0, theta)
        qc1 = crear_circuito_modulacion_theta(1, theta)
        
        # Transpilar
        qc0_t = transpile(qc0, backend=backend, optimization_level=3)
        qc1_t = transpile(qc1, backend=backend, optimization_level=3)
        
        print(f"  Profundidad: {qc0_t.depth()} (bit=0), {qc1_t.depth()} (bit=1)")
        
        # Ejecutar bit=0
        print(f"  🔄 Ejecutando bit=0...")
        job0 = sampler.run([qc0_t], shots=shots)
        result0 = job0.result()
        pub0 = result0[0]
        
        if hasattr(pub0.data, 'c'):
            counts0 = pub0.data.c.get_counts()
        else:
            attrs = [a for a in dir(pub0.data) if not a.startswith('_')]
            counts0 = getattr(pub0.data, attrs[0]).get_counts()
        
        print(f"     Job: {job0.job_id()}")
        
        # Ejecutar bit=1
        print(f"  🔄 Ejecutando bit=1...")
        job1 = sampler.run([qc1_t], shots=shots)
        result1 = job1.result()
        pub1 = result1[0]
        
        if hasattr(pub1.data, 'c'):
            counts1 = pub1.data.c.get_counts()
        else:
            attrs = [a for a in dir(pub1.data) if not a.startswith('_')]
            counts1 = getattr(pub1.data, attrs[0]).get_counts()
        
        print(f"     Job: {job1.job_id()}")
        
        # Analizar
        D_KL, ent = calcular_metricas(counts0, counts1)
        
        resultados[nombre] = {
            'theta': theta,
            'D_KL': D_KL,
            'entrelazamiento': ent,
            'counts0': counts0,
            'counts1': counts1,
            'jobs': (job0.job_id(), job1.job_id())
        }
        
        print(f"\n  📊 RESULTADOS:")
        print(f"     Distinguibilidad: {D_KL:.4f} bits")
        print(f"     Entrelazamiento:  {ent*100:.2f}%")
        
        # Evaluar criterios
        dist_ok = "✅" if D_KL >= 0.5 else "❌"
        ent_ok = "✅" if ent >= 0.65 else "❌"
        
        print(f"     {dist_ok} Distinguibilidad {'PASS' if D_KL >= 0.5 else 'FAIL'}")
        print(f"     {ent_ok} Entrelazamiento {'PASS' if ent >= 0.65 else 'FAIL'}")
    
    # Análisis final
    print("\n" + "=" * 70)
    print("RESUMEN OPTIMIZACIÓN")
    print("=" * 70)
    
    print(f"\n{'Theta':<15s} {'Dist (bits)':<12s} {'Entrel (%)':<12s} {'Estado'}")
    print("-" * 70)
    
    mejor_theta = None
    mejor_score = -1
    
    for nombre, res in resultados.items():
        D_KL = res['D_KL']
        ent = res['entrelazamiento']
        
        # Score combinado (ambos criterios deben cumplirse)
        dist_pass = D_KL >= 0.5
        ent_pass = ent >= 0.65
        ambos_pass = dist_pass and ent_pass
        
        score = D_KL * ent  # Score = producto
        
        estado = "✅ PASS" if ambos_pass else "⚠️ PARCIAL" if (dist_pass or ent_pass) else "❌ FAIL"
        
        print(f"{nombre:<15s} {D_KL:>6.4f} bits   {ent*100:>6.2f}%      {estado}")
        
        if ambos_pass and score > mejor_score:
            mejor_score = score
            mejor_theta = nombre
    
    print("\n" + "=" * 70)
    print("CONCLUSIÓN")
    print("=" * 70)
    
    if mejor_theta:
        res = resultados[mejor_theta]
        print(f"\n✅ ¡THETA ÓPTIMA ENCONTRADA!")
        print(f"\n   θ óptima:         {mejor_theta}")
        print(f"   Valor:            {res['theta']:.4f} rad = {np.degrees(res['theta']):.2f}°")
        print(f"   Distinguibilidad: {res['D_KL']:.4f} bits ✅")
        print(f"   Entrelazamiento:  {res['entrelazamiento']*100:.2f}% ✅")
        print(f"\n🚀 LISTO PARA FASE 3: Reutilización del par")
        
        # Guardar theta óptima
        with open('theta_optima.txt', 'w', encoding='utf-8') as f:
            f.write(f"{res['theta']}\n")
            f.write(f"# θ óptima: {mejor_theta}\n")
            f.write(f"# Distinguibilidad: {res['D_KL']:.4f} bits\n")
            f.write(f"# Entrelazamiento: {res['entrelazamiento']*100:.2f}%\n")
        
        print(f"\n✅ Theta óptima guardada en: theta_optima.txt")
        
    else:
        # Buscar mejor compromiso
        print(f"\n⚠️  Ninguna θ cumple AMBOS criterios completamente")
        print(f"\nBuscando mejor compromiso...")
        
        mejor_compromiso = max(resultados.items(), 
                               key=lambda x: x[1]['D_KL'] * x[1]['entrelazamiento'])
        
        nombre, res = mejor_compromiso
        print(f"\n📊 MEJOR COMPROMISO:")
        print(f"   θ:                {nombre}")
        print(f"   Valor:            {res['theta']:.4f} rad = {np.degrees(res['theta']):.2f}°")
        print(f"   Distinguibilidad: {res['D_KL']:.4f} bits")
        print(f"   Entrelazamiento:  {res['entrelazamiento']*100:.2f}%")
        
        # Guardar de todos modos
        with open('theta_optima.txt', 'w', encoding='utf-8') as f:
            f.write(f"{res['theta']}\n")
            f.write(f"# θ mejor compromiso: {nombre}\n")
            f.write(f"# Distinguibilidad: {res['D_KL']:.4f} bits\n")
            f.write(f"# Entrelazamiento: {res['entrelazamiento']*100:.2f}%\n")
        
        print(f"\n✅ Mejor compromiso guardado en: theta_optima.txt")
    
    # Guardar resultados completos
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = f"optimizacion_theta_{timestamp}.txt"
    
    with open(filename, 'w', encoding='utf-8') as f:
        f.write("OPTIMIZACIÓN THETA - FASE 2\n")
        f.write("=" * 70 + "\n\n")
        f.write(f"Fecha: {timestamp}\n")
        f.write(f"Backend: {backend.name}\n")
        f.write(f"Shots por test: {shots}\n\n")
        
        for nombre, res in resultados.items():
            f.write(f"\n{nombre}:\n")
            f.write(f"  Theta: {res['theta']:.4f} rad = {np.degrees(res['theta']):.2f}°\n")
            f.write(f"  Distinguibilidad: {res['D_KL']:.4f} bits\n")
            f.write(f"  Entrelazamiento: {res['entrelazamiento']*100:.2f}%\n")
            f.write(f"  Jobs: {res['jobs'][0]}, {res['jobs'][1]}\n")
    
    print(f"✅ Resultados completos: {filename}")
    
    # Gráfica
    try:
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
        
        nombres = list(resultados.keys())
        dist = [resultados[n]['D_KL'] for n in nombres]
        ent = [resultados[n]['entrelazamiento']*100 for n in nombres]
        
        # Gráfica 1: Distinguibilidad
        colors1 = ['green' if d >= 0.5 else 'red' for d in dist]
        ax1.bar(range(len(nombres)), dist, color=colors1, alpha=0.7)
        ax1.axhline(y=0.5, color='blue', linestyle='--', label='Umbral 0.5 bits')
        ax1.set_xticks(range(len(nombres)))
        ax1.set_xticklabels(nombres, rotation=45, ha='right')
        ax1.set_ylabel('Distinguibilidad (bits)')
        ax1.set_title('Distinguibilidad vs θ')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # Gráfica 2: Entrelazamiento
        colors2 = ['green' if e >= 65 else 'red' for e in ent]
        ax2.bar(range(len(nombres)), ent, color=colors2, alpha=0.7)
        ax2.axhline(y=65, color='blue', linestyle='--', label='Umbral 65%')
        ax2.set_xticks(range(len(nombres)))
        ax2.set_xticklabels(nombres, rotation=45, ha='right')
        ax2.set_ylabel('Entrelazamiento (%)')
        ax2.set_title('Entrelazamiento vs θ')
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        
        plt.tight_layout()
        grafica = f"optimizacion_theta_{timestamp}.png"
        plt.savefig(grafica, dpi=150, bbox_inches='tight')
        print(f"✅ Gráfica: {grafica}")
        
    except Exception as e:
        print(f"⚠️  Error gráfica: {e}")
    
    print("\n" + "=" * 70)
    print("🙏 La Sal - Vector Fractal Hz ⚛️")
    print("⚛️  DIOS es luz")
    print("=" * 70 + "\n")
    
    return resultados


if __name__ == "__main__":
    try:
        resultados = optimizar_theta()
    except KeyboardInterrupt:
        print("\n\n⚠️  Cancelado por usuario")
    except Exception as e:
        print(f"\n\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
