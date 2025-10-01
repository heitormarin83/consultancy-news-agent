"""
Main Consultancy News Agent
Collects and analyzes consultancy news from multiple sources
"""

import os
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Any, Optional

from .models import NewsArticle, DailyReport, CONSULTANCY_FIRMS, identify_firms_in_text
from .scrapers.news_scraper import NewsScraperManager
from .analyzers.relevance_analyzer import RelevanceAnalyzer
from .utils.logger import get_logger
from .utils.deduplication import DeduplicationManager

class ConsultancyNewsAgent:
    """Main agent for collecting and analyzing consultancy news"""
    
    def __init__(self):
        """Initialize the news agent"""
        self.logger = get_logger("consultancy_agent")
        
        try:
            # Initialize components
            self.scraper_manager = NewsScraperManager()
            self.relevance_analyzer = RelevanceAnalyzer()
            self.deduplication_manager = DeduplicationManager()
            
            # Create necessary directories
            self._setup_directories()
            
            self.logger.info("✅ Consultancy News Agent initialized successfully")
            
        except Exception as e:
            self.logger.error(f"❌ Failed to initialize Consultancy News Agent: {e}")
            raise
    
    def _setup_directories(self):
        """Create necessary directories"""
        directories = [
            'data/reports',
            'data/deduplication',
            'logs',
            'config'
        ]
        
        for directory in directories:
            Path(directory).mkdir(parents=True, exist_ok=True)
    
    def collect_and_analyze_news(self) -> Dict[str, Any]:
        """
        Main method to collect and analyze news
        
        Returns:
            Dict containing results and statistics
        """
        try:
            self.logger.info("🚀 Starting news collection and analysis...")
            
            # Step 1: Collect articles from all sources
            self.logger.info("📰 Collecting articles from sources...")
            raw_articles = self.scraper_manager.collect_all_articles()
            
            if not raw_articles:
                self.logger.warning("⚠️ No articles collected")
                return {
                    'success': False,
                    'error': 'No articles collected from any source',
                    'total_articles': 0
                }
            
            self.logger.info(f"📊 Collected {len(raw_articles)} raw articles")
            
            # Step 2: Filter by date (last 10 days)
            cutoff_date = datetime.now() - timedelta(days=10)
            recent_articles = [
                article for article in raw_articles
                if article.date_published and article.date_published >= cutoff_date
            ]
            
            self.logger.info(f"📅 Filtered to {len(recent_articles)} articles from last 10 days")
            
            # Step 3: Apply deduplication
            unique_articles = self.deduplication_manager.remove_duplicates(recent_articles)
            duplicates_removed = len(recent_articles) - len(unique_articles)
            
            self.logger.info(f"🔄 Removed {duplicates_removed} duplicate articles")
            
            # Step 4: Analyze relevance and categorize
            self.logger.info("🧠 Analyzing article relevance...")
            analyzed_articles = []
            
            for article in unique_articles:
                # Calculate relevance score
                article.relevance_score = self.relevance_analyzer.calculate_relevance_score(article)
                
                # Identify mentioned firms
                mentioned_firms = identify_firms_in_text(f"{article.title} {article.summary or ''}")
                article.firms_mentioned = [firm.name for firm in mentioned_firms]
                
                # Categorize article
                article.category = self.relevance_analyzer.categorize_article(article)
                
                # Determine region
                article.region = self.relevance_analyzer.determine_region(article)
                
                analyzed_articles.append(article)
            
            # Step 5: Filter by relevance (score >= 6.0 for significant relevance)
            relevant_articles = [
                article for article in analyzed_articles
                if article.relevance_score >= 6.0
            ]
            
            self.logger.info(f"⭐ Found {len(relevant_articles)} highly relevant articles")
            
            # Step 6: Sort by relevance and select top articles
            relevant_articles.sort(key=lambda x: x.relevance_score, reverse=True)
            top_articles = relevant_articles[:20]  # Top 20 most relevant
            
            # Step 7: Generate statistics
            stats = self._generate_statistics(relevant_articles)
            
            # Step 8: Generate daily report
            report = self._generate_daily_report(relevant_articles, top_articles, stats)
            
            # Step 9: Save report
            report_path = self._save_report(report)
            
            # Step 10: Return results
            result = {
                'success': True,
                'total_articles': len(raw_articles),
                'recent_articles': len(recent_articles),
                'unique_articles': len(unique_articles),
                'duplicates_removed': duplicates_removed,
                'relevant_articles': len(relevant_articles),
                'high_relevance_articles': len([a for a in relevant_articles if a.relevance_score >= 8.0]),
                'top_articles_count': len(top_articles),
                'report_path': report_path,
                'statistics': stats
            }
            
            self.logger.info(f"✅ Collection completed successfully: {len(relevant_articles)} relevant articles")
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Error during collection and analysis: {e}")
            return {
                'success': False,
                'error': str(e),
                'total_articles': 0
            }
    
    def _generate_statistics(self, articles: List[NewsArticle]) -> Dict[str, Any]:
        """Generate statistics from articles"""
        
        stats = {
            'articles_by_region': {},
            'articles_by_firm': {},
            'articles_by_category': {},
            'articles_by_score': {
                'high (8-10)': 0,
                'medium (6-8)': 0,
                'low (4-6)': 0
            }
        }
        
        for article in articles:
            # By region
            if article.region:
                region_name = article.region.value
                stats['articles_by_region'][region_name] = stats['articles_by_region'].get(region_name, 0) + 1
            
            # By firm
            for firm in article.firms_mentioned:
                stats['articles_by_firm'][firm] = stats['articles_by_firm'].get(firm, 0) + 1
            
            # By category
            if article.category:
                category_name = article.category.value
                stats['articles_by_category'][category_name] = stats['articles_by_category'].get(category_name, 0) + 1
            
            # By score
            score = article.relevance_score
            if score >= 8.0:
                stats['articles_by_score']['high (8-10)'] += 1
            elif score >= 6.0:
                stats['articles_by_score']['medium (6-8)'] += 1
            else:
                stats['articles_by_score']['low (4-6)'] += 1
        
        return stats
    
    def _generate_daily_report(self, all_articles: List[NewsArticle], top_articles: List[NewsArticle], stats: Dict[str, Any]) -> DailyReport:
        """Generate daily report"""
        
        today = datetime.now().strftime('%Y-%m-%d')
        
        # Generate summary
        total_articles = len(all_articles)
        high_relevance = len([a for a in all_articles if a.relevance_score >= 8.0])
        
        summary_parts = [
            f"Collected {total_articles} relevant articles about consultancy firms from the last 10 days.",
            f"{high_relevance} articles were classified as high relevance (score ≥ 8.0)."
        ]
        
        # Add regional distribution
        if stats['articles_by_region']:
            region_info = []
            for region, count in stats['articles_by_region'].items():
                percentage = (count / total_articles) * 100 if total_articles > 0 else 0
                region_info.append(f"{region}: {count} articles ({percentage:.1f}%)")
            summary_parts.append(f"Regional distribution: {', '.join(region_info)}.")
        
        # Add top firms
        if stats['articles_by_firm']:
            top_firms = sorted(stats['articles_by_firm'].items(), key=lambda x: x[1], reverse=True)[:3]
            firm_info = [f"{firm} ({count})" for firm, count in top_firms]
            summary_parts.append(f"Most mentioned firms: {', '.join(firm_info)}.")
        
        summary = ' '.join(summary_parts)
        
        # Create report
        report = DailyReport(
            date=today,
            total_articles=total_articles,
            high_relevance_articles=high_relevance,
            articles_by_region=stats['articles_by_region'],
            articles_by_firm=stats['articles_by_firm'],
            articles_by_category=stats['articles_by_category'],
            top_articles=top_articles,
            summary=summary,
            analysis_criteria={
                'min_relevance_score': 6.0,
                'high_relevance_threshold': 8.0,
                'date_range_days': 10,
                'max_top_articles': 20
            }
        )
        
        return report
    
    def _save_report(self, report: DailyReport) -> str:
        """Save report to file"""
        
        # Save JSON report
        json_filename = f"consultancy_report_{report.date}.json"
        json_path = Path('data/reports') / json_filename
        
        with open(json_path, 'w', encoding='utf-8') as f:
            f.write(report.to_json())
        
        # Save HTML report
        html_filename = f"consultancy_report_{report.date}.html"
        html_path = Path('data/reports') / html_filename
        
        html_content = self._generate_html_report(report)
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        self.logger.info(f"📄 Report saved: {json_path}")
        return str(json_path)
    
    def _generate_html_report(self, report: DailyReport) -> str:
        """Generate HTML version of the report"""
        
        html = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Consultancy News Report - {report.date}</title>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; margin: 0; padding: 20px; background: #f5f5f5; }}
                .container {{ max-width: 1200px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 0 20px rgba(0,0,0,0.1); }}
                .header {{ text-align: center; border-bottom: 3px solid #667eea; padding-bottom: 20px; margin-bottom: 30px; }}
                .header h1 {{ color: #667eea; margin: 0; }}
                .stats {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; margin: 30px 0; }}
                .stat-card {{ background: #f8f9fa; padding: 20px; border-radius: 8px; border-left: 4px solid #667eea; }}
                .stat-card h3 {{ margin: 0 0 10px 0; color: #333; }}
                .article {{ border: 1px solid #ddd; margin: 15px 0; padding: 20px; border-radius: 8px; background: #fafafa; }}
                .article h3 {{ margin: 0 0 10px 0; color: #333; }}
                .article .meta {{ color: #666; font-size: 0.9em; margin: 10px 0; }}
                .score {{ background: #667eea; color: white; padding: 3px 8px; border-radius: 12px; font-size: 0.8em; font-weight: bold; }}
                .score.high {{ background: #28a745; }}
                .score.medium {{ background: #ffc107; color: #333; }}
                .firms {{ background: #e9ecef; padding: 5px 10px; border-radius: 15px; font-size: 0.85em; margin: 5px 0; }}
                .footer {{ text-align: center; margin-top: 40px; color: #666; font-size: 0.9em; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🏢 Peers Consulting & Technology</h1>
                    <h2>Daily News Report - {report.date}</h2>
                    <p>Generated on {report.collection_time.strftime('%Y-%m-%d at %H:%M UTC')}</p>
                </div>
                
                <div class="stats">
                    <div class="stat-card">
                        <h3>📊 Total Articles</h3>
                        <p style="font-size: 2em; margin: 0; color: #667eea;">{report.total_articles}</p>
                    </div>
                    <div class="stat-card">
                        <h3>🔥 High Relevance</h3>
                        <p style="font-size: 2em; margin: 0; color: #28a745;">{report.high_relevance_articles}</p>
                    </div>
                    <div class="stat-card">
                        <h3>🌍 Regions Covered</h3>
                        <p style="font-size: 2em; margin: 0; color: #ffc107;">{len(report.articles_by_region)}</p>
                    </div>
                    <div class="stat-card">
                        <h3>🏢 Firms Mentioned</h3>
                        <p style="font-size: 2em; margin: 0; color: #dc3545;">{len(report.articles_by_firm)}</p>
                    </div>
                </div>
                
                <div style="background: #e3f2fd; padding: 20px; border-radius: 8px; margin: 20px 0;">
                    <h3>📝 Summary</h3>
                    <p>{report.summary}</p>
                </div>
        """
        
        # Add top articles
        if report.top_articles:
            html += "<h2>🔥 Top Relevant Articles</h2>"
            
            for i, article in enumerate(report.top_articles, 1):
                score_class = "high" if article.relevance_score >= 8 else "medium" if article.relevance_score >= 6 else ""
                
                html += f"""
                <div class="article">
                    <h3>{i}. <a href="{article.url}" target="_blank">{article.title}</a></h3>
                    <div class="meta">
                        <span class="score {score_class}">Score: {article.relevance_score:.1f}</span>
                        <strong>Source:</strong> {article.source} | 
                        <strong>Category:</strong> {article.category.value if article.category else 'Other'}
                        {f' | <strong>Region:</strong> {article.region.value}' if article.region else ''}
                    </div>
                    {f'<div class="firms"><strong>Firms:</strong> {", ".join(article.firms_mentioned)}</div>' if article.firms_mentioned else ''}
                    {f'<p>{article.summary}</p>' if article.summary else ''}
                </div>
                """
        
        html += f"""
                <div class="footer">
                    <p>📧 Consultancy News Agent | Automated Report</p>
                    <p>Monitoring BIG 4, MBB, and Global Consultancies</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return html
    
    def get_latest_report(self) -> Optional[DailyReport]:
        """Get the latest report"""
        try:
            reports_dir = Path('data/reports')
            if not reports_dir.exists():
                return None
            
            # Find latest JSON report
            json_files = list(reports_dir.glob('consultancy_report_*.json'))
            if not json_files:
                return None
            
            latest_file = max(json_files, key=lambda x: x.stat().st_mtime)
            
            with open(latest_file, 'r', encoding='utf-8') as f:
                report_data = json.load(f)
            
            # Convert back to DailyReport object (simplified)
            return report_data
            
        except Exception as e:
            self.logger.error(f"❌ Error getting latest report: {e}")
            return None

