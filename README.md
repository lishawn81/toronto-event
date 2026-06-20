# 🗓️ Toronto Events Aggregator

A Python-powered scraper that extracts upcoming Toronto events from blogTO and publishes them to a GitHub Pages site.

## 🚀 What It Does

- Scrapes event listings from [BlogTO Events](https://www.blogto.com/events/)
- Cleans and formats event data (title, date, location, description, and image)
- Generates a Markdown table of events
- Automatically updates `docs/index.md` for GitHub Pages display

## 🌐 Live Site

Check out the latest Toronto events at:  
👉 [Toronto Events](https://lishawn81.github.io/toronto-event/)

## 📁 Project Structure

```
├── events.py # Scraper that generates the event feed
├── docs/
│ └── index.md # GitHub Pages home (auto-updated)
| └── img/
├── .github/
│ └── workflows/
│   └── update.yml # GitHub Actions automation (optional)
├── README.md # You're reading it
├── requirements.txt
```

## 🧠 How It Works

The script uses:

- `requests` to fetch the blogTO events RSS feed
- `BeautifulSoup` to parse the HTML inside each feed item
- Python string processing to generate Markdown
- GitHub Actions to run the script on a schedule

## 🔧 Setup

### 1. Clone the repository

```bash
git clone https://github.com/lishawn81/toronto-event.git
cd toronto-event
```
### 2. Install dependencies
```bash
pip install -r requirements.txt
```
### 3. Run the script
```bash
python events.py
```
This will generate or overwrite docs/index.md with the latest event table.

## 🌐 View the GitHub Pages Site
Once deployed, your live events page will be available at:

https://lishawn81.github.io/toronto-event/
Make sure GitHub Pages is enabled with the docs folder as the source.

## ⚙️ Optional: Automate with GitHub Actions
You can set up a GitHub Actions workflow to update your site daily.

See .github/workflows/update.yml for an example.

## 📄 License
MIT License. Feel free to use, modify, or contribute.

Made with ❤️ for the Toronto community.