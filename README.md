# Job Bot - FIESC & IEL

An automation script built in Python that monitors the **FIESC** and **IEL** career pages (Pandape/Infojobs platform). The bot performs *web scraping* to identify new job openings published that day and sends detailed, real-time notifications directly to your **Telegram**.

## Features

- **Efficient Web Scraping:** Extracts vital job data (title, link, date, and location) using `BeautifulSoup`.
- **Telegram Alerts:** Sends well-formatted HTML messages, ready for viewing on mobile or desktop.
- **Work Mode Detection:** Automatically identifies whether the position is **Remote (Home Office)** or **On-site** based on keywords.
- **Anti-Spam System (Local Cache):** Records the IDs of the latest processed jobs in independent JSON files to prevent duplicate notifications.
- **Automation (CI/CD):** Ready to run 100% autonomously via **GitHub Actions** (through the `1-bot-start.yml` file).