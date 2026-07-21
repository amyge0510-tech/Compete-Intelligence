#!/usr/bin/env python3
"""
Dynamic competitor page scraper.
Discovery strategy: crawl known paths + search for new content.
"""

import json
import os
from datetime import datetime
from pathlib import Path
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

CONFIG_PATH = Path(__file__).parent.parent / "config" / "competitors.json"
DATA_DIR = Path(__file__).parent.parent / "data"
DATA_DIR.mkdir(exist_ok=True)

class CompetitorScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        with open(CONFIG_PATH) as f:
            self.config = json.load(f)
    
    def scrape_url(self, url, timeout=10):
        """Scrape a single URL and extract text content."""
        try:
            resp = self.session.get(url, timeout=timeout)
            resp.raise_for_status()
            soup = BeautifulSoup(resp.content, 'html.parser')
            
            # Remove script and style tags
            for tag in soup(['script', 'style', 'nav', 'footer']):
                tag.decompose()
            
            text = soup.get_text(separator='\n', strip=True)
            # Limit to 3000 chars to keep data manageable
            text = text[:3000]
            
            return {
                "url": url,
                "content": text,
                "title": soup.title.string if soup.title else "Unknown",
                "status": "success",
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            logger.warning(f"Failed to scrape {url}: {str(e)}")
            return {
                "url": url,
                "content": "",
                "title": "Error",
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def discover_pages(self, competitor):
        """Discover pages for a competitor by crawling known paths."""
        pages = []
        base_url = competitor['base_url']
        
        # Scrape base paths
        for path in competitor['paths']:
            url = urljoin(base_url, path)
            logger.info(f"Scraping {url}")
            result = self.scrape_url(url)
            if result['status'] == 'success':
                pages.append(result)
        
        return pages
    
    def scrape_all_competitors(self):
        """Scrape all configured competitors."""
        all_data = {}
        
        for competitor in self.config['competitors']:
            logger.info(f"\n=== Scraping {competitor['name']} ===")
            pages = self.discover_pages(competitor)
            all_data[competitor['name']] = {
                "pages": pages,
                "competitor_config": {
                    "name": competitor['name'],
                    "domain": competitor['domain'],
                    "base_url": competitor['base_url']
                },
                "scrape_timestamp": datetime.now().isoformat()
            }
        
        # Save to timestamped file
        week_num = datetime.now().isocalendar()[1]
        year = datetime.now().year
        filename = DATA_DIR / f"week_{year}_{week_num}_raw.json"
        
        with open(filename, 'w') as f:
            json.dump(all_data, f, indent=2)
        
        logger.info(f"\nScraped data saved to {filename}")
        return all_data

if __name__ == "__main__":
    scraper = CompetitorScraper()
    data = scraper.scrape_all_competitors()
    logger.info("Scraping complete!")
