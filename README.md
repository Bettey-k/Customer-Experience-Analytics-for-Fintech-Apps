# Fintech App Review Analysis

A powerful tool for analyzing customer reviews of banking and fintech applications, with support for both English and Amharic languages. This project helps identify user sentiment, common issues, and areas for improvement based on app store reviews.

## ✨ Features

- **Bilingual Sentiment Analysis**
  - English and Amharic language support
  - Custom models for each language
  - Sentiment classification (Positive/Negative/Neutral)

- **Thematic Analysis**
  - Identifies common themes in reviews
  - Language-specific keyword matching
  - Categorizes feedback into meaningful topics

- **Comprehensive Reporting**
  - Language distribution analysis
  - Sentiment trends by bank
  - Most common issues and praises
  - Detailed CSV exports

## 🚀 Getting Started

### Prerequisites

- Python 3.8+
- pip (Python package manager)

### Installation

1. Clone the repository:
   ```bash
   git clone [https://github.com/yourusername/Customer-Experience-Analytics-for-Fintech-Apps.git](https://github.com/yourusername/Customer-Experience-Analytics-for-Fintech-Apps.git)
   cd Customer-Experience-Analytics-for-Fintech-Apps

2. Create and activate a virtual environment (recommended):

python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

3. Install dependencies:
bash
pip install -r requirements.txt

4. Download spaCy language model:
bash
python -m spacy download en_core_web_sm

🛠️ Usage
Place your clean review data in 
data/clean_reviews.csv

Run the analysis:
bash
python scripts/sentiment_analysis.py

Check the data directory for the output file (e.g., analyzed_reviews_YYYYMMDD_HHMMSS.csv)

📊 Output
The analysis generates:
A timestamped CSV file with detailed analysis of each review
Console output with summary statistics including:
Language distribution
Sentiment distribution
Common themes
Performance metrics by bank

📁 Project Structure
Customer-Experience-Analytics-for-Fintech-Apps/
├── data/                    # Data files
│   ├── clean_reviews.csv    # Input data
│   └── analyzed_reviews_*.csv # Output files (ignored in git)
├── scripts/
│   ├── sentiment_analysis.py # Main analysis script
│   └── scrape_reviews.py    # Web scraping utility (optional)
├── .gitignore              # Git ignore rules
├── README.md               # This file
└── requirements.txt        # Python dependencies


📝 Requirements
The project requires the following Python packages (automatically installed via 
requirements.txt
):

pandas
numpy
transformers
torch
spacy
langdetect
python-dotenv
🤝 Contributing
Fork the repository
Create a feature branch (git checkout -b feature/AmazingFeature)
Commit your changes (git commit -m 'Add some AmazingFeature')
Push to the branch (git push origin feature/AmazingFeature)
Open a Pull Request

🙏 Acknowledgments
Hugging Face Transformers
spaCy for NLP processing
All open-source contributors
To use this README:
