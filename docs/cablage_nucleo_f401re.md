# Guide de Câblage & Brochage : STM32 Nucleo-F401RE

La carte **STM32 Nucleo-F401RE** (Cortex-M4 @ 84 MHz, 512 Ko Flash, 96 Ko RAM) est **parfaitement adaptée** à ce projet :
- Support natif complet pour **X-CUBE-AI** et **TensorFlow Lite Micro**.
- Port série virtuel (**VCP**) sur le câble USB ST-Link via `USART2` (`PA2`/`PA3`), idéal pour déboguer et collecter les données sur PC sans câble convertisseur supplémentaire.
- Périphérique ADC1 rapide (12 bits) pour le capteur d'humidité du sol.
- Périphérique I2C1 matériel pour le BME280 ou temporisateur précis pour le DHT22.

---

## 1. Tableau de Brochage (Pinout Nucleo-F401RE)

| Composant | Broche Composant | Broche Nucleo-F401RE | Fonction STM32 / Alias Arduino | Remarques |
| :--- | :--- | :--- | :--- | :--- |
| **Capteur Humidité Sol** | VCC | **3V3** | Alimentation 3.3V | Version capacitive v1.2 |
| | GND | **GND** | Masse commune | |
| | AOUT | **PA0** | `ADC1_IN0` (Arduino `A0`) | Signal analogique (12 bits : 0 à 4095) |
| **BME280 (I2C)** *(Option A)* | VCC | **3V3** | Alimentation 3.3V | Adresse I2C : 0x76 ou 0x77 |
| | GND | **GND** | Masse commune | |
| | SCL | **PB8** | `I2C1_SCL` (Arduino `D15`) | Pull-up interne ou externe |
| | SDA | **PB9** | `I2C1_SDA` (Arduino `D14`) | |
| **DHT22** *(Option B)* | Pin 1 (VCC) | **3V3** | Alimentation 3.3V | |
| | Pin 2 (DATA) | **PA1** | `GPIO_Input/Output` (Arduino `A1`) | **Résistance 10 kΩ entre DATA et 3V3 obligatoire** |
| | Pin 4 (GND) | **GND** | Masse commune | |
| **Module Relais 5V** | VCC | **5V** | Alimentation 5V (broche 5V Nucleo) | Optocouplé |
| | GND | **GND** | Masse commune | |
| | IN | **PA4** | `GPIO_Output` (Arduino `A2`) | Commande logique 3.3V |
| **ESP32 / ESP8266 (Fog)** | RX | **PA9** | `USART1_TX` (Arduino `D8`) | Envoi de télémétrie STM32 -> ESP |
| | TX | **PA10** | `USART1_RX` (Arduino `D2`) | Réception commandes Fog -> STM32 |
| | GND | **GND** | Masse commune | Relier impérativement les masses |
| **ST-Link (USB PC)** | TX / RX | **PA2 / PA3** | `USART2_TX` / `USART2_RX` | Routé en interne vers l'USB ST-Link |

---

## 2. Circuit de Puissance de la Pompe (Sécurité Électrique)

```text
[Alimentation Externe 5V / 12V] (+) --------------------+
                                                        |
                                                  [Borne COM Relais]
                                                  [Borne NO  Relais] ---> (+) Pompe
                                                                             |
                                                                        [Moteur Pompe]
                                                                        + Diode 1N4007
                                                                        en parallèle inverse
                                                                        (Cathode / trait blanc au +)
                                                                             |
[Alimentation Externe 5V / 12V] (-) -----------------------------------------+
                                                        |
                                                  (Optionnel : relier GND externe au GND STM32)
```

> [!WARNING]
> La diode 1N4007 est branchée directement aux bornes de la pompe :
> - **Cathode (anneau argenté)** sur le fil positif (+) de la pompe.
> - **Anode** sur le fil négatif (-) de la pompe.
> Elle absorbe les pointes de tension négatives générées par l'arrêt brutal du moteur (effet selfique).
