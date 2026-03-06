import feedparser
import requests
import time
import hashlib
import os
from datetime import datetime

# ============================================================
#   VICTOR'S FOREX ALERT BOT 🤖
#   Sends real-time Forex, Crypto, Trump & Market news
#   to your Telegram automatically 24/7
# ============================================================

# --- YOUR SETTINGS (Fill these in) ---
TELEGRAM_BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"   # From BotFather
TELEGRAM_CHAT_ID   = "YOUR_CHAT_ID_HERE"     # From @userinfobot
CHECK_INTERVAL     = 300                      # Check every 5 minutes (seconds)

# --- NEWS SOURCES ---
RSS_FEEDS = [
    {
        "url": "https://www.forexlive.com/feed/news",
        "label": "📊 ForexLive",
        "emoji": "📊"
    },
    {
        "url": "https://news.google.com/rss/search?q=Trump+forex+dollar+economy&hl=en-US&gl=US&ceid=US:en",
        "label": "🇺🇸 Trump & Markets",
        "emoji": "🇺🇸"
    },
    {
        "url": "https://cointelegraph.com/rss",
        "label": "₿ Crypto News",
        "emoji": "₿"
    },
    {
        "url": "https://feeds.reuters.com/reuters/businessNews",
        "label": "📰 Reuters Business",
        "emoji": "📰"
    },
    {
        "url": "https://www.fxstreet.com/rss/news",
        "label": "💹 FXStreet",
        "emoji": "💹"
    },
]

# --- KEYWORDS FILTER (only send relevant news) ---
KEYWORDS = [
    "dollar", "usd", "eur", "gbp", "jpy", "forex", "currency",
    "trump", "fed", "federal reserve", "interest rate", "inflation",
    "bitcoin", "btc", "crypto", "ethereum", "eth",
    "gold", "oil", "nasdaq", "s&p", "dow", "market", "tariff",
    "trade war", "recession", "gdp", "nonfarm", "payroll"
]

# --- SEEN ARTICLES (prevents duplicate alerts) ---
seen_articles = set()


def get_article_id(entry):
    """Create a unique ID for each article"""
    unique = (entry.get("link", "") + entry.get("title", ""))
    return hashlib.md5(unique.encode()).hexdigest()


def is_relevant(title):
    """Check if article matches our keywords"""
    title_lower = title.lower()
    return any(keyword in title_lower for keyword in KEYWORDS)


def send_telegram_message(message):
    """Send a message to Telegram"""
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "Markdown",
        "disable_web_page_preview": True
    }
    try:
        response = requests.post(url, json=payload, timeout=10)
        return response.status_code == 200
    except Exception as e:
        print(f"Telegram error: {e}")
        return False


def format_message(entry, feed_label, emoji):
    """Format the news alert message"""
    title    = entry.get("title", "No title")
    link     = entry.get("link", "")
    pub_date = entry.get("published", datetime.now().strftime("%Y-%m-%d %H:%M"))

    message = (
        f"{emoji} *{feed_label}*\n\n"
        f"📌 *{title}*\n\n"
        f"🕐 {pub_date}\n\n"
        f"🔗 {link}\n\n"
        f"#Forex #Markets #Trading"
    )
    return message


def check_feeds():
    """Check all RSS feeds for new articles"""
    new_count = 0

    for feed in RSS_FEEDS:
        try:
            parsed = feedparser.parse(feed["url"])
            entries = parsed.entries[:5]  # Check latest 5 articles per feed

            for entry in entries:
                article_id = get_article_id(entry)
                title = entry.get("title", "")

                # Skip if already seen
                if article_id in seen_articles:
                    continue

                # Mark as seen
                seen_articles.add(article_id)

                # Skip if not relevant
                if not is_relevant(title):
                    continue

                # Format and send
                message = format_message(entry, feed["label"], feed["emoji"])
                success = send_telegram_message(message)

                if success:
                    print(f"✅ Sent: {title[:60]}...")
                    new_count += 1
                    time.sleep(1)  # Small delay between messages

        except Exception as e:
            print(f"❌ Error reading {feed['label']}: {e}")

    return new_count


def send_startup_message():
    """Send a message when bot starts"""
    message = (
        "🤖 *Victor Forex Alert Bot is LIVE!*\n\n"
        "📊 Monitoring:\n"
        "• ForexLive\n"
        "• Trump & Market News\n"
        "• Crypto (CoinTelegraph)\n"
        "• Reuters Business\n"
        "• FXStreet\n\n"
        f"⏱ Checking every {CHECK_INTERVAL // 60} minutes\n\n"
        "🚀 You'll receive alerts on market-moving news automatically!"
    )
    send_telegram_message(message)


# ============================================================
#   MAIN LOOP — Runs forever checking for news
# ============================================================
if __name__ == "__main__":
    print("🚀 Victor Forex Alert Bot Starting...")
    print(f"📡 Monitoring {len(RSS_FEEDS)} news sources")
    print(f"⏱  Checking every {CHECK_INTERVAL // 60} minutes\n")

    # Send startup notification
    send_startup_message()

    # Initial check — load existing articles without sending
    print("📥 Loading existing articles (no alerts for old news)...")
    for feed in RSS_FEEDS:
        try:
            parsed = feedparser.parse(feed["url"])
            for entry in parsed.entries[:10]:
                seen_articles.add(get_article_id(entry))
        except:
            pass
    print(f"✅ Loaded {len(seen_articles)} existing articles\n")

    # Main loop
    while True:
        print(f"🔍 Checking feeds at {datetime.now().strftime('%H:%M:%S')}...")
        new_articles = check_feeds()
        print(f"📬 Sent {new_articles} new alerts\n")
        time.sleep(CHECK_INTERVAL)
