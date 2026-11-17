#!/usr/bin/env python3
"""
Pipeline d'entraînement TinyML basé sur les données Copernicus du SOUSS (Membre 2).
Entraîne les modèles sur les variables climatiques réelles (T, Humidité, Vent, Rayonnement, ET0).
Génère le header C 'tinyml_model_souss.h' prêt pour la STM32 (Membre 1).
"""

import os
import sys
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.neural_network import MLPClassifier
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score

DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "copernicus_souss_climate_data.csv")
EXPORT_C_PATH = os.path.join(os.path.dirname(__file__), "..", "firmware_stm32", "Drivers_Custom", "Inc", "tinyml_model_souss.h")

def export_tree_to_c(tree, feature_names, output_path):
    from sklearn.tree import _tree
    tree_ = tree.tree_
    feature_name = [
        feature_names[i] if i != _tree.TREE_UNDEFINED else "undefined!"
        for i in tree_.feature
    ]

    c_code = []
    c_code.append("/**\n * @file tinyml_model_souss.h\n")
    c_code.append(" * @brief Modèle TinyML pour la région du SOUSS (Données Copernicus ERA5 / FAO-56)\n")
    c_code.append(" * @details Généré pour STM32 Nucleo-F401RE (0 allocation dynamique, exécution < 1 µs)\n */\n\n")
    c_code.append("#ifndef TINYML_MODEL_SOUSS_H_\n#define TINYML_MODEL_SOUSS_H_\n\n#include <stdint.h>\n\n")
    c_code.append("/**\n * Prédit le besoin d'arrosage dans la région du Souss\n")
    for f in feature_names:
        c_code.append(f" * @param {f}\n")
    c_code.append(" * @return uint8_t 1 = Arrosage Requis, 0 = Pas d'arrosage\n */\n")

    args = ", ".join([f"float {f}" for f in feature_names])
    c_code.append(f"static inline uint8_t tinyml_predict_souss_irrigation({args}) {{\n")

    def recurse(node, depth):
        indent = "    " * depth
        if tree_.feature[node] != _tree.TREE_UNDEFINED:
            name = feature_name[node]
            threshold = tree_.threshold[node]
            c_code.append(f"{indent}if ({name} <= {threshold:.4f}f) {{\n")
            recurse(tree_.children_left[node], depth + 1)
            c_code.append(f"{indent}}} else {{\n")
            recurse(tree_.children_right[node], depth + 1)
            c_code.append(f"{indent}}}\n")
        else:
            val = tree_.value[node][0]
            pred_class = int(np.argmax(val))
            c_code.append(f"{indent}return {pred_class};\n")

    recurse(0, 1)
    c_code.append("}\n\n#endif /* TINYML_MODEL_SOUSS_H_ */\n")

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.writelines(c_code)
    print(f"[OK] Header C généré avec succès dans : {output_path}")

def train_souss_models():
    if not os.path.exists(DATA_PATH):
        print(f"Téléchargement préalable des données Copernicus Souss...")
        from download_copernicus_souss import fetch_souss_copernicus_data
        fetch_souss_copernicus_data()

    df = pd.read_csv(DATA_PATH)
    print(f"Chargement des données Copernicus Souss ({len(df)} jours)...")

    # Features climatiques requises par le professeur
    feature_cols = [
        "temp_mean_c",
        "humidity_mean_pct",
        "wind_speed_max_ms",
        "solar_radiation_mj",
        "et0_fao_mm"
    ]
    target_col = "water_required"

    X = df[feature_cols]
    y = df[target_col]

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=42, stratify=y)

    print("\n--- 1. Entraînement de l'Arbre de Décision TinyML (Cible STM32) ---")
    dt = DecisionTreeClassifier(max_depth=4, min_samples_leaf=8, random_state=42)
    dt.fit(X_train, y_train)
    y_pred_dt = dt.predict(X_test)
    acc_dt = accuracy_score(y_test, y_pred_dt)
    print(f"Accuracy Arbre de Décision : {acc_dt*100:.2f} %")
    print("Matrice de confusion :")
    print(confusion_matrix(y_test, y_pred_dt))
    print(classification_report(y_test, y_pred_dt, target_names=["Pas d'arrosage", "Arrosage requis"]))

    print("\n--- 2. Random Forest (Comparatif) ---")
    rf = RandomForestClassifier(n_estimators=50, max_depth=5, random_state=42)
    rf.fit(X_train, y_train)
    print(f"Accuracy Random Forest : {accuracy_score(y_test, rf.predict(X_test))*100:.2f} %")

    print("\n--- 3. Réseau de Neurones MLP (Comparatif) ---")
    mlp = MLPClassifier(hidden_layer_sizes=(16, 8), max_iter=500, random_state=42)
    mlp.fit(X_train, y_train)
    print(f"Accuracy MLP : {accuracy_score(y_test, mlp.predict(X_test))*100:.2f} %")

    # Export C pur pour la STM32 (Membre 1)
    export_tree_to_c(dt, feature_cols, EXPORT_C_PATH)

if __name__ == "__main__":
    train_souss_models()
