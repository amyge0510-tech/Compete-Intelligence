#!/usr/bin/env python3
"""
Change detection: Compare this week's data with last week's using LLM.
"""

import json
import os
from pathlib import Path
from datetime import datetime
import logging
from openai import OpenAI
import glob

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DATA_DIR = Path(__file__).parent.parent / "data"
REPORTS_DIR = Path(__file__).parent.parent / "reports"
REPORTS_DIR.mkdir(exist_ok=True)

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

class ChangeDetector:
    def __init__(self):
        self.data_dir = DATA_DIR
    
    def get_latest_two_weeks(self):
        """Load this week and last week's raw data."""
        files = sorted(glob.glob(str(self.data_dir / "week_*_raw.json")))
        
        if len(files) < 1:
            logger.warning("No raw data files found")
            return None, None
        
        current = None
        previous = None
        
        with open(files[-1]) as f:
            current = json.load(f)
        
        if len(files) >= 2:
            with open(files[-2]) as f:
                previous = json.load(f)
        
        return previous, current
    
    def format_competitor_data(self, data):
        """Format competitor pages into readable text."""
        text_parts = []
        for page in data.get('pages', []):
            text_parts.append(f"\nURL: {page['url']}")
            text_parts.append(f"Title: {page['title']}")
            if page['status'] == 'success':
                text_parts.append(f"Content Preview: {page['content'][:500]}...")
        
        return "\n".join(text_parts)
    
    def detect_changes(self, competitor_name, prev_data, curr_data):
        """Use GPT to detect changes between weeks."""
        
        prev_text = self.format_competitor_data(prev_data) if prev_data else "[No previous data]"
        curr_text = self.format_competitor_data(curr_data) if curr_data else "[No current data]"
        
        prompt = f"""You are a competitive intelligence analyst specializing in AI/ML and education platforms.

Competitor: {competitor_name}

LAST WEEK'S DATA:
{prev_text}

THIS WEEK'S DATA:
{curr_text}

Analyze what changed. Be specific and actionable.

Format your response as:
NEW OFFERINGS:
- [List new courses, features, or capabilities]

CHANGES:
- [List what changed from last week]

THREATS (Why this matters to us):
- [Competitive threats]

OPPORTUNITIES (Gaps we could exploit):
- [Our advantages]

If this is the first week or no data, say so.
"""
        
        try:
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=500
            )
            
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"GPT call failed for {competitor_name}: {str(e)}")
            return f"Error: {str(e)}"
    
    def run(self):
        """Run change detection for all competitors."""
        prev_data, curr_data = self.get_latest_two_weeks()
        
        if not curr_data:
            logger.error("No current week data to analyze")
            return
        
        findings = {}
        for competitor_name, curr_comp_data in curr_data.items():
            logger.info(f"Analyzing {competitor_name}...")
            
            prev_comp_data = prev_data.get(competitor_name) if prev_data else None
            changes = self.detect_changes(competitor_name, prev_comp_data, curr_comp_data)
            
            findings[competitor_name] = {
                "analysis": changes,
                "timestamp": datetime.now().isoformat(),
                "week": datetime.now().isocalendar()[1],
                "year": datetime.now().year
            }
        
        # Save findings
        report_file = REPORTS_DIR / "findings.json"
        with open(report_file, 'w') as f:
            json.dump(findings, f, indent=2)
        
        logger.info(f"Findings saved to {report_file}")
        return findings

if __name__ == "__main__":
    detector = ChangeDetector()
    detector.run()
