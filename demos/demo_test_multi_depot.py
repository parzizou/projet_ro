# -*- coding: utf-8 -*-
"""
demo_test_multi_depot.py
Démonstration de l'utilisation du système de test multi-dépôts.

Ce script montre comment utiliser test_multi_depot.py pour optimiser
les paramètres du système multi-dépôts.
"""

import subprocess
import sys
import os

def run_command(cmd: str, description: str):
    """Exécute une commande et affiche le résultat."""
    print("\n" + "=" * 80)
    print(f"🔬 {description}")
    print("=" * 80)
    print(f"Commande: {cmd}\n")
    
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=False,
            text=True
        )
        return result.returncode == 0
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False


def main():
    print("""
╔══════════════════════════════════════════════════════════════════════════════╗
║                    DÉMONSTRATION - TEST MULTI-DÉPÔTS                         ║
║                                                                              ║
║  Ce script démontre l'utilisation de test_multi_depot.py pour optimiser     ║
║  les paramètres du système multi-dépôts.                                    ║
╚══════════════════════════════════════════════════════════════════════════════╝
""")
    
    # Vérifier que l'instance existe
    instance_path = "data/instances/data.vrp"
    if not os.path.exists(instance_path):
        print(f"❌ Instance non trouvée: {instance_path}")
        print("   Veuillez ajuster le chemin dans ce script.")
        return
    
    demos = [
        {
            "cmd": f'python scripts/test_multi_depot.py --instance {instance_path} --param k_depots --values 2,3,4 --repeats 2 --fixed "ga_time_limit_sec=15"',
            "description": "Test 1: Optimisation du nombre de dépôts (k_depots)",
            "explanation": """
    📊 Ce test compare différents nombres de dépôts (2, 3, 4).
    
    Objectif: Trouver le nombre optimal de dépôts pour minimiser le coût total.
    
    Paramètres:
    - k_depots: 2, 3, 4 (valeurs testées)
    - repeats: 2 (2 répétitions par valeur pour la stabilité)
    - ga_time_limit_sec: 15s (temps limité pour la démo)
    
    Résultat attendu: Le système testera chaque valeur et affichera:
    - Coût moyen et meilleur coût
    - Nombre moyen de routes
    - Temps d'exécution
    - Configuration optimale
"""
        },
        {
            "cmd": f'python scripts/test_multi_depot.py --instance {instance_path} --param types_alphabet --values AB,ABC,ABCD --repeats 2 --fixed "k_depots=3,ga_time_limit_sec=15"',
            "description": "Test 2: Optimisation des types de dépôts (types_alphabet)",
            "explanation": """
    📊 Ce test compare différents alphabets de types de dépôts.
    
    Objectif: Déterminer si plus de types améliore la qualité de solution.
    
    Paramètres:
    - types_alphabet: "AB", "ABC", "ABCD" (2, 3, ou 4 types)
    - k_depots: 3 (fixé)
    - repeats: 2
    
    Note: Avec k_depots=3 et types_alphabet="ABCD", certains types ne seront pas utilisés.
"""
        },
        {
            "cmd": f'python scripts/test_multi_depot.py --instance {instance_path} --param ga_pop_size --values 20,40,60 --repeats 2 --fixed "k_depots=3,types_alphabet=ABC,ga_time_limit_sec=15"',
            "description": "Test 3: Optimisation de la taille de population GA (ga_pop_size)",
            "explanation": """
    📊 Ce test optimise les paramètres de l'algorithme génétique en mode multi-dépôt.
    
    Objectif: Trouver la meilleure taille de population pour le GA.
    
    Paramètres:
    - ga_pop_size: 20, 40, 60 (population de l'AG)
    - k_depots: 3 (fixé)
    - types_alphabet: "ABC" (fixé)
    - repeats: 2
    
    Note: Tous les paramètres GA sont préfixés "ga_" en mode multi-dépôt.
"""
        },
        {
            "cmd": f'python scripts/test_multi_depot.py --instance {instance_path} --param ga_pm --values 0.02,0.06,0.10 --repeats 2 --fixed "k_depots=2,ga_time_limit_sec=15" --save-csv results/demo_md_pm.csv',
            "description": "Test 4: Optimisation du taux de mutation (ga_pm) avec export CSV",
            "explanation": """
    📊 Ce test optimise le taux de mutation et exporte les résultats en CSV.
    
    Objectif: Trouver le meilleur taux de mutation (pm) pour le GA.
    
    Paramètres:
    - ga_pm: 0.02, 0.06, 0.10 (taux de mutation)
    - k_depots: 2 (simplifié pour la démo)
    - save-csv: Sauvegarde des résultats en CSV
    
    Sortie: Fichier results/demo_md_pm.csv avec toutes les statistiques.
"""
        }
    ]
    
    print("\n📋 TESTS DISPONIBLES:")
    for i, demo in enumerate(demos, 1):
        print(f"\n{i}. {demo['description']}")
    
    print("\n" + "=" * 80)
    choice = input("\nChoisissez un test à exécuter (1-4, 'all' pour tous, ou 'q' pour quitter): ").strip().lower()
    
    if choice == 'q':
        print("\n👋 Au revoir!")
        return
    
    tests_to_run = []
    if choice == 'all':
        tests_to_run = demos
    elif choice.isdigit() and 1 <= int(choice) <= len(demos):
        tests_to_run = [demos[int(choice) - 1]]
    else:
        print("❌ Choix invalide.")
        return
    
    # Exécuter les tests sélectionnés
    for demo in tests_to_run:
        print(demo['explanation'])
        input("\n⏸️  Appuyez sur Entrée pour lancer ce test...")
        
        success = run_command(demo['cmd'], demo['description'])
        
        if success:
            print(f"\n✅ Test terminé avec succès!")
        else:
            print(f"\n❌ Le test a échoué.")
        
        if len(tests_to_run) > 1:
            input("\n⏸️  Appuyez sur Entrée pour continuer vers le test suivant...")
    
    print("\n" + "=" * 80)
    print("🎉 DÉMONSTRATION TERMINÉE")
    print("=" * 80)
    print("""
📚 Pour en savoir plus:
   - Documentation: scripts/README.md
   - Aide complète: python scripts/test_multi_depot.py --help
   - Tests standards: python scripts/test.py --help

💡 Conseils:
   - Augmentez --repeats pour des résultats plus stables
   - Utilisez --target pour calculer le gap vs optimal
   - Utilisez --save-csv pour sauvegarder les résultats
   - Ajustez ga_time_limit_sec selon vos besoins (15-60s recommandé)
""")


if __name__ == "__main__":
    main()
