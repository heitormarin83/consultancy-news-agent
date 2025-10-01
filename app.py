"""
Peers Consulting & Technology News Agent
Main Flask Application
"""

import os
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any

from flask import Flask, render_template, jsonify, request
from loguru import logger

from src.main import ConsultancyNewsAgent
from src.utils.logger import setup_logger
from src.email_sender.webhook_sender import WebhookEmailSender

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'consultancy-news-agent-2024')

# Setup logging
setup_logger()
logger.info("🚀 Starting Peers Consulting & Technology News Agent")

# Initialize components
try:
    news_agent = ConsultancyNewsAgent()
    email_sender = WebhookEmailSender()
    logger.info("✅ Components initialized successfully")
except Exception as e:
    logger.error(f"❌ Failed to initialize components: {e}")
    news_agent = None
    email_sender = None

@app.route('/')
def dashboard():
    """Main dashboard page"""
    try:
        # Get latest statistics
        stats = get_system_stats()
        
        # Get recent reports
        recent_reports = get_recent_reports(limit=5)
        
        return render_template('dashboard.html', 
                             stats=stats, 
                             recent_reports=recent_reports)
    except Exception as e:
        logger.error(f"❌ Dashboard error: {e}")
        return render_template('error.html', error=str(e)), 500

@app.route('/api/status')
def api_status():
    """System status endpoint"""
    try:
        status = {
            'status': 'online',
            'timestamp': datetime.now().isoformat(),
            'version': '1.0.0',
            'components': {
                'news_agent': news_agent is not None,
                'email_sender': email_sender is not None,
                'webhook_configured': bool(os.getenv('EMAIL_WEBHOOK_URL'))
            },
            'stats': get_system_stats()
        }
        
        return jsonify(status)
    except Exception as e:
        logger.error(f"❌ Status API error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/collect', methods=['POST'])
def api_collect():
    """Manual news collection endpoint"""
    try:
        if not news_agent:
            return jsonify({'error': 'News agent not initialized'}), 500
        
        logger.info("🔄 Starting manual news collection...")
        
        # Run collection
        result = news_agent.collect_and_analyze_news()
        
        if result.get('success', False):
            logger.info(f"✅ Collection completed: {result.get('total_articles', 0)} articles")
            return jsonify(result)
        else:
            error_msg = result.get('error', 'Unknown error')
            logger.error(f"❌ Collection failed: {error_msg}")
            return jsonify({'error': error_msg}), 500
            
    except Exception as e:
        logger.error(f"❌ Collection API error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/reports')
def api_reports():
    """Get available reports"""
    try:
        reports = get_recent_reports(limit=10)
        return jsonify({'reports': reports})
    except Exception as e:
        logger.error(f"❌ Reports API error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/reports/<date>')
def api_report_detail(date):
    """Get specific report by date"""
    try:
        report_path = Path(f'data/reports/consultancy_report_{date}.json')
        
        if not report_path.exists():
            return jsonify({'error': 'Report not found'}), 404
        
        with open(report_path, 'r', encoding='utf-8') as f:
            report_data = json.load(f)
        
        return jsonify(report_data)
    except Exception as e:
        logger.error(f"❌ Report detail API error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/email/test', methods=['POST'])
def api_test_email():
    """Test email webhook"""
    try:
        if not email_sender:
            return jsonify({'error': 'Email sender not initialized'}), 500
        
        if not os.getenv('EMAIL_WEBHOOK_URL'):
            return jsonify({'error': 'EMAIL_WEBHOOK_URL not configured'}), 400
        
        # Send test email
        test_content = {
            'subject': 'Test - Peers Consulting & Technology News Agent',
            'message': f'Test email sent at {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}',
            'recipient': 'heitor.a.marin@gmail.com'
        }
        
        success = email_sender.send_test_email(test_content)
        
        if success:
            logger.info("✅ Test email sent successfully")
            return jsonify({'success': True, 'message': 'Test email sent successfully'})
        else:
            logger.error("❌ Failed to send test email")
            return jsonify({'error': 'Failed to send test email'}), 500
            
    except Exception as e:
        logger.error(f"❌ Test email API error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/webhook/collect', methods=['POST'])
def webhook_collect():
    """Webhook endpoint for automated collection (GitHub Actions)"""
    try:
        # Verify webhook (optional security)
        webhook_secret = request.headers.get('X-Webhook-Secret')
        expected_secret = os.getenv('WEBHOOK_SECRET')
        
        if expected_secret and webhook_secret != expected_secret:
            logger.warning("❌ Invalid webhook secret")
            return jsonify({'error': 'Invalid webhook secret'}), 401
        
        if not news_agent:
            return jsonify({'error': 'News agent not initialized'}), 500
        
        logger.info("🔄 Starting webhook-triggered collection...")
        
        # Run collection
        result = news_agent.collect_and_analyze_news()
        
        if result.get('success', False):
            # Send email report if configured
            if email_sender and result.get('report_path'):
                try:
                    email_sender.send_daily_report(result['report_path'])
                    logger.info("✅ Daily report email sent")
                except Exception as e:
                    logger.error(f"❌ Failed to send email: {e}")
            
            logger.info(f"✅ Webhook collection completed: {result.get('total_articles', 0)} articles")
            return jsonify(result)
        else:
            error_msg = result.get('error', 'Unknown error')
            logger.error(f"❌ Webhook collection failed: {error_msg}")
            return jsonify({'error': error_msg}), 500
            
    except Exception as e:
        logger.error(f"❌ Webhook collection error: {e}")
        return jsonify({'error': str(e)}), 500

def get_system_stats() -> Dict[str, Any]:
    """Get system statistics"""
    try:
        stats = {
            'total_sources': 0,
            'active_sources': 0,
            'total_reports': 0,
            'last_collection': None,
            'webhook_configured': bool(os.getenv('EMAIL_WEBHOOK_URL')),
            'uptime': get_uptime()
        }
        
        # Count sources
        sources_file = Path('config/sources.yaml')
        if sources_file.exists():
            import yaml
            with open(sources_file, 'r', encoding='utf-8') as f:
                sources_config = yaml.safe_load(f)
                if sources_config and 'sources' in sources_config:
                    sources = sources_config['sources']
                    stats['total_sources'] = len(sources)
                    stats['active_sources'] = len([s for s in sources.values() if s.get('enabled', True)])
        
        # Count reports
        reports_dir = Path('data/reports')
        if reports_dir.exists():
            stats['total_reports'] = len(list(reports_dir.glob('consultancy_report_*.json')))
        
        # Get last collection time
        reports = get_recent_reports(limit=1)
        if reports:
            stats['last_collection'] = reports[0]['date']
        
        return stats
    except Exception as e:
        logger.error(f"❌ Error getting system stats: {e}")
        return {
            'total_sources': 0,
            'active_sources': 0,
            'total_reports': 0,
            'last_collection': None,
            'webhook_configured': False,
            'uptime': '0 minutes'
        }

def get_recent_reports(limit: int = 10) -> List[Dict[str, Any]]:
    """Get recent reports"""
    try:
        reports_dir = Path('data/reports')
        if not reports_dir.exists():
            return []
        
        reports = []
        for report_file in sorted(reports_dir.glob('consultancy_report_*.json'), reverse=True)[:limit]:
            try:
                with open(report_file, 'r', encoding='utf-8') as f:
                    report_data = json.load(f)
                
                reports.append({
                    'date': report_data.get('date', 'Unknown'),
                    'total_articles': report_data.get('total_articles', 0),
                    'high_relevance': len([a for a in report_data.get('articles', []) if a.get('relevance_score', 0) >= 8]),
                    'filename': report_file.name
                })
            except Exception as e:
                logger.warning(f"⚠️ Error reading report {report_file}: {e}")
                continue
        
        return reports
    except Exception as e:
        logger.error(f"❌ Error getting recent reports: {e}")
        return []

def get_uptime() -> str:
    """Get application uptime"""
    try:
        # Simple uptime calculation (could be improved with actual start time tracking)
        return "Running"
    except Exception:
        return "Unknown"

@app.errorhandler(404)
def not_found(error):
    """404 error handler"""
    return render_template('error.html', 
                         error="Page not found", 
                         error_code=404), 404

@app.errorhandler(500)
def internal_error(error):
    """500 error handler"""
    logger.error(f"❌ Internal server error: {error}")
    return render_template('error.html', 
                         error="Internal server error", 
                         error_code=500), 500

if __name__ == '__main__':
    # Create necessary directories
    Path('data/reports').mkdir(parents=True, exist_ok=True)
    Path('logs').mkdir(parents=True, exist_ok=True)
    
    # Get port from environment (Railway compatibility)
    port = int(os.getenv('PORT', 5000))
    
    logger.info(f"🚀 Starting Flask server on port {port}")
    
    # Run Flask app
    app.run(
        host='0.0.0.0',
        port=port,
        debug=os.getenv('DEBUG_MODE', 'false').lower() == 'true'
    )

