# Tutoriel Pas-à-Pas : Configuration STM32CubeIDE (Nucleo-F401RE)

Ce guide détaille la mise en place du projet dans **STM32CubeIDE 2.2.0** pour valider le banc de test de la **Semaine 1**.

---

## 1. Création du Projet dans STM32CubeIDE

1. Lancez **STM32CubeIDE**.
2. Allez dans le menu : **File** > **New** > **STM32 Project**.
3. Dans l'onglet **Board Selector** :
   - Tapez `NUCLEO-F401RE` dans la barre de recherche.
   - Sélectionnez la carte et cliquez sur **Next**.
4. Donnez un nom au projet (ex: `Firmware_Irrigation_F401RE`), choisissez le langage **C**, puis cliquez sur **Finish**.
5. À la question *"Initialize all peripherals with their default Mode ?"*, répondez **Yes**.
   *(Cela configure automatiquement l'horloge à 84 MHz et le port série ST-Link `USART2` sur `PA2`/`PA3`)*.

---

## 2. Configuration des Périphériques dans le fichier `.ioc`

### A. Capteur Humidité du Sol (ADC1)
1. Dans le volet de gauche, développez **Analog** > **ADC1**.
2. Cochez **IN0** (broche `PA0` sur le schéma).
3. Dans **Configuration** > **Parameter Settings** :
   - **Resolution** : `ADC 12-bit resolution`
   - **Data Alignment** : `Right alignment`
   - **Scan Conversion Mode** : `Disabled`
   - **Continuous Conversion Mode** : `Disabled`

### B. Capteur Air BME280 (I2C1)
1. Dans le volet de gauche, développez **Connectivity** > **I2C1**.
2. Dans le menu déroulant **I2C**, sélectionnez **I2C**.
3. Vérifiez sur le schéma graphique que :
   - `PB8` correspond à `I2C1_SCL`.
   - `PB9` correspond à `I2C1_SDA`.
4. Dans **Parameter Settings** :
   - **I2C Speed Mode** : `Standard Mode` (100 KHz).

### C. Commande du Relais Pompe (GPIO)
1. Sur la vue graphique de la puce, cliquez sur la broche **PA4** et sélectionnez **GPIO_Output**.
2. Dans **System Core** > **GPIO** > cliquez sur `PA4` :
   - **GPIO Output level** : `High` *(Pour maintenir le relais éteint au démarrage si module Active LOW)*
   - **GPIO mode** : `Output Push Pull`
   - **GPIO Pull-up/Pull-down** : `Pull-up`
   - **User Label** : `RELAY_PUMP`

### D. Liaison Série ST-Link PC (USART2)
- Normalement déjà configuré : `PA2` (TX) et `PA3` (RX), vitesse `115200 Bits/s`, 8 bits, pas de parité.

### E. Génération du Code
- Sauvegardez le fichier `.ioc` (`Ctrl + S`) pour générer le code HAL automatiquement.

---

## 3. Intégration de nos Drivers dans le Projet

Les fichiers drivers pré-conçus se trouvent dans `Projet Edge/firmware_stm32/Drivers_Custom/` :

1. Dans STM32CubeIDE, copiez le dossier `Drivers_Custom` dans votre projet (ou ajoutez son chemin aux includes du compilateur).
2. Dans le fichier `Core/Src/main.c` de CubeIDE :
   - Ajoutez les includes dans la section `/* USER CODE BEGIN Includes */` :
     ```c
     #include "bme280.h"
     #include "soil_sensor.h"
     #include "relay.h"
     #include <stdio.h>
     ```
   - Ajoutez la redirection `printf` dans `/* USER CODE BEGIN 0 */` :
     ```c
     #ifdef __GNUC__
     int __io_putchar(int ch)
     #else
     int fputc(int ch, FILE *f)
     #endif
     {
         HAL_UART_Transmit(&huart2, (uint8_t *)&ch, 1, HAL_MAX_DELAY);
         return ch;
     }
     ```
   - Ajoutez le contenu de test (visible dans [test_sensors_main.c](file:///c:/Users/unui/OneDrive/Desktop/Projet%20Edge/firmware_stm32/test_sensors_main.c)) dans votre boucle principale `main.c`.

---

## 4. Compilation et Flash

1. Branchez la carte **Nucleo-F401RE** au PC avec un câble USB (sur le port mini-USB du ST-Link).
2. Cliquez sur le marteau pour compiler (**Build Project** `Ctrl+B`). Assurez-vous d'avoir `0 error`.
3. Cliquez sur l'icône verte **Run** (ou `F11` / **Debug**). Le binaire est alors téléversé dans la Flash de la carte.

---

## 5. Visualisation des Données

- Vous pouvez ouvrir un terminal série à 115200 bauds (dans CubeIDE : `Window` > `Show View` > `Terminal`),
- Ou bien lancer le script de collecte automatique :
  ```powershell
  python "c:\Users\unui\OneDrive\Desktop\Projet Edge\ai_model\serial_logger.py"
  ```
