import os
from pathlib import Path
import pandas as pd
import numpy as np
from transformers import pipeline
from langdetect import detect, DetectorFactory
from collections import Counter
import spacy
from datetime import datetime

# Set up paths
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data"
os.makedirs(DATA_DIR, exist_ok=True)

# Set seed for language detection consistency
DetectorFactory.seed = 0

# Set output filename with timestamp
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
output_filename = f"analyzed_reviews_{timestamp}.csv"
output_path = DATA_DIR / output_filename

def detect_language(text):
    try:
        text = str(text).strip()
        if not text:
            return 'unknown'
            
        # Check for Amharic characters (Unicode range for Amharic)
        amharic_range = (0x1200, 0x137F)
        has_amharic = any(amharic_range[0] <= ord(c) <= amharic_range[1] for c in text)
        
        # If text is very short, prioritize Amharic detection
        if len(text) < 10 and has_amharic:
            return 'am'
            
        # For longer texts, use language detection
        try:
            lang = detect(text)
            if lang == 'am':
                return 'am'
            elif lang == 'en':
                return 'en'
            # If detected language is not am/en but has Amharic chars, prioritize Amharic
            elif has_amharic:
                return 'am'
            else:
                return 'other'
        except:
            return 'am' if has_amharic else 'unknown'
    except Exception as e:
        return 'unknown'

def main():
    print("Starting sentiment analysis...")
    
    # 1. Load data
    input_path = DATA_DIR / "clean_reviews.csv"
    print(f"Loading data from: {input_path}")
    df = pd.read_csv(input_path)
    print(f"Loaded {len(df)} reviews for analysis")

    # 2. Language detection
    print("\n🌐 Detecting languages in reviews...")
    df['language'] = df['review'].apply(detect_language)

    # 3. Sentiment Analysis
    print("\n🔍 Running sentiment analysis...")
    try:
        # Load models
        en_sentiment = pipeline("sentiment-analysis", model="distilbert-base-uncased-finetuned-sst-2-english")
        multi_sentiment = pipeline("sentiment-analysis", model="nlptown/bert-base-multilingual-uncased-sentiment")
        print("   Models loaded successfully")
    except Exception as e:
        print(f"Error loading models: {e}")
        return

    def analyze_sentiment(text, language='en'):
        try:
            if not isinstance(text, str) or not text.strip():
                return "NEUTRAL", 0.0
                
            text = str(text).strip()
            if len(text) < 3:
                return "NEUTRAL", 0.0
                
            if language == 'am':
                try:
                    result = multi_sentiment(text[:512])[0]
                    score = result['score']
                    if result['label'] in ['4 stars', '5 stars']:
                        return "POSITIVE", score
                    elif result['label'] in ['1 star', '2 stars']:
                        return "NEGATIVE", score
                    return "NEUTRAL", score
                except:
                    language = 'en'  # Fallback to English model
            
            if language in ['en', 'other', 'unknown']:
                result = en_sentiment(text[:512])[0]
                return result['label'].upper(), result['score']
            return "NEUTRAL", 0.0
        except Exception as e:
            return "ERROR", 0.0

    print("   Analyzing sentiment for all reviews...")
    df[['sentiment', 'sentiment_score']] = df.apply(
        lambda x: pd.Series(analyze_sentiment(x['review'], x['language'])), 
        axis=1
    )

    # 4. Thematic Analysis
    print("\n🔍 Running thematic analysis...")
    try:
        nlp_en = spacy.load("en_core_web_sm")
    except:
        import spacy.cli
        spacy.cli.download("en_core_web_sm")
        nlp_en = spacy.load("en_core_web_sm")

    theme_keywords = {
        'App Performance': {
            'en': ['slow', 'fast', 'crash', 'lag', 'freeze', 'speed', 'performance', 'working', 'not working'],
            'am': ['ዘግይቷል', 'ፈጣን', 'ፕሮግራሙ', 'ስልክ', 'መተግበሪያ', 'ፈረሰ', 'ተቋርጧል', 'ስራ', 'አይሰራም']
        },
        'User Interface': {
            'en': ['ui', 'design', 'layout', 'interface', 'button', 'screen', 'navigate', 'look', 'appearance'],
            'am': ['መልክ', 'ዲዛይን', 'ማያሽን', 'መስተጋብር', 'አማራጭ', 'ማየት', 'ቀላል', 'አስቸጋሪ']
        },
        'Transaction Issues': {
            'en': ['transfer', 'transaction', 'failed', 'error', 'stuck', 'decline', 'send money', 'receive'],
            'am': ['ገንዘብ', 'መላላክ', 'ገቢ', 'ወጪ', 'ባንክ', 'መላላፊያ', 'አልሰራም', 'ችግር']
        },
        'Customer Support': {
            'en': ['support', 'service', 'help', 'response', 'contact', 'assistance', 'call', 'email'],
            'am': ['አገልግሎት', 'አስተዳደር', 'ሰራተኞች', 'እርዳታ', 'መልስ', 'ደውለው ሂዱ', 'አገናኝ', 'ድጋፍ']
        },
        'Fees & Charges': {
            'en': ['fee', 'charge', 'cost', 'money', 'payment', 'expensive', 'cheap', 'price'],
            'am': ['ክፍያ', 'ቀሪ ሒሳብ', 'ተቀናሽ', 'ወጪ', 'ገንዘብ', 'ቀንሷል', 'ጨምሯል', 'ዋጋ']
        }
    }

    def extract_themes(text, language='en'):
        try:
            if not isinstance(text, str) or not text.strip():
                return ['Other']
                
            text_lower = str(text).lower()
            theme_scores = {theme: 0 for theme in theme_keywords}
            
            for theme, keywords in theme_keywords.items():
                lang = language if language in ['en', 'am'] else 'en'
                for keyword in keywords.get(lang, []):
                    if keyword in text_lower:
                        theme_scores[theme] += 1
            
            top_themes = sorted(theme_scores.items(), key=lambda x: x[1], reverse=True)[:2]
            return [theme for theme, score in top_themes if score > 0] or ['Other']
        except Exception as e:
            return ['Error']

    print("   Identifying themes...")
    df['themes'] = df.apply(lambda x: extract_themes(x['review'], x['language']), axis=1)

    # 5. Save Results
    print(f"\n💾 Saving results to: {output_path}")
    try:
        df.to_csv(str(output_path), index=False)
        print(f"✅ Successfully saved analysis to: {output_path}")
    except Exception as e:
        print(f"❌ Error saving to {output_path}: {str(e)}")
        home_path = Path.home() / output_filename
        print(f"⚠️  Trying fallback location: {home_path}")
        try:
            df.to_csv(str(home_path), index=False)
            print(f"✅ Successfully saved to fallback location: {home_path}")
        except Exception as e2:
            print(f"❌ Critical error: Could not save analysis results. Error: {str(e2)}")
            print("First 5 rows of analysis:")
            print(df.head().to_string())

    # 6. Generate Summary Statistics
    print("\n📊 Analysis Summary:")
    print(f"Total reviews analyzed: {len(df)}")

    # Language distribution
    print("\n🌍 Language Distribution:")
    print(df['language'].value_counts())

    # Sentiment distribution by language
    print("\n😊 Sentiment Distribution by Language:")
    for lang in sorted(df['language'].unique()):
        lang_data = df[df['language'] == lang]
        print(f"\n{lang.upper()} reviews ({len(lang_data)}):")
        print(lang_data['sentiment'].value_counts(normalize=True).mul(100).round(2))

    # Sentiment by bank and language
    print("\n🏦 Sentiment by Bank and Language:")
    for bank in sorted(df['bank'].unique()):
        bank_data = df[df['bank'] == bank]
        print(f"\n{bank} (Total: {len(bank_data)} reviews):")
        
        for lang in sorted(bank_data['language'].unique()):
            lang_data = bank_data[bank_data['language'] == lang]
            print(f"  {lang.upper()}: {len(lang_data)} reviews")
            print("  " + str(lang_data['sentiment'].value_counts(normalize=True).mul(100).round(2)))

    # Theme distribution
    print("\n🎭 Most Common Themes:")
    all_themes = [theme for sublist in df['themes'] for theme in (sublist if isinstance(sublist, list) else [sublist])]
    print(pd.Series(all_themes).value_counts().head(10))

    print("\n🎉 Analysis completed successfully!")

if __name__ == "__main__":
    main()