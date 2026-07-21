# Competitive Intelligence Platform

Automated competitor monitoring and intelligence synthesis system that scrapes product releases, blogs, and course catalogs from key competitors, detects changes week-over-week, and automatically populates Power BI dashboards with actionable insights.

## Competitors Monitored
- AWS Skill Builder
- Salesforce Trailhead
- Google Skills
- Anthropic Learn
- OpenAI Academy
- Coursera

## Architecture
- **Scraper**: Dynamic discovery of competitor pages (blogs, products, courses)
- **Change Detection**: LLM-powered diff analysis vs. previous week
- **Synthesis**: AI-generated insights and competitive findings
- **Power BI Integration**: Automatic CSV export and Power BI data refresh

## Quick Start
See setup instructions in `docs/` directory.
