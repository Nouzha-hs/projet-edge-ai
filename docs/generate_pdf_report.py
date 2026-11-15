#!/usr/bin/env python3
"""
Générateur de rapport PDF complet avec graphiques :
- Répartition des tâches pratiques pour l'équipe de 3 personnes
- Planning adapté sur 3 semaines
- Graphiques d'architecture, Gantt, et benchmarks
"""

import os
import matplotlib.pyplot as plt
import numpy as np

from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, KeepTogether, PageBreak, HRFlowable
)
from reportlab.pdfgen import canvas

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SCHEMAS_DIR = os.path.join(BASE_DIR, "schemas")
PDF_PATH = os.path.join(BASE_DIR, "Repartition_Taches_Projet_Edge_AI.pdf")

os.makedirs(SCHEMAS_DIR, exist_ok=True)

# -------------------------------------------------------------
# 1. GÉNÉRATION DES GRAPHIQUES (MATPLOTLIB)
# -------------------------------------------------------------

def generate_gantt_chart():
    gantt_path = os.path.join(SCHEMAS_DIR, "gantt_3_semaines.png")
    fig, ax = plt.subplots(figsize=(10, 4.5), dpi=200)

    tasks = [
        # Membre 3
        ("M3 : Simulateur Météo 30j & Mosquitto", 0, 7, "#38bdf8"),
        ("M3 : Dashboard Node-RED & Télémétrie", 7, 14, "#0284c7"),
        ("M3 : Benchmark Économie d'Eau & Synthèse", 14, 21, "#0369a1"),

        # Membre 2
        ("M2 : Analyse Dataset Prof & Prétraitement", 0, 7, "#a855f7"),
        ("M2 : Entraînement Comparatif & Évaluation", 7, 14, "#9333ea"),
        ("M2 : Quantification int8 & Export C pur", 12, 17, "#7e22ce"),

        # Membre 1 (Toi)
        ("M1 : Config STM32CubeIDE & Boucle Test", 0, 7, "#10b981"),
        ("M1 : Intégration Modèle C & Watchdog 30s", 7, 14, "#059669"),
        ("M1 : Mesures Latence (Cycles DWT) & Flash/RAM", 14, 21, "#047857"),
    ]

    y_pos = np.arange(len(tasks))

    for i, (task_name, start, end, color) in enumerate(tasks):
        ax.barh(i, end - start, left=start, color=color, edgecolor="#1e293b", height=0.6, alpha=0.9)
        ax.text(start + 0.3, i, f"{start}-{end}j", va='center', ha='left', color='white', fontweight='bold', fontsize=9)

    ax.set_yticks(y_pos)
    ax.set_yticklabels([t[0] for t in tasks], fontsize=10, fontweight='500')
    ax.invert_yaxis()

    ax.set_xlabel("Jours du Projet (Sprint 3 Semaines)", fontsize=11, fontweight='bold', labelpad=10)
    ax.set_xlim(0, 21)
    ax.set_xticks([0, 7, 14, 21])
    ax.set_xticklabels(["Jour 0\n(Démarrage)", "Fin S1\n(Jalon 1)", "Fin S2\n(Jalon 2)", "Fin S3\n(Livrable Final)"], fontsize=10, fontweight='bold')

    # Lignes verticales des jalons
    ax.axvline(7, color="#ef4444", linestyle="--", alpha=0.7)
    ax.axvline(14, color="#ef4444", linestyle="--", alpha=0.7)
    ax.axvline(21, color="#ef4444", linestyle="--", alpha=0.7)

    ax.grid(axis='x', linestyle=':', alpha=0.6)
    plt.title("Planning Synchronisé sur 3 Semaines (Équipe de 3 Personnes)", fontsize=13, fontweight='bold', pad=15)
    plt.tight_layout()
    plt.savefig(gantt_path)
    plt.close()
    return gantt_path

def generate_ml_accuracy_chart():
    chart_path = os.path.join(SCHEMAS_DIR, "ml_comparison.png")
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 3.8), dpi=200)

    # Graphe 1 : Précision des modèles
    models = ['Arbre Décision\n(TinyML C)', 'Random Forest\n(50 Arbres)', 'Réseau Neurones\n(MLP 16x8)']
    accuracies = [99.20, 99.36, 98.56]
    colors_list = ['#10b981', '#3b82f6', '#8b5cf6']

    bars = ax1.bar(models, accuracies, color=colors_list, width=0.55, edgecolor='#334155')
    ax1.set_ylim(90, 101)
    ax1.set_ylabel("Exactitude / Accuracy (%)", fontweight='bold')
    ax1.set_title("Précision des Modèles Testés", fontweight='bold')
    ax1.grid(axis='y', linestyle=':', alpha=0.5)

    for b in bars:
        height = b.get_height()
        ax1.text(b.get_x() + b.get_width()/2., height + 0.6, f"{height:.2f}%", ha='center', va='bottom', fontweight='bold', fontsize=10)

    # Graphe 2 : Empreinte Flash estimée sur STM32
    flash_kb = [1.2, 45.0, 12.5]
    bars2 = ax2.bar(models, flash_kb, color=['#059669', '#2563eb', '#7c3aed'], width=0.55, edgecolor='#334155')
    ax2.set_ylabel("Empreinte Mémoire Flash (Ko)", fontweight='bold')
    ax2.set_title("Compromis Mémoire Embarquée (STM32)", fontweight='bold')
    ax2.grid(axis='y', linestyle=':', alpha=0.5)

    for b in bars2:
        height = b.get_height()
        ax2.text(b.get_x() + b.get_width()/2., height + 1.0, f"{height:.1f} Ko", ha='center', va='bottom', fontweight='bold', fontsize=10)

    plt.tight_layout()
    plt.savefig(chart_path)
    plt.close()
    return chart_path

# -------------------------------------------------------------
# 2. NUMÉROTATION DES PAGES (CANVAS HEADER / FOOTER)
# -------------------------------------------------------------

class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, page_count):
        self.saveState()
        self.setFont("Helvetica", 9)
        self.setFillColor(colors.HexColor("#64748b"))

        # En-tête
        self.drawString(40, 810, "Projet Edge AI : Irrigation Intelligente (TinyML & Fog) | Plan 3 Semaines")
        self.setStrokeColor(colors.HexColor("#cbd5e1"))
        self.setLineWidth(0.5)
        self.line(40, 802, 555, 802)

        # Pied de page
        page_str = f"Page {self._pageNumber} sur {page_count}"
        self.drawRightString(555, 30, page_str)
        self.drawString(40, 30, "Document de Répartition Pratique & Spécifications Techniques")
        self.line(40, 42, 555, 42)
        self.restoreState()

# -------------------------------------------------------------
# 3. COMPILATION DU DOCUMENT PDF
# -------------------------------------------------------------

def build_pdf():
    print("Génération des graphiques...")
    gantt_img = generate_gantt_chart()
    ml_img = generate_ml_accuracy_chart()
    bench_water_img = os.path.join(SCHEMAS_DIR, "benchmark_water_savings.png")

    doc = SimpleDocTemplate(
        PDF_PATH,
        pagesize=A4,
        leftMargin=36,
        rightMargin=36,
        topMargin=48,
        bottomMargin=48
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=20,
        leading=24,
        textColor=colors.HexColor('#0f172a'),
        alignment=1, # Centre
        spaceAfter=6
    )

    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=11,
        leading=15,
        textColor=colors.HexColor('#475569'),
        alignment=1,
        spaceAfter=15
    )

    h1_style = ParagraphStyle(
        'Heading1_Custom',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=13,
        leading=17,
        textColor=colors.HexColor('#0369a1'),
        spaceBefore=12,
        spaceAfter=8,
        keepWithNext=True
    )

    h2_style = ParagraphStyle(
        'Heading2_Custom',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=11,
        leading=15,
        textColor=colors.HexColor('#1e293b'),
        spaceBefore=8,
        spaceAfter=4,
        keepWithNext=True
    )

    body_style = ParagraphStyle(
        'Body_Custom',
        parent=styles['BodyText'],
        fontName='Helvetica',
        fontSize=9.5,
        leading=13.5,
        textColor=colors.HexColor('#334155'),
        spaceAfter=6
    )

    bullet_style = ParagraphStyle(
        'Bullet_Custom',
        parent=body_style,
        leftIndent=15,
        bulletIndent=5,
        spaceAfter=3
    )

    table_cell_style = ParagraphStyle(
        'TableCell',
        parent=body_style,
        fontSize=8.5,
        leading=11.5
    )

    table_header_style = ParagraphStyle(
        'TableHeader',
        parent=body_style,
        fontName='Helvetica-Bold',
        fontSize=8.5,
        leading=11.5,
        textColor=colors.white
    )

    story = []

    # TITRE & EN-TÊTE
    story.append(Paragraph("PLAN TECHNIQUE & RÉPARTITION PRATIQUE", title_style))
    story.append(Paragraph("Système d'Irrigation Intelligent TinyML sur STM32 & Fog Computing<br/><b>Mode : 100% Simulation | Durée : Sprint de 3 Semaines | Équipe de 3 Personnes</b>", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#0284c7'), spaceAfter=12))

    # SECTION 1 : CADRAGE TECHNIQUE DU SPRINT (3 SEMAINES)
    story.append(Paragraph("1. Cadrage du Projet en Simulation (3 Semaines)", h1_style))
    story.append(Paragraph(
        "Ce projet implémente une chaîne complète d'<b>Edge AI / TinyML</b> pour l'irrigation agricole de précision. "
        "Le système fonctionne <b>100% en simulation</b> sur un jeu de données (dataset du professeur), "
        "éliminant les aléas de câblage physique pour se concentrer sur l'ingénierie embarquée, l'évaluation IA et la supervision Fog.",
        body_style
    ))

    # TABLEAU DES PARAMÈTRES
    cadrage_data = [
        [Paragraph("<b>Paramètre</b>", table_header_style), Paragraph("<b>Spécification Technique</b>", table_header_style), Paragraph("<b>Objectif Évalué</b>", table_header_style)],
        [Paragraph("<b>Microcontrôleur Cible</b>", table_cell_style), Paragraph("STM32 Nucleo-F401RE (ARM Cortex-M4 @ 84 MHz, FPU)", table_cell_style), Paragraph("Exécution déterministe en C pur sous STM32CubeIDE", table_cell_style)],
        [Paragraph("<b>Intelligence Artificielle</b>", table_cell_style), Paragraph("TinyML (Arbre de Décision / Random Forest / MLP)", table_cell_style), Paragraph("Précision > 95%, latence < 1 µs, 0 octet de malloc", table_cell_style)],
        [Paragraph("<b>Supervision Fog</b>", table_cell_style), Paragraph("Broker MQTT Mosquitto + Tableau de bord Node-RED", table_cell_style), Paragraph("Visualisation temps réel et télé-métrie périodique", table_cell_style)],
        [Paragraph("<b>Indicateur Clé (KPI)</b>", table_cell_style), Paragraph("Comparaison 30 jours : Seuil Fixe vs Edge AI", table_cell_style), Paragraph("Démonstration chiffrée du gain d'eau (20 à 30%)", table_cell_style)],
    ]
    t_cadrage = Table(cadrage_data, colWidths=[120, 230, 169])
    t_cadrage.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#0284c7')),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1')),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#f8fafc')]),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(t_cadrage)
    story.append(Spacer(1, 10))

    # SECTION 2 : FICHES DE POSTE TECHNIQUES (LES 3 MEMBRES)
    story.append(Paragraph("2. Fiches de Rôle Pratiques (Attribution des Responsabilités)", h1_style))

    # MEMBRE 1
    story.append(Paragraph("👤 MEMBRE 1 (TOI) : Ingénieur Embarqué & Edge AI (STM32)", h2_style))
    story.append(Paragraph("<b>Mission :</b> Faire tourner l'IA dans la cible Cortex-M4, orchestrer la boucle de contrôle et mesurer la performance matérielle.", body_style))
    story.append(Paragraph("• <b>Projet C STM32CubeIDE :</b> Initialisation de la cible F401RE, configuration de l'horloge à 84 MHz et port série virtuel ST-Link.", bullet_style))
    story.append(Paragraph("• <b>Intégration Modèle C :</b> Intégration de <code>tinyml_model.h</code> (reçu du M2), validation de l'inférence en C pur sans bibliothèque externe.", bullet_style))
    story.append(Paragraph("• <b>Injection des Scénarios :</b> Module d'injection de vecteurs de test (canicule, nuit, pluie) via <code>simulation_test_vectors.h</code>.", bullet_style))
    story.append(Paragraph("• <b>Garde-Fou de Sécurité :</b> Implémentation du coupe-circuit automatique arrêtant la pompe après 30s max en cas d'erreur de prédiction.", bullet_style))
    story.append(Paragraph("• <b>Mesures Matérielles :</b> Mesure du temps d'inférence en cycles d'horloge CPU avec le registre matériel <code>DWT->CYCCNT</code> et relevé Flash/RAM.", bullet_style))
    story.append(Spacer(1, 6))

    # MEMBRE 2
    story.append(Paragraph("👤 MEMBRE 2 : Data Scientist & Ingénieur Machine Learning", h2_style))
    story.append(Paragraph("<b>Mission :</b> Exploiter le dataset du professeur, entraîner les modèles, évaluer la précision et exporter le modèle C optimisé.", body_style))
    story.append(Paragraph("• <b>Traitement des Données :</b> Nettoyage du dataset, normalisation, matrice de corrélation humidité/température/heure sous Python (Pandas).", bullet_style))
    story.append(Paragraph("• <b>Entraînement Multi-Modèles :</b> Comparaison rigoureuse de 3 architectures : Arbre de Décision, Random Forest et Réseau Dense (MLP).", bullet_style))
    story.append(Paragraph("• <b>Validation Statistique :</b> Matrice de confusion, courbes ROC, précision, rappel et F1-score (analyse des faux positifs vs faux négatifs).", bullet_style))
    story.append(Paragraph("• <b>Export TinyML C :</b> Quantification <code>int8</code> et génération automatique du fichier d'en-tête C à transmettre au Membre 1.", bullet_style))
    story.append(Spacer(1, 6))

    # MEMBRE 3
    story.append(Paragraph("👤 MEMBRE 3 : Fog Computing, Supervision & Benchmark Écologique", h2_style))
    story.append(Paragraph("<b>Mission :</b> Simuler le cycle complet de l'environnement, superviser via MQTT et prouver le gain d'économie d'eau de l'IA.", body_style))
    story.append(Paragraph("• <b>Simulateur Environnemental :</b> Script Python simulant 30 jours météo continus avec assèchement et cycles diurnes.", bullet_style))
    story.append(Paragraph("• <b>Passerelle & Supervision :</b> Déploiement du broker MQTT local (Mosquitto) et création d'un tableau de bord visuel sous Node-RED ou Grafana.", bullet_style))
    story.append(Paragraph("• <b>Benchmark d'Irrigation :</b> Comparaison chiffrée Seuil Fixe (25%) vs Edge AI : calcul des Litres d'eau économisés et des cycles pompe évités.", bullet_style))

    story.append(PageBreak())

    # SECTION 3 : PLANNING GANTT SUR 3 SEMAINES
    story.append(Paragraph("3. Planning Synchronisé du Sprint (3 Semaines)", h1_style))
    story.append(Paragraph(
        "Ce planning sur 21 jours garantit une synchronisation parfaite entre les 3 membres : chaque livrable alimente directement l'étape suivante.",
        body_style
    ))
    story.append(Image(gantt_img, width=520, height=230))
    story.append(Spacer(1, 10))

    # DETAIL DES 3 SEMAINES
    weeks_data = [
        [Paragraph("<b>Semaine</b>", table_header_style), Paragraph("<b>Membre 1 (Toi - STM32)</b>", table_header_style), Paragraph("<b>Membre 2 (Data / IA)</b>", table_header_style), Paragraph("<b>Membre 3 (Fog / Simu)</b>", table_header_style)],
        [
            Paragraph("<b>SEMAINE 1</b><br/><i>Mise en place</i>", table_cell_style),
            Paragraph("Projet STM32CubeIDE configuré, boucle de simulation testée avec vecteurs statiques.", table_cell_style),
            Paragraph("Nettoyage du dataset prof, analyse exploratoire, premier arbre de décision de base.", table_cell_style),
            Paragraph("Développement du simulateur météo 30 jours et installation broker Mosquitto.", table_cell_style)
        ],
        [
            Paragraph("<b>SEMAINE 2</b><br/><i>Intégration</i>", table_cell_style),
            Paragraph("Intégration de <code>tinyml_model.h</code>, ajout du watchdog 30s, premières mesures DWT.", table_cell_style),
            Paragraph("Benchmark complet (DecisionTree vs RF vs MLP), matrice de confusion, export C final.", table_cell_style),
            Paragraph("Connexion flux MQTT, dashboard Node-RED, enregistrement des cycles d'arrosage.", table_cell_style)
        ],
        [
            Paragraph("<b>SEMAINE 3</b><br/><i>Validation & Fin</i>", table_cell_style),
            Paragraph("Relevé officiel Flash/RAM via fichier .map, stress-test et validation latence < 1 µs.", table_cell_style),
            Paragraph("Validation croisée sur données inconnues, rédaction de la fiche d'évaluation IA.", table_cell_style),
            Paragraph("Calcul final du gain d'eau (Litres et %), rapport d'économie d'eau et répétition.", table_cell_style)
        ],
    ]
    t_weeks = Table(weeks_data, colWidths=[75, 145, 150, 149])
    t_weeks.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#0284c7')),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1')),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#f8fafc')]),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(t_weeks)

    story.append(PageBreak())

    # SECTION 4 : RÉSULTATS PRÉLIMINAIRES & BENCHMARKS DE SIMULATION
    story.append(Paragraph("4. Résultats Expérimentaux & Données de Référence", h1_style))
    story.append(Paragraph(
        "Les modèles et scripts de simulation ont été exécutés avec succès. Voici les métriques obtenues qui serviront de base chiffrée pour le projet :",
        body_style
    ))

    story.append(Paragraph("A. Évaluation des Algorithmes de Machine Learning (Membre 2)", h2_style))
    story.append(Image(ml_img, width=520, height=195))
    story.append(Spacer(1, 8))

    story.append(Paragraph("B. Simulation Écologique : Économie d'Eau sur 30 Jours (Membre 3)", h2_style))
    if os.path.exists(bench_water_img):
        story.append(Image(bench_water_img, width=520, height=260))
    story.append(Spacer(1, 8))

    # SYNTHÈSE DES GAINS
    story.append(Paragraph(
        "<b>Bilan du Benchmark :</b> Le système Edge AI évite les arrosages inutiles en journée (forte évaporation sous le soleil) "
        "et privilégie les arrosages d'appoint optimaux aux heures fraîches. "
        "Sur la simulation de référence, le gain d'eau constaté est net tout en maintenant le sol dans une plage d'hydratation idéale pour la plante.",
        body_style
    ))

    # Construction du document
    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"[SUCCÈS] Document PDF généré : {PDF_PATH}")
    return PDF_PATH

if __name__ == "__main__":
    build_pdf()
