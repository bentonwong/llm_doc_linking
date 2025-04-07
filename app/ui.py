import gradio as gr
import requests
import json
import random
import re
import time
import matplotlib.pyplot as plt

# Static English stopwords
STOP_WORDS = {
    'i', 'me', 'my', 'myself', 'we', 'our', 'ours', 'ourselves', 'you', "you're", "you've",
    "you'll", "you'd", 'your', 'yours', 'yourself', 'yourselves', 'he', 'him', 'his',
    'himself', 'she', "she's", 'her', 'hers', 'herself', 'it', "it's", 'its', 'itself',
    'they', 'them', 'their', 'theirs', 'themselves', 'what', 'which', 'who', 'whom',
    'this', 'that', "that'll", 'these', 'those', 'am', 'is', 'are', 'was', 'were', 'be',
    'been', 'being', 'have', 'has', 'had', 'having', 'do', 'does', 'did', 'doing', 'a',
    'an', 'the', 'and', 'but', 'if', 'or', 'because', 'as', 'until', 'while', 'of', 'at',
    'by', 'for', 'with', 'about', 'against', 'between', 'into', 'through', 'during',
    'before', 'after', 'above', 'below', 'to', 'from', 'up', 'down', 'in', 'out', 'on',
    'off', 'over', 'under', 'again', 'further', 'then', 'once', 'here', 'there', 'when',
    'where', 'why', 'how', 'all', 'any', 'both', 'each', 'few', 'more', 'most', 'other',
    'some', 'such', 'no', 'nor', 'not', 'only', 'own', 'same', 'so', 'than', 'too',
    'very', 's', 't', 'can', 'will', 'just', 'don', "don't", 'should', "should've", 'now',
    'd', 'll', 'm', 'o', 're', 've', 'y', 'ain', 'aren', "aren't", 'couldn', "couldn't",
    'didn', "didn't", 'doesn', "doesn't", 'hadn', "hadn't", 'hasn', "hasn't", 'haven',
    "haven't", 'isn', "isn't", 'ma', 'mightn', "mightn't", 'mustn', "mustn't", 'needn',
    "needn't", 'shan', "shan't", 'shouldn', "shouldn't", 'wasn', "wasn't", 'weren',
    "weren't", 'won', "won't", 'wouldn', "wouldn't"
}

# Load brief data
with open("sample_briefs.json", "r") as f:
    brief_pairs = json.load(f)

def highlight_common_terms(text1, text2):
    def get_keywords(text):
        words = re.findall(r'\b\w+\b', text.lower())
        return set(word for word in words if word not in STOP_WORDS)

    keywords1 = get_keywords(text1)
    keywords2 = get_keywords(text2)
    common_keywords = keywords1 & keywords2

    def highlight(text, keywords):
        for word in sorted(keywords, key=len, reverse=True):
            text = re.sub(rf"\b({word})\b", r"<mark>\1</mark>", text, flags=re.IGNORECASE)
        return text

    return highlight(text1, common_keywords), highlight(text2, common_keywords)

def analyze_briefs(moving_json, response_json, top_n):
    try:
        start_time = time.time()

        payload = {
            "moving_brief": json.loads(moving_json),
            "response_brief": json.loads(response_json),
            "top_n": int(top_n)
        }
        res = requests.post("http://localhost:8000/analyze", json=payload)
        res.raise_for_status()
        data = res.json()

        elapsed = time.time() - start_time

        plain_html = f"<h3>Top Matches (Brief {data['moving_brief_id']} vs {data['response_brief_id']})</h3><ul>"
        highlighted_html = f"<h3>Top Matches (Brief {data['moving_brief_id']} vs {data['response_brief_id']})</h3><ul>"

        for i, link in enumerate(data["top_links"], 1):
            m_content_h, r_content_h = highlight_common_terms(link["moving_content"], link["response_content"])
            m_content_p = link["moving_content"]
            r_content_p = link["response_content"]

            block_template = lambda match_id, m_heading, m_text, r_heading, r_text, score: f"""
                <li>
                    <strong style="font-size: 1.1em;">🔗 Match #{match_id}</strong><br><br>
                    <strong>🔹 Moving Heading:</strong> {m_heading}<br>
                    <div style="margin-left: 1em; color: darkblue;">{m_text}</div><br>
                    <strong>🔸 Response Heading:</strong> {r_heading}<br>
                    <div style="margin-left: 1em; color: darkgreen;">{r_text}</div><br>
                    <strong>🧮 Score:</strong> {score:.1f}%
                </li><hr>
            """

            plain_html += block_template(i, link['moving_heading'], m_content_p, link['response_heading'], r_content_p, link['score'] * 100)
            highlighted_html += block_template(i, link['moving_heading'], m_content_h, link['response_heading'], r_content_h, link['score'] * 100)

        plain_html += "</ul>"
        highlighted_html += "</ul>"

        chart_fig = create_score_chart(data["top_links"])

        return plain_html, highlighted_html, gr.update(visible=True), f"✅ **Completed in {elapsed:.2f} seconds**", chart_fig

    except Exception as e:
        error_html = f"<pre>❌ Error: {str(e)}</pre>"
        return error_html, error_html, gr.update(visible=False), f"❌ Error: {str(e)}", None

def toggle_highlight(show_highlight, plain_html, highlighted_html):
    return highlighted_html if show_highlight else plain_html

def get_random_pair():
    pair = random.choice(brief_pairs)
    return (
        json.dumps(pair["moving_brief"], indent=2),
        json.dumps(pair["response_brief"], indent=2),
        1
    )

def create_score_chart(top_links):
    scores = [link['score'] * 100 for link in top_links]
    labels = [f"{i+1}" for i in range(len(scores))]

    fig, ax = plt.subplots()
    ax.bar(labels, scores)
    ax.set_ylim(0, 100)
    ax.set_title("Similarity Scores for Top Matching Sections")
    ax.set_xlabel("Match #")
    ax.set_ylabel("Similarity Score (%)")
    return fig

# --- Gradio UI ---
with gr.Blocks(title="🧠 Brief Match") as demo:
    gr.HTML("""
        <div style="display: flex; align-items: center; gap: 12px; padding-bottom: 12px;">
            <div style="font-size: 1.8em; font-weight: bold; color: #2c3e50;">📘 BriefMatch</div>
        </div>
    """)
    gr.Markdown("### Analyze and compare moving and response briefs. Shared terms will be <mark>highlighted</mark> in the results. DEMO ONLY: Inputs must be in predefined JSON format. Reload for new pairs.")

    with gr.Row():
        moving_input = gr.Textbox(label="📜 Moving Brief (JSON)", lines=20)
        response_input = gr.Textbox(label="📄 Response Brief (JSON)", lines=20)

    top_n_input = gr.Number(label="Top N Matches", value=1)
    highlight_checkbox = gr.Checkbox(label="🔦 Highlight shared keywords", value=False, visible=False)
    submit_button = gr.Button("🔍 Analyze")

    status_output = gr.Markdown("")
    output_html = gr.HTML()
    chart_output = gr.Plot()  # 👈 chart comes after output_html

    # Store both plain and highlighted HTML
    plain_html_state = gr.State()
    highlighted_html_state = gr.State()

    submit_button.click(
        fn=lambda: "<span style='color:#333333; font-weight:600; font-size:1.05em;'>🔄 Analyzing... Please wait.</span>",
        inputs=[],
        outputs=[status_output]
    ).then(
        fn=analyze_briefs,
        inputs=[moving_input, response_input, top_n_input],
        outputs=[output_html, highlighted_html_state, highlight_checkbox, status_output, chart_output],
    ).then(
        fn=lambda h: h,
        inputs=output_html,
        outputs=plain_html_state
    ).then(
        fn=toggle_highlight,
        inputs=[highlight_checkbox, plain_html_state, highlighted_html_state],
        outputs=output_html
    )

    # Toggle to switch view without reprocessing
    highlight_checkbox.change(
        fn=toggle_highlight,
        inputs=[highlight_checkbox, plain_html_state, highlighted_html_state],
        outputs=output_html
    )

    demo.load(get_random_pair, inputs=[], outputs=[moving_input, response_input, top_n_input])

demo = demo
