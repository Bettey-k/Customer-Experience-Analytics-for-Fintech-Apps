import os
import sys
import unittest
from unittest.mock import patch, MagicMock

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.sentiment_analysis import detect_language, analyze_sentiment, extract_themes, _ensure_models_loaded

class TestSentimentAnalysis(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Mock the model loading to avoid downloading during tests
        cls.patcher = patch('scripts.sentiment_analysis.pipeline')
        cls.mock_pipeline = cls.patcher.start()
        
        # Setup mock return values
        cls.mock_en_sentiment = MagicMock()
        cls.mock_multi_sentiment = MagicMock()
        
        # Configure the pipeline to return our mock sentiment analyzers
        cls.mock_pipeline.side_effect = [
            cls.mock_en_sentiment,  # First call returns English sentiment analyzer
            cls.mock_multi_sentiment  # Second call returns multilingual sentiment analyzer
        ]
        
        # Set up the mock return values for the sentiment analyzers
        cls.mock_en_sentiment.return_value = [{'label': 'POSITIVE', 'score': 0.99}]
        cls.mock_multi_sentiment.return_value = [{'label': '5 stars', 'score': 0.99}]
        
        # Initialize models
        _ensure_models_loaded()
    
    @classmethod
    def tearDownClass(cls):
        cls.patcher.stop()
    
    def test_detect_language_english(self):
        self.assertEqual(detect_language("This is an English sentence"), "en")
    
    def test_detect_language_amharic(self):
        amharic_text = "ይህ አማርኛ ጽሑፍ ነው"
        self.assertEqual(detect_language(amharic_text), "am")
    
    def test_sentiment_analysis_english_positive(self):
        # Test with English text
        with patch('scripts.sentiment_analysis.en_sentiment', self.mock_en_sentiment):
            sentiment, score = analyze_sentiment("I love this app! It works great!", "en")
            self.assertEqual(sentiment, "POSITIVE")
            self.assertGreater(score, 0.9)
    
    def test_sentiment_analysis_amharic_positive(self):
        # Test with Amharic text
        with patch('scripts.sentiment_analysis.multi_sentiment', self.mock_multi_sentiment):
            sentiment, score = analyze_sentiment("በጣም ጥሩ ነው!", "am")
            self.assertEqual(sentiment, "POSITIVE")
            self.assertGreater(score, 0.9)

if __name__ == '__main__':
    unittest.main()