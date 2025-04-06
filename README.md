🧠 Legal Brief Matcher API

This FastAPI-based service uses OpenAI embeddings and cosine similarity to analyze and compare legal brief arguments. It takes structured legal arguments from two briefs and returns the most semantically similar argument pairs.

⸻

🚀 Features
	•	Accepts JSON input with “moving” and “response” briefs.
	•	Returns the top N most similar argument matches (defaults to top 1).
	•	Uses OpenAI’s text-embedding-ada-002 model.
	•	Easily configurable and runs locally with FastAPI.

⸻

📦 Setup

1. Clone the repo

git clone https://github.com/yourusername/legal-brief-matcher.git
cd legal-brief-matcher

2. Create a virtual environment

python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows

3. Install dependencies

pip install -r requirements.txt

4. Add your OpenAI API key

Create a .env file in the project root:

OPENAI_API_KEY=your_openai_api_key_here



⸻

🦢 Run the API locally

uvicorn app.main:app --reload

Your API will be running at http://localhost:8000

⸻

📬 Making API Requests

Endpoint

POST /analyze

Request Body Example

{
  "moving_brief": {
    "brief_id": "BRIEF_001",
    "brief_arguments": [
      {
        "heading": "I. Background",
        "content": "The plaintiff asserts the land was used improperly..."
      },
      {
        "heading": "II. Legal Standard",
        "content": "Under Virginia law, a claim of trespass requires..."
      }
    ]
  },
  "response_brief": {
    "brief_id": "BRIEF_002",
    "brief_arguments": [
      {
        "heading": "A. Factual Background",
        "content": "This dispute concerns a construction project..."
      },
      {
        "heading": "B. Argument",
        "content": "There was no trespass as defined under common law..."
      }
    ]
  },
  "top_n": 2
}

Sample curl Request

curl -X POST http://localhost:8000/analyze \
  -H "Content-Type: application/json" \
  -d @sample_request.json

Where sample_request.json contains the request body.

⸻

Response Format

{
  "moving_brief_id": "BRIEF_001",
  "response_brief_id": "BRIEF_002",
  "top_links": [
    {
      "moving_heading": "II. Legal Standard",
      "moving_content": "...",
      "response_heading": "B. Argument",
      "response_content": "...",
      "score": 0.874
    },
    {
      "moving_heading": "I. Background",
      "moving_content": "...",
      "response_heading": "A. Factual Background",
      "response_content": "...",
      "score": 0.843
    }
  ]
}



⸻

🧰 Project Structure

app/
├── main.py             # FastAPI entrypoint
├── api.py              # API router
├── config.py           # Loads .env
├── logic.py            # Embedding and similarity logic
├── models.py           # Pydantic request/response models
└── utils.py            # Cosine similarity
.env



⸻

✨ Notes
	•	You must have access to the text-embedding-ada-002 model from OpenAI.
	•	Large briefs may take time due to API rate limits.

⸻

📬 Questions?

Open an issue or ping your friendly neighborhood developer.
