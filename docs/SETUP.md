# Setup Guide

## Prerequisites
- Python 3.11+
- GitHub account with repo access
- OpenAI API key (for GPT access)
- Power BI account (for dashboard)

## Local Setup

### 1. Clone the repository
```bash
git clone https://github.com/amyge0510-tech/Compete-Intelligence.git
cd Compete-Intelligence
```

### 2. Create virtual environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Set up environment variables
```bash
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY
```

### 5. Test locally
```bash
python scripts/scraper.py
python scripts/change_detector.py
python scripts/synthesize.py
```

## GitHub Setup

### 1. Add GitHub Secrets

Go to Settings → Secrets and variables → Actions → New repository secret

Add:
- `OPENAI_API_KEY`: Your OpenAI API key

### 2. Enable GitHub Actions

Go to Actions tab and enable workflows.

### 3. Workflow Schedule

The workflow runs automatically every Monday at 9 AM UTC.
To test manually: Actions → Weekly Competitor Intelligence Scrape → Run workflow

## Power BI Integration

### 1. Get the CSV URL

The `data/powerbi_feed.csv` file is committed to the repo after each run.
You can access it at:
```
https://raw.githubusercontent.com/amyge0510-tech/Compete-Intelligence/main/data/powerbi_feed.csv
```

### 2. Connect Power BI to GitHub CSV

1. Open Power BI Desktop
2. Get Data → Web
3. Paste the CSV URL above
4. Load and transform data as needed
5. Create visuals (tables, cards, slicers)
6. Publish to Power BI Service

### 3. Set up Automatic Refresh

In Power BI Service:
1. Go to Dataset Settings
2. Set up a scheduled refresh or use GitHub API trigger
3. Data will automatically update after each Monday's run

## Monitoring

### Check Workflow Status
- Go to Actions tab
- View latest run logs
- Check for errors in Scraper, Detector, or Synthesizer steps

### Check Generated Files
- `data/week_YYYY_WW_raw.json`: Raw scraped data
- `reports/findings.json`: LLM-analyzed changes
- `reports/synthesis.txt`: Human-readable synthesis
- `data/powerbi_feed.csv`: Power BI feed (new rows added weekly)

## Configuration

### Add/Remove Competitors

Edit `config/competitors.json`:
```json
{
  "competitors": [
    {
      "name": "Competitor Name",
      "domain": "domain.com",
      "base_url": "https://domain.com/",
      "paths": ["/courses", "/blog"],
      "search_patterns": ["course", "blog"],
      "rss_urls": []
    }
  ]
}
```

### Customize Scraping

Edit `scripts/scraper.py`:
- Adjust `timeout` for slower sites
- Modify text extraction logic in `scrape_url()`
- Add RSS feed parsing

### Customize Analysis Prompts

Edit `scripts/change_detector.py` and `scripts/synthesize.py`:
- Modify the prompt templates
- Adjust GPT temperature/model
- Change output format

## Troubleshooting

### Scraper times out
- Check if competitor URLs are accessible
- Increase timeout in `scraper.py`
- Some sites may require JavaScript rendering (use Playwright)

### GPT API errors
- Verify `OPENAI_API_KEY` is set correctly
- Check OpenAI account has sufficient credits
- Monitor token usage

### Power BI not updating
- Verify CSV file is being committed to repo
- Check Power BI data source URL
- Try manual refresh in Power BI

## Costs

- **OpenAI API**: ~$0.50-1.00 per week (GPT-3.5-turbo calls)
- **GitHub Actions**: Free (500 min/month included)
- **Power BI**: Depends on license (free or paid)

## Support

For issues, check:
1. GitHub Actions logs
2. Generated JSON files in `data/` and `reports/`
3. OpenAI API usage/errors
