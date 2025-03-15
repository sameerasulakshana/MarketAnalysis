import streamlit as st
from duckduckgo_search import DDGS
from datetime import datetime, timedelta
import requests
import json
import base64
from PIL import Image

# Initialize OpenRouter API key
OPENROUTER_API_KEY = "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"

def get_news(topic):
    # Initialize DuckDuckGo Search
    with DDGS() as ddgs:
        # Calculate date range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=1)
        
        # Format dates for DuckDuckGo
        time_filter = 'd'  # d=day
        
        # Search for news articles
        articles = []
        try:
            results = ddgs.news(
                topic,
                region='wt-wt',
                timelimit=time_filter,
                max_results=25
            )
            
            articles = list(results)
        except Exception as e:
            st.error(f"Search error: {str(e)}")
            return []
            
        return articles

def summarize_articles(articles, symbol):
    try:
        # Aggregate all article bodies into a single string
        aggregated_content = " ".join(article.get('body', '') for article in articles)
        
        # Read and concatenate the images
        images = []
        for timeframe in ['M5', 'H1', 'D1']:
            filename = f'{symbol}_{timeframe}.png'
            images.append(Image.open(filename))
        
        # Concatenate images vertically
        widths, heights = zip(*(i.size for i in images))
        total_height = sum(heights)
        max_width = max(widths)
        
        combined_image = Image.new('RGB', (max_width, total_height))
        y_offset = 0
        for img in images:
            combined_image.paste(img, (0, y_offset))
            y_offset += img.height
        
        # Save the combined image
        combined_image.save('combined_chart.png')
        
        # Read and encode the combined image to base64
        with open('combined_chart.png', 'rb') as image_file:
            base64_image = base64.b64encode(image_file.read()).decode('utf-8')
        
        response = requests.post(
            url="https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "HTTP-Referer": "<YOUR_SITE_URL>",  # Optional
                "X-Title": "<YOUR_SITE_NAME>",  # Optional
            },
            data=json.dumps({
                "model": "qwen/qwen2.5-vl-72b-instruct:free",  # Optional
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": f"Summarize the following news articles and analyze the {symbol} charts for M5, H1, and D1 timeframes. Provide a decision on whether to buy or sell {symbol}: {aggregated_content}"
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/png;base64,{base64_image}"
                                }
                            }
                        ]
                    }
                ]
            })
        )
        response_data = response.json()
        if 'choices' in response_data:
            summary = response_data['choices'][0]['message']['content'].strip()
            return summary
        else:
            return "No summary available"
    except Exception as e:
        return f"Error in summarization: {str(e)}"