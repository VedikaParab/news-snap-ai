# ⚡ NewsSnap AI

> Turn long news into quick insights.

NewsSnap AI is an AI-powered web app that extracts news articles from URLs and generates concise summaries with key highlights in seconds.

---

## ✨ Features

- 🔗 Paste any news article URL  
- 📰 Automatic article extraction  
- ✨ AI-generated short summaries  
- 📌 Bullet point highlights  
- ⚡ Fast responses using Groq LLM  
- 🎨 Clean, modern UI (Streamlit)  

---

## 🧠 How It Works

1. User inputs a news article URL  
2. The app extracts article content using:
   - `newspaper3k` (primary)
   - `BeautifulSoup` (fallback)
3. Text is processed by a Large Language Model (LLM)  
4. AI generates:
   - 📝 Short summary  
   - 📌 Key bullet points  

---

## 🛠️ Tech Stack

| Layer       | Technology |
|------------|-----------|
| Frontend    | Streamlit |
| Backend     | Python |
| LLM         | Groq (LLaMA 3.1) |
| Scraping    | Newspaper3k, BeautifulSoup |
| Environment | dotenv |

---

## 🚀 Installation

### 1️⃣ Clone the repository

```bash
<<<<<<< HEAD
git clone https://github.com/your-username/news-snap-ai.git
cd news-snap-ai
=======
git clone https://github.com/VedikaParab/news-snap-ai.git
cd news-snap-ai
>>>>>>> bd02f669a1e776171032e0c7b9b1ce2acb251e4a
