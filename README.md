# Job Bot - FIESC & IEL

An automation script built in Python that monitors the **FIESC** and **IEL** career pages (Pandape/Infojobs platform). The bot performs *web scraping* to identify new job openings published that day and sends detailed, real-time notifications directly to your **Telegram**.

## Features

- **Efficient Web Scraping:** Extracts vital job data (title, link, date, and location) using `BeautifulSoup`.
- **Telegram Alerts:** Sends well-formatted HTML messages, ready for viewing on mobile or desktop.
- **Work Mode Detection:** Automatically identifies whether the position is **Remote (Home Office)** or **On-site** based on keywords.
- **Anti-Spam System (Local Cache):** Records the IDs of the latest processed jobs in independent JSON files to prevent duplicate notifications.
- **Automation (CI/CD):** Ready to run 100% autonomously via **GitHub Actions** (through the `1-bot-start.yml` file).

## Getting Started (Local Testing)

To test and run this application locally, follow the steps below.

### Prerequisites

- **Python > 3.12:** Please ensure your Python version is greater than 3.12 to avoid dependency conflicts.
- Create a Telegram Bot (obtained via [@BotFather](https://t.me/botfather)).
- get your Telegram Chat ID and Telegram token.

### Installation & Setup

**1. Clone the repository**
```bash
git clone <your-repository-url>
cd <your-repository-folder>
```

**2. Create and activate a Virtual Environment (Recommended)**
```bash
python -m venv venv

# On Linux/macOS:
source venv/bin/activate

# On Windows:
venv\Scripts\activate
```

**3. Install Dependencies**
```bash
pip install -r requirements.txt
```

**4. Configure Environment Variables**
You must create a file named `.env` in the root directory of the project to store your credentials safely. Add your Telegram token and Chat ID to this file:
```env
TOKEN_TELEGRAM=your_bot_token_here
CHAT_ID=your_chat_id_here
```

**5. Run the Application**
With the virtual environment activated and the `.env` file configured, run the bot using the following command:
```bash
python src/bot.py
```