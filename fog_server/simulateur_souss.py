"""
simulateur_souss.py - Membre 3
Simule le climat du Souss (Agadir / Taroudant) et publie en MQTT.

Usage:
    python simulateur_souss.py                      # scenario canicule, 1 s = 30 min simulees
    python simulateur_souss.py --scenario chergui
    python simulateur_souss.py --scenario hiver --interval 0.5
    python simulateur_souss.py --dry-run            # sans broker (affiche seulement)

Topics:
    souss/sensors  (publie)  -> JSON: t, rh, wind, rad, et0, soil, pump, scenario, hour
    souss/pump     (ecoute)  -> "ON" ou "OFF" (decision envoyee par la STM32 via le bridge)

NB: l'ET0 ici est une approximation simplifiee. Remplace-la par l'ET0 FAO-56
reelle de Membre 2 (Copernicus) quand elle est disponible.
"""
import argparse
import json
import math
import random
import time

try:
    import paho.mqtt.client as mqtt
except ImportError:
    mqtt = None

KC = 0.85  # coefficient cultural (cf. document)

# Tmin, Tmax (deg C), humidite relative min/max (%), vent moyen (m/s), rayonnement max (W/m2)
SCENARIOS = {
    "canicule": dict(tmin=24, tmax=38, rh_min=18, rh_max=45, wind=4.0, rad_max=950),
    "chergui":  dict(tmin=28, tmax=42, rh_min=8,  rh_max=22, wind=8.0, rad_max=900),
    "hiver":    dict(tmin=8,  tmax=16, rh_min=55, rh_max=85, wind=2.0, rad_max=500),
}


def meteo(hour, sc):
    """Meteo pour une heure donnee (0-24) selon le scenario."""
    # Temperature: minimum ~6h, maximum ~15h
    t_mean = (sc["tmax"] + sc["tmin"]) / 2
    amp = (sc["tmax"] - sc["tmin"]) / 2
    t = t_mean + amp * math.sin(2 * math.pi * (hour - 9) / 24) + random.gauss(0, 0.3)

    # Humidite: inverse de la temperature
    frac = (t - sc["tmin"]) / (sc["tmax"] - sc["tmin"])
    frac = min(1, max(0, frac))
    rh = sc["rh_max"] - frac * (sc["rh_max"] - sc["rh_min"]) + random.gauss(0, 1)
    rh = min(100, max(3, rh))

    # Vent: plus fort l'apres-midi
    wind = max(0.0, sc["wind"] * (0.7 + 0.5 * max(0, math.sin(math.pi * (hour - 8) / 12))) + random.gauss(0, 0.3))

    # Rayonnement: courbe solaire 6h-18h
    if 6 <= hour <= 18:
        rad = sc["rad_max"] * math.sin(math.pi * (hour - 6) / 12) + random.gauss(0, 15)
    else:
        rad = 0.0
    rad = max(0.0, rad)
    return t, rh, wind, rad


def et0_hourly(t, rh, wind, rad):
    """ET0 approximative en mm/h (formule simplifiee, a remplacer par FAO-56 reelle)."""
    et0 = 0.0004 * rad * (1 + 0.02 * (t - 20)) + 0.05 * wind * (1 - rh / 100)
    return max(0.0, et0)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--scenario", choices=SCENARIOS, default="canicule")
    p.add_argument("--host", default="localhost")
    p.add_argument("--port", type=int, default=1883)
    p.add_argument("--interval", type=float, default=1.0, help="secondes reelles par pas")
    p.add_argument("--step-min", type=int, default=30, help="minutes simulees par pas")
    p.add_argument("--days", type=int, default=1)
    p.add_argument("--soil0", type=float, default=45.0, help="humidite initiale du sol (%%)")
    p.add_argument("--dry-run", action="store_true")
    args = p.parse_args()

    sc = SCENARIOS[args.scenario]
    state = {"pump": False}
    client = None

    if not args.dry_run:
        if mqtt is None:
            raise SystemExit("paho-mqtt manquant: pip install paho-mqtt (ou utilise --dry-run)")

        def on_message(c, u, msg):
            state["pump"] = msg.payload.decode().strip().upper() == "ON"

        try:
            client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)  # paho-mqtt >= 2.0
        except AttributeError:
            client = mqtt.Client()  # paho-mqtt 1.x
        client.on_message = on_message
        client.connect(args.host, args.port)
        client.subscribe("souss/pump")
        client.loop_start()

    soil = args.soil0
    step_h = args.step_min / 60
    steps = int(24 / step_h) * args.days

    for i in range(steps):
        hour = (i * step_h) % 24
        t, rh, wind, rad = meteo(hour, sc)
        et0 = et0_hourly(t, rh, wind, rad)

        # Bilan hydrique du sol (%): pertes = Kc*ET0, gain = irrigation si pompe ON
        soil -= KC * et0 * step_h * 2.0
        if state["pump"]:
            soil += 1.5
        soil = min(100.0, max(0.0, soil))

        msg = {
            "hour": round(hour, 2),
            "t": round(t, 1),
            "rh": round(rh, 1),
            "wind": round(wind, 1),
            "rad": round(rad, 0),
            "et0": round(et0, 3),
            "soil": round(soil, 1),
            "pump": state["pump"],
            "scenario": args.scenario,
        }
        payload = json.dumps(msg)
        if client:
            client.publish("souss/sensors", payload)
        print(payload)
        time.sleep(args.interval)

    if client:
        client.loop_stop()
        client.disconnect()


if __name__ == "__main__":
    main()
