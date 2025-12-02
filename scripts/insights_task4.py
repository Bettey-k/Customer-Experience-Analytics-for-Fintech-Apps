import os
import glob
import ast
from collections import Counter
from datetime import datetime

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# ---------- CONFIG ----------
DATA_DIR = os.path.join("data")
VIS_DIR = os.path.join("visualizations")

os.makedirs(VIS_DIR, exist_ok=True)

sns.set_theme(style="whitegrid")


# ---------- DATA LOADING ----------

def get_latest_analyzed_file(data_dir: str = DATA_DIR) -> str:
    """Find the latest analyzed_reviews_*.csv file in data/."""
    pattern = os.path.join(data_dir, "analyzed_reviews_*.csv")
    files = glob.glob(pattern)
    if not files:
        raise FileNotFoundError(f"No analyzed_reviews_*.csv found in {data_dir}")
    # sort by modified time, pick latest
    files.sort(key=os.path.getmtime, reverse=True)
    return files[0]


def parse_themes(x):
    """Safely parse theme strings into Python lists."""
    if x is None:
        return []
    if isinstance(x, float):  # catches NaN
        return []
    if isinstance(x, list):
        return x
    if not isinstance(x, str):
        return []

    x = x.strip()
    if x == "" or x == "[]":
        return []

    # Try literal_eval first
    try:
        result = ast.literal_eval(x)
        if isinstance(result, list):
            return result
    except Exception:
        pass

    # Fallback: manual split
    try:
        cleaned = x.strip("[]")
        parts = [p.strip().strip("'").strip('"') for p in cleaned.split(",")]
        return [p for p in parts if p]
    except Exception:
        return []


def load_data() -> pd.DataFrame:
    """Load the latest analyzed reviews CSV and prepare columns."""
    csv_path = get_latest_analyzed_file()
    print(f"Using analyzed file: {csv_path}")
    df = pd.read_csv(csv_path)

    # Ensure date is datetime
    df["date"] = pd.to_datetime(df["date"])

    # Parse themes into lists
    df["themes"] = df["themes"].apply(parse_themes)

    return df


# ---------- INSIGHT FUNCTIONS ----------

def top_themes(df: pd.DataFrame, bank: str, sentiment: str | None = None, n: int = 5):
    """Return top N themes for a bank, optionally filtered by sentiment."""
    temp = df[df["bank"] == bank]
    if sentiment:
        temp = temp[temp["sentiment"].str.upper() == sentiment.upper()]

    theme_list = []
    for t_list in temp["themes"]:
        if isinstance(t_list, list):
            theme_list.extend(t_list)

    if not theme_list:
        return []

    return Counter(theme_list).most_common(n)


def compute_bank_metrics(df: pd.DataFrame) -> pd.DataFrame:
    """Compute per-bank metrics: avg rating, avg sentiment, review_count."""
    grouped = df.groupby("bank").agg(
        avg_rating=("rating", "mean"),
        avg_sentiment=("sentiment_score", "mean"),
        review_count=("review", "count"),
    )
    return grouped.sort_values("review_count", ascending=False).reset_index()


# ---------- PLOTTING FUNCTIONS ----------

def plot_sentiment_distribution(df: pd.DataFrame):
    """Plot count of sentiment per bank."""
    plt.figure(figsize=(10, 6))
    sns.countplot(data=df, x="bank", hue="sentiment")
    plt.title("Sentiment Distribution per Bank")
    plt.xlabel("Bank")
    plt.ylabel("Number of Reviews")
    plt.xticks(rotation=30, ha="right")
    plt.tight_layout()

    out_path = os.path.join(VIS_DIR, "sentiment_distribution_per_bank.png")
    plt.savefig(out_path)
    plt.close()
    print(f"Saved: {out_path}")


def plot_rating_distribution(df: pd.DataFrame):
    """Plot overall rating distribution."""
    plt.figure(figsize=(8, 5))
    sns.histplot(data=df, x="rating", bins=5, kde=True)
    plt.title("Overall Rating Distribution")
    plt.xlabel("Rating")
    plt.ylabel("Count")
    plt.tight_layout()

    out_path = os.path.join(VIS_DIR, "rating_distribution.png")
    plt.savefig(out_path)
    plt.close()
    print(f"Saved: {out_path}")


def plot_sentiment_trend(df: pd.DataFrame, bank: str):
    """Plot sentiment score trend over time for a single bank."""
    temp = df[df["bank"] == bank].copy()
    if temp.empty:
        print(f"No data for bank: {bank}")
        return

    temp["month"] = temp["date"].dt.to_period("M")
    trend = temp.groupby("month")["sentiment_score"].mean()

    plt.figure(figsize=(9, 4))
    trend.index = trend.index.to_timestamp()
    plt.plot(trend.index, trend.values, marker="o")
    plt.title(f"Sentiment Trend Over Time - {bank}")
    plt.xlabel("Month")
    plt.ylabel("Average Sentiment Score")
    plt.tight_layout()

    filename = f"sentiment_trend_{bank.lower().replace(' ', '_')}.png"
    out_path = os.path.join(VIS_DIR, filename)
    plt.savefig(out_path)
    plt.close()
    print(f"Saved: {out_path}")


def plot_top_themes(df: pd.DataFrame, bank: str, sentiment: str | None = None):
    """Barplot of top 10 themes for a bank (optionally filtered by sentiment)."""
    tt = top_themes(df, bank, sentiment=sentiment, n=10)
    if not tt:
        print(f"No themes for bank: {bank} (sentiment={sentiment})")
        return

    labels, counts = zip(*tt)

    plt.figure(figsize=(9, 5))
    sns.barplot(x=list(counts), y=list(labels))
    title = f"Top Themes - {bank}"
    if sentiment:
        title += f" ({sentiment.title()})"
    plt.title(title)
    plt.xlabel("Count")
    plt.ylabel("Theme")
    plt.tight_layout()

    sentiment_tag = sentiment.lower() if sentiment else "all"
    filename = f"top_themes_{bank.lower().replace(' ', '_')}_{sentiment_tag}.png"
    out_path = os.path.join(VIS_DIR, filename)
    plt.savefig(out_path)
    plt.close()
    print(f"Saved: {out_path}")


# ---------- MAIN TASK-4 PIPELINE ----------

def main():
    df = load_data()

    print("\n=== Per-bank metrics ===")
    metrics = compute_bank_metrics(df)
    print(metrics.to_string(index=False))

    banks = metrics["bank"].tolist()

    # Drivers & pain points per bank
    print("\n=== Drivers & Pain Points (by themes) ===")
    for bank in banks:
        drivers = top_themes(df, bank, sentiment="POSITIVE", n=5)
        pains = top_themes(df, bank, sentiment="NEGATIVE", n=5)

        print(f"\nBank: {bank}")
        print(f"  Drivers (POSITIVE themes): {drivers}")
        print(f"  Pain points (NEGATIVE themes): {pains}")

    # Required plots (3–5):
    plot_sentiment_distribution(df)
    plot_rating_distribution(df)

    # Sentiment trend + themes for first 1–2 banks (for evidence)
    for bank in banks[:2]:
        plot_sentiment_trend(df, bank)
        plot_top_themes(df, bank, sentiment="POSITIVE")
        plot_top_themes(df, bank, sentiment="NEGATIVE")

    print("\nTask 4 insights and visualizations generated successfully.")


if __name__ == "__main__":
    main()
