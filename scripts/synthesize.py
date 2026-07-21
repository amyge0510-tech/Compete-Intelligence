#!/usr/bin/env python3
"""
Synthesize findings into Power BI-ready CSV format.
"""

import json
import csv
from pathlib import Path
from datetime import datetime
import logging
from openai import OpenAI
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

REPORTS_DIR = Path(__file__).parent.parent / "reports"
DATA_DIR = Path(__file__).parent.parent / "data"

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

class Synthesizer:
    def __init__(self):
        self.reports_dir = REPORTS_DIR
        self.data_dir = DATA_DIR
    
    def load_findings(self):
        """Load the findings from change_detector."""
        findings_file = self.reports_dir / "findings.json"
        if not findings_file.exists():
            logger.warning("No findings file found")
            return {}
        
        with open(findings_file) as f:
            return json.load(f)
    
    def synthesize_insights(self, findings):
        """Use GPT to synthesize cross-competitor insights."""
        
        findings_text = "\n\n".join([
            f"## {competitor}\n{data['analysis']}"
            for competitor, data in findings.items()
        ])
        
        prompt = f"""You are a competitive strategy analyst. Synthesize the following competitive intelligence into 3-5 key insights.

COMPETITIVE FINDINGS:
{findings_text}

Provide:
1. TOP THREATS: What are competitors doing that we should worry about?
2. MARKET TRENDS: What patterns do you see across competitors?
3. OUR OPPORTUNITIES: Where are the gaps?
4. RECOMMENDED ACTIONS: What should we do?

Be concise and actionable.
"""
        
        try:
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=800
            )
            
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"Synthesis failed: {str(e)}")
            return f"Error: {str(e)}"
    
    def generate_powerbi_csv(self, findings, synthesis):
        """Generate CSV for Power BI ingestion."""
        
        rows = []
        week = datetime.now().isocalendar()[1]
        year = datetime.now().year
        timestamp = datetime.now().isoformat()
        
        # Add synthesis row
        rows.append({
            "Week": week,
            "Year": year,
            "Date": timestamp,
            "Competitor": "CROSS-COMPETITOR",
            "Category": "SYNTHESIS",
            "Finding_Type": "Strategic Insights",
            "Content": synthesis,
            "Priority": "HIGH"
        })
        
        # Add per-competitor findings
        for competitor, data in findings.items():
            rows.append({
                "Week": week,
                "Year": year,
                "Date": timestamp,
                "Competitor": competitor,
                "Category": "DETAILED ANALYSIS",
                "Finding_Type": "Weekly Changes",
                "Content": data['analysis'],
                "Priority": "MEDIUM"
            })
        
        # Save to CSV
        csv_file = self.data_dir / "powerbi_feed.csv"
        
        # Append mode if file exists
        mode = 'a' if csv_file.exists() else 'w'
        
        with open(csv_file, mode, newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=rows[0].keys())
            if mode == 'w':
                writer.writeheader()
            writer.writerows(rows)
        
        logger.info(f"Power BI CSV updated: {csv_file}")
        logger.info(f"Added {len(rows)} rows")
        return csv_file
    
    def run(self):
        """Run synthesis pipeline."""
        logger.info("Loading findings...")
        findings = self.load_findings()
        
        if not findings:
            logger.warning("No findings to synthesize")
            return
        
        logger.info("Synthesizing insights...")
        synthesis = self.synthesize_insights(findings)
        
        logger.info("Generating Power BI CSV...")
        csv_file = self.generate_powerbi_csv(findings, synthesis)
        
        # Also save human-readable report
        report_file = self.reports_dir / "synthesis.txt"
        with open(report_file, 'w') as f:
            f.write(f"COMPETITIVE INTELLIGENCE SYNTHESIS\n")
            f.write(f"Week {datetime.now().isocalendar()[1]}, {datetime.now().year}\n")
            f.write(f"Generated: {datetime.now().isoformat()}\n")
            f.write(f"\n{'='*60}\n\n")
            f.write(synthesis)
        
        logger.info(f"Synthesis report saved to {report_file}")
        logger.info("Synthesis complete!")

if __name__ == "__main__":
    synthesizer = Synthesizer()
    synthesizer.run()
