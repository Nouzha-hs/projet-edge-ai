# Guide de Mission : Membre 1 (Ingénieur Embarqué & Edge AI)
## Cible : STM32 Nucleo-F401RE (ARM Cortex-M4 @ 84 MHz)

Félicitations pour le choix de ce rôle ! En tant que **Membre 1**, vous êtes le garant de la partie la plus technique et valorisante du projet : **l'intelligence artificielle qui s'exécute directement dans le microcontrôleur**.

---

## 1. Vos Responsabilités & Livrables

| Livrable | Fichier associé | Description |
| :--- | :--- | :--- |
| **Firmware de Simulation** | [firmware_stm32/test_simulation_main.c](file:///c:/Users/unui/OneDrive/Desktop/Projet%20Edge/firmware_stm32/test_simulation_main.c) | Boucle principale, orchestration des scénarios météo, pilotage virtuel |
| **Moteur d'Inférence TinyML** | [firmware_stm32/Drivers_Custom/Inc/tinyml_model.h](file:///c:/Users/unui/OneDrive/Desktop/Projet%20Edge/firmware_stm32/Drivers_Custom/Inc/tinyml_model.h) | Modèle IA en C pur (reçu du Membre 2), 0 allocation dynamique |
| **Jeu de Test Virtuel** | [firmware_stm32/Drivers_Custom/Inc/simulation_test_vectors.h](file:///c:/Users/unui/OneDrive/Desktop/Projet%20Edge/firmware_stm32/Drivers_Custom/Inc/simulation_test_vectors.h) | Scénarios de simulation météo (canicule, nuit, pluie, etc.) |
| **Mesures & Métriques** | Tableau de bord Flash/RAM/Latence | Extraction des métriques pour les **Slides 7, 8 et 9** |

---

## 2. Vos 3 Diapositives Dédiées pour la Soutenance

### 📌 Diapositive 7 : Architecture Logicielle & Boucle d'Exécution
- Présentation de la machine à états finis du firmware :
  ```text
  [Vecteur Capteurs Simulés] 
             │
             ▼
  [Inférence TinyML Locale] ────> [Décision : Arrosage 0 ou 1]
                                              │
                                              ▼
                                 [Vérification Garde-fou 30s]
                                              │
                                              ▼
                                 [Commande Actionneur Virtuel]
  ```
- Explication de l'exécution déterministe (aucun système d'exploitation lourd, code C optimisé).

### 📌 Diapositive 8 : Sécurité & Robustesse Embarquée
- Pourquoi une règle de sécurité temporelle est obligatoire en Edge AI : si le modèle fait une erreur de prédiction (faux positif), le **garde-fou matériel (timer 30s max)** coupe la pompe pour empêcher l'inondation.
- Gestion des erreurs et résilience locale (le système continue de fonctionner même en cas de coupure réseau).

### 📌 Diapositive 9 : Performances & Métriques Matérielles
- **Temps d'inférence** : mesuré grâce au registre matériel Cortex-M4 `DWT->CYCCNT` (mesure au cycle près).  
  *Exemple : ~42 cycles CPU @ 84 MHz = **0,50 microseconde** !*
- **Empreinte Flash (ROM)** : code d'inférence < **1,5 Ko** (sur 512 Ko disponibles = moins de 0,3% de la mémoire).
- **Empreinte RAM (SRAM)** : **0 octet** d'allocation dynamique `malloc`, tout s'exécute sur la pile (stack).
- **Bilan énergétique** : consommation CPU négligeable permettant de mettre le microcontrôleur en veille profonde (*Low Power Sleep*) entre deux lectures.

---

## 3. Comment Faire Tourner la Simulation Pas-à-Pas

### Option A : Si vous avez la carte Nucleo branchée en USB
1. Ouvrez **STM32CubeIDE 2.2.0**.
2. Créez le projet pour **NUCLEO-F401RE** (ou ouvrez votre projet existant).
3. Ajoutez les fichiers [tinyml_model.h](file:///c:/Users/unui/OneDrive/Desktop/Projet%20Edge/firmware_stm32/Drivers_Custom/Inc/tinyml_model.h) et [simulation_test_vectors.h](file:///c:/Users/unui/OneDrive/Desktop/Projet%20Edge/firmware_stm32/Drivers_Custom/Inc/simulation_test_vectors.h) dans les Includes.
4. Intégrez le code de [test_simulation_main.c](file:///c:/Users/unui/OneDrive/Desktop/Projet%20Edge/firmware_stm32/test_simulation_main.c) dans `Core/Src/main.c`.
5. Compilez (`Ctrl+B`) et lancez le programme (`Run` ou `F11`).
6. Ouvrez le terminal série dans CubeIDE (115200 bauds) : vous verrez s'afficher les scénarios et les mesures de cycles en temps réel !

### Option B : Si vous n'avez pas la carte physique (Simulation 100% PC)
- Vous pouvez lancer le projet en mode **Debug Simulateur** dans STM32CubeIDE (GDB Simulator) pour voir les variables évoluer en direct dans la fenêtre `Live Expressions` !
