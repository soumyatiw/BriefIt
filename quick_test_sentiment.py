from dotenv import load_dotenv
load_dotenv()

from ai_engine.understanding.sentiment import analyze_sentiment

fake_story = {
    "articles": [
        {
            "source_name": "The Hindu",
            "clean_text": "The government announced a new policy today aimed at reducing inflation, calling it a decisive step forward.",
        },
        {
            "source_name": "The Wire",
            "clean_text": "Critics called the government's new economic policy a hasty measure that fails to address root causes of inflation.",
        },
    ]
}

result = analyze_sentiment(fake_story)
print("Sentiment:", result.sentiment)
print("Perspective note:", result.perspective_note)
