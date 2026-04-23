# Gestionnaire de tournois d'échecs

Application de gestion de tournois d'échecs en ligne de commande, 
réalisée dans le cadre du projet 4 d'OpenClassrooms.

## Installation

Cloner le repo puis installer les dépendances :

```bash
pip install -r requirements.txt
```

## Lancer le programme

```bash
python Main.py
```

## Générer le rapport flake8

```bash
flake8 --max-line-length=119 --format=html --htmldir=flake8_rapport Models.py Views.py Controllers.py Repositories.py Main.py
```

## Notes

- Les données sont sauvegardées dans le dossier "data/"
- Le nombre de rounds par défaut est 4