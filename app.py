import os
import json
import datetime
import streamlit as st
import streamlit.components.v1 as components
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from newspaper import Article
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse

load_dotenv()
groq_api_key   = os.getenv("GROQ_API_KEY")
tavily_api_key = os.getenv("TAVILY_API_KEY")

st.set_page_config(page_title="NewsSnap AI", page_icon="⚡", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400;0,700;0,900;1,400;1,700&family=DM+Sans:wght@300;400;500;600&family=JetBrains+Mono:wght@400;500&display=swap');

:root {
    --ink:#0d0d0f;--ink-2:#3a3a44;--ink-3:#7a7a88;
    --paper:#fafaf8;--paper-2:#f2f2ee;--paper-3:#e8e8e2;
    --accent:#c8392b;--accent-2:#e8b84b;
    --positive:#1a7a4a;--negative:#c8392b;--neutral:#3a6ea8;
    --card-bg:#ffffff;--border:#e0e0d8;
    --shadow:0 2px 20px rgba(0,0,0,0.07);--shadow-lg:0 8px 40px rgba(0,0,0,0.12);
}
html,body,[class*="css"]{font-family:'DM Sans',sans-serif;color:var(--ink);}
#MainMenu,footer,header{visibility:hidden;}
.block-container{max-width:1160px!important;padding:0 2rem 4rem;}

body::before{content:'';position:fixed;inset:0;background-color:#fafaf8;background-image:radial-gradient(circle,#c8c8c0 1px,transparent 1px);background-size:22px 22px;z-index:-2;pointer-events:none;}
body::after{content:'';position:fixed;inset:0;background:linear-gradient(180deg,rgba(250,250,248,0) 0%,rgba(250,250,248,0.4) 40%,rgba(250,250,248,0.85) 100%);z-index:-1;pointer-events:none;}

@keyframes ticker-scroll{0%{transform:translateX(0)}100%{transform:translateX(-50%)}}
.ticker-wrap{background:var(--ink);overflow:hidden;white-space:nowrap;padding:5px 0;border-bottom:2px solid var(--accent);}
.ticker-inner{display:inline-block;animation:ticker-scroll 38s linear infinite;}
.ticker-item{display:inline-block;font-family:'JetBrains Mono',monospace;font-size:0.67rem;color:rgba(255,255,255,0.75);padding:0 2.5rem;letter-spacing:0.06em;}
.ticker-item strong{color:var(--accent-2);font-weight:500;}
.ticker-sep{color:var(--accent);opacity:0.6;}

.masthead{border-bottom:3px solid var(--ink);padding:1.6rem 0 1.2rem;margin-bottom:2.5rem;display:flex;align-items:baseline;justify-content:space-between;gap:1rem;}
.masthead-left{display:flex;align-items:baseline;gap:1rem;}
.masthead-logo{font-family:'Playfair Display',serif;font-size:2.8rem;font-weight:900;color:var(--ink);line-height:1;letter-spacing:-1.5px;}
.masthead-logo span{color:var(--accent);}
.masthead-tagline{font-size:0.72rem;color:var(--ink-3);font-weight:400;letter-spacing:0.08em;text-transform:uppercase;border-left:1px solid var(--border);padding-left:1rem;line-height:1.5;}
.masthead-date{font-family:'JetBrains Mono',monospace;font-size:0.68rem;color:var(--ink-3);text-align:right;line-height:1.8;}
.masthead-date strong{color:var(--ink);font-weight:500;}

@keyframes fadeUp{from{opacity:0;transform:translateY(18px)}to{opacity:1;transform:translateY(0)}}
.reveal-1{animation:fadeUp 0.5s ease both 0.05s;}
.reveal-2{animation:fadeUp 0.5s ease both 0.15s;}
.reveal-3{animation:fadeUp 0.5s ease both 0.25s;}
.reveal-4{animation:fadeUp 0.5s ease both 0.35s;}
.reveal-5{animation:fadeUp 0.5s ease both 0.45s;}
.reveal-6{animation:fadeUp 0.5s ease both 0.55s;}

.input-zone{background:var(--card-bg);border:1.5px solid var(--border);border-radius:4px;padding:1.2rem 1.8rem 0.5rem;margin-bottom:1rem;box-shadow:var(--shadow);}
.input-label{font-size:0.72rem;font-weight:600;letter-spacing:0.12em;text-transform:uppercase;color:var(--ink-3);margin-bottom:0.3rem;}
.stTextInput>div>div>input{font-family:'JetBrains Mono',monospace!important;font-size:0.82rem!important;background:var(--paper-2)!important;border:1.5px solid var(--border)!important;border-radius:3px!important;color:var(--ink)!important;padding:0.6rem 1rem!important;}
.stTextInput>div>div>input:focus{border-color:var(--accent)!important;box-shadow:0 0 0 3px rgba(200,57,43,0.1)!important;}
.stButton>button{font-family:'DM Sans',sans-serif!important;font-weight:600!important;font-size:0.82rem!important;letter-spacing:0.06em!important;text-transform:uppercase!important;border-radius:3px!important;transition:all 0.15s ease!important;}
.stButton:first-child>button{background:var(--ink)!important;color:white!important;border:2px solid var(--ink)!important;}
.stButton:first-child>button:hover{background:var(--accent)!important;border-color:var(--accent)!important;}
.stButton:last-child>button{background:transparent!important;color:var(--ink-2)!important;border:2px solid var(--border)!important;}

.section-header{display:flex;align-items:center;gap:0.6rem;margin:2.2rem 0 1rem;}
.section-header-rule{flex:1;height:1px;background:var(--border);}
.section-title{font-family:'Playfair Display',serif;font-size:1.5rem;color:var(--ink);letter-spacing:-0.3px;}
.section-kicker{font-size:0.68rem;font-weight:600;letter-spacing:0.14em;text-transform:uppercase;color:var(--accent);background:rgba(200,57,43,0.07);padding:2px 8px;border-radius:2px;}

.context-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:1rem;margin-bottom:1rem;}
.context-card{background:var(--card-bg);border:1.5px solid var(--border);border-top:3px solid var(--accent);border-radius:4px;padding:1.2rem 1.4rem;box-shadow:var(--shadow);}
.context-card-number{font-family:'JetBrains Mono',monospace;font-size:0.68rem;color:var(--accent);font-weight:500;margin-bottom:0.5rem;letter-spacing:0.06em;}
.context-card-term{font-family:'Playfair Display',serif;font-size:1.15rem;color:var(--ink);margin-bottom:0.4rem;line-height:1.2;}
.context-card-oneliner{font-size:0.8rem;font-weight:600;color:var(--ink-2);margin-bottom:0.6rem;line-height:1.4;padding-bottom:0.6rem;border-bottom:1px solid var(--border);}
.context-card-body{font-size:0.8rem;color:var(--ink-3);line-height:1.65;}

.summary-block{background:var(--ink);color:white;padding:1.8rem 2rem;border-radius:4px;margin-bottom:1rem;position:relative;overflow:hidden;}
.summary-block::before{content:'\201C';position:absolute;top:-0.5rem;left:1.2rem;font-family:'Playfair Display',serif;font-size:7rem;color:rgba(255,255,255,0.07);line-height:1;pointer-events:none;}
.summary-block p{font-family:'Playfair Display',serif;font-size:1.15rem;line-height:1.75;color:rgba(255,255,255,0.92);margin:0;position:relative;z-index:1;}

.meta-chip{display:inline-block;font-family:'JetBrains Mono',monospace;font-size:0.72rem;padding:3px 10px;border-radius:2px;border:1px solid var(--border);color:var(--ink-3);background:var(--paper-2);}
.meta-chip.positive{color:var(--positive);border-color:rgba(26,122,74,0.3);background:rgba(26,122,74,0.06);}
.meta-chip.negative{color:var(--negative);border-color:rgba(200,57,43,0.3);background:rgba(200,57,43,0.06);}
.meta-chip.neutral{color:var(--neutral);border-color:rgba(58,110,168,0.3);background:rgba(58,110,168,0.06);}

.bullets-list{list-style:none;padding:0;margin:0;}
.bullet-item{display:flex;gap:0.8rem;padding:0.8rem 0;border-bottom:1px solid var(--border);align-items:flex-start;font-size:0.9rem;line-height:1.6;color:var(--ink-2);}
.bullet-item:last-child{border-bottom:none;}
.bullet-num{font-family:'JetBrains Mono',monospace;font-size:0.65rem;font-weight:500;color:var(--accent);background:rgba(200,57,43,0.08);padding:2px 6px;border-radius:2px;flex-shrink:0;margin-top:3px;}

.question-item{background:var(--card-bg);border:1.5px solid var(--border);border-left:3px solid var(--accent-2);border-radius:3px;padding:1rem 1.2rem;margin-bottom:0.7rem;font-size:0.88rem;color:var(--ink-2);line-height:1.6;}
.question-num{font-family:'JetBrains Mono',monospace;font-size:0.65rem;color:var(--accent-2);font-weight:600;letter-spacing:0.06em;margin-bottom:0.3rem;}

.stats-bar{display:flex;background:var(--card-bg);border-radius:4px;border:1.5px solid var(--border);margin-bottom:1.5rem;overflow:hidden;box-shadow:var(--shadow);}
.stat-item{text-align:center;padding:0.9rem 1.4rem;flex:1;}
.stat-val{font-family:'Playfair Display',serif;font-size:1.3rem;color:var(--ink);display:block;line-height:1;}
.stat-lbl{font-size:0.62rem;text-transform:uppercase;letter-spacing:0.1em;color:var(--ink-3);font-weight:600;}
.stat-divider{width:1px;background:var(--border);margin:0.6rem 0;}

.entities-strip{display:flex;gap:0.55rem;flex-wrap:wrap;margin-bottom:0.5rem;}
.entity-pill{display:flex;align-items:center;gap:0.45rem;background:var(--card-bg);border:1.5px solid var(--border);border-radius:999px;padding:0.38rem 0.9rem 0.38rem 0.45rem;box-shadow:var(--shadow);}
.entity-badge{font-family:'JetBrains Mono',monospace;font-size:0.55rem;font-weight:700;letter-spacing:0.08em;text-transform:uppercase;padding:2px 6px;border-radius:999px;}
.entity-badge.person{color:#7b3fa0;background:rgba(123,63,160,0.1);}
.entity-badge.org{color:#1a7a4a;background:rgba(26,122,74,0.1);}
.entity-badge.place{color:#3a6ea8;background:rgba(58,110,168,0.1);}
.entity-name-pill{font-size:0.83rem;color:var(--ink);font-weight:500;}
.entity-role-pill{font-size:0.74rem;color:var(--ink-3);}

.footer{border-top:2px solid var(--ink);padding-top:1rem;margin-top:3rem;display:flex;justify-content:space-between;align-items:center;font-size:0.72rem;color:var(--ink-3);letter-spacing:0.04em;}
</style>
""", unsafe_allow_html=True)

# ── TICKER + MASTHEAD ──
now = datetime.datetime.now()
TICKER = [("LIVE","AI-powered editorial analysis engine"),("⚡","Paste any URL — instant intelligence"),
          ("NEW","Research Chatbot with live Tavily web search"),("POWERED BY","Groq · LLaMA 3.1 · Tavily Search"),
          ("EXPORT","Download full analysis reports as .txt")]
ticker_html = '<div class="ticker-wrap"><div class="ticker-inner">' + (
    "".join(f'<span class="ticker-item"><strong>{k}</strong> &nbsp;{v}&nbsp;<span class="ticker-sep"> /// </span></span>'
            for k, v in TICKER) * 4
) + '</div></div>'
st.markdown(ticker_html, unsafe_allow_html=True)
st.markdown(f"""
<div class="masthead">
  <div class="masthead-left">
    <div class="masthead-logo">News<span>Snap</span>&thinsp;AI</div>
    <div class="masthead-tagline">AI-powered editorial analysis<br>Paste · Read · Understand · Explore</div>
  </div>
  <div class="masthead-date"><strong>{now.strftime('%A, %d %B %Y')}</strong><br>{now.strftime('%H:%M')}</div>
</div>""", unsafe_allow_html=True)

if not groq_api_key:
    st.error("GROQ_API_KEY not found in .env"); st.stop()

llm = ChatGroq(model="llama-3.1-8b-instant", api_key=groq_api_key, temperature=0.2, timeout=60, max_retries=3)

# ── HELPERS ──
def safe_json(raw):
    raw = raw.strip()
    if raw.startswith("```"):
        parts = raw.split("```"); raw = parts[1] if len(parts) > 1 else raw
        if raw.startswith("json"): raw = raw[4:]
    return json.loads(raw.strip())

def reading_time(t): return max(1, round(len(t.split()) / 200))
def word_count(t):   return len(t.split())
def get_domain(url):
    try:    return urlparse(url).netloc.replace("www.", "")
    except: return "unknown"

# ── EXTRACTION ──
@st.cache_data(show_spinner=False)
def extract_article(url):
    try:
        a = Article(url); a.download(); a.parse()
        if a.text and len(a.text) > 200: return a.text, None
    except: pass
    try:
        r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")
        text = " ".join(p.get_text() for p in soup.find_all("p"))
        if len(text) > 200: return text, None
        return None, "No readable content found."
    except requests.exceptions.HTTPError as e: return None, f"HTTP {e.response.status_code}"
    except requests.exceptions.Timeout:        return None, "Request timed out."
    except Exception as e:                     return None, str(e)

# ── LLM CALLS ──
@st.cache_data(show_spinner=False)
def analyze_article(text):
    r = llm.invoke(f"""Analyze this news article. Return ONLY valid JSON, no markdown.
Keys: "summary"(2-3 sentences),"bullets"(5 strings),"sentiment"("Positive"|"Negative"|"Neutral"),
"category"("Politics"|"Business"|"Technology"|"Science"|"Sports"|"Health"|"World"|"Environment"|"Crime"|"Culture"),
"reading_complexity"("Easy"|"Moderate"|"Complex")
Article:{text[:8000]}""")
    return safe_json(r.content)

@st.cache_data(show_spinner=False)
def generate_context_cards(text):
    r = llm.invoke(f"""Identify exactly 3 key concepts needed to understand this article.
Return ONLY a JSON array of 3 objects:{{"term":str,"one_liner":str(<15 words),"explanation":str(2-3 sentences)}}
Article:{text[:6000]}""")
    return safe_json(r.content)

@st.cache_data(show_spinner=False)
def generate_timeline(text):
    r = llm.invoke(f"""Extract chronological timeline from this article.
Return ONLY a JSON array (3-6 items):{{"when":str,"event":str(<20 words)}}. If none, return [].
Article:{text[:6000]}""")
    result = safe_json(r.content)
    return result if isinstance(result, list) else []

@st.cache_data(show_spinner=False)
def extract_entities(text):
    r = llm.invoke(f"""Extract the TOP 5 most important named entities from this article.
Return ONLY a JSON array of exactly 5:{{"name":str,"type":"person"|"org"|"place","role":str(<10 words)}}
Article:{text[:6000]}""")
    result = safe_json(r.content)
    return (result if isinstance(result, list) else [])[:5]

@st.cache_data(show_spinner=False)
def generate_followup_questions(summary):
    r = llm.invoke(f"""Generate exactly 3 thought-provoking follow-up questions for a curious reader.
Format: numbered list (1. 2. 3.) only. Summary:{summary}""")
    qs = []
    for line in r.content.splitlines():
        line = line.strip()
        if line and line[0].isdigit() and "." in line:
            qs.append(line.split(".", 1)[1].strip())
    return qs[:3]

# ── TAVILY SEARCH ──
def tavily_search(query, max_results=4):
    if not tavily_api_key: return [], ""
    try:
        resp = requests.post("https://api.tavily.com/search", json={
            "api_key": tavily_api_key, "query": query,
            "search_depth": "basic", "max_results": max_results,
            "include_answer": True, "include_raw_content": False,
        }, timeout=15)
        resp.raise_for_status()
        data = resp.json()
        return data.get("results", []), data.get("answer", "")
    except: return [], ""

def chat_with_search(question, article_text, article_summary, chat_history):
    search_results, tavily_answer = tavily_search(f"{question} {article_summary[:120]}")
    search_ctx = ""
    sources = []
    if tavily_answer: search_ctx += f"Web summary: {tavily_answer}\n\n"
    for r in search_results:
        search_ctx += f"[{r.get('url','')}]\n{r.get('title','')}\n{r.get('content','')[:350]}\n\n"
        sources.append({"title": r.get("title", ""), "url": r.get("url", "")})

    history_str = "\n".join([
        f"{'User' if m['role']=='user' else 'Assistant'}: {m['content']}"
        for m in chat_history[-6:]
    ])
    prompt = f"""You are a sharp news analyst. Answer using BOTH the article AND web search results.
Be direct, concise (3-5 sentences). Cite sources naturally. Highlight new info from web beyond article.

ARTICLE:{article_text[:3500]}

WEB SEARCH:{search_ctx}

HISTORY:{history_str}

Question: {question}
Answer:"""
    return llm.invoke(prompt).content, sources

def build_report(url, domain, result, entities, timeline, text):
    now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    lines = ["="*70,"  NEWSSNAP AI — EDITORIAL ANALYSIS REPORT",f"  Generated: {now_str}","="*70,"",
             f"SOURCE:  {url}",f"DOMAIN:  {domain}",
             f"WORDS:   {word_count(text):,}   |   READ TIME: {reading_time(text)} min",
             f"CATEGORY:{result.get('category','—')}  SENTIMENT:{result.get('sentiment','—')}  COMPLEXITY:{result.get('reading_complexity','—')}",
             "","─"*70,"SUMMARY","─"*70,result.get("summary",""),"","─"*70,"KEY POINTS","─"*70]
    for i, b in enumerate(result.get("bullets", []), 1): lines.append(f"  {i}. {b}")
    lines += ["","─"*70,"TIMELINE","─"*70]
    for evt in (timeline or []): lines.append(f"  [{evt.get('when','')}]  {evt.get('event','')}")
    if not timeline: lines.append("  No clear timeline detected.")
    lines += ["","─"*70,"KEY ENTITIES","─"*70]
    for e in (entities or []): lines.append(f"  [{e.get('type','').upper()}]  {e.get('name','')}  —  {e.get('role','')}")
    lines += ["","="*70,"  Powered by Groq · LLaMA 3.1 · Tavily · NewsSnap AI","="*70]
    return "\n".join(lines)

# ── INPUT ──
st.markdown('<div class="reveal-1"><div class="input-zone"><div class="input-label">Paste a news article URL to analyse</div>', unsafe_allow_html=True)
url = st.text_input(label="url", label_visibility="collapsed", placeholder="https://timesofindia.indiatimes.com/...")
st.markdown('</div></div>', unsafe_allow_html=True)

col1, col2 = st.columns([5, 1])
with col1: generate = st.button("⚡  Analyse Article", use_container_width=True)
with col2:
    if st.button("✕  Clear", use_container_width=True):
        for k in ["article_text","result","cards","timeline","entities","domain","rt","wc","url_analysed","chat_history"]:
            st.session_state.pop(k, None)
        st.rerun()

# ── ANALYSIS ──
if generate:
    if not url.strip(): st.warning("Please enter a URL."); st.stop()
    with st.spinner("Fetching article…"):
        text, err = extract_article(url)
    if err: st.error(f"**Could not extract article.** {err}"); st.stop()

    st.session_state.update({"article_text": text, "url_analysed": url, "chat_history": []})

    with st.spinner("Running AI analysis…"):
        try: result = analyze_article(text)
        except Exception as e: st.error(f"Analysis failed: {e}"); st.stop()

    with st.spinner("Building context cards…"):
        try: cards = generate_context_cards(text)
        except: cards = []

    with st.spinner("Extracting timeline…"):
        try: timeline = generate_timeline(text)
        except: timeline = []

    with st.spinner("Extracting key entities…"):
        try: entities = extract_entities(text)
        except: entities = []

    st.session_state.update({"result": result, "cards": cards, "timeline": timeline, "entities": entities,
                              "domain": get_domain(url), "rt": reading_time(text), "wc": word_count(text)})

# ── RENDER ──
if "result" not in st.session_state: st.stop()

result   = st.session_state["result"]
cards    = st.session_state.get("cards", [])
timeline = st.session_state.get("timeline", [])
entities = st.session_state.get("entities", [])
domain   = st.session_state.get("domain", "")
rt       = st.session_state.get("rt", 1)
wc       = st.session_state.get("wc", 0)
text     = st.session_state.get("article_text", "")
url      = st.session_state.get("url_analysed", "")
sent     = result.get("sentiment", "Neutral")
cat      = result.get("category", "—")
complexity = result.get("reading_complexity", "—")

# STATS BAR
st.markdown(f"""<div class="reveal-2"><div class="stats-bar">
  <div class="stat-item"><span class="stat-val">{rt}</span><span class="stat-lbl">min read</span></div>
  <div class="stat-divider"></div>
  <div class="stat-item"><span class="stat-val">{wc:,}</span><span class="stat-lbl">words</span></div>
  <div class="stat-divider"></div>
  <div class="stat-item"><span class="stat-val" style="font-size:0.9rem;margin-top:4px">{domain}</span><span class="stat-lbl">source</span></div>
  <div class="stat-divider"></div>
  <div class="stat-item"><span class="stat-val" style="font-size:0.9rem;margin-top:4px">{cat}</span><span class="stat-lbl">category</span></div>
  <div class="stat-divider"></div>
  <div class="stat-item"><span class="stat-val" style="font-size:0.9rem;margin-top:4px">{complexity}</span><span class="stat-lbl">complexity</span></div>
  <div class="stat-divider"></div>
  <div class="stat-item"><span class="meta-chip {sent.lower()}" style="margin-top:6px;display:inline-block">{sent}</span><span class="stat-lbl" style="display:block;margin-top:4px">sentiment</span></div>
</div></div>""", unsafe_allow_html=True)

# CONTEXT CARDS
if cards:
    st.markdown("""<div class="reveal-3"><div class="section-header"><span class="section-kicker">Before You Read</span><span class="section-title">&nbsp;Background Context</span><div class="section-header-rule"></div></div></div>""", unsafe_allow_html=True)
    ch = '<div class="reveal-3"><div class="context-grid">'
    for i, c in enumerate(cards, 1):
        ch += f'<div class="context-card"><div class="context-card-number">CONCEPT {i:02d}</div><div class="context-card-term">{c.get("term","")}</div><div class="context-card-oneliner">{c.get("one_liner","")}</div><div class="context-card-body">{c.get("explanation","")}</div></div>'
    ch += '</div></div>'
    st.markdown(ch, unsafe_allow_html=True)

# SUMMARY
st.markdown("""<div class="reveal-3"><div class="section-header"><span class="section-kicker">TL;DR</span><span class="section-title">&nbsp;Summary</span><div class="section-header-rule"></div></div></div>""", unsafe_allow_html=True)
st.markdown(f'<div class="reveal-3"><div class="summary-block"><p>{result.get("summary","")}</p></div></div>', unsafe_allow_html=True)

# KEY POINTS + TIMELINE
col_l, col_r = st.columns([3, 2])
with col_l:
    st.markdown("""<div class="reveal-4"><div class="section-header"><span class="section-kicker">Key Points</span><span class="section-title">&nbsp;What Happened</span><div class="section-header-rule"></div></div></div>""", unsafe_allow_html=True)
    bh = '<div class="reveal-4"><ul class="bullets-list">'
    for i, b in enumerate(result.get("bullets", []), 1):
        bh += f'<li class="bullet-item"><span class="bullet-num">0{i}</span>{b}</li>'
    bh += '</ul></div>'
    st.markdown(bh, unsafe_allow_html=True)

with col_r:
    st.markdown("""<div class="reveal-4"><div class="section-header"><span class="section-kicker">Chronology</span><span class="section-title">&nbsp;Timeline</span><div class="section-header-rule"></div></div></div>""", unsafe_allow_html=True)
    if timeline:
        th = "<div class='reveal-4'>"
        for i, evt in enumerate(timeline):
            connector = "" if i == len(timeline)-1 else '<div style="width:2px;height:18px;background:var(--border);margin-left:6px;"></div>'
            th += f"""<div style="display:flex;gap:0.8rem;align-items:flex-start">
  <div style="display:flex;flex-direction:column;align-items:center;flex-shrink:0">
    <div style="width:14px;height:14px;border-radius:50%;background:var(--accent);border:2px solid var(--paper);box-shadow:0 0 0 2px var(--accent);flex-shrink:0;margin-top:2px"></div>{connector}
  </div>
  <div style="padding-bottom:0.9rem">
    <div style="font-family:'JetBrains Mono',monospace;font-size:0.66rem;color:var(--accent);font-weight:500;margin-bottom:2px">{evt.get('when','')}</div>
    <div style="font-size:0.83rem;color:var(--ink-2);line-height:1.55">{evt.get('event','')}</div>
  </div>
</div>"""
        th += "</div>"
        st.markdown(th, unsafe_allow_html=True)
    else:
        st.markdown('<p style="color:var(--ink-3);font-size:0.83rem">No clear timeline detected.</p>', unsafe_allow_html=True)

# ENTITIES
if entities:
    st.markdown("""<div class="reveal-5"><div class="section-header"><span class="section-kicker">Who & Where</span><span class="section-title">&nbsp;Key Entities</span><div class="section-header-rule"></div></div></div>""", unsafe_allow_html=True)
    eh = '<div class="reveal-5"><div class="entities-strip">'
    for e in entities[:5]:
        etype = e.get("type", "").lower()
        eh += f'<div class="entity-pill"><span class="entity-badge {etype}">{etype.upper()}</span><span class="entity-name-pill">{e.get("name","")}</span><span class="entity-role-pill">— {e.get("role","")}</span></div>'
    eh += '</div></div>'
    st.markdown(eh, unsafe_allow_html=True)

# FOLLOW-UP QUESTIONS
st.markdown("""<div class="reveal-5"><div class="section-header"><span class="section-kicker">Go Deeper</span><span class="section-title">&nbsp;Questions to Explore</span><div class="section-header-rule"></div></div></div>""", unsafe_allow_html=True)
with st.spinner("Generating questions…"):
    try: questions = generate_followup_questions(result.get("summary", ""))
    except: questions = []
qh = "<div class='reveal-5'>"
for i, q in enumerate(questions, 1):
    qh += f'<div class="question-item"><div class="question-num">Q{i:02d}</div>{q}</div>'
qh += "</div>"
st.markdown(qh, unsafe_allow_html=True)

# EXPORT
st.markdown("""<div class="reveal-6"><div class="section-header"><span class="section-kicker">Download</span><span class="section-title">&nbsp;Export Report</span><div class="section-header-rule"></div></div></div>""", unsafe_allow_html=True)
report = build_report(url, domain, result, entities, timeline, text)
st.download_button(
    label="⬇  Download Full Analysis Report (.txt)",
    data=report.encode("utf-8"),
    file_name=f"newssnap_{domain}_{datetime.datetime.now().strftime('%Y%m%d_%H%M')}.txt",
    mime="text/plain", use_container_width=True,
)

st.markdown("""<div class="footer">
  <span>NewsSnap AI</span>
  <span>Powered by Groq · LLaMA 3.1 · Tavily Search</span>
</div>""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════
# FLOATING CHAT WIDGET  — injected via components.html so it escapes
# Streamlit's iframe and can use position:fixed on the real viewport.
# The widget talks back to Streamlit through a hidden st.text_input
# that gets programmatically set + a form submit via JS.
# ══════════════════════════════════════════════════════════════════════

# Init chat history
if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = []

# ── invisible form that captures JS-submitted questions ──
with st.form("chat_form", clear_on_submit=True):
    hidden_q = st.text_input("chat_question", label_visibility="collapsed", key="chat_question_input")
    submitted = st.form_submit_button("send", disabled=True)   # JS clicks this

if submitted and hidden_q.strip() and "article_text" in st.session_state:
    st.session_state["chat_history"].append({"role": "user", "content": hidden_q})
    with st.spinner("Thinking…"):
        try:
            answer, sources = chat_with_search(
                hidden_q,
                st.session_state["article_text"],
                st.session_state["result"].get("summary", ""),
                st.session_state["chat_history"],
            )
            st.session_state["chat_history"].append(
                {"role": "assistant", "content": answer, "sources": sources}
            )
        except Exception as e:
            st.session_state["chat_history"].append(
                {"role": "assistant", "content": f"Error: {e}", "sources": []}
            )
    st.rerun()

# Hide the invisible form from view completely
st.markdown("""
<style>
div[data-testid="stForm"]{position:absolute!important;left:-9999px!important;width:0!important;height:0!important;overflow:hidden!important;}
</style>""", unsafe_allow_html=True)

# ── Serialise chat history to JSON for the JS widget ──
tavily_ok = bool(tavily_api_key)
article_ready = "article_text" in st.session_state
chat_history_json = json.dumps(st.session_state.get("chat_history", []))

# ── Inject the floating widget via components.html (true fixed positioning) ──
CHAT_WIDGET_HTML = f"""
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
  * {{ margin:0; padding:0; box-sizing:border-box; }}
  body {{ background:transparent; font-family:'DM Sans','Segoe UI',sans-serif; overflow:hidden; }}

  /* ── FAB button ── */
  #fab {{
    position:fixed; bottom:28px; right:28px; z-index:99999;
    width:56px; height:56px; border-radius:50%;
    background:#0d0d0f; border:2.5px solid #e8b84b;
    display:flex; align-items:center; justify-content:center;
    cursor:pointer; box-shadow:0 6px 28px rgba(0,0,0,0.35);
    font-size:22px; transition:transform .18s, background .18s;
    user-select:none;
  }}
  #fab:hover {{ transform:scale(1.1); background:#c8392b; }}

  /* tooltip above FAB */
  #fab-tip {{
    position:fixed; bottom:92px; right:22px; z-index:99998;
    background:#0d0d0f; color:rgba(255,255,255,0.88);
    font-family:'JetBrains Mono',monospace; font-size:11px;
    letter-spacing:.07em; padding:5px 12px; border-radius:3px;
    white-space:nowrap; box-shadow:0 4px 16px rgba(0,0,0,0.28);
    border:1px solid rgba(255,255,255,0.08);
    pointer-events:none; opacity:0; transition:opacity .2s;
  }}
  #fab:hover + #fab-tip {{ opacity:1; }}

  /* ── Chat panel ── */
  #panel {{
    position:fixed; bottom:96px; right:28px; z-index:99998;
    width:400px; max-height:560px;
    background:#fff; border:1.5px solid #e0e0d8;
    border-radius:12px; box-shadow:0 12px 48px rgba(0,0,0,0.22);
    display:none; flex-direction:column; overflow:hidden;
    animation:slideUp .22s ease both;
  }}
  @keyframes slideUp {{ from{{opacity:0;transform:translateY(20px)}} to{{opacity:1;transform:translateY(0)}} }}

  /* top bar */
  .topbar {{
    background:#0d0d0f; padding:12px 16px;
    display:flex; align-items:center; justify-content:space-between; flex-shrink:0;
  }}
  .topbar-left {{ display:flex; align-items:center; gap:8px; }}
  .dot {{ width:8px; height:8px; border-radius:50%; background:#e8b84b;
          animation:pulse 2s ease infinite; }}
  @keyframes pulse {{ 0%,100%{{opacity:1;transform:scale(1)}} 50%{{opacity:.5;transform:scale(.8)}} }}
  .topbar-title {{ font-family:'JetBrains Mono',monospace; font-size:11px;
                   color:rgba(255,255,255,.85); letter-spacing:.08em; text-transform:uppercase; }}
  .topbar-badge {{ font-family:'JetBrains Mono',monospace; font-size:10px; color:#e8b84b;
                   border:1px solid rgba(232,184,75,.3); padding:2px 7px;
                   border-radius:2px; letter-spacing:.05em; }}
  .close-btn {{ background:none; border:none; color:rgba(255,255,255,.5);
                cursor:pointer; font-size:18px; line-height:1; padding:0 4px; }}
  .close-btn:hover {{ color:#fff; }}

  /* messages */
  #messages {{
    flex:1; overflow-y:auto; padding:14px 14px 6px;
    display:flex; flex-direction:column; gap:10px;
    max-height:380px; scroll-behavior:smooth;
  }}
  .msg {{ display:flex; gap:8px; align-items:flex-start; animation:fadeIn .25s ease both; }}
  @keyframes fadeIn {{ from{{opacity:0;transform:translateY(8px)}} to{{opacity:1;transform:translateY(0)}} }}
  .msg.user {{ flex-direction:row-reverse; }}
  .avatar {{
    width:28px; height:28px; border-radius:50%; flex-shrink:0;
    display:flex; align-items:center; justify-content:center;
    font-size:9px; font-weight:700;
  }}
  .avatar.ai  {{ background:#0d0d0f; color:#e8b84b; }}
  .avatar.user{{ background:#c8392b; color:#fff; }}
  .bubble {{ max-width:82%; padding:9px 12px; border-radius:4px; font-size:13.5px; line-height:1.6; }}
  .bubble.ai  {{ background:#f2f2ee; color:#3a3a44; border:1px solid #e0e0d8;
                 border-radius:2px 10px 10px 10px; }}
  .bubble.user{{ background:#0d0d0f; color:rgba(255,255,255,.92);
                 border-radius:10px 2px 10px 10px; }}

  /* sources */
  .sources {{ margin-top:7px; padding-top:6px; border-top:1px solid #e0e0d8; }}
  .src-label {{ font-family:'JetBrains Mono',monospace; font-size:9px; text-transform:uppercase;
                letter-spacing:.08em; color:#7a7a88; margin-bottom:4px; }}
  .src-chip {{
    display:inline-block; font-size:11px; color:#3a6ea8;
    background:rgba(58,110,168,.07); border:1px solid rgba(58,110,168,.2);
    border-radius:2px; padding:2px 8px; margin:2px 3px 2px 0;
    text-decoration:none; cursor:pointer;
  }}
  .src-chip:hover {{ background:rgba(58,110,168,.16); }}

  /* typing dots */
  #typing {{ display:none; padding:0 14px 8px; gap:8px; align-items:center; flex-shrink:0; }}
  .typing-bubble {{ background:#f2f2ee; border:1px solid #e0e0d8;
                    border-radius:2px 10px 10px 10px; padding:9px 14px;
                    display:flex; gap:5px; align-items:center; }}
  .dot-t {{ width:6px; height:6px; border-radius:50%; background:#7a7a88;
            animation:bounce .9s ease infinite; }}
  .dot-t:nth-child(2){{ animation-delay:.2s; }}
  .dot-t:nth-child(3){{ animation-delay:.4s; }}
  @keyframes bounce {{ 0%,80%,100%{{transform:translateY(0)}} 40%{{transform:translateY(-5px)}} }}

  /* input row */
  .input-row {{
    display:flex; gap:8px; padding:10px 12px; flex-shrink:0;
    border-top:1.5px solid #e0e0d8; background:#fafaf8;
  }}
  #chat-input {{
    flex:1; font-family:'DM Sans',sans-serif; font-size:13.5px;
    background:#fff; border:1.5px solid #e0e0d8; border-radius:4px;
    padding:8px 12px; color:#0d0d0f; outline:none;
    transition:border-color .15s;
  }}
  #chat-input:focus {{ border-color:#c8392b; box-shadow:0 0 0 3px rgba(200,57,43,.1); }}
  #chat-input:disabled {{ opacity:.5; cursor:not-allowed; }}
  #send-btn {{
    background:#0d0d0f; color:#fff; border:none; border-radius:4px;
    padding:0 14px; cursor:pointer; font-size:16px;
    transition:background .15s; display:flex; align-items:center; justify-content:center;
  }}
  #send-btn:hover {{ background:#c8392b; }}
  #send-btn:disabled {{ background:#ccc; cursor:not-allowed; }}

  /* disabled state overlay */
  .disabled-notice {{
    text-align:center; font-size:12px; color:#7a7a88;
    padding:6px 0 2px; font-style:italic;
  }}
</style>
</head>
<body>

<!-- FAB -->
<div id="fab" onclick="togglePanel()" title="Ask about this article">💬</div>
<div id="fab-tip">ASK THE ARTICLE</div>

<!-- Chat panel -->
<div id="panel">
  <div class="topbar">
    <div class="topbar-left">
      <div class="dot"></div>
      <div class="topbar-title">Research Chatbot</div>
    </div>
    <div style="display:flex;align-items:center;gap:8px;">
      <div class="topbar-badge">{'TAVILY + ARTICLE' if tavily_ok else 'ARTICLE ONLY'}</div>
      <button class="close-btn" onclick="togglePanel()">×</button>
    </div>
  </div>

  <div id="messages"></div>

  <div id="typing" style="display:none;padding:0 14px 8px;">
    <div style="display:flex;gap:8px;align-items:center;">
      <div class="avatar ai">AI</div>
      <div class="typing-bubble">
        <div class="dot-t"></div><div class="dot-t"></div><div class="dot-t"></div>
      </div>
    </div>
  </div>

  {'<div class="disabled-notice">Analyse an article first to enable chat</div>' if not article_ready else ''}

  <div class="input-row">
    <input id="chat-input" type="text"
      placeholder="{'Ask about this story…' if article_ready else 'Analyse an article first…'}"
      {'disabled' if not article_ready else ''}
      onkeydown="if(event.key==='Enter')sendMessage()"
    />
    <button id="send-btn" onclick="sendMessage()" {'disabled' if not article_ready else ''}>➤</button>
  </div>
</div>

<script>
  // ── State ──
  var isOpen = false;
  var chatHistory = {chat_history_json};
  var sending = false;

  // ── Toggle panel ──
  function togglePanel() {{
    isOpen = !isOpen;
    var panel = document.getElementById('panel');
    if (isOpen) {{
      panel.style.display = 'flex';
      renderMessages();
      setTimeout(function(){{ document.getElementById('chat-input').focus(); }}, 100);
    }} else {{
      panel.style.display = 'none';
    }}
  }}

  // ── Render all messages ──
  function renderMessages() {{
    var box = document.getElementById('messages');
    box.innerHTML = '';

    // welcome message if empty
    if (chatHistory.length === 0) {{
      box.innerHTML = '<div class="msg"><div class="avatar ai">AI</div><div class="bubble ai">Ask me anything about this story. I\'ll search the web for related coverage to give you the full picture.</div></div>';
      return;
    }}

    chatHistory.forEach(function(msg) {{
      var cls = msg.role === 'user' ? 'user' : 'ai';
      var lbl = msg.role === 'user' ? 'YOU' : 'AI';
      var srcHtml = '';
      if (msg.sources && msg.sources.length > 0) {{
        srcHtml = '<div class="sources"><div class="src-label">Sources</div>';
        msg.sources.slice(0,3).forEach(function(s) {{
          var title = (s.title || '').substring(0, 45);
          srcHtml += '<a class="src-chip" href="' + s.url + '" target="_blank" rel="noopener">' + title + '…</a>';
        }});
        srcHtml += '</div>';
      }}
      var div = document.createElement('div');
      div.className = 'msg ' + cls;
      div.innerHTML = '<div class="avatar ' + cls + '">' + lbl + '</div><div class="bubble ' + cls + '">' + escapeHtml(msg.content) + srcHtml + '</div>';
      box.appendChild(div);
    }});
    box.scrollTop = box.scrollHeight;
  }}

  function escapeHtml(s) {{
    return String(s)
      .replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;')
      .replace(/\\n/g,'<br>');
  }}

  // ── Send message via Streamlit hidden form ──
  function sendMessage() {{
    if (sending) return;
    var inp = document.getElementById('chat-input');
    var q = inp.value.trim();
    if (!q) return;
    inp.value = '';

    sending = true;
    document.getElementById('send-btn').disabled = true;
    document.getElementById('typing').style.display = 'block';

    // Append optimistic user bubble
    chatHistory.push({{role:'user', content:q, sources:[]}});
    renderMessages();

    // ── Write into Streamlit's hidden text input and submit the form ──
    // Streamlit renders inputs inside shadow-like divs; we target by label key.
    var attempts = 0;
    function tryInject() {{
      // Find the hidden input (Streamlit renders it with data-testid="stTextInput")
      var allInputs = window.parent.document.querySelectorAll('input[type="text"]');
      var target = null;
      allInputs.forEach(function(el) {{
        // Our hidden input has placeholder "" and is inside the invisible form
        if (el.closest('form') && el.value === '' && el.placeholder === '') target = el;
      }});

      if (!target && attempts < 20) {{
        attempts++;
        setTimeout(tryInject, 100);
        return;
      }}

      if (target) {{
        // Set value via React's synthetic event system
        var nativeInputValueSetter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'value').set;
        nativeInputValueSetter.call(target, q);
        target.dispatchEvent(new Event('input', {{bubbles:true}}));

        setTimeout(function() {{
          // Click the hidden submit button
          var btns = window.parent.document.querySelectorAll('button[kind="secondaryFormSubmit"], button[type="submit"]');
          btns.forEach(function(btn) {{
            if (btn.closest('form')) btn.click();
          }});
        }}, 80);
      }}
    }}
    tryInject();
  }}

  // ── Poll for new messages from Streamlit (session state updates) ──
  // Streamlit re-renders the page; the component gets a new chatHistory prop
  // encoded in the HTML. We compare lengths to detect new AI replies.
  var lastLen = chatHistory.length;
  setInterval(function() {{
    // The updated chat_history is baked into a new render of this component.
    // Since components.html re-renders on st.rerun(), the whole iframe reloads,
    // so polling isn't needed — the iframe will reload with fresh data.
  }}, 1000);

  // Auto-open panel if there's history (i.e. user just got a reply)
  if (chatHistory.length > 0) {{
    isOpen = true;
    document.getElementById('panel').style.display = 'flex';
    setTimeout(renderMessages, 50);
  }}

  // Hide typing indicator (it was shown pre-rerun)
  sending = false;
</script>
</body>
</html>
"""

# Render the floating widget — height=1 because it uses fixed positioning
# within the iframe's viewport which is sized to the parent window by Streamlit
components.html(CHAT_WIDGET_HTML, height=1, scrolling=False)

# Streamlit injects a style to make the iframe height=1px but position:fixed
# children escape the iframe clip in Chrome/Edge. We also set the iframe to
# be transparent and full-window so fixed children are visible everywhere.
st.markdown("""
<style>
iframe[title="components.html"] {
    position: fixed !important;
    bottom: 0 !important;
    right: 0 !important;
    width: 520px !important;
    height: 100vh !important;
    border: none !important;
    z-index: 99997 !important;
    pointer-events: none;
    background: transparent !important;
}
iframe[title="components.html"] * {
    pointer-events: all;
}
</style>
""", unsafe_allow_html=True)