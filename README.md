# ChessMaster

Application Python en ligne de commande pour gérer des tournois d’échecs.

---

## Installation

1. Cloner le projet :

```bash
git clone https://github.com/JulienJ-dev/ChessMaster.git
cd ChessMaster
```

2. Créer un environnement virtuel :

```bash
python -m venv venv
```

3. Activer l’environnement :

```bash
venv\Scripts\activate
```

4. Installer les dépendances :

```bash
pip install -r requirements.txt
```

---

## Lancer le programme

```bash
python Main.py
```

---

## Vérification du code avec flake8

Lancer :

```bash
flake8
```

Générer le rapport HTML :

```bash
flake8 --format=html --htmldir=flake8_rapport
```

Ouvrir ensuite :

```text
flake8_rapport/index.html
```

---

## Structure

* `Main.py` : point d’entrée
* `Models.py` : modèles
* `Views.py` : affichage
* `Controllers.py` : logique
* `Repositories.py` : sauvegarde
* `data/` : données (non versionnées)

---
