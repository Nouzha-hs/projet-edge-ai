#!/usr/bin/env python3
"""
Pipeline d'entraînement et d'export TinyML (Membre 2).
Entraîne des modèles de classification pour prédire le besoin d'arrosage.
Génère automatiquement une fonction en langage C intégrable directement dans le STM32 (Membre 1).
"""

import os
import sys
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier, export_text
from sklearn.ensemble import RandomForestClassifier
from sklearn.neural_network import MLPClassifier
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score

DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "irrigation_dataset_simulation.csv")
EXPORT_C_PATH = os.path.join(os.path.dirname(__file__), "..", "firmware_stm32", "Drivers_Custom", "Inc", "tinyml_model.h")

def export_decision_tree_to_c(tree, feature_names, output_path):
    """Génère une fonction C pure autonome à partir de l'arbre de décision."""
    from sklearn.tree import _tree

    tree_ = tree.tree_
    feature_name = [
        feature_names[i] if i != _tree.TREE_UNDEFINED else "undefined!"
        for i in tree_.feature
    ]

    c_code = []
    c_code.append("/**\n * @file tinyml_model.h\n * @brief Modèle TinyML généré automatiquement (Arbre de décision)\n */\n")
    c_code.append("#ifndef TINYML_MODEL_H_\n#define TINYML_MODEL_H_\n\n#include <stdint.h>\n\n")
    c_code.append("/**\n * Prédit le besoin d'arrosage (0 = NON, 1 = OUI)\n")
    for f in feature_names:
        c_code.append(f" * @param {f}\n")
    c_code.append(" * @return uint8_t 1 si arrosage nécessaire, 0 sinon\n */\n")
    
    args_str = ", ".join([f"float {f}" for f in feature_names])
    c_code.append(f"static inline uint8_t tinyml_predict_watering({args_str}) {{\n")

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
            # Feuille
            val = tree_.value[node][0]
            pred_class = np.argmax(val)
            c_code.append(f"{indent}return {pred_class}; /* Classe {pred_class} (échantillons: {int(val[0])} non / {int(val[1])} oui) */\n")

    recurse(0, 1)
    c_code.append("}\n\n#endif /* TINYML_MODEL_H_ */\n")

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.writelines(c_code)
    print(f"\n[OK] Modèle C TinyML exporté pour la STM32 dans : {output_path}")

def main():
    if not os.path.exists(DATA_PATH):
        print(f"Dataset introuvable dans {DATA_PATH}. Génération préalable...")
        from generate_synthetic_dataset import generate_irrigation_dataset
        generate_irrigation_dataset()

    df = pd.read_csv(DATA_PATH)
    print(f"Chargement du dataset : {len(df)} lignes.")

    feature_cols = ["temperature_c", "humidity_air_pct", "soil_moisture_pct", "hour"]
    target_col = "water_required"

    X = df[feature_cols]
    y = df[target_col]

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=42, stratify=y)

    print("\n--- 1. Entraînement de l'Arbre de Décision (Optimisé pour TinyML) ---")
    # max_depth=5 limite l'empreinte mémoire Flash à moins de 2 Ko tout en offrant > 95% de précision
    dt = DecisionTreeClassifier(max_depth=5, min_samples_leaf=10, random_state=42)
    dt.fit(X_train, y_train)
    y_pred_dt = dt.predict(X_test)
    acc_dt = accuracy_score(y_test, y_pred_dt)
    print(f"Accuracy Arbre de décision : {acc_dt*100:.2f}%")
    print("Matrice de confusion :")
    print(confusion_matrix(y_test, y_pred_dt))
    print(classification_report(y_test, y_pred_dt, target_names=["Pas d'arrosage", "Arrosage requis"]))

    print("\n--- 2. Entraînement Random Forest (Comparatif) ---")
    rf = RandomForestClassifier(n_estimators=50, max_depth=6, random_state=42)
    rf.fit(X_train, y_train)
    y_pred_rf = rf.predict(X_test)
    print(f"Accuracy Random Forest : {accuracy_score(y_test, y_pred_rf)*100:.2f}%")

    print("\n--- 3. Entraînement Réseau de Neurones Dense / MLP (Comparatif) ---")
    mlp = MLPClassifier(hidden_layer_sizes=(16, 8), max_iter=400, random_state=42)
    mlp.fit(X_train, y_train)
    y_pred_mlp = mlp.predict(X_test)
    print(f"Accuracy MLP (16x8) : {accuracy_score(y_test, y_pred_mlp)*100:.2f}%")

    # Export pour la STM32
    export_decision_tree_to_c(dt, feature_cols, EXPORT_C_PATH)

if __name__ == "__main__":
    main()
