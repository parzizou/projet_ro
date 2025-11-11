# -*- coding: utf-8 -*-
"""
demo_multithreading.py
Démonstration du multi-threading dans le système d'analyse.
Montre visuellement l'utilisation des cores CPU.
"""

import os
import sys
import time
import psutil
from datetime import datetime

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.optimization.ga_parameter_analyzer import GAParameterAnalyzer


def print_cpu_usage():
    """Affiche l'utilisation CPU actuelle."""
    cpu_percent = psutil.cpu_percent(interval=0.1, percpu=True)
    print(f"\n⚡ Utilisation CPU par core:")
    for i, usage in enumerate(cpu_percent, 1):
        bar = "█" * int(usage / 5)
        print(f"  Core {i:2d}: [{bar:<20}] {usage:5.1f}%")
    print(f"  Total: {psutil.cpu_percent(interval=0.1):.1f}%")


def demo_sequential_vs_parallel():
    """Compare exécution séquentielle vs parallèle."""
    print("\n" + "="*70)
    print("🔬 DÉMONSTRATION: SÉQUENTIEL VS PARALLÈLE".center(70))
    print("="*70)
    
    instance_path = "data/instances/data.vrp"
    
    if not os.path.exists(instance_path):
        print(f"❌ Instance introuvable: {instance_path}")
        return
    
    print("\n📊 Configuration du test:")
    print(f"  - Instance: {instance_path}")
    print(f"  - Nombre de runs: 5")
    print(f"  - Temps limite par run: 10s")
    print(f"  - Générations: 5000")
    
    # Info système
    cpu_count = os.cpu_count()
    print(f"\n💻 Système:")
    print(f"  - Nombre de cores: {cpu_count}")
    print(f"  - RAM disponible: {psutil.virtual_memory().available / (1024**3):.1f} GB")
    
    analyzer = GAParameterAnalyzer(instance_path, n_runs=5)
    
    # Test 1: Séquentiel (1 worker)
    print("\n" + "─"*70)
    print("TEST 1: EXÉCUTION SÉQUENTIELLE (1 worker)".center(70))
    print("─"*70)
    
    input("\n⏸️  Appuyez sur Entrée pour lancer le test séquentiel...")
    print(f"\n🕐 Début: {datetime.now().strftime('%H:%M:%S')}")
    print_cpu_usage()
    
    start = time.time()
    costs, elapsed = analyzer._run_multiple_tests(
        analyzer.default_params,
        num_runs=5,
        time_limit=10.0,
        generations=5000,
        max_workers=1  # 1 seul worker
    )
    sequential_time = time.time() - start
    
    print_cpu_usage()
    print(f"\n⏱️  Temps total: {sequential_time:.1f}s")
    print(f"📊 Coûts obtenus: {costs}")
    
    # Test 2: Parallèle (auto)
    print("\n" + "─"*70)
    print("TEST 2: EXÉCUTION PARALLÈLE (auto workers)".center(70))
    print("─"*70)
    
    input("\n⏸️  Appuyez sur Entrée pour lancer le test parallèle...")
    print(f"\n🕐 Début: {datetime.now().strftime('%H:%M:%S')}")
    print_cpu_usage()
    
    start = time.time()
    costs, elapsed = analyzer._run_multiple_tests(
        analyzer.default_params,
        num_runs=5,
        time_limit=10.0,
        generations=5000,
        max_workers=None  # Auto: utilise tous les cores
    )
    parallel_time = time.time() - start
    
    print_cpu_usage()
    print(f"\n⏱️  Temps total: {parallel_time:.1f}s")
    print(f"📊 Coûts obtenus: {costs}")
    
    # Comparaison
    print("\n" + "="*70)
    print("📊 RÉSULTATS DE LA COMPARAISON".center(70))
    print("="*70)
    
    speedup = sequential_time / parallel_time if parallel_time > 0 else 0
    efficiency = (speedup / cpu_count) * 100 if cpu_count > 0 else 0
    
    print(f"\n  Séquentiel (1 worker): {sequential_time:.1f}s")
    print(f"  Parallèle (auto):      {parallel_time:.1f}s")
    print(f"\n  🚀 Accélération (Speedup):  {speedup:.2f}x")
    print(f"  ⚡ Efficacité:              {efficiency:.1f}%")
    print(f"  💾 Temps économisé:         {sequential_time - parallel_time:.1f}s")
    
    if speedup > 1:
        print(f"\n  ✅ Le multi-threading est {speedup:.1f}x plus rapide!")
    
    print("\n" + "="*70)


def demo_live_monitoring():
    """Monitore l'utilisation CPU pendant un test."""
    print("\n" + "="*70)
    print("📡 MONITORING LIVE DE L'UTILISATION CPU".center(70))
    print("="*70)
    
    instance_path = "data/instances/data.vrp"
    
    if not os.path.exists(instance_path):
        print(f"❌ Instance introuvable: {instance_path}")
        return
    
    analyzer = GAParameterAnalyzer(instance_path, n_runs=10)
    
    print("\n⚡ Test avec 10 runs en parallèle...")
    input("⏸️  Appuyez sur Entrée pour lancer (surveillez votre Gestionnaire des tâches)...")
    
    print(f"\n🕐 Début: {datetime.now().strftime('%H:%M:%S')}")
    print("\n⚡ UTILISATION CPU PENDANT L'EXÉCUTION:\n")
    
    # Lancer le test en arrière-plan
    import threading
    
    test_running = [True]
    
    def run_test():
        analyzer._run_multiple_tests(
            analyzer.default_params,
            num_runs=10,
            time_limit=15.0,
            generations=10000,
            max_workers=None
        )
        test_running[0] = False
    
    # Lancer dans un thread
    thread = threading.Thread(target=run_test)
    thread.start()
    
    # Monitorer pendant l'exécution
    while test_running[0]:
        print("\033[F" * (os.cpu_count() + 3))  # Remonter dans le terminal
        print_cpu_usage()
        time.sleep(1)
    
    thread.join()
    
    print(f"\n✅ Test terminé à {datetime.now().strftime('%H:%M:%S')}")


def main():
    """Menu principal."""
    print("\n" + "="*70)
    print("🧬 DÉMONSTRATION DU MULTI-THREADING 🧬".center(70))
    print("="*70)
    
    print("\n📋 MENU:")
    print("  1 - Comparaison Séquentiel vs Parallèle")
    print("  2 - Monitoring Live de l'utilisation CPU")
    print("  0 - Quitter")
    
    choice = input("\n👉 Votre choix: ")
    
    if choice == '1':
        demo_sequential_vs_parallel()
    elif choice == '2':
        demo_live_monitoring()
    elif choice == '0':
        print("\n👋 Au revoir!")
    else:
        print("\n❌ Choix invalide")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ Interrompu par l'utilisateur")
    except Exception as e:
        print(f"\n❌ Erreur: {e}")
