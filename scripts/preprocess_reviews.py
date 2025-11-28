import pandas as pd
import os

# Load raw data
df = pd.read_csv("data/raw_reviews.csv")
print(f"Initial rows: {len(df)}")

# Remove rows with no review text
df = df.dropna(subset=["review"])

# Remove duplicate reviews
df = df.drop_duplicates(subset=["review"])

# Normalize date format
df["date"] = pd.to_datetime(df["date"], errors="coerce")
df = df.dropna(subset=["date"])
df["date"] = df["date"].dt.strftime("%Y-%m-%d")

# Keep only required columns
df = df[["review", "rating", "date", "bank", "source"]]
print(f"Cleaned rows: {len(df)}")

# Save cleaned data
os.makedirs("data", exist_ok=True)
df.to_csv("data/clean_reviews.csv", index=False)

print("✅ Data cleaning complete! Cleaned data saved to data/clean_reviews.csv")