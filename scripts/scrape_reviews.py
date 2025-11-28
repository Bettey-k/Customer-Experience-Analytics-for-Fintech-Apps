from google_play_scraper import Sort, reviews
import pandas as pd
import os
import time

# Correct app IDs
apps = {
    "CBE": "com.combanketh.mobilebanking",
    "BOA": "com.boa.boaMobileBanking",
    "Dashen": "com.cr2.amolelight"
}

all_reviews = []

for bank, app_id in apps.items():
    print(f"\n🔍 Scraping reviews for {bank}...")

    try:
        scraped, _ = reviews(
            app_id,
            lang="en",
            country="et",    # Ethiopian region
            count=600,       # LIMIT to 600 reviews only
            sort=Sort.NEWEST
        )

        print(f"   ✔ {len(scraped)} reviews scraped for {bank}")

        for r in scraped:
            all_reviews.append({
                "review": r.get("content"),
                "rating": r.get("score"),
                "date": r.get("at"),
                "bank": bank,
                "source": "Google Play"
            })

        time.sleep(1)

    except Exception as e:
        print(f"   ❌ Error scraping {bank}: {e}")

# Save results
os.makedirs("data", exist_ok=True)

df = pd.DataFrame(all_reviews)
df.to_csv("data/raw_reviews.csv", index=False)

print(f"\n🎉 Done! Total {len(df)} reviews saved to data/raw_reviews.csv")
