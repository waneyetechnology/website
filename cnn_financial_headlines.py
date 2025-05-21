import requests

# Replace with your LLM API endpoint and key
#LLM_API_URL = "https://api.your-llm-provider.com/v1/chat/complet"
#LLM_API_KEY = "YOUR_API_KEY"
LLM_API_URL = "http://localhost:11434/api/generate"
LLM_API_KEY = "YOUR_API_KEY"

def get_cnn_homepage_html():
    response = requests.get("https://www.cnn.com")
    response.raise_for_status()
    return response.text

def extract_financial_headlines(html):
    prompt = (
        "Extract the top 5 financial or economics-related headlines and their URLs from the following CNN.com HTML. "
        "Return a Python list of dictionaries with 'headline' and 'url' keys. Only include unique, relevant headlines.\n\n"
        f"HTML:\n{html[:120000]}"  # Truncate to avoid token limits
    )
    headers = {
        "Authorization": f"Bearer {LLM_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "deepseek-r1:8b",  # or your preferred model
        "messages": [
            {"role": "system", "content": "You are a helpful assistant that extracts news headlines from HTML."},
            {"role": "user", "content": prompt}
        ],
        "max_tokens": 500,
        "temperature": 0
    }
    print('data', data)
    response = requests.post(LLM_API_URL, headers=headers, json=data)
    response.raise_for_status()
    result = response.json()
    print('result', result)
    # Extract the Python list from the LLM's response
    import ast
    headlines = ast.literal_eval(result['choices'][0]['message']['content'])
    return headlines

if __name__ == "__main__":
    html = get_cnn_homepage_html()
    headlines = extract_financial_headlines(html)
    for i, item in enumerate(headlines, 1):
        print(f"{i}. {item['headline']}\n   {item['url']}")
