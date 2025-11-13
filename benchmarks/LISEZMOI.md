# 📁 Dossier Benchmarks

Ce dossier contient le système de benchmark professionnel pour le projet CVRP.

## 📋 Contenu

- **benchmark.py**: Script principal de benchmark (69 configurations, 15 min)
- **test_benchmark.py**: Test rapide de validation (6 configurations, 2-3 min)
- **README.md**: Documentation complète du système de benchmark

## 🚀 Utilisation

```bash
# Depuis la racine du projet

# Test rapide pour valider l'installation
python benchmarks/test_benchmark.py

# Benchmark complet professionnel
python benchmarks/benchmark.py
```

## 📊 Résultats

Les résultats sont sauvegardés dans `results/benchmarks/` :
- JSON avec toutes les données
- CSV pour analyse externe
- 7 visualisations (histogrammes professionnels)

Pour plus de détails, consultez **README.md** dans ce dossier.
