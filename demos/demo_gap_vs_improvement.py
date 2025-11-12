# -*- coding: utf-8 -*-
"""
demo_gap_vs_improvement.py
Démontre la différence entre gap vs optimal et amélioration vs baseline.
"""

def demo_comparison():
    """Montre la différence d'interprétation entre gap et amélioration."""
    
    print("\n" + "="*80)
    print("📊 COMPARAISON: Gap vs Optimal  VS  Amélioration vs Baseline".center(80))
    print("="*80)
    
    optimal = 22901
    baseline = 23316
    
    # Configurations de test
    configs = [
        ("Config A - Excellente", 22950),
        ("Config B - Très bonne", 23050),
        ("Config C - Baseline", 23316),
        ("Config D - Sous-optimale", 23500),
    ]
    
    print(f"\n🎯 Références:")
    print(f"   • Optimal connu: {optimal}")
    print(f"   • Baseline (défaut): {baseline}")
    print(f"   • Différence: {baseline - optimal} (+{((baseline - optimal) / optimal * 100):.2f}%)")
    
    print("\n" + "-"*80)
    print(f"{'Configuration':<25} {'Coût':<10} {'Gap vs Optimal':<25} {'Amélioration vs Baseline':<30}")
    print("-"*80)
    
    for name, cost in configs:
        # Calcul gap vs optimal
        gap = ((cost - optimal) / optimal) * 100
        if gap < 5.0:
            gap_status = "✅ BON"
        elif gap < 10.0:
            gap_status = "🟡 ACCEPTABLE"
        else:
            gap_status = "❌ À AMÉLIORER"
        
        # Calcul amélioration vs baseline
        improvement = ((baseline - cost) / baseline) * 100
        if improvement > 1.0:
            imp_status = "📈 AMÉLIORATION"
        elif improvement > 0:
            imp_status = "➡️ LÉGÈRE AMÉLIORATION"
        elif improvement == 0:
            imp_status = "⏸️ IDENTIQUE"
        else:
            imp_status = "📉 DÉGRADATION"
        
        gap_str = f"{gap:+.2f}% {gap_status}"
        imp_str = f"{improvement:+.2f}% {imp_status}"
        
        print(f"{name:<25} {cost:<10} {gap_str:<25} {imp_str:<30}")
    
    print("-"*80)
    
    # Analyse comparative
    print("\n" + "="*80)
    print("🔍 ANALYSE COMPARATIVE".center(80))
    print("="*80)
    
    print("\n📊 Méthode 1: GAP VS OPTIMAL")
    print("   ✅ Avantages:")
    print("      • Référence absolue (le meilleur possible)")
    print("      • Interprétation claire: distance au minimum")
    print("      • Comparable entre différentes instances")
    print("      • Standard en recherche opérationnelle")
    print("      • Objectif précis: gap < 1% = excellent")
    
    print("\n   ⚠️ Inconvénient:")
    print("      • Nécessite de connaître l'optimal")
    
    print("\n📊 Méthode 2: AMÉLIORATION VS BASELINE")
    print("   ✅ Avantages:")
    print("      • Ne nécessite pas l'optimal")
    print("      • Montre le progrès par rapport au point de départ")
    
    print("\n   ⚠️ Inconvénients:")
    print("      • Référence relative (dépend de la qualité de la baseline)")
    print("      • Ne dit pas si on est proche de l'optimal")
    print("      • Difficile à interpréter absolument")
    print("      • Peut être trompeur si baseline mauvaise")
    
    # Exemple concret
    print("\n" + "="*80)
    print("💡 EXEMPLE CONCRET".center(80))
    print("="*80)
    
    print("\n📍 Scénario: Vous obtenez un coût de 23050")
    print("\n   Avec AMÉLIORATION VS BASELINE (23316):")
    print("      → Amélioration = +1.14%")
    print("      → ✅ \"C'est bien, on a amélioré de 1%\"")
    print("      → Mais on ne sait pas si on est proche de l'optimal...")
    
    print("\n   Avec GAP VS OPTIMAL (22901):")
    print("      → Gap = +0.65%")
    print("      → ✅ \"Excellent ! On est à 0.65% de l'optimal (< 5%)\"")
    print("      → On sait exactement où on en est !")
    
    print("\n🎯 CONCLUSION:")
    print("   Le GAP VS OPTIMAL est plus informatif car il donne une mesure ABSOLUE")
    print("   de la qualité de la solution, indépendamment de la baseline.")
    
    print("\n" + "="*80)
    
    # Recommandation
    print("\n💡 RECOMMANDATION POUR VOTRE PROJET:")
    print("\n   Utilisez le GAP VS OPTIMAL car:")
    print("   ✓ Vous connaissez l'optimal (22901 dans solution_data.sol)")
    print("   ✓ Vous pouvez mesurer précisément la qualité de vos résultats")
    print("   ✓ Vous avez un objectif clair: gap < 5% = bon résultat")
    print("\n   Objectif concret: Trouver une configuration qui donne coût < 24046")
    print("   (soit 22901 + 5% = 24046)")
    print("\n   Échelle de qualité pour CVRP:")
    print("   • Gap < 5%  : Bon résultat ✅")
    print("   • Gap < 10% : Acceptable 🟡") 
    print("   • Gap > 10% : À améliorer ❌")
    
    print("\n" + "="*80 + "\n")


if __name__ == "__main__":
    demo_comparison()
