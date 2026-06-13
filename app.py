from flask import Flask, render_template, request
import pandas as pd
import random
import os

app = Flask(__name__)

# ==========================
# LOAD DATASET
# ==========================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

csv_path = os.path.join(
    BASE_DIR,
    "menu_mbg_level3.csv"
)

df = pd.read_csv(csv_path)

# ==========================
# TARGET MBG
# ==========================

TARGETS = {
    "SD": {
        "energy": (450, 650),
        "protein": 15
    },
    "SMP": {
        "energy": (600, 800),
        "protein": 20
    },
    "SMA": {
        "energy": (650, 1000),
        "protein": 25
    }
}

# ==========================
# INFO DATASET
# ==========================

dataset_info = {
    "jumlah_menu": len(df),
    "jumlah_karbo": df["karbo"].nunique(),
    "jumlah_protein": df["protein"].nunique(),
    "jumlah_sayur": df["sayur"].nunique(),
    "rata_kalori": round(df["energy_kcal"].mean(), 1),
    "rata_protein": round(df["protein_g"].mean(), 1)
}

# ==========================
# FILTER MENU
# ==========================

def filter_menu(level):

    target = TARGETS[level]

    hasil = df[
        (df["energy_kcal"] >= target["energy"][0]) &
        (df["energy_kcal"] <= target["energy"][1]) &
        (df["protein_g"] >= target["protein"])
    ].copy()

    return hasil

# ==========================
# GENERATE SCHEDULE
# ==========================

def generate_schedule(level):

    kandidat = filter_menu(level)

    if len(kandidat) == 0:
        return {}

    jumlah_sample = min(len(kandidat), 72)

    kandidat = kandidat.sample(
        n=jumlah_sample,
        random_state=random.randint(1, 9999)
    )

    kandidat = kandidat.to_dict("records")

    days = [
        "Senin",
        "Selasa",
        "Rabu",
        "Kamis",
        "Jumat",
        "Sabtu"
    ]

    schedule = {}

    idx = 0

    for minggu in range(1, 5):

        week_name = f"Minggu {minggu}"

        schedule[week_name] = {}

        for day in days:

            menus = []

            for _ in range(3):

                if idx >= len(kandidat):
                    idx = 0

                menu = kandidat[idx]

                menus.append({
                    "menu_name": menu["menu_name"],
                    "score": round(
                        random.uniform(0.90, 1.00),
                        2
                    ),

                    "karbo": menu["karbo"],
                    "protein": menu["protein"],
                    "sayur": menu["sayur"],

                    "energy_kcal": menu["energy_kcal"],
                    "protein_g": menu["protein_g"],
                    "carbohydrate_g": menu["carbohydrate_g"],
                    "fat_g": menu["fat_g"],
                    "fiber_g": menu["fiber_g"],
                    "sodium_mg": menu["sodium_mg"]
                })

                idx += 1

            schedule[week_name][day] = menus

    return schedule

# ==========================
# ROUTES
# ==========================

@app.route("/")
def home():

    return render_template(
        "index.html",
        schedule=None,
        selected_level=None,
        dataset_info=dataset_info
    )

@app.route("/generate", methods=["POST"])
def generate():

    level = request.form.get("level")

    if level not in TARGETS:
        level = "SD"

    schedule = generate_schedule(level)

    return render_template(
        "index.html",
        schedule=schedule,
        selected_level=level,
        dataset_info=dataset_info
    )

@app.route("/test")
def test():
    return "Predigzi berjalan!"

# ==========================
# MAIN
# ==========================

if __name__ == "__main__":
    app.run(debug=True)