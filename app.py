import base64
import io
from pathlib import Path
import hashlib

import dash
from dash import html, dcc, Input, Output
import pandas as pd

import matplotlib as mpl
mpl.use("Agg")

import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
from PIL import Image

# Mindre text så det passar med mockupbilden
mpl.rcParams.update({
    "font.size": 8,
    "axes.titlesize": 8,
    "axes.labelsize": 7,
    "xtick.labelsize": 7,
    "ytick.labelsize": 7,
    "legend.fontsize": 6,
})

# Sökväg till externa filer
BASE_DIR = Path(__file__).parent
ASSETS_DIR = BASE_DIR / "assets"

# Läs in data från externa filer
athletes = pd.read_csv(ASSETS_DIR / "athlete_events.csv")
regions = pd.read_csv(ASSETS_DIR / "noc_regions.csv")

# Slå ihop data för att få regionsnamn
df = athletes.merge(regions[["NOC", "region"]], on="NOC", how="left")

jpn = df[df["NOC"] == "JPN"].copy()

# Anonymisera namn (SHA-256)
def sha256_name(name: str) -> str:
    if pd.isna(name) or name is None:
        return ""
    return hashlib.sha256(str(name).encode("utf-8")).hexdigest()

jpn["Name_hash"] = jpn["Name"].apply(sha256_name)

# Medalj-rader enkelt filter för att minska dubblering
jpn_medals = (
    jpn[jpn["Medal"].notna()]
    .drop_duplicates(subset=["Games", "Event", "Medal", "ID"])
    .copy()
)

# Art Competitions

art = df[df["Sport"] == "Art Competitions"].copy()

art_medals = (
    art[art["Medal"].notna()]
    .drop_duplicates(subset=["NOC", "Games", "Event", "Medal"])
    .copy()
)

jpn_art_medals = art_medals[art_medals["NOC"] == "JPN"].copy()
jpn_art = art[art["NOC"] == "JPN"].copy()

# Judo + Taekwondo

sports_of_interest = ["Judo", "Taekwondo"]
df_js = df[df["Sport"].isin(sports_of_interest)].copy()

df_js_medals = (
    df_js[df_js["Medal"].notna()]
    .drop_duplicates(subset=["Games", "Event", "Medal", "ID"])
    .copy()
)

jpn_js_medals = df_js_medals[df_js_medals["NOC"] == "JPN"].copy()
jpn_js = df_js[df_js["NOC"] == "JPN"].copy()

# Lägga diagram på bildmockup

def plot_japan_medals_by_sport_top10():
    """Japan: Flest medaljer per sport (Top 10)"""
    sport_medals = (
        jpn_medals.groupby("Sport")["Medal"]
        .count()
        .sort_values(ascending=False)
        .head(10)
    )

    fig, ax = plt.subplots(figsize=(4.0, 2.6), dpi=150)
    ax.bar(range(len(sport_medals)), sport_medals.values)
    ax.set_title("Japan: Flest medaljer per sport (Top 10)")
    ax.set_xticks(range(len(sport_medals)))
    ax.set_xticklabels(sport_medals.index, rotation=60, ha="right")
    ax.yaxis.set_major_locator(MaxNLocator(integer=True))
    ax.grid(axis="y", alpha=0.3)
    fig.tight_layout()
    return fig


def plot_japan_medals_over_time_by_season():
    
    medals_per_games = (
        jpn_medals.groupby(["Year", "Season"])["Medal"]
        .count()
        .reset_index(name="Antal medaljer")
    )

    pivot = (
        medals_per_games.pivot(index="Year", columns="Season", values="Antal medaljer")
        .fillna(0)
        .sort_index()
    )

    fig, ax = plt.subplots(figsize=(4.0, 2.6), dpi=150)

    years = pivot.index.values
    seasons = [c for c in ["Summer", "Winter"] if c in pivot.columns] + [c for c in pivot.columns if c not in ["Summer", "Winter"]]
    width = 0.4

    for i, season in enumerate(seasons):
        ax.bar(years + (i - (len(seasons)-1)/2) * width, pivot[season].values, width=width, label=season)

    ax.set_title("Japan: Antal medaljer per år (Sommar/Vinter)")
    ax.yaxis.set_major_locator(MaxNLocator(integer=True))
    ax.xaxis.set_major_locator(MaxNLocator(integer=True))
    ax.grid(axis="y", alpha=0.3)
    ax.legend(frameon=False)
    fig.tight_layout()
    return fig


def plot_japan_age_distribution_all():
 
    ages = jpn.dropna(subset=["Age"]).copy()["Age"]

    fig, ax = plt.subplots(figsize=(4.0, 2.6), dpi=150)
    ax.hist(ages, bins=25)
    ax.set_title("Japan: Åldersfördelning (alla deltagare)")
    ax.set_xlabel("Ålder")
    ax.set_ylabel("Antal")
    ax.yaxis.set_major_locator(MaxNLocator(integer=True))
    ax.grid(axis="y", alpha=0.3)
    fig.tight_layout()
    return fig


def plot_japan_top_sports_by_sex_top10():

    sex_sport = (
        jpn_medals.groupby(["Sex", "Sport"])["Medal"]
        .count()
        .reset_index(name="Antal medaljer")
    )

    # Top 10 sporter per kön
    top_m = sex_sport[sex_sport["Sex"] == "M"].sort_values("Antal medaljer", ascending=False).head(10)
    top_f = sex_sport[sex_sport["Sex"] == "F"].sort_values("Antal medaljer", ascending=False).head(10)

    # För att få en gemensam x-axel
    sports = list(dict.fromkeys(list(top_m["Sport"]) + list(top_f["Sport"])))
    m_map = dict(zip(top_m["Sport"], top_m["Antal medaljer"]))
    f_map = dict(zip(top_f["Sport"], top_f["Antal medaljer"]))

    m_vals = [m_map.get(s, 0) for s in sports]
    f_vals = [f_map.get(s, 0) for s in sports]

    fig, ax = plt.subplots(figsize=(4.0, 2.6), dpi=150)
    x = range(len(sports))
    ax.bar(x, m_vals, label="Män", alpha=0.85)
    ax.bar(x, f_vals, bottom=m_vals, label="Kvinnor", alpha=0.65)

    ax.set_title("Japan: Medaljer per sport & kön (Top 10/kön)")
    ax.set_xticks(list(x))
    ax.set_xticklabels(sports, rotation=60, ha="right")
    ax.yaxis.set_major_locator(MaxNLocator(integer=True))
    ax.grid(axis="y", alpha=0.3)
    ax.legend(frameon=False)
    fig.tight_layout()
    return fig


def plot_japan_art_medals_per_year():

    art_medals_per_year = (
        jpn_art_medals.groupby("Year")["Medal"]
        .count()
        .reset_index(name="Antal medaljer")
        .sort_values("Year")
    )

    fig, ax = plt.subplots(figsize=(4.0, 2.6), dpi=150)
    ax.bar(art_medals_per_year["Year"].astype(int).astype(str), art_medals_per_year["Antal medaljer"])
    ax.set_title("Japan: Medaljer i Art Competitions per år")
    ax.set_xlabel("")
    ax.set_ylabel("")
    ax.yaxis.set_major_locator(MaxNLocator(integer=True))
    ax.grid(axis="y", alpha=0.3)
    ax.tick_params(axis="x", rotation=60)
    fig.tight_layout()
    return fig


def plot_judo_taekwondo_medals_over_time():
 
    medals_over_time = (
        jpn_js_medals.groupby(["Year", "Sport"])["Medal"]
        .count()
        .reset_index(name="Antal medaljer")
        .sort_values("Year")
    )

    pivot = (
        medals_over_time.pivot(index="Year", columns="Sport", values="Antal medaljer")
        .fillna(0)
        .sort_index()
    )

    fig, ax = plt.subplots(figsize=(4.0, 2.6), dpi=150)

    years = pivot.index.values
    sports = [c for c in ["Judo", "Taekwondo"] if c in pivot.columns] + [c for c in pivot.columns if c not in ["Judo", "Taekwondo"]]
    width = 0.4

    for i, sport in enumerate(sports):
        ax.bar(years + (i - (len(sports)-1)/2) * width, pivot[sport].values, width=width, label=sport)

    ax.set_title("Japan: Medaljer i Judo & Taekwondo per år")
    ax.yaxis.set_major_locator(MaxNLocator(integer=True))
    ax.xaxis.set_major_locator(MaxNLocator(integer=True))
    ax.grid(axis="y", alpha=0.3)
    ax.legend(frameon=False)
    fig.tight_layout()
    return fig


def plot_judo_taekwondo_top5_countries():

    top5 = (
        df_js_medals.groupby("NOC")["Medal"]
        .count()
        .sort_values(ascending=False)
        .head(5)
    )

    fig, ax = plt.subplots(figsize=(4.0, 2.6), dpi=150)
    ax.bar(range(len(top5)), top5.values)
    ax.set_title("Judo & Taekwondo: Topp 5 länder (medaljer)")
    ax.set_xticks(range(len(top5)))
    ax.set_xticklabels(top5.index, rotation=0)
    ax.yaxis.set_major_locator(MaxNLocator(integer=True))
    ax.grid(axis="y", alpha=0.3)
    fig.tight_layout()
    return fig


def plot_judo_taekwondo_age_distribution():

    ages = jpn_js.dropna(subset=["Age"])["Age"]

    fig, ax = plt.subplots(figsize=(4.0, 2.6), dpi=150)
    ax.hist(ages, bins=25)
    ax.set_title("Japan: Åldersfördelning i Judo & Taekwondo")
    ax.set_xlabel("Ålder")
    ax.set_ylabel("Antal")
    ax.yaxis.set_major_locator(MaxNLocator(integer=True))
    ax.grid(axis="y", alpha=0.3)
    fig.tight_layout()
    return fig


# Bildhanteringen
def fig_to_png_rgba(fig) -> Image.Image:
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=150, transparent=True)
    plt.close(fig)
    buf.seek(0)
    return Image.open(buf).convert("RGBA")


# Grafens placering på mockup-bilden
def compose_on_mockup(chart_img: Image.Image) -> str:

    base = Image.open(ASSETS_DIR / "mockup.png").convert("RGBA")

    # Skala grafen så den passar in i mockupen
    max_w = int(base.width * 0.75)
    max_h = int(base.height * 0.65)

    w, h = chart_img.size
    scale = min(max_w / w, max_h / h, 1.0)
    if scale < 1.0:
        chart_img = chart_img.resize(
            (int(w * scale), int(h * scale)),
            resample=Image.LANCZOS,
        )

    # Grafens position i höjd/sidled (+ = ner och - = upp)
    w, h = chart_img.size
    x = (base.width - w) // 2
    y = (base.height - h) // 2 - 100

    base.alpha_composite(chart_img, dest=(x, y))

    out_buf = io.BytesIO()
    base.save(out_buf, format="PNG")
    out_buf.seek(0)
    encoded = base64.b64encode(out_buf.read()).decode("ascii")
    return f"data:image/png;base64,{encoded}"


# -- DASH-APP -- #

app = dash.Dash(__name__)


def generate_src_for_view(view_value: str) -> str:

    if view_value == "jpn_medals_sport_top10":
        fig = plot_japan_medals_by_sport_top10()
    elif view_value == "jpn_medals_over_time_season":
        fig = plot_japan_medals_over_time_by_season()
    elif view_value == "jpn_age_distribution":
        fig = plot_japan_age_distribution_all()
    elif view_value == "jpn_top_sports_by_sex":
        fig = plot_japan_top_sports_by_sex_top10()
    elif view_value == "jpn_art_medals_per_year":
        fig = plot_japan_art_medals_per_year()
    elif view_value == "jpn_judo_tkd_over_time":
        fig = plot_judo_taekwondo_medals_over_time()
    elif view_value == "judo_tkd_top5_countries":
        fig = plot_judo_taekwondo_top5_countries()
    elif view_value == "jpn_judo_tkd_age":
        fig = plot_judo_taekwondo_age_distribution()
    else:
        fig = plot_japan_medals_by_sport_top10()

    chart_img = fig_to_png_rgba(fig)
    return compose_on_mockup(chart_img)


initial_src = generate_src_for_view("jpn_medals_sport_top10")

app.layout = html.Div(
    className="mockup-wrapper",
    children=[
        html.Div(
            className="controls",
            children=[
                html.H3(
                    "Japan i OS – Uppgift 1 & 2 (medaljer, ålder, sporter)",
                    className="title-text",
                ),
                dcc.Dropdown(
                    id="view-dropdown",
                    options=[
                        {"label": "Uppgift 1: Flest medaljer per sport (Top 10)", "value": "jpn_medals_sport_top10"},
                        {"label": "Uppgift 1: Medaljer per år (Sommar/Vinter)", "value": "jpn_medals_over_time_season"},
                        {"label": "Uppgift 1: Åldersfördelning (alla deltagare)", "value": "jpn_age_distribution"},
                        {"label": "Uppgift 1: Medaljer per sport & kön (Top 10/kön)", "value": "jpn_top_sports_by_sex"},
                        {"label": "Uppgift 1: Art Competitions – medaljer per år", "value": "jpn_art_medals_per_year"},
                        {"label": "Uppgift 2: Judo & Taekwondo – medaljer per år (Japan)", "value": "jpn_judo_tkd_over_time"},
                        {"label": "Uppgift 2: Judo & Taekwondo – topp 5 länder (medaljer)", "value": "judo_tkd_top5_countries"},
                        {"label": "Uppgift 2: Judo & Taekwondo – åldersfördelning (Japan)", "value": "jpn_judo_tkd_age"},
                    ],
                    value="jpn_medals_sport_top10",
                    clearable=False,
                ),
            ],
        ),
        html.Div(
            className="mockup-container",
            children=[
                html.Img(
                    id="mockup-with-chart",
                    className="mockup-img",
                    src=initial_src,
                    alt="Mockup med graf",
                )
            ],
        ),
    ],
)

# Callback
@app.callback(
    Output("mockup-with-chart", "src"),
    Input("view-dropdown", "value"),
)
def update_chart(view_value):
    return generate_src_for_view(view_value)


if __name__ == "__main__":
    app.run_server(debug=True)
