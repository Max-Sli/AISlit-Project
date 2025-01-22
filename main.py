import ssl
ssl._create_default_https_context = ssl._create_unverified_context
import requests
import re
from textblob import TextBlob
from bs4 import BeautifulSoup
import sqlite3

# Database Setup
def setup_database():
    """
    Set up SQLite database for storing analyzed data.
    """
    conn = sqlite3.connect('aislit_token.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS analysis (
                      id INTEGER PRIMARY KEY AUTOINCREMENT,
                      source TEXT,
                      polarity REAL,
                      subjectivity REAL,
                      keywords TEXT)''')
    conn.commit()
    conn.close()

# Text Analysis Module
def analyze_text_content(url):
    """
    Extract and analyze text content from a webpage.

    Args:
        url (str): URL of the webpage to analyze.
    Returns:
        dict: Analysis results with sentiment and key phrases.
    """
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        paragraphs = soup.find_all('p')
        text_content = " ".join(p.get_text() for p in paragraphs)
        text_content = re.sub(r'[\n\t]', ' ', text_content)

        blob = TextBlob(text_content)
        sentiment = blob.sentiment

        return {
            "source": url,
            "polarity": sentiment.polarity,
            "subjectivity": sentiment.subjectivity,
            "keywords": ", ".join(blob.noun_phrases[:10])
        }
    except Exception as e:
        print(f"Error analyzing text content: {e}")
        return None

# Save Analysis Results to Database
def save_to_database(result):
    """
    Save analysis results to the database.

    Args:
        result (dict): Analysis result to save.
    """
    try:
        conn = sqlite3.connect('aislit_token.db')
        cursor = conn.cursor()
        cursor.execute('''INSERT INTO analysis (source, polarity, subjectivity, keywords) 
                          VALUES (?, ?, ?, ?)''',
                       (result["source"], result["polarity"], result["subjectivity"], result["keywords"]))
        conn.commit()
        conn.close()
        print("Analysis saved successfully.")
    except Exception as e:
        print(f"Error saving to database: {e}")

# Example Usage
if __name__ == "__main__":
    setup_database()

    # Example URL for analysis
    url = "https://example.com/political-news"
    analysis_result = analyze_text_content(url)

    if analysis_result:
        print("Analysis Result:", analysis_result)
        save_to_database(analysis_result)
