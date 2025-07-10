
# 🧠 AI-Powered University ERP Assistant  
> 🚀 Say Goodbye to Boring Portals — Just Talk to Your ERP like ChatGPT 🎓

## 🎥 Demo

https://github.com/user-attachments/assets/fd92cf70-e02e-46c8-a771-f1b513bdef05

---

## 📌 Overview

Everyone struggles with university ERPs:
- ⚠️ Slow login
- ⚠️ Confusing UI
- ⚠️ No smart features

So I built something better — **an AI that talks to your University ERP** like magic 🪄

> ✨ Ask it anything — “What’s my CGPA?”, “How many absents?”, “What’s my next class?”

---

## 🧩 Built With

- ⚡ **[Groq](https://groq.com/)** — Lightning-fast LLM inference
- 🧠 **[LLaMA 3](https://llama.meta.com/)** + **RAG** — Intelligent contextual responses
- 🕸️ **Selenium** — Real-time scraping of ERP portal
- 🗂️ **JSON caching** — To speed up and avoid redundant scraping
- 🖥️ **Streamlit** — Clean, interactive web UI
- 📲 **Twilio WhatsApp API** — Auto-send alerts to parents

---

## 💡 Features

| Feature | Description |
|--------|-------------|
| 🧠 Smart Q&A | Ask questions like "What is my attendance?" |
| 📊 Visual Dashboard | GPA, attendance, and performance graphs |
| 📨 Parent Alerts | Auto WhatsApp message on absents or low grades |
| 🧾 Invoice & Result Fetch | Automatically fetch ERP data |
| 🔒 Auto Login | No need to enter credentials each time |
| 🎓 Final Year Ready | Scalable architecture, real-time data, AI-powered backend |

## ⚙️ Installation

```bash
git clone https://github.com/yourusername/university-erp-ai.git
cd university-erp-ai

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install requirements
pip install -r requirements.txt

Set environment variables in a .env file:

ERP_ROLL_NO=your_roll_number (dummy)
ERP_PASSWORD=your_password (dummy)
TWILIO_ACCOUNT_SID=your_sid
TWILIO_AUTH_TOKEN=your_token
PARENT_PHONE_NUMBER=+92xxxxxxxxxx


Let me know if you also want:

- A `requirements.txt` file  
- `.env.example` file

🗣️ Want to Build This?
Feel free to fork, star ⭐, or DM me on LinkedIn if you're interested in collaborating or learning how this works.
