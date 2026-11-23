"""
bridge_serial_mqtt.py - Membre 3
Pont entre la STM32 (port serie virtuel ST-Link) et le broker MQTT.

    simulateur --MQTT souss/sensors--> [ce bridge] --serie--> STM32
    STM32 --serie "PUMP=ON/OFF"--> [ce bridge] --MQTT souss/pump--> simulateur / dashboard

Usage:
    python bridge_serial_mqtt.py --list-ports            # trouver le port COM de la STM32
    python bridge_serial_mqtt.py --port COM5             # bridge reel
    python bridge_serial_mqtt.py --fake-stm32            # test SANS carte (decision simulee)

Installation:  pip install pyserial paho-mqtt

PROTOCOLE PAR DEFAUT (A CONFIRMER AVEC MEMBRE 1 - voir les constantes en haut):
  PC -> STM32 (une ligne par mesure, 115200 baud, fin de ligne \\n):
      format "kv":   T=38.2,RH=22.0,WIND=4.5,RAD=850,ET0=0.61,SOIL=31.0
      format "csv":  38.2,22.0,4.5,850,0.61,31.0        (ordre: T,RH,WIND,RAD,ET0,SOIL)
  STM32 -> PC (toute ligne contenant PUMP=ON ou PUMP=OFF est une decision;
               les autres lignes sont transmises telles quelles a souss/stm32/log):
      PUMP=ON
      PUMP=OFF

Securite: si la STM32 ne repond plus pendant --timeout secondes alors que la pompe
est ON, le bridge publie OFF (en plus du watchdog de 30 s cote STM32).
"""
import argparse
import json
import re
import sys
import threading
import time

try:
    import paho.mqtt.client as mqtt
except ImportError:
    mqtt = None
try:
    import serial
    from serial.tools import list_ports
except ImportError:
    serial = None
    list_ports = None

TOPIC_SENSORS = "souss/sensors"
TOPIC_PUMP = "souss/pump"
TOPIC_LOG = "souss/stm32/log"

PUMP_RE = re.compile(r"PUMP\s*[=:]\s*(ON|OFF|1|0)", re.IGNORECASE)


def build_line(d, fmt="kv"):
    """Ligne envoyee a la STM32 pour une mesure d (dict du simulateur)."""
    vals = [d.get("t", 0), d.get("rh", 0), d.get("wind", 0),
            d.get("rad", 0), d.get("et0", 0), d.get("soil", 0)]
    if fmt == "csv":
        return ",".join(str(v) for v in vals) + "\n"
    keys = ["T", "RH", "WIND", "RAD", "ET0", "SOIL"]
    return ",".join(f"{k}={v}" for k, v in zip(keys, vals)) + "\n"


def parse_decision(line):
    """'PUMP=ON' -> 'ON', 'PUMP=OFF' -> 'OFF', sinon None."""
    m = PUMP_RE.search(line)
    if not m:
        return None
    return "ON" if m.group(1).upper() in ("ON", "1") else "OFF"


def fake_decision(d):
    """Decision de remplacement pour tester SANS carte (pas l'IA de Membre 1)."""
    soil, rad = d.get("soil", 50), d.get("rad", 0)
    if soil < 30:
        return "ON"
    if soil < 40 and rad < 100:    # arrosage de nuit/aube seulement
        return "ON"
    return "OFF"


class Bridge:
    def __init__(self, args):
        self.args = args
        self.ser = None
        self.lock = threading.Lock()
        self.pump_state = "OFF"
        self.last_rx = time.time()
        self.client = None

    # ---------------- MQTT
    def on_message(self, client, userdata, msg):
        try:
            d = json.loads(msg.payload.decode())
        except (ValueError, UnicodeDecodeError):
            return
        if not isinstance(d, dict):
            return
        if self.args.fake_stm32:
            self.publish_pump(fake_decision(d))
            return
        line = build_line(d, self.args.format)
        with self.lock:
            try:
                self.ser.write(line.encode("ascii"))
            except Exception as e:          # port deconnecte, etc.
                print(f"[ERREUR serie] ecriture impossible: {e}", flush=True)
                return
        print(f"PC -> STM32 : {line.strip()}", flush=True)

    def publish_pump(self, state):
        self.pump_state = state
        self.client.publish(TOPIC_PUMP, state)
        print(f"decision -> {TOPIC_PUMP} : {state}", flush=True)

    def connect_mqtt(self):
        try:
            self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)   # paho-mqtt >= 2.0
        except AttributeError:
            self.client = mqtt.Client()                                  # paho-mqtt 1.x
        self.client.on_message = self.on_message
        self.client.connect(self.args.host, self.args.mqtt_port)
        self.client.subscribe(TOPIC_SENSORS)
        self.client.loop_start()
        print(f"MQTT connecte a {self.args.host}:{self.args.mqtt_port}, "
              f"ecoute {TOPIC_SENSORS}", flush=True)

    # ---------------- serie
    def open_serial(self):
        try:
            self.ser = serial.Serial(self.args.port, self.args.baud, timeout=0.2)
        except serial.SerialException as e:
            sys.exit(f"Impossible d'ouvrir {self.args.port}: {e}\n"
                     "- Mauvais port? Lance:  python bridge_serial_mqtt.py --list-ports\n"
                     "- Port deja utilise? Ferme le terminal serie de STM32CubeIDE / PuTTY / Tera Term.")
        print(f"Serie ouvert: {self.args.port} @ {self.args.baud} baud", flush=True)

    def run(self):
        self.connect_mqtt()
        if self.args.fake_stm32:
            print("MODE TEST: pas de carte, decision simulee (fake_decision).", flush=True)
            while True:
                time.sleep(1)
        self.open_serial()
        while True:
            raw = self.ser.readline()
            if raw:
                line = raw.decode("ascii", errors="ignore").strip()
                if line:
                    self.last_rx = time.time()
                    print(f"STM32 -> PC : {line}", flush=True)
                    self.client.publish(TOPIC_LOG, line)
                    state = parse_decision(line)
                    if state:
                        self.publish_pump(state)
            elif (self.pump_state == "ON"
                  and time.time() - self.last_rx > self.args.timeout):
                print(f"[SECURITE] STM32 muette depuis {self.args.timeout} s -> pompe OFF",
                      flush=True)
                self.publish_pump("OFF")
                self.last_rx = time.time()


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--port", help="port COM de la STM32, ex: COM5")
    p.add_argument("--baud", type=int, default=115200)
    p.add_argument("--format", choices=["kv", "csv"], default="kv")
    p.add_argument("--host", default="localhost")
    p.add_argument("--mqtt-port", type=int, default=1883)
    p.add_argument("--timeout", type=float, default=30.0,
                   help="secondes sans reponse STM32 avant pompe OFF")
    p.add_argument("--list-ports", action="store_true")
    p.add_argument("--fake-stm32", action="store_true", help="test sans carte")
    args = p.parse_args()

    if args.list_ports:
        if list_ports is None:
            sys.exit("pyserial manquant: pip install pyserial")
        ports = list(list_ports.comports())
        if not ports:
            print("Aucun port serie trouve (carte branchee? driver ST-Link installe?)")
        for pt in ports:
            print(f"{pt.device}\t{pt.description}")
        return
    if mqtt is None:
        sys.exit("paho-mqtt manquant: pip install paho-mqtt")
    if not args.fake_stm32:
        if serial is None:
            sys.exit("pyserial manquant: pip install pyserial")
        if not args.port:
            sys.exit("Donne le port: --port COM5  (liste: --list-ports)  ou teste avec --fake-stm32")
    try:
        Bridge(args).run()
    except KeyboardInterrupt:
        print("\nArret du bridge.")


if __name__ == "__main__":
    main()
