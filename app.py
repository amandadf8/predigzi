from flask import Flask, render_template, request
import pandas as pd
import random
import os
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

app = Flask(__name__)

# ==========================
# LOAD DATASET
# ==========================

df = pd.read_csv("menu_mbg_level3.csv")

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
# VISUALISASI DATASET
# ==========================

def generate_dataset_charts():

    os.makedirs("static/charts", exist_ok=True)

    # Histogram Kalori
    plt.figure(figsize=(8, 5))
    plt.hist(df["energy_kcal"], bins=20)
    plt.title("Distribusi Kalori Menu")
    plt.xlabel("Kalori (kkal)")
    plt.ylabel("Jumlah Menu")
    plt.tight_layout()
    plt.savefig("static/charts/distribusi_kalori.png")
    plt.close()

    # Top Karbo
    top_karbo = df["karbo"].value_counts().head(10)

    plt.figure(figsize=(8, 5))
    top_karbo.plot(kind="bar")
    plt.title("Top 10 Karbohidrat")
    plt.ylabel("Jumlah")
    plt.tight_layout()
    plt.savefig("static/charts/top_karbo.png")
    plt.close()

    # Top Protein
    top_protein = df["protein"].value_counts().head(10)

    plt.figure(figsize=(8, 5))
    top_protein.plot(kind="bar")
    plt.title("Top 10 Protein")
    plt.ylabel("Jumlah")
    plt.tight_layout()
    plt.savefig("static/charts/top_protein.png")
    plt.close()

    # Top Sayur
    top_sayur = df["sayur"].value_counts().head(10)

    plt.figure(figsize=(8, 5))
    top_sayur.plot(kind="bar")
    plt.title("Top 10 Sayur")
    plt.ylabel("Jumlah")
    plt.tight_layout()
    plt.savefig("static/charts/top_sayur.png")
    plt.close()

    # Scatter Plot
    plt.figure(figsize=(8, 5))
    plt.scatter(
        df["protein_g"],
        df["energy_kcal"]
    )

    plt.xlabel("Protein (g)")
    plt.ylabel("Kalori (kkal)")
    plt.title("Protein vs Kalori")
    plt.tight_layout()
    plt.savefig("static/charts/scatter_protein_kalori.png")
    plt.close()


# Jalankan sekali saat startup
generate_dataset_charts()

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
# GENERATE JADWAL
# ==========================

def generate_schedule(level):

    kandidat = filter_menu(level)

    if len(kandidat) == 0:
        return {}

    kandidat = kandidat.sample(
        min(len(kandidat), 72),
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
                    "score": round(random.uniform(0.90, 1.00), 2),

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

    schedule = generate_schedule(level)

    return render_template(
        "index.html",
        schedule=schedule,
        selected_level=level,
        dataset_info=dataset_info
    )


# ==========================
# RUN APP
# ==========================

if __name__ == "__main__":
    app.run(debug=True)