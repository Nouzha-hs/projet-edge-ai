"""
benchmark_eau.py - Membre 3
Benchmark ecologique offline: seuil fixe (A) vs Edge AI base sur l'ET0 (B).

Les deux strategies tournent sur LA MEME meteo (meme graine), sans MQTT:
une saison de 90 jours se simule en quelques secondes.

Usage:
    python benchmark_eau.py
    python benchmark_eau.py --days 120 --seed 7
    python benchmark_eau.py --mix canicule=0.7,chergui=0.2,hiver=0.1

Sorties (dans le dossier courant, ou --out):
    resultats_benchmark.csv      tableau chiffre
    benchmark_graphiques.png     4 graphiques

Fichier requis dans le meme dossier: simulateur_souss.py (meteo + ET0).

HYPOTHESES (a citer dans le rapport, a ajuster si Membre 2 fournit mieux):
  - Meteo et ET0: celles de simulateur_souss.py (ET0 simplifiee, pas FAO-56 reelle).
  - Sol: 1 mm d'eau = 2 % d'humidite (50 mm utiles = 100 %).
  - Debit de la pompe: 4 mm/h (= 40 m3/ha/h).   1 mm = 10 m3/ha.
  - Besoin de la culture: ETc = Kc * ET0, Kc = 0.85. Pas de pluie (P_eff = 0).
  - Pertes d'application (evaporation, derive du vent): fraction de l'eau pompee
    qui n'atteint pas les racines, plus forte en plein soleil / vent / air sec.
    C'est une HYPOTHESE du modele: on donne donc le resultat AVEC et SANS pertes.
    Sans pertes, l'avantage vient uniquement de la regulation (pas de sur-arrosage).
  - Strategie A (seuil fixe): pompe ON si humidite < 30 %, OFF a partir de 40 %,
    a n'importe quelle heure.
  - Strategie B (Edge AI): chaque jour, besoin net I_net = max(0, Kc*ET0_veille - P_eff).
    A l'aube (03h-07h, avant le soleil) la pompe remonte l'humidite jusqu'a
    30 % + I_net (pour finir la journee vers 30 %, comme A). Securite: ON si < 20 %.
    L'ET0 du jour est estimee par celle de la veille (prevision par persistance).
  - Comparaison equitable: les deux strategies visent la meme humidite minimale (30 %);
    verifier "Humidite moyenne/finale" dans les resultats.
"""
import argparse
import csv
import os
import random

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from simulateur_souss import SCENARIOS, meteo, et0_hourly, KC

STEP_H = 0.5            # un pas = 30 min
STEPS_PER_DAY = 48
MM_TO_PCT = 2.0         # 1 mm = 2 % d'humidite du sol
PUMP_MM_H = 4.0         # debit de la pompe (mm/h)
MM_TO_M3HA = 10.0       # 1 mm = 10 m3/ha
P_EFF = 0.0             # pluie efficace (mm/jour)
SOIL0 = 45.0
STRESS_LEVEL = 20.0     # en dessous: stress hydrique


# ---------------------------------------------------------------- meteo
def generate_season(days, mix, seed):
    random.seed(seed)   # meteo() utilise random.gauss
    rng = random.Random(seed)
    names = list(mix)
    weights = [mix[n] for n in names]
    steps = []
    for d in range(days):
        name = rng.choices(names, weights)[0]
        sc = SCENARIOS[name]
        for k in range(STEPS_PER_DAY):
            hour = k * STEP_H
            t, rh, wind, rad = meteo(hour, sc)
            steps.append(dict(day=d, hour=hour, scenario=name, t=t, rh=rh,
                              wind=wind, rad=rad, et0=et0_hourly(t, rh, wind, rad)))
    return steps


def loss_fraction(s):
    """Part de l'eau pompee perdue (evaporation/derive): plus forte en plein soleil."""
    f = 0.02 + 0.15 * s["rad"] / 1000.0 + 0.015 * s["wind"] * (1 - s["rh"] / 100.0) * (s["t"] / 30.0)
    return min(0.5, max(0.0, f))


# ---------------------------------------------------------------- strategies
class SeuilFixe:
    def decide(self, soil, pump, s, steps, i):
        if soil < 30:
            return True
        if soil >= 40:
            return False
        return pump


class EdgeAI:
    SAFETY_LOW = 20.0   # securite: pompe ON si humidite < 20 %
    SOIL_MIN = 30.0     # humidite qu'on veut garder en fin de journee (= seuil de A)

    def __init__(self):
        self.level = self.SOIL_MIN
        self.safety = False

    def decide(self, soil, pump, s, steps, i):
        if s["hour"] == 0:
            # besoin net prevu pour la journee: I_net = max(0, Kc*ET0_veille - P_eff)
            if i >= STEPS_PER_DAY:
                et0_day = sum(x["et0"] for x in steps[i - STEPS_PER_DAY:i]) * STEP_H
            else:
                et0_day = 5.0
            i_net = max(0.0, KC * et0_day - P_EFF)
            # niveau a atteindre a l'aube pour finir la journee vers SOIL_MIN
            self.level = self.SOIL_MIN + i_net * MM_TO_PCT
        if soil < self.SAFETY_LOW:
            self.safety = True
        elif soil >= self.SAFETY_LOW + 5:
            self.safety = False
        if self.safety:
            return True
        # arrosage de nuit/aube (avant le soleil), jusqu'au niveau voulu
        return 3.0 <= s["hour"] < 7.0 and soil < self.level


# ---------------------------------------------------------------- simulation
def simulate(steps, policy, losses=True):
    soil, pump = SOIL0, False
    applied = lost = drained = 0.0
    stress = 0
    soil_h, pump_h, cum_h = [], [], []
    for i, s in enumerate(steps):
        pump = policy.decide(soil, pump, s, steps, i)
        etc = KC * s["et0"] * STEP_H
        eff = 0.0
        if pump:
            raw = PUMP_MM_H * STEP_H
            lf = loss_fraction(s) if losses else 0.0
            eff = raw * (1 - lf)
            applied += raw
            lost += raw * lf
        soil += (eff - etc) * MM_TO_PCT
        if soil > 100:
            drained += (soil - 100) / MM_TO_PCT
            soil = 100.0
        soil = max(0.0, soil)
        stress += soil < STRESS_LEVEL
        soil_h.append(soil)
        pump_h.append(1 if pump else 0)
        cum_h.append(applied * MM_TO_M3HA)
    n = len(steps)
    return dict(
        eau_m3ha=applied * MM_TO_M3HA,
        pertes_m3ha=lost * MM_TO_M3HA,
        drainage_m3ha=drained * MM_TO_M3HA,
        stress_pct=100.0 * stress / n,
        humidite_moy=sum(soil_h) / n,
        humidite_finale=soil_h[-1],
        heures_pompe=sum(pump_h) * STEP_H,
        soil=soil_h, pump=pump_h, cum=cum_h)


# ---------------------------------------------------------------- graphiques
SURFACE, INK, INK2, GRID = "#fcfcfb", "#0b0b0b", "#52514e", "#e5e5e3"
C_FIXE, C_AI = "#eb6834", "#2a78d6"     # orange = seuil fixe, bleu = Edge AI


def style(ax, title, xlabel, ylabel):
    ax.set_facecolor(SURFACE)
    ax.set_title(title, loc="left", fontsize=11, color=INK, fontweight="bold")
    ax.set_xlabel(xlabel, color=INK2, fontsize=9)
    ax.set_ylabel(ylabel, color=INK2, fontsize=9)
    ax.grid(axis="y", color=GRID, linewidth=0.8)
    ax.set_axisbelow(True)
    for sp in ("top", "right", "left"):
        ax.spines[sp].set_visible(False)
    ax.spines["bottom"].set_color(GRID)
    ax.tick_params(colors=INK2, labelsize=8, length=0)


def make_plots(steps, A, B, res_no_loss, days, path):
    fig, axs = plt.subplots(2, 2, figsize=(13, 8.5), facecolor=SURFACE)
    t_days = [i * STEP_H / 24 for i in range(len(steps))]

    # 1. eau cumulee
    ax = axs[0, 0]
    style(ax, "Eau cumulée appliquée", "Jours", "m³/ha")
    ax.plot(t_days, A["cum"], color=C_FIXE, linewidth=2)
    ax.plot(t_days, B["cum"], color=C_AI, linewidth=2)
    ax.text(t_days[-1], A["cum"][-1], f" {A['cum'][-1]:.0f}", color=INK, va="center", fontsize=9)
    ax.text(t_days[-1], B["cum"][-1], f" {B['cum'][-1]:.0f}", color=INK, va="center", fontsize=9)
    ax.set_xlim(0, days * 1.07)

    # 2. humidite du sol
    ax = axs[0, 1]
    style(ax, "Humidité du sol (%)", "Jours", "%")
    ax.axhline(STRESS_LEVEL, color=INK2, linewidth=1, linestyle=(0, (4, 3)))
    ax.text(0.2, STRESS_LEVEL + 1.5, "seuil de stress 20 %", color=INK2, fontsize=8)
    ax.plot(t_days, A["soil"], color=C_FIXE, linewidth=1.4)
    ax.plot(t_days, B["soil"], color=C_AI, linewidth=1.4)
    ax.set_ylim(0, 100)
    ax.set_xlim(0, days)

    # 3. pompe ON/OFF sur une journee chaude
    ax = axs[1, 0]
    # journee la plus chaude parmi celles ou les 2 pompes ont tourne (hors jours 1-3: regime de depart)
    def day_pumps(d):
        s2 = slice(d * STEPS_PER_DAY, (d + 1) * STEPS_PER_DAY)
        return sum(A["pump"][s2]) > 0 and sum(B["pump"][s2]) > 0
    cand = [d for d in range(min(3, days - 1), days) if day_pumps(d)] or list(range(days))
    hot_day = max(cand, key=lambda d: sum(
        steps[d * STEPS_PER_DAY + k]["t"] for k in range(STEPS_PER_DAY)))
    sl = slice(hot_day * STEPS_PER_DAY, (hot_day + 1) * STEPS_PER_DAY)
    hours = [steps[i]["hour"] for i in range(sl.start, sl.stop)]
    style(ax, f"Pompe ON/OFF - journée chaude (jour {hot_day + 1}, {steps[sl.start]['scenario']})",
          "Heure", "")
    ax.fill_between(hours, 1.6, [1.6 + v for v in B["pump"][sl]], step="post", color=C_AI, linewidth=0)
    ax.fill_between(hours, 0, A["pump"][sl], step="post", color=C_FIXE, linewidth=0)
    ax.set_yticks([0.5, 2.1])
    ax.set_yticklabels(["Seuil fixe", "Edge AI"], color=INK, fontsize=9)
    ax.set_xlim(0, 24)
    ax.set_xticks(range(0, 25, 3))
    ax.set_ylim(0, 2.8)
    ax.grid(axis="y", visible=False)
    ax.grid(axis="x", color=GRID, linewidth=0.8)

    # 4. barres: eau avec / sans pertes
    ax = axs[1, 1]
    style(ax, "Eau totale par stratégie (m³/ha)", "", "m³/ha")
    groups = [("Avec pertes\nd'application", A["eau_m3ha"], B["eau_m3ha"]),
              ("Sans pertes\n(régulation seule)", res_no_loss[0]["eau_m3ha"], res_no_loss[1]["eau_m3ha"])]
    w = 0.34
    for gi, (lab, a, b) in enumerate(groups):
        ax.bar(gi - w / 2 - 0.01, a, w, color=C_FIXE)
        ax.bar(gi + w / 2 + 0.01, b, w, color=C_AI)
        ax.text(gi - w / 2 - 0.01, a, f"{a:.0f}", ha="center", va="bottom", fontsize=9, color=INK)
        ax.text(gi + w / 2 + 0.01, b, f"{b:.0f}", ha="center", va="bottom", fontsize=9, color=INK)
        sav = 100 * (a - b) / a if a else 0
        ax.text(gi, max(a, b) * 1.12, f"Économie {sav:+.1f} %", ha="center", fontsize=10,
                color=INK, fontweight="bold")
    ax.set_xticks([0, 1])
    ax.set_xticklabels([g[0] for g in groups], color=INK, fontsize=9)
    ax.set_ylim(0, max(groups[0][1], groups[1][1]) * 1.3)

    handles = [plt.Line2D([0], [0], color=C_FIXE, linewidth=4),
               plt.Line2D([0], [0], color=C_AI, linewidth=4)]
    fig.legend(handles, ["A : seuil fixe", "B : Edge AI (ET₀)"], loc="upper center",
               ncol=2, frameon=False, fontsize=10, labelcolor=INK)
    fig.suptitle("")
    fig.tight_layout(rect=(0, 0, 1, 0.94))
    fig.savefig(path, dpi=140, facecolor=SURFACE)
    plt.close(fig)


# ---------------------------------------------------------------- main
def parse_mix(txt):
    mix = {}
    for part in txt.split(","):
        k, v = part.split("=")
        k = k.strip()
        if k not in SCENARIOS:
            raise SystemExit(f"scenario inconnu: {k} (choix: {', '.join(SCENARIOS)})")
        mix[k] = float(v)
    return mix


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--days", type=int, default=90)
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--mix", default="canicule=0.6,chergui=0.15,hiver=0.25",
                   help="probabilite de chaque type de journee")
    p.add_argument("--out", default=".")
    args = p.parse_args()

    mix = parse_mix(args.mix)
    steps = generate_season(args.days, mix, args.seed)
    et0_tot = sum(s["et0"] for s in steps) * STEP_H
    print(f"Saison: {args.days} jours, mix={mix}, graine={args.seed}")
    print(f"ET0 totale: {et0_tot:.0f} mm   -> besoin culture (Kc={KC}): {KC * et0_tot:.0f} mm "
          f"= {KC * et0_tot * MM_TO_M3HA:.0f} m3/ha\n")

    results = {}
    for label, losses in (("avec_pertes", True), ("sans_pertes", False)):
        A = simulate(steps, SeuilFixe(), losses)
        B = simulate(steps, EdgeAI(), losses)
        results[label] = (A, B)

    rows = []
    for label in ("avec_pertes", "sans_pertes"):
        A, B = results[label]
        saving = 100 * (A["eau_m3ha"] - B["eau_m3ha"]) / A["eau_m3ha"]
        print(f"=== {label.replace('_', ' ')} ===")
        print(f"{'':28s}{'A seuil fixe':>14s}{'B Edge AI':>14s}")
        for key, name, fmt in (("eau_m3ha", "Eau pompee (m3/ha)", "{:.0f}"),
                               ("pertes_m3ha", "dont pertes (m3/ha)", "{:.0f}"),
                               ("drainage_m3ha", "Drainage >100 % (m3/ha)", "{:.0f}"),
                               ("heures_pompe", "Heures de pompe", "{:.0f}"),
                               ("humidite_moy", "Humidite moyenne (%)", "{:.1f}"),
                               ("humidite_finale", "Humidite finale (%)", "{:.1f}"),
                               ("stress_pct", "Temps en stress (<20 %) (%)", "{:.1f}")):
            print(f"{name:28s}{fmt.format(A[key]):>14s}{fmt.format(B[key]):>14s}")
            rows.append([label, name, fmt.format(A[key]), fmt.format(B[key])])
        print(f"{'ECONOMIE D EAU':28s}{saving:>13.1f} %\n")
        rows.append([label, "Economie d'eau (%)", "", f"{saving:.1f}"])

    os.makedirs(args.out, exist_ok=True)
    csv_path = os.path.join(args.out, "resultats_benchmark.csv")
    with open(csv_path, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f, delimiter=";")
        w.writerow(["hypothese", "indicateur", "A_seuil_fixe", "B_edge_ai"])
        w.writerows(rows)

    png_path = os.path.join(args.out, "benchmark_graphiques.png")
    A, B = results["avec_pertes"]
    make_plots(steps, A, B, results["sans_pertes"], args.days, png_path)
    print(f"Ecrit: {csv_path}\n       {png_path}")


if __name__ == "__main__":
    main()
