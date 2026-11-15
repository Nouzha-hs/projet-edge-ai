# Organisation & Répartition des Tâches : Équipe de 3 Personnes
## Projet Edge AI : Système d'Irrigation Intelligent (100% Simulation)

Consultez le document complet avec schémas interactifs et fiches de rôle détaillées dans :
👉 [repartition_equipe_3_personnes.md](file:///C:/Users/unui/.gemini/antigravity/brain/078486af-25e6-49d5-9520-ab81c644e4ad/repartition_equipe_3_personnes.md)

---

### Résumé des Rôles :

1. **Membre 1 : Ingénieur Embarqué & Edge AI (STM32)**
   - Environnement STM32CubeIDE (Nucleo-F401RE / Cortex-M4).
   - Intégration du modèle IA converti en C (TFLite Micro / STM32Cube.AI).
   - Boucle de contrôle autonome, garde-fou anti-noyade (30s max).
   - Mesure des métriques cibles : Flash (Ko), RAM (Ko), temps d'inférence (ms / cycles CPU).

2. **Membre 2 : Data Scientist & Ingénieur Machine Learning**
   - Exploration et nettoyage du dataset fourni par le professeur.
   - Entraînement et comparaison de modèles (Arbres de décision, Random Forest, Réseau de neurones MLP).
   - Évaluation complète (Précision, Rappel, F1-score, Matrice de confusion).
   - Quantification `int8` (TinyML) et génération du code C / TFLite pour le Membre 1.

3. **Membre 3 : Architecte Fog/Cloud, Supervision & Banc de Simulation**
   - Script de simulation météo (injection de flux de données simulées vers le système).
   - Passerelle et supervision : Broker MQTT Mosquitto + Dashboard (Node-RED ou Grafana).
   - Démonstration du gain : Calcul comparatif de l'économie d'eau (Seuil fixe traditionnel vs Edge AI).
   - Coordination de la présentation et synthèse des résultats.

---

### Répartition des 12 Diapositives pour la Soutenance :
- **Intro & Contexte (Slides 1-2)** : Membre 3
- **Architecture Système (Slide 3)** : Membre 3
- **Dataset & Modélisation IA (Slides 4-6)** : Membre 2
- **Déploiement Edge STM32 & Métriques Flash/RAM (Slides 7-9)** : Membre 1
- **Supervision Fog & Démonstration Dashboard (Slide 10)** : Membre 3
- **Résultats Comparatifs & Économies d'Eau (Slide 11)** : Membres 1, 2, 3
- **Conclusion & Perspectives (Slide 12)** : Membres 1, 2, 3
