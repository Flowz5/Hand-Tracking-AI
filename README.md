# 🖐️ Hand Tracker Ultimate (Palm & Back Detection)

![Python](https://img.shields.io/badge/Python-3.10%20%7C%203.11-blue)
![MediaPipe](https://img.shields.io/badge/MediaPipe-0.10.9-orange)
![OpenCV](https://img.shields.io/badge/OpenCV-Computer%20Vision-green)

Un détecteur de mains en temps réel capable de compter les doigts avec précision, même lorsque la main est retournée (Dos/Paume) ou inversée (Gauche/Droite).

## 🚀 Fonctionnalités

* **Suivi Temps Réel** : Utilise la webcam pour tracker les 21 points clés de la main.
* **Comptage Intelligent** : Compte le nombre de doigts levés (0 à 5).
* **Détection d'Orientation** : Distingue si la main est vue de face (**Palm**) ou de dos (**Back**).
* **Logique Universelle** : L'algorithme adapte la détection du Pouce selon l'orientation et la main (Gauche/Droite).
* **Miroir** : L'image est retournée horizontalement pour une expérience utilisateur naturelle.

## 🛠️ Installation

### Pré-requis
Ce projet nécessite **Python 3.10** ou **3.11** (MediaPipe peut être instable sur les versions plus récentes comme 3.12+ ou 3.14).

1.  **Cloner le dépôt**
    ```bash
    git clone [https://github.com/TonPseudo/Hand-Tracker.git](https://github.com/TonPseudo/Hand-Tracker.git)
    cd Hand-Tracker
    ```

2.  **Créer un environnement virtuel (Recommandé)**
    ```bash
    python -m venv .venv
    # Windows :
    .venv\Scripts\activate
    # Mac/Linux :
    source .venv/bin/activate
    ```

3.  **Installer les dépendances**
    ```bash
    pip install opencv-python mediapipe==0.10.9 protobuf==3.20.3
    ```

## 🎮 Utilisation

Lancer simplement le script principal :

```bash
python main.py

```

* **`q`** : Appuyer sur la touche `q` pour quitter l'application.

## 🧠 Comment ça marche ? (La Logique)

Le défi principal de la détection de main est le **Pouce**, car il bouge sur l'axe horizontal (X), contrairement aux autres doigts (axe Y). De plus, la logique s'inverse si on montre le dos de la main.

### 1. Détection Paume vs Dos

Pour savoir si la main est de face ou de dos, nous comparons la position horizontale () de la base de l'**Index** (Point 5) et du **Petit Doigt** (Point 17).

* *Main Droite (Paume)* : L'Index est à gauche du Petit Doigt.
* *Main Droite (Dos)* : L'Index passe à droite du Petit Doigt.

### 2. Le "Théorème du Pouce"

Une fois l'orientation connue, nous appliquons une logique conditionnelle :

| Main | Orientation | Condition pour Pouce Levé |
| --- | --- | --- |
| **Droite** | **Paume** | Bout du pouce < Base (vers la gauche) |
| **Gauche** | **Dos** | Bout du pouce < Base (vers la gauche) |
| **Droite** | **Dos** | Bout du pouce > Base (vers la droite) |
| **Gauche** | **Paume** | Bout du pouce > Base (vers la droite) |

## 📂 Structure du Projet

```text
Hand-Tracker/
│
├── main.py          # Le script principal contenant toute la logique
├── README.md        # Documentation du projet
└── .gitignore       # Fichiers à ignorer (venv, cache...)

```