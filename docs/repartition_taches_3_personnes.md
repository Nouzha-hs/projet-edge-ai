# Répartition des Tâches du Groupe (3 Personnes) - Projet Simulation Edge AI

Ce document fixe la feuille de route et l'attribution des rôles pour le projet d'irrigation intelligente en mode **simulation intégrale**.

---

## Les 3 Pôles de Compétences

### 👤 Membre 1 : Ingénieur Edge & Contraintes Embarquées (TinyML)
- **Objectif** : Simuler le comportement d'un microcontrôleur STM32 et évaluer la viabilité embarquée de l'IA.
- **Tâches** :
  1. Écrire le simulateur du microcontrôleur Edge (lecture séquentielle des capteurs simulés, déclenchement de la pompe virtuelle).
  2. Implémenter les algorithmes de sécurité (durée maximale de pompage, temps de repos du sol).
  3. Intégrer le modèle quantifié en `int8` (fourni par le Membre 2) dans le simulateur Edge.
  4. Calculer les métriques matérielles : estimation de l'empreinte Flash et RAM, nombre d'opérations et latence d'inférence.
  5. Réaliser le benchmark comparatif : Volume d'eau consommé avec une logique de seuil fixe vs Modèle IA.

### 👤 Membre 2 : Data Scientist / Ingénieur Modélisation IA
- **Objectif** : Transformer le dataset fourni par le professeur en un modèle prédictif optimal pour l'embarqué.
- **Tâches** :
  1. Exploration des données (EDA) : distribution de l'humidité du sol, de la température et de l'humidité de l'air, détection des anomalies.
  2. Prétraitement et ingénierie des caractéristiques (*Feature Engineering*, normalisation adaptée aux entiers `int8`).
  3. Entraînement et comparaison de 3 modèles :
     - Modèle 1 : Arbre de Décision (*Decision Tree*)
     - Modèle 2 : Forêt Aléatoire (*Random Forest*)
     - Modèle 3 : Réseau de neurones dense compact (*Tiny MLP*)
  4. Évaluation approfondie : Précision, Rappel, F1-Score, Matrice de confusion et Courbe ROC/AUC.
  5. Quantification du modèle retenu en format léger (`.tflite` / structure C) pour le Membre 1.

### 👤 Membre 3 : Ingénieur Fog Computing, Télémétrie & Dashboard
- **Objectif** : Orchestrer le flux de données réseau et concevoir l'interface de contrôle pour la démonstration.
- **Tâches** :
  1. Définir le protocole de communication et le format des messages JSON échangés en MQTT.
  2. Déployer et configurer le broker MQTT local (Eclipse Mosquitto).
  3. Développer le script d'injection/simulation temps réel rejouant les données du professeur comme si les capteurs émettaient minute par minute.
  4. Concevoir le tableau de bord interactif de supervision (Streamlit ou Node-RED) avec courbes en direct, jauges de sol/air, alertes et statut de la pompe.
  5. Préparer la démonstration interactive en direct pour le jury de soutenance.

---

## Planning par Semaines

- **Semaine 1** : Réception du dataset, cadrage du simulateur Edge et choix des technologies du Dashboard.
- **Semaine 2** : Prétraitement des données (Membre 2), écriture du moteur de simulation du sol/pompe (Membre 1), mise en place du broker MQTT et flux JSON (Membre 3).
- **Semaine 3** : Entraînement des modèles IA (Membre 2), développement de l'interface graphique / Dashboard (Membre 3), implémentation de la logique de seuil de référence (Membre 1).
- **Semaine 4** : Quantification `int8` et transmission du modèle (Membre 2 ➔ Membre 1), intégration complète Edge-Fog-Dashboard (Membre 1 & 3), tests de bout en bout.
- **Semaine 5** : Mesures comparatives finales (eau économisée, latence), rédaction du rapport et répétition orale de la soutenance (répartition des diapositives).
