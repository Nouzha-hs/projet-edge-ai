#!/usr/bin/env python3
"""
Script de collecte automatique des mesures série de la carte STM32 Nucleo-F401RE.
Enregistre les données au format CSV dans ../data/sensor_readings.csv.
"""

import sys
import os
import time
from datetime import datetime

try:
    import serial
    import serial.tools.list_ports
except ImportError:
    print("Le module 'pyserial' n'est pas encore installé.")
    print("Installez-le avec : pip install pyserial")
    sys.exit(1)

OUTPUT_FILE = os.path.join(os.path.dirname(__file__), "..", "data", "sensor_readings.csv")

def find_stlink_port():
    """Détecte automatiquement le port COM du ST-Link."""
    ports = list(serial.tools.list_ports.comports())
    for p in ports:
        description = p.description.lower()
        if "stlink" in description or "st-link" in description or "stm32" in description:
            return p.device
    if ports:
        # Retourne le premier port disponible par défaut
        return ports[0].device
    return None

def main():
    port = find_stlink_port()
    if not port:
        print("Aucun port série ST-Link ou périphérique COM détecté.")
        print("Vérifiez que votre carte STM32 Nucleo est bien branchée en USB.")
        sys.exit(1)

    print(f"Connexion au port série : {port} à 115200 bauds...")
    
    # Création du fichier CSV avec en-têtes si inexistant
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    if not os.path.exists(OUTPUT_FILE):
        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            f.write("iso_timestamp,timestamp_ms,temp_c,hum_air_pct,press_hpa,soil_raw,soil_pct,pump_state\n")

    try:
        ser = serial.Serial(port, 115200, timeout=2)
        time.sleep(1) # Attente stabilisation
        print(f"Écoute active. Données sauvegardées dans : {OUTPUT_FILE}")
        print("Appuyez sur Ctrl+C pour arrêter l'enregistrement.\n")

        with open(OUTPUT_FILE, "a", encoding="utf-8") as f:
            while True:
                line = ser.readline().decode("utf-8", errors="ignore").strip()
                if not line:
                    continue
                
                # Ignorer les lignes de messages d'information
                if line.startswith("[") or line.startswith("=") or "Format CSV" in line:
                    print(f"Log Nucleo: {line}")
                    continue

                parts = line.split(";")
                if len(parts) == 7:
                    iso_time = datetime.now().isoformat()
                    csv_row = f"{iso_time},{parts[0]},{parts[1]},{parts[2]},{parts[3]},{parts[4]},{parts[5]},{parts[6]}\n"
                    f.write(csv_row)
                    f.flush()
                    print(f"[{iso_time}] Sol: {parts[5]}% | Temp: {parts[1]}°C | HumAir: {parts[2]}% | Pompe: {parts[6]}")
                else:
                    print(f"Télémétrie brute : {line}")

    except KeyboardInterrupt:
        print("\nArrêt de l'enregistrement.")
    except Exception as e:
        print(f"Erreur série : {e}")

if __name__ == "__main__":
    main()
