import os
import streamlit as st
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from newspaper import Article
import requests
from bs4 import BeautifulSoup

load_dotenv()
groq_api_key = os.getenv("GROQ_API_KEY")

# 🔥 Wide layout
st.set_page_config(page_title="NewsSnap AI", page_icon="⚡", layout="wide")

# 🎨 UI
st.markdown("""
<style>
.block-container {
    max-width: 1200px !important;
    padding: 2.5rem 3rem;
}
.section-title {
    font-weight: 600;
    margin-top: 25px;
    color: #7c5cbf;
}
</style>
""", unsafe_allow_html=True)

st.title("⚡ NewsSnap AI")
st.caption("Smart news, instantly summarized")

# API check
if not groq_api_key:
    st.error("Add GROQ_API_KEY in .env")
    st.stop()

# LLM
llm = ChatGroq(
    model="llama-3.1-8b-instant",
    api_key=groq_api_key,
    temperature=0.2,
    timeout=60,
    max_retries=3
)

# 📰 Extract article
def extract_article(url):
    try:
        article = Article(url)
        article.download()
        article.parse()
        if article.text:
            return article.text
    except:
        pass

    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        r = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(r.text, "html.parser")
        return " ".join([p.get_text() for p in soup.find_all("p")])
    except:
        return None

# 🧠 Parse output
def parse_output(raw):
    summary = ""
    bullets = []
    sentiment = ""

    lines = raw.splitlines()
    mode = None

    for line in lines:
        line = line.strip()

        if not line:
            continue

        if line.lower().startswith("summary"):
            mode = "summary"
            continue
        elif line.lower().startswith("bullet"):
            mode = "bullets"
            continue
        elif line.lower().startswith("sentiment"):
            mode = "sentiment"
            continue

        if mode == "summary":
            summary += " " + line

        elif mode == "bullets":
            clean = line.lstrip("•-–—*0123456789.) ").strip()
            bullets.append(clean)

        elif mode == "sentiment":
            sentiment = line.strip()

    return summary.strip(), bullets[:5], sentiment

# Input
url = st.text_input("🔗 Paste article URL", placeholder="https://news.com/...")

col1, col2 = st.columns([4,1])

with col1:
    generate = st.button("Generate Analysis", use_container_width=True)

with col2:
    clear = st.button("Clear", use_container_width=True)

if clear:
    st.rerun()

# Output
if generate:
    if not url:
        st.warning("Enter URL")
    else:
        with st.spinner("Fetching article..."):
            text = extract_article(url)

        if not text:
            st.error("Could not extract article")
        else:
            with st.spinner("Analyzing..."):

                prompt = f"""
Analyze the following news article.

Return ONLY in this exact format:

Summary:
<2-3 sentence summary>

Bullet Points:
• point 1
• point 2
• point 3
• point 4
• point 5

Sentiment:
<ONLY ONE WORD: Positive OR Negative OR Neutral>

Do NOT write anything else.

Article:
{text[:4000]}
"""

                response = llm.invoke(prompt)

            summary, bullets, sentiment = parse_output(response.content)

            # 📝 Summary
            st.markdown("### 📝 Summary")
            st.write(summary)

            # 📌 Bullet Points
            st.markdown("### 📌 Key Points")
            for b in bullets:
                st.markdown(f"- {b}")

            # 🎯 Sentiment
            st.markdown("### 🎯 Sentiment")

            sent = sentiment.lower()

            if "positive" in sent:
                st.success("😊 Positive")
            elif "negative" in sent:
                st.error("😡 Negative")
            elif "neutral" in sent:
                st.info("😐 Neutral")
            else:
                st.warning(f"⚠️ Could not detect clearly: {sentiment}")

# Footer
st.markdown("---")
st.caption("NewsSnap AI • Powered by Groq")