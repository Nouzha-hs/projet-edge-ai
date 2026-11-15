# Répartition des Tâches Pratiques (100% Technique & Simulation)
## Projet Edge AI : Système d'Irrigation Intelligent (3 Personnes)

---

### 👤 MEMBRE 1 : TOI (Firmware STM32 & Inférence Embarquée)
**Ton rôle : Faire tourner l'IA dans le microcontrôleur et mesurer ses performances.**

1. **Configuration du projet C dans STM32CubeIDE** :
   - Créer et configurer le projet pour STM32F401RE (Cortex-M4).
   - Structurer le code avec les dossiers `Drivers_Custom` et la boucle principale.
2. **Intégration du modèle IA en C** :
   - Récupérer le modèle optimisé fourni par le Membre 2 (`tinyml_model.h`).
   - Intégrer la fonction d'inférence locale dans la boucle de contrôle.
3. **Moteur d'injection de données simulées** :
   - Écrire le module qui injecte les données météo/sol dans le firmware (via tableau C de vecteurs de test ou lecture de trames sur le port série virtuel).
4. **Sécurité logicielle (Watchdog anti-inondation)** :
   - Programmer un timer matériel ou logiciel qui force l'arrêt de la pompe après 30 secondes maximum, même si l'IA demande de continuer à arroser.
5. **Mesures des métriques matérielles** :
   - Activer le compteur matériel `DWT->CYCCNT` pour mesurer la latence d'inférence exacte en cycles d'horloge CPU et en microsecondes.
   - Relever dans le fichier `.map` de compilation l'empreinte mémoire exacte : Flash utilisée (Ko) et RAM utilisée (Ko).

---

### 👤 MEMBRE 2 : DATA SCIENTIST (Pipeline IA & Entraînement)
**Son rôle : Préparer les données, concevoir le modèle IA et le traduire en C pour le Membre 1.**

1. **Prétraitement du Dataset du Professeur** :
   - Charger et nettoyer les données (gestion des valeurs manquantes, filtrage des anomalies).
   - Normaliser les variables d'entrée (température, humidité de l'air, humidité du sol, heure).
2. **Conception et entraînement des modèles** :
   - Développer le script d'entraînement sous Python (`pandas`, `scikit-learn`).
   - Entraîner et comparer au moins 2 architectures :
     * Modèle léger : Arbre de Décision / Random Forest.
     * Modèle neuronal : Perceptron multicouche (MLP) ou petit réseau dense.
3. **Validation et métriques statistiques** :
   - Calculer la matrice de confusion, l'exactitude (Accuracy), la précision, le rappel et le score F1.
4. **Optimisation TinyML & Export C** :
   - Quantifier le modèle en entiers `int8` pour qu'il soit ultra-compact.
   - Générer le fichier C (`tinyml_model.h`) contenant la fonction d'inférence pure sans dépendance externe et le transmettre au Membre 1.

---

### 👤 MEMBRE 3 : FOG & SIMULATION SYSTÈME (Supervision & Benchmark)
**Son rôle : Simuler l'environnement complet et créer le tableau de bord de supervision.**

1. **Script de simulation d'environnement (Python)** :
   - Développer un simulateur qui rejoue la météo sur plusieurs jours/semaines (cycle jour/nuit, chaleur, pluie, évaporation naturelle du sol).
   - Envoyer ces données vers le système et enregistrer les décisions de la pompe.
2. **Supervision Fog (MQTT & Dashboard)** :
   - Installer et configurer un broker MQTT local (**Mosquitto**).
   - Créer un tableau de bord graphique (**Node-RED** ou **Grafana**) qui affiche en temps réel les courbes d'humidité du sol, la température et l'état marche/arrêt de la pompe.
3. **Benchmark comparatif (Le résultat clé du projet)** :
   - Programmer la comparaison sur 30 jours simulés entre :
     * *Système classique à seuil fixe* (arrose dès que humidité < 25%).
     * *Système Edge AI* (arrose intelligemment selon les prédictions).
   - Calculer les métriques concrètes : volume d'eau consommé (Litres), nombre de cycles pompe, et pourcentage d'eau économisée (ex: 25% d'économie).

---

### 🔄 Schéma des Échanges Pratiques entre Vous 3 :

```text
[MEMBRE 2 : Data / IA]
   │  Génère le modèle optimisé en C (tinyml_model.h)
   ▼
[MEMBRE 1 : Toi (STM32)] ◄─── Injecte les conditions météo du simulateur
   │                           [MEMBRE 3 : Simulateur Météo]
   │  Prend la décision d'arrosage (0 ou 1) en < 1 µs
   │  Mesure : Cycles CPU, Flash (Ko), RAM (Ko)
   ▼
[MEMBRE 3 : Fog & Benchmark]
   │  Reçoit l'état de la pompe
   │  Affiche les courbes sur le Dashboard Node-RED
   ▼
Résultat final : % d'eau économisée + Rapport de performance globale
```
