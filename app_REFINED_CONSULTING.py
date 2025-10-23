"""
Peers Consultancy News Monitor - FILTROS REFINADOS PARA CONSULTORIAS
Sistema focado especificamente em players de consultoria
"""

import os
import json
import logging
import requests
import hashlib
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any
import re
from urllib.parse import urljoin, urlparse
import sqlite3
import base64
from threading import Timer
import time
import threading
from bs4 import BeautifulSoup
import feedparser
import ssl
import urllib3
from concurrent.futures import ThreadPoolExecutor, as_completed
import random

# Desabilitar avisos SSL para scraping
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
ssl._create_default_https_context = ssl._create_unverified_context

# Imports condicionais para evitar erros
try:
    import schedule
except ImportError:
    schedule = None
    
try:
    import resend
except ImportError:
    resend = None

from flask import Flask, render_template_string, jsonify, request

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'peers-consultancy-news-2024')

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

logger.info("🎯 Starting Peers Consultancy News Monitor - REFINED CONSULTING FOCUS")

class RefinedConsultingCollector:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
        # FONTES REFINADAS FOCADAS EM CONSULTORIA
        self.consulting_sources = self.build_consulting_focused_sources()
        
        # PALAVRAS-CHAVE ESPECÍFICAS DE CONSULTORIA (não economia geral)
        self.consulting_specific_keywords = {
            'en': {
                'firms': [
                    'mckinsey', 'bcg', 'bain', 'deloitte', 'pwc', 'ey', 'kpmg', 'accenture',
                    'oliver wyman', 'roland berger', 'simon-kucher', 'arthur d little',
                    'capgemini', 'atos', 'sopra steria', 'wavestone', 'pa consulting',
                    'cambridge consultants', 'reply', 'engineering'
                ],
                'activities': [
                    'consulting', 'consultancy', 'consultant', 'advisory services',
                    'management consulting', 'strategy consulting', 'digital transformation consulting',
                    'consulting firm', 'consulting practice', 'consulting division',
                    'consulting revenue', 'consulting growth', 'consulting acquisition',
                    'consulting partnership', 'consulting expansion', 'consulting office',
                    'consulting hire', 'consulting promotion', 'consulting award',
                    'consulting project', 'consulting engagement', 'consulting client'
                ],
                'exclude': [
                    'stock market', 'gdp', 'inflation', 'interest rate', 'central bank',
                    'unemployment', 'retail sales', 'housing market', 'commodity prices',
                    'currency exchange', 'bond market', 'economic indicator', 'fiscal policy'
                ]
            },
            'pt': {
                'firms': [
                    'falconi', 'elo group', 'visagio', 'peers', 'bip', 'gouvêa',
                    'mckinsey brasil', 'bcg brasil', 'bain brasil', 'deloitte brasil',
                    'pwc brasil', 'ey brasil', 'kpmg brasil', 'accenture brasil'
                ],
                'activities': [
                    'consultoria', 'consultor', 'consultores', 'serviços de consultoria',
                    'consultoria de gestão', 'consultoria estratégica', 'consultoria em transformação',
                    'empresa de consultoria', 'escritório de consultoria', 'divisão de consultoria',
                    'receita de consultoria', 'crescimento consultoria', 'aquisição consultoria',
                    'parceria consultoria', 'expansão consultoria', 'contratação consultoria',
                    'projeto de consultoria', 'cliente de consultoria', 'prêmio consultoria'
                ],
                'exclude': [
                    'bolsa de valores', 'pib', 'inflação', 'taxa de juros', 'banco central',
                    'desemprego', 'vendas varejo', 'mercado imobiliário', 'preços commodities',
                    'câmbio', 'mercado títulos', 'indicador econômico', 'política fiscal'
                ]
            },
            'de': {
                'firms': [
                    'roland berger', 'simon-kucher', 'arthur d little', 'zeb',
                    'mckinsey deutschland', 'bcg deutschland', 'deloitte deutschland'
                ],
                'activities': [
                    'beratung', 'berater', 'beratungsunternehmen', 'strategieberatung',
                    'managementberatung', 'beratungsdienstleistungen', 'beratungspraxis'
                ],
                'exclude': [
                    'börse', 'bruttoinlandsprodukt', 'inflation', 'zinssatz', 'zentralbank'
                ]
            },
            'fr': {
                'firms': [
                    'capgemini', 'atos', 'sopra steria', 'wavestone',
                    'mckinsey france', 'bcg france', 'bain france'
                ],
                'activities': [
                    'conseil', 'consultant', 'cabinet de conseil', 'conseil en stratégie',
                    'conseil en management', 'services de conseil', 'pratique conseil'
                ],
                'exclude': [
                    'bourse', 'pib', 'inflation', 'taux intérêt', 'banque centrale'
                ]
            },
            'es': {
                'firms': [
                    'everis', 'ntt data', 'indra', 'accenture españa',
                    'mckinsey españa', 'bcg españa', 'deloitte españa'
                ],
                'activities': [
                    'consultoría', 'consultor', 'empresa consultoría', 'consultoría estratégica',
                    'consultoría gestión', 'servicios consultoría'
                ],
                'exclude': [
                    'bolsa', 'pib', 'inflación', 'tipo interés', 'banco central'
                ]
            },
            'it': {
                'firms': [
                    'reply', 'engineering', 'accenture italia',
                    'mckinsey italia', 'bcg italia', 'deloitte italia'
                ],
                'activities': [
                    'consulenza', 'consulente', 'società consulenza', 'consulenza strategica',
                    'consulenza gestione', 'servizi consulenza'
                ],
                'exclude': [
                    'borsa', 'pil', 'inflazione', 'tasso interesse', 'banca centrale'
                ]
            }
        }
    
    def build_consulting_focused_sources(self):
        """Construir base de fontes focadas especificamente em consultoria"""
        return {
            # PUBLICAÇÕES ESPECIALIZADAS EM CONSULTORIA (PRIORIDADE MÁXIMA)
            "consulting_publications": [
                {"url": "https://www.consultancy.org/news/rss", "name": "Consultancy.org", "country": "Global", "language": "en", "priority": "high"},
                {"url": "https://www.managementconsulted.com/feed/", "name": "Management Consulted", "country": "USA", "language": "en", "priority": "high"},
                {"url": "https://www.vault.com/industries-professions/consulting/rss", "name": "Vault Consulting", "country": "USA", "language": "en", "priority": "high"},
                {"url": "https://www.consulting.com/rss", "name": "Consulting.com", "country": "Global", "language": "en", "priority": "high"},
                {"url": "https://www.strategy-business.com/rss", "name": "Strategy+Business", "country": "Global", "language": "en", "priority": "high"}
            ],
            
            # SITES INSTITUCIONAIS DAS CONSULTORIAS (PRIORIDADE ALTA)
            "consulting_firms_news": {
                "big4_mbb": [
                    {"url": "https://www.mckinsey.com/news", "name": "McKinsey Global", "country": "Global", "language": "en", "priority": "high"},
                    {"url": "https://www.bcg.com/news", "name": "BCG Global", "country": "Global", "language": "en", "priority": "high"},
                    {"url": "https://www.bain.com/insights/", "name": "Bain Global", "country": "Global", "language": "en", "priority": "high"},
                    {"url": "https://www2.deloitte.com/global/en/pages/about-deloitte/articles/news.html", "name": "Deloitte Global", "country": "Global", "language": "en", "priority": "high"},
                    {"url": "https://www.pwc.com/gx/en/news-room.html", "name": "PwC Global", "country": "Global", "language": "en", "priority": "high"},
                    {"url": "https://www.ey.com/en_gl/news", "name": "EY Global", "country": "Global", "language": "en", "priority": "high"},
                    {"url": "https://www.kpmg.com/xx/en/home/insights.html", "name": "KPMG Global", "country": "Global", "language": "en", "priority": "high"},
                    {"url": "https://www.accenture.com/us-en/about/newsroom", "name": "Accenture Global", "country": "Global", "language": "en", "priority": "high"}
                ],
                "local_leaders": [
                    {"url": "https://www.falconi.com/noticias/", "name": "Falconi", "country": "Brazil", "language": "pt", "priority": "high"},
                    {"url": "https://www.elogroup.com.br/noticias/", "name": "Elo Group", "country": "Brazil", "language": "pt", "priority": "high"},
                    {"url": "https://www.visagio.com/noticias/", "name": "Visagio", "country": "Brazil", "language": "pt", "priority": "high"},
                    {"url": "https://www.rolandberger.com/en/Press/", "name": "Roland Berger", "country": "Germany", "language": "en", "priority": "high"},
                    {"url": "https://www.simon-kucher.com/en/press", "name": "Simon-Kucher", "country": "Germany", "language": "en", "priority": "high"},
                    {"url": "https://www.oliverwyman.com/our-expertise/insights.html", "name": "Oliver Wyman", "country": "UK", "language": "en", "priority": "high"}
                ]
            },
            
            # MÍDIA ECONÔMICA COM FILTROS ESPECÍFICOS PARA CONSULTORIA
            "business_media_consulting": [
                {"url": "https://feeds.reuters.com/reuters/businessNews", "name": "Reuters Business", "country": "Global", "language": "en", "priority": "medium"},
                {"url": "https://feeds.bloomberg.com/markets/news.rss", "name": "Bloomberg", "country": "Global", "language": "en", "priority": "medium"},
                {"url": "https://www.ft.com/rss/companies", "name": "Financial Times", "country": "Global", "language": "en", "priority": "medium"},
                {"url": "https://valor.globo.com/rss/empresas/", "name": "Valor Econômico", "country": "Brazil", "language": "pt", "priority": "medium"},
                {"url": "https://www.handelsblatt.com/contentexport/feed/schlagzeilen", "name": "Handelsblatt", "country": "Germany", "language": "de", "priority": "medium"}
            ]
        }
    
    def is_consulting_specific(self, title, summary="", language="en"):
        """Verificar se a notícia é especificamente sobre consultoria (não economia geral)"""
        text = f"{title} {summary}".lower()
        
        keywords = self.consulting_specific_keywords.get(language, self.consulting_specific_keywords['en'])
        
        # Verificar se menciona firmas de consultoria específicas
        firm_mentions = sum(1 for firm in keywords['firms'] if firm.lower() in text)
        
        # Verificar se menciona atividades específicas de consultoria
        activity_mentions = sum(1 for activity in keywords['activities'] if activity.lower() in text)
        
        # Verificar se contém termos de economia geral que devemos excluir
        exclude_mentions = sum(1 for exclude in keywords['exclude'] if exclude.lower() in text)
        
        # Lógica refinada:
        # - Deve ter pelo menos 1 menção a firma OU 2 menções a atividades de consultoria
        # - NÃO deve ter mais de 1 menção a termos excluídos
        # - Se tem firma + atividade = alta relevância
        
        has_firm = firm_mentions >= 1
        has_activity = activity_mentions >= 2
        has_excludes = exclude_mentions > 1
        
        if has_excludes:
            return False  # Rejeitar se tem muitos termos de economia geral
        
        if has_firm and activity_mentions >= 1:
            return True  # Firma + atividade = perfeito
        
        if has_firm:
            return True  # Só firma já é bom
        
        if has_activity:
            return True  # Múltiplas atividades de consultoria
        
        return False
    
    def calculate_consulting_relevance_score(self, title, summary, source_name, language="en"):
        """Calcular score focado especificamente em consultoria"""
        text = f"{title} {summary}".lower()
        score = 30  # Score base mais baixo
        
        keywords = self.consulting_specific_keywords.get(language, self.consulting_specific_keywords['en'])
        
        # ALTA PONTUAÇÃO: Firmas específicas mencionadas
        for firm in keywords['firms']:
            if firm.lower() in text:
                score += 35  # Pontuação alta para firmas específicas
        
        # MÉDIA PONTUAÇÃO: Atividades de consultoria
        for activity in keywords['activities']:
            if activity.lower() in text:
                score += 15  # Pontuação média para atividades
        
        # PENALIZAÇÃO: Termos de economia geral
        for exclude in keywords['exclude']:
            if exclude.lower() in text:
                score -= 20  # Penalizar economia geral
        
        # BONUS: Fonte especializada em consultoria
        specialized_sources = ['consultancy.org', 'management consulted', 'strategy+business', 'vault consulting']
        if any(source in source_name.lower() for source in specialized_sources):
            score += 25  # Bonus alto para fontes especializadas
        
        # BONUS: Sites institucionais das consultorias
        consulting_firms = ['mckinsey', 'bcg', 'bain', 'deloitte', 'pwc', 'ey', 'kpmg', 'accenture', 'falconi', 'elo group', 'visagio']
        if any(firm in source_name.lower() for firm in consulting_firms):
            score += 20  # Bonus para sites das próprias consultorias
        
        # BONUS: Palavras-chave de alta relevância no título
        title_lower = title.lower()
        high_value_title_words = ['consulting', 'consultancy', 'consultant', 'advisory', 'strategy', 'transformation']
        for word in high_value_title_words:
            if word in title_lower:
                score += 10
        
        return min(max(score, 0), 100)  # Entre 0 e 100
    
    def fetch_consulting_rss_feed(self, source):
        """Buscar feed RSS com foco específico em consultoria"""
        try:
            logger.info(f"🎯 Buscando RSS consultoria: {source['name']} ({source['country']})")
            
            feed = feedparser.parse(source['url'])
            
            if not feed.entries:
                logger.warning(f"⚠️ Nenhuma entrada em {source['name']}")
                return []
            
            articles = []
            for entry in feed.entries[:20]:  # Mais entradas para filtrar melhor
                try:
                    title = entry.get('title', '').strip()
                    link = entry.get('link', '').strip()
                    summary = entry.get('summary', entry.get('description', '')).strip()
                    
                    # Limpar HTML
                    if summary:
                        soup = BeautifulSoup(summary, 'html.parser')
                        summary = soup.get_text().strip()
                    
                    # FILTRO ESPECÍFICO: Verificar se é especificamente sobre consultoria
                    if not self.is_consulting_specific(title, summary, source.get('language', 'en')):
                        logger.debug(f"⏭️ Rejeitada (não específica): {title[:40]}...")
                        continue
                    
                    # Extrair data
                    pub_date = entry.get('published_parsed') or entry.get('updated_parsed')
                    if pub_date:
                        article_date = datetime(*pub_date[:6])
                    else:
                        article_date = datetime.now()
                    
                    # Filtrar por data (últimos 14 dias para mais frescor)
                    if article_date < datetime.now() - timedelta(days=14):
                        continue
                    
                    # Calcular score específico de consultoria
                    relevance_score = self.calculate_consulting_relevance_score(
                        title, summary, source['name'], source.get('language', 'en')
                    )
                    
                    # Threshold mais alto para garantir qualidade
                    if relevance_score >= 70:
                        article = {
                            'title': title,
                            'url': link,
                            'summary': summary[:400] + '...' if len(summary) > 400 else summary,
                            'source': source['name'],
                            'country': source['country'],
                            'language': source.get('language', 'en'),
                            'date': article_date.strftime('%Y-%m-%d'),
                            'relevance_score': relevance_score,
                            'category': 'Consulting RSS',
                            'priority': source.get('priority', 'medium')
                        }
                        articles.append(article)
                        logger.info(f"🎯 Consultoria coletada: {title[:50]}... (Score: {relevance_score})")
                
                except Exception as e:
                    logger.error(f"❌ Erro ao processar entrada: {e}")
                    continue
            
            logger.info(f"✅ {len(articles)} notícias específicas de consultoria de {source['name']}")
            return articles
            
        except Exception as e:
            logger.error(f"❌ Erro em {source['name']}: {e}")
            return []
    
    def scrape_consulting_website(self, source):
        """Fazer scraping focado em sites de consultoria"""
        try:
            logger.info(f"🌐 Scraping consultoria: {source['name']} ({source['country']})")
            
            response = self.session.get(source['url'], timeout=15)
            if response.status_code != 200:
                return []
            
            soup = BeautifulSoup(response.content, 'html.parser')
            articles = []
            
            # Seletores específicos para sites de consultoria
            consulting_selectors = [
                'article', '.news-item', '.press-release', '.insight-item',
                '.news-card', '.article-card', '.content-item', '.post-item',
                '.press-item', '.media-item', '.announcement', '.update'
            ]
            
            for selector in consulting_selectors:
                items = soup.select(selector)[:8]  # Menos itens, mais qualidade
                
                for item in items:
                    try:
                        # Extrair título
                        title_elem = item.find(['h1', 'h2', 'h3', 'h4']) or item.find('a')
                        if not title_elem:
                            continue
                        
                        title = title_elem.get_text().strip()
                        if len(title) < 25:  # Títulos muito curtos provavelmente não são notícias
                            continue
                        
                        # Extrair link
                        link_elem = item.find('a') or title_elem
                        if not link_elem or not link_elem.get('href'):
                            continue
                        
                        link = urljoin(source['url'], link_elem['href'])
                        
                        # Extrair resumo
                        summary_elem = item.find(['p', '.summary', '.excerpt', '.description'])
                        summary = summary_elem.get_text().strip() if summary_elem else title
                        
                        # FILTRO ESPECÍFICO: Verificar se é especificamente sobre consultoria
                        if not self.is_consulting_specific(title, summary, source.get('language', 'en')):
                            logger.debug(f"⏭️ Scraping rejeitado: {title[:40]}...")
                            continue
                        
                        # Calcular score específico
                        relevance_score = self.calculate_consulting_relevance_score(
                            title, summary, source['name'], source.get('language', 'en')
                        )
                        
                        # Threshold alto para scraping
                        if relevance_score >= 75:
                            article = {
                                'title': title,
                                'url': link,
                                'summary': summary[:350] + '...' if len(summary) > 350 else summary,
                                'source': source['name'],
                                'country': source['country'],
                                'language': source.get('language', 'en'),
                                'date': datetime.now().strftime('%Y-%m-%d'),
                                'relevance_score': relevance_score,
                                'category': 'Consulting Website',
                                'priority': source.get('priority', 'medium')
                            }
                            articles.append(article)
                            logger.info(f"🌐 Consultoria scraped: {title[:40]}... (Score: {relevance_score})")
                    
                    except Exception as e:
                        continue
            
            logger.info(f"✅ {len(articles)} notícias específicas scraped de {source['name']}")
            return articles
            
        except Exception as e:
            logger.error(f"❌ Erro no scraping de {source.get('name', 'Unknown')}: {e}")
            return []
    
    def collect_refined_consulting_news(self):
        """Coletar notícias refinadas focadas especificamente em consultoria"""
        all_articles = []
        
        # Preparar lista de fontes priorizadas
        all_sources = []
        
        # PRIORIDADE 1: Publicações especializadas em consultoria
        all_sources.extend(self.consulting_sources['consulting_publications'])
        
        # PRIORIDADE 2: Sites das consultorias
        for category, sources in self.consulting_sources['consulting_firms_news'].items():
            all_sources.extend(sources[:5])  # Top 5 de cada categoria
        
        # PRIORIDADE 3: Mídia econômica (com filtros rigorosos)
        all_sources.extend(self.consulting_sources['business_media_consulting'][:3])  # Só top 3
        
        logger.info(f"🎯 Iniciando coleta refinada de {len(all_sources)} fontes especializadas")
        
        # Threading com menos workers para mais controle
        with ThreadPoolExecutor(max_workers=6) as executor:
            rss_futures = []
            scraping_futures = []
            
            for source in all_sources:
                if 'rss' in source.get('url', '').lower() or 'feed' in source.get('url', '').lower():
                    future = executor.submit(self.fetch_consulting_rss_feed, source)
                    rss_futures.append(future)
                else:
                    future = executor.submit(self.scrape_consulting_website, source)
                    scraping_futures.append(future)
            
            # Coletar resultados
            for future in as_completed(rss_futures + scraping_futures):
                try:
                    articles = future.result(timeout=25)
                    all_articles.extend(articles)
                except Exception as e:
                    logger.error(f"❌ Erro em future: {e}")
        
        # Remover duplicatas com hash mais rigoroso
        seen_hashes = set()
        unique_articles = []
        
        for article in all_articles:
            # Hash baseado em título + fonte para evitar duplicatas
            content_key = f"{article['title'].lower().strip()}|{article['source']}"
            content_hash = hashlib.md5(content_key.encode()).hexdigest()
            
            if content_hash not in seen_hashes:
                seen_hashes.add(content_hash)
                unique_articles.append(article)
        
        # Ordenar por prioridade e relevância
        def sort_key(article):
            priority_scores = {'high': 100, 'medium': 50, 'low': 10}
            priority_score = priority_scores.get(article.get('priority', 'medium'), 50)
            return (priority_score, article['relevance_score'])
        
        unique_articles.sort(key=sort_key, reverse=True)
        
        # Garantir diversidade refinada
        refined_articles = []
        source_count = {}
        country_count = {}
        
        for article in unique_articles:
            source = article.get('source', 'Unknown')
            country = article.get('country', 'Global')
            
            # Limites mais restritivos para qualidade
            if (source_count.get(source, 0) < 2 and 
                country_count.get(country, 0) < 3 and
                len(refined_articles) < 20):  # Máximo 20 notícias refinadas
                
                refined_articles.append(article)
                source_count[source] = source_count.get(source, 0) + 1
                country_count[country] = country_count.get(country, 0) + 1
        
        logger.info(f"🎯 Coleta refinada concluída: {len(refined_articles)} notícias específicas de consultoria")
        return refined_articles

class PeersRefinedNewsMonitor:
    def __init__(self):
        # Lista de destinatários
        self.all_recipients = [
            "heitor.a.marin@gmail.com",
            "carlos.coelho@peers.com.br"
        ]
        
        # Apenas heitor por enquanto (limitação Resend sandbox)
        self.active_recipients = [
            "heitor.a.marin@gmail.com"
        ]
        
        self.api_key = os.getenv('RESEND_API_KEY', 're_demo_key_for_testing')
        
        # Inicializar coletor refinado
        self.news_collector = RefinedConsultingCollector()
        
        # Inicializar banco de dados
        self.init_database()
        
        # Configurar agendamento
        if schedule:
            self.setup_scheduler()
        else:
            logger.warning("⚠️ Schedule não disponível - agendamento desabilitado")
    
    def init_database(self):
        """Inicializar banco de dados para controle de duplicatas"""
        try:
            conn = sqlite3.connect('consulting_news_history.db')
            cursor = conn.cursor()
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS sent_consulting_news (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    news_hash TEXT UNIQUE,
                    title TEXT,
                    url TEXT,
                    source TEXT,
                    country TEXT,
                    language TEXT,
                    category TEXT,
                    priority TEXT,
                    relevance_score INTEGER,
                    sent_date DATETIME,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Índices para performance
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_consulting_news_hash ON sent_consulting_news(news_hash)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_consulting_sent_date ON sent_consulting_news(sent_date)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_consulting_source ON sent_consulting_news(source)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_consulting_priority ON sent_consulting_news(priority)')
            
            conn.commit()
            conn.close()
            logger.info("✅ Banco de dados refinado para consultoria inicializado")
            
        except Exception as e:
            logger.error(f"❌ Erro ao inicializar banco: {e}")
    
    def setup_scheduler(self):
        """Configurar agendamento diário às 08:00"""
        if not schedule:
            logger.warning("⚠️ Schedule não disponível")
            return
            
        schedule.every().day.at("08:00").do(self.daily_refined_consulting_job)
        logger.info("⏰ Agendamento refinado configurado: todos os dias às 08:00")
        
        # Iniciar thread do scheduler
        def run_scheduler():
            while True:
                try:
                    schedule.run_pending()
                    time.sleep(60)
                except Exception as e:
                    logger.error(f"❌ Erro no scheduler: {e}")
                    time.sleep(60)
        
        scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
        scheduler_thread.start()
    
    def daily_refined_consulting_job(self):
        """Job diário de coleta refinada de consultoria"""
        try:
            logger.info("🕐 Executando job diário REFINADO para consultoria...")
            
            # Coletar notícias refinadas
            news_items = self.collect_fresh_consulting_news()
            
            if news_items:
                # Enviar relatório
                success, message = self.send_refined_consulting_report(news_items)
                if success:
                    logger.info(f"✅ Relatório refinado enviado: {len(news_items)} notícias de consultoria")
                else:
                    logger.error(f"❌ Falha no envio refinado: {message}")
            else:
                logger.info("📰 Nenhuma notícia nova de consultoria encontrada hoje")
                
        except Exception as e:
            logger.error(f"❌ Erro no job refinado: {e}")
    
    def get_news_hash(self, title, url):
        """Gerar hash único para identificar notícias"""
        content = f"{title.lower().strip()}|{url.lower().strip()}"
        return hashlib.sha256(content.encode()).hexdigest()[:16]
    
    def is_news_already_sent(self, news_hash):
        """Verificar se notícia já foi enviada"""
        try:
            conn = sqlite3.connect('consulting_news_history.db')
            cursor = conn.cursor()
            cursor.execute('SELECT id FROM sent_consulting_news WHERE news_hash = ?', (news_hash,))
            result = cursor.fetchone()
            conn.close()
            return result is not None
        except Exception as e:
            logger.error(f"❌ Erro ao verificar duplicata: {e}")
            return False
    
    def mark_news_as_sent(self, news_item):
        """Marcar notícia como enviada"""
        try:
            news_hash = self.get_news_hash(news_item['title'], news_item['url'])
            
            conn = sqlite3.connect('consulting_news_history.db')
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR IGNORE INTO sent_consulting_news 
                (news_hash, title, url, source, country, language, category, priority, relevance_score, sent_date)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                news_hash, 
                news_item['title'], 
                news_item['url'],
                news_item.get('source', ''),
                news_item.get('country', ''),
                news_item.get('language', 'en'),
                news_item.get('category', 'Unknown'),
                news_item.get('priority', 'medium'),
                news_item.get('relevance_score', 0),
                datetime.now()
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"❌ Erro ao marcar como enviada: {e}")
    
    def collect_fresh_consulting_news(self):
        """Coletar notícias refinadas de consultoria não enviadas anteriormente"""
        # Coletar notícias refinadas
        all_news = self.news_collector.collect_refined_consulting_news()
        fresh_news = []
        
        for item in all_news:
            news_hash = self.get_news_hash(item['title'], item['url'])
            
            if not self.is_news_already_sent(news_hash):
                item['news_hash'] = news_hash
                fresh_news.append(item)
                logger.info(f"🎯 Nova consultoria: {item['title'][:50]}... ({item['source']})")
            else:
                logger.debug(f"⏭️ Já enviada: {item['title'][:30]}...")
        
        logger.info(f"📊 {len(fresh_news)} notícias frescas de consultoria coletadas")
        return fresh_news
    
    def get_peers_logo_base64(self):
        """Converter logo da Peers para base64"""
        try:
            logo_path = "/home/ubuntu/consultancy-news-agent/peers_logo.png"
            if os.path.exists(logo_path):
                with open(logo_path, "rb") as img_file:
                    return base64.b64encode(img_file.read()).decode()
            else:
                logger.warning("⚠️ Logo da Peers não encontrado")
                return None
        except Exception as e:
            logger.error(f"❌ Erro ao carregar logo: {e}")
            return None
    
    def create_refined_consulting_html_report(self, news_items):
        """Criar relatório HTML refinado focado em consultoria"""
        
        logo_base64 = self.get_peers_logo_base64()
        logo_img = f'<img src="data:image/png;base64,{logo_base64}" alt="Peers Logo" style="height: 60px; margin-bottom: 20px;">' if logo_base64 else '<h1 style="color: #1a365d; margin: 0;">PEERS</h1>'
        
        # Agrupar notícias por categoria e prioridade
        news_by_priority = {'high': [], 'medium': [], 'low': []}
        for item in news_items:
            priority = item.get('priority', 'medium')
            news_by_priority[priority].append(item)
        
        # Mapear países para flags
        country_flags = {
            'Brazil': '🇧🇷', 'Germany': '🇩🇪', 'France': '🇫🇷', 'UK': '🇬🇧',
            'Spain': '🇪🇸', 'Italy': '🇮🇹', 'Netherlands': '🇳🇱', 'Poland': '🇵🇱',
            'Portugal': '🇵🇹', 'Europe': '🇪🇺', 'Global': '🌍', 'USA': '🇺🇸'
        }
        
        news_html = ""
        item_counter = 1
        
        # Processar por prioridade
        priority_labels = {
            'high': '🔥 ALTA PRIORIDADE - Fontes Especializadas',
            'medium': '📈 MÉDIA PRIORIDADE - Mídia Econômica',
            'low': '📰 BAIXA PRIORIDADE - Outras Fontes'
        }
        
        for priority in ['high', 'medium', 'low']:
            priority_news = news_by_priority[priority]
            if not priority_news:
                continue
                
            news_html += f"""
            <div style="margin: 40px 0;">
                <h2 style="color: #1a365d; font-size: 24px; font-weight: 700; margin: 0 0 25px 0; padding: 20px 30px; background: linear-gradient(135deg, #f8fafc, #e2e8f0); border-radius: 12px; border-left: 6px solid #1a365d; box-shadow: 0 3px 10px rgba(0,0,0,0.1);">
                    {priority_labels[priority]} ({len(priority_news)} notícia{'s' if len(priority_news) > 1 else ''})
                </h2>
            """
            
            for item in priority_news:
                flag = country_flags.get(item.get('country', 'Global'), '🌍')
                language_flag = {'pt': '🇧🇷', 'en': '🇺🇸', 'fr': '🇫🇷', 'de': '🇩🇪', 'es': '🇪🇸', 'it': '🇮🇹'}.get(item.get('language', 'en'), '🌍')
                category_icon = {'Consulting RSS': '📡', 'Consulting Website': '🌐'}.get(item.get('category', 'Consulting RSS'), '🎯')
                
                # Cor do score baseada na relevância
                score_color = '#28a745' if item['relevance_score'] >= 85 else '#ffc107' if item['relevance_score'] >= 70 else '#6c757d'
                
                news_html += f"""
                <div style="background: white; margin: 30px 0; padding: 35px; border-radius: 18px; box-shadow: 0 8px 25px rgba(0,0,0,0.12); border-left: 6px solid #1a365d; transition: transform 0.2s;">
                    <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 20px;">
                        <div style="color: #1a365d; font-size: 22px; font-weight: 700; line-height: 1.3; flex: 1;">
                            {item_counter}. {item['title']}
                        </div>
                        <div style="display: flex; gap: 15px; margin-left: 25px;">
                            <div style="background: {score_color}; color: white; padding: 8px 15px; border-radius: 25px; font-size: 13px; font-weight: 700; white-space: nowrap;">
                                🎯 {item['relevance_score']}
                            </div>
                            <div style="background: #e2e8f0; color: #1a365d; padding: 8px 15px; border-radius: 25px; font-size: 13px; font-weight: 600; white-space: nowrap;">
                                {language_flag} {item.get('language', 'en').upper()}
                            </div>
                            <div style="background: #f0f9ff; color: #0369a1; padding: 8px 15px; border-radius: 25px; font-size: 13px; font-weight: 600; white-space: nowrap;">
                                {category_icon} {item.get('category', 'Consulting RSS')}
                            </div>
                        </div>
                    </div>
                    <div style="color: #666; font-size: 15px; margin-bottom: 20px; display: flex; align-items: center; gap: 25px;">
                        <span>📅 {item['date']}</span>
                        <span>🏢 {item['source']}</span>
                        <span>{flag} {item.get('country', 'Global')}</span>
                        <span style="background: #fff3cd; color: #856404; padding: 4px 10px; border-radius: 12px; font-size: 12px; font-weight: 600;">
                            {priority.upper()} PRIORITY
                        </span>
                    </div>
                    <div style="margin-bottom: 25px; line-height: 1.8; color: #444; font-size: 16px; background: #f8fafc; padding: 25px; border-radius: 12px; border-left: 4px solid #1a365d;">
                        {item['summary']}
                    </div>
                    <div style="display: flex; gap: 20px; align-items: center;">
                        <a href="{item['url']}" style="color: white; background: linear-gradient(135deg, #1a365d, #2d5a87); text-decoration: none; font-weight: 700; display: inline-flex; align-items: center; gap: 12px; padding: 15px 25px; border-radius: 12px; transition: all 0.3s; box-shadow: 0 5px 15px rgba(26, 54, 93, 0.3);" target="_blank">
                            🔗 Ler Notícia Completa
                        </a>
                        <div style="background: #d4edda; color: #155724; padding: 8px 15px; border-radius: 10px; font-size: 13px; font-weight: 700;">
                            ✅ CONSULTORIA ESPECÍFICA
                        </div>
                        <div style="background: #e1f5fe; color: #01579b; padding: 8px 15px; border-radius: 10px; font-size: 13px; font-weight: 700;">
                            {category_icon} {item.get('category', 'Consulting RSS')}
                        </div>
                    </div>
                </div>
                """
                item_counter += 1
            
            news_html += "</div>"
        
        # Estatísticas refinadas
        total_sources = len(set(item['source'] for item in news_items))
        total_countries = len(set(item.get('country', 'Global') for item in news_items))
        avg_score = sum(item['relevance_score'] for item in news_items) / len(news_items) if news_items else 0
        high_priority_count = len(news_by_priority['high'])
        
        # Top fontes especializadas
        source_counts = {}
        for item in news_items:
            source = item['source']
            source_counts[source] = source_counts.get(source, 0) + 1
        
        top_sources = sorted(source_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        top_sources_html = " • ".join([f"{source} ({count})" for source, count in top_sources])
        
        stats_html = f"""
        <div style="background: white; padding: 35px; border-radius: 18px; margin: 35px 0; border: 1px solid #e2e8f0; box-shadow: 0 6px 20px rgba(0,0,0,0.08);">
            <h3 style="color: #1a365d; margin: 0 0 25px 0; font-size: 22px; font-weight: 700;">🎯 Estatísticas do Relatório Refinado de Consultoria</h3>
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 25px; margin-bottom: 30px;">
                <div style="text-align: center; padding: 25px; background: linear-gradient(135deg, #f8fafc, #e2e8f0); border-radius: 15px;">
                    <div style="font-size: 32px; font-weight: 800; color: #1a365d;">{len(news_items)}</div>
                    <div style="font-size: 14px; color: #666; font-weight: 600;">Notícias Específicas</div>
                </div>
                <div style="text-align: center; padding: 25px; background: linear-gradient(135deg, #f8fafc, #e2e8f0); border-radius: 15px;">
                    <div style="font-size: 32px; font-weight: 800; color: #1a365d;">{high_priority_count}</div>
                    <div style="font-size: 14px; color: #666; font-weight: 600;">Alta Prioridade</div>
                </div>
                <div style="text-align: center; padding: 25px; background: linear-gradient(135deg, #f8fafc, #e2e8f0); border-radius: 15px;">
                    <div style="font-size: 32px; font-weight: 800; color: #1a365d;">{total_sources}</div>
                    <div style="font-size: 14px; color: #666; font-weight: 600;">Fontes</div>
                </div>
                <div style="text-align: center; padding: 25px; background: linear-gradient(135deg, #f8fafc, #e2e8f0); border-radius: 15px;">
                    <div style="font-size: 32px; font-weight: 800; color: #1a365d;">{avg_score:.0f}</div>
                    <div style="font-size: 14px; color: #666; font-weight: 600;">Score Médio</div>
                </div>
            </div>
            <div style="background: #f0f9ff; padding: 25px; border-radius: 12px; border-left: 5px solid #0369a1;">
                <h4 style="color: #0369a1; margin: 0 0 12px 0; font-size: 18px;">🏆 Fontes Especializadas:</h4>
                <p style="margin: 0; color: #0369a1; font-size: 15px; font-weight: 600;">{top_sources_html}</p>
            </div>
        </div>
        """
        
        # Alerta sobre sistema refinado
        refined_system_alert = """
        <div style="background: linear-gradient(135deg, #d4edda, #c3e6cb); padding: 30px; border-radius: 18px; margin: 35px 0; border: 1px solid #c3e6cb; box-shadow: 0 6px 20px rgba(0,0,0,0.08);">
            <h3 style="color: #155724; margin: 0 0 25px 0; font-size: 22px;">🎯 Sistema Refinado para Consultoria Implementado!</h3>
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 25px;">
                <div>
                    <p style="margin: 10px 0; color: #155724; font-weight: 700;">🏢 Foco Específico:</p>
                    <p style="margin: 5px 0; color: #666; font-size: 15px;">Apenas notícias sobre consultorias específicas, não economia geral</p>
                </div>
                <div>
                    <p style="margin: 10px 0; color: #155724; font-weight: 700;">🎯 Filtros Avançados:</p>
                    <p style="margin: 5px 0; color: #666; font-size: 15px;">Exclusão de termos econômicos gerais, foco em atividades de consultoria</p>
                </div>
                <div>
                    <p style="margin: 10px 0; color: #155724; font-weight: 700;">📡 Fontes Especializadas:</p>
                    <p style="margin: 5px 0; color: #666; font-size: 15px;">Consultancy.org, Management Consulted, sites das próprias firmas</p>
                </div>
                <div>
                    <p style="margin: 10px 0; color: #155724; font-weight: 700;">🔍 Threshold Alto:</p>
                    <p style="margin: 5px 0; color: #666; font-size: 15px;">Score mínimo 70+ para garantir relevância específica</p>
                </div>
            </div>
            <div style="margin-top: 25px; padding: 20px; background: rgba(255,255,255,0.8); border-radius: 12px;">
                <p style="margin: 0; color: #155724; font-weight: 700; text-align: center; font-size: 16px;">
                    ✅ Foco específico • Filtros refinados • Fontes especializadas • Qualidade premium
                </p>
            </div>
        </div>
        """
        
        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Peers Refined Consultancy News Report - {datetime.now().strftime('%d/%m/%Y')}</title>
    <style>
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }}
        a:hover {{ transform: translateY(-2px); box-shadow: 0 8px 30px rgba(26, 54, 93, 0.5) !important; }}
    </style>
</head>
<body style="font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; line-height: 1.6; color: #333; max-width: 1100px; margin: 0 auto; background: #f8fafc; padding: 25px;">
    <div style="background: white; border-radius: 25px; overflow: hidden; box-shadow: 0 20px 60px rgba(0,0,0,0.15);">
        <div style="background: linear-gradient(135deg, #1a365d 0%, #2d5a87 50%, #4a90a4 100%); color: white; padding: 60px 50px; text-align: center;">
            {logo_img}
            <h1 style="margin: 0; font-size: 40px; font-weight: 800;">Refined Consultancy News Report</h1>
            <p style="margin: 18px 0 0 0; font-size: 22px; opacity: 0.95;">Sistema Refinado • Foco Específico • Fontes Especializadas</p>
            <p style="margin: 10px 0 0 0; font-size: 20px; opacity: 0.85;">{datetime.now().strftime('%d de %B de %Y')}</p>
        </div>
        
        <div style="padding: 60px 50px; background: #f8fafc;">
            {refined_system_alert}
            {stats_html}
            
            <h2 style="color: #1a365d; font-size: 32px; font-weight: 800; margin: 60px 0 35px 0; text-align: center;">🎯 Notícias Específicas de Consultoria</h2>
            
            {news_html}
        </div>
        
        <div style="padding: 50px; text-align: center; background: #1a365d; color: white;">
            <p style="margin: 10px 0; font-size: 20px;"><strong>Peers Consulting + Technology</strong></p>
            <p style="margin: 10px 0; font-size: 18px;">Sistema Refinado para Consultoria</p>
            <p style="margin: 10px 0; font-size: 16px;">Relatório gerado em {datetime.now().strftime('%d/%m/%Y às %H:%M:%S')}</p>
            <p style="margin: 10px 0; font-size: 14px; opacity: 0.9;">Filtros específicos • {len(news_items)} notícias • {total_sources} fontes • Score médio {avg_score:.0f}</p>
        </div>
    </div>
</body>
</html>
        """
        
        return html_content
    
    def send_refined_consulting_report(self, news_items):
        """Enviar relatório refinado de consultoria"""
        try:
            url = "https://api.resend.com/emails"
            
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            html_content = self.create_refined_consulting_html_report(news_items)
            
            data = {
                "from": "Peers Refined Consulting Monitor <onboarding@resend.dev>",
                "to": self.active_recipients,
                "subject": f"🎯 Peers Refined Consultancy News - {len(news_items)} notícias específicas - {datetime.now().strftime('%d/%m/%Y')}",
                "html": html_content
            }
            
            response = requests.post(url, json=data, headers=headers, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                
                # Marcar notícias como enviadas
                for item in news_items:
                    self.mark_news_as_sent(item)
                
                sources = list(set(item['source'] for item in news_items))
                countries = list(set(item.get('country', 'Global') for item in news_items))
                high_priority = len([item for item in news_items if item.get('priority') == 'high'])
                
                logger.info(f"✅ Relatório refinado enviado! ID: {result.get('id', 'N/A')}")
                return True, f"Relatório refinado com {len(news_items)} notícias específicas de consultoria ({high_priority} alta prioridade) de {len(sources)} fontes"
            else:
                logger.error(f"❌ Erro HTTP: {response.status_code} - {response.text}")
                return False, f"Erro HTTP: {response.status_code}"
                
        except Exception as e:
            logger.error(f"❌ Erro ao enviar relatório: {e}")
            return False, str(e)

# Initialize refined news monitor
refined_news_monitor = PeersRefinedNewsMonitor()

# HEALTHCHECK ENDPOINT
@app.route('/api/status')
def api_status():
    """Endpoint de healthcheck para Railway"""
    try:
        # Contar fontes refinadas
        total_sources = 0
        for category in refined_news_monitor.news_collector.consulting_sources.values():
            if isinstance(category, dict):
                for sources in category.values():
                    total_sources += len(sources)
            elif isinstance(category, list):
                total_sources += len(category)
        
        return jsonify({
            'status': 'healthy',
            'service': 'peers_refined_consulting_monitor',
            'version': '5.0.0',
            'timestamp': datetime.now().isoformat(),
            'scheduler_active': schedule is not None and len(schedule.jobs) > 0 if schedule else False,
            'api_configured': refined_news_monitor.api_key != 're_demo_key_for_testing',
            'database_ready': True,
            'active_recipients': len(refined_news_monitor.active_recipients),
            'total_recipients': len(refined_news_monitor.all_recipients),
            'refined_filtering': True,
            'consulting_focused': True,
            'total_sources': total_sources,
            'threading_enabled': True,
            'quality_threshold': 70
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/')
def dashboard():
    """Dashboard principal refinado"""
    try:
        api_configured = refined_news_monitor.api_key and refined_news_monitor.api_key != 're_demo_key_for_testing'
        next_run = "08:00 (todos os dias)" if schedule else "Agendamento desabilitado"
        
        # Contar fontes refinadas
        total_sources = 0
        for category in refined_news_monitor.news_collector.consulting_sources.values():
            if isinstance(category, dict):
                for sources in category.values():
                    total_sources += len(sources)
            elif isinstance(category, list):
                total_sources += len(category)
        
        html_template = f"""
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Peers Refined Consulting Monitor - Foco Específico</title>
    <style>
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 0; padding: 25px; background: #f8fafc; }}
        .container {{ max-width: 1500px; margin: 0 auto; background: white; padding: 60px; border-radius: 25px; box-shadow: 0 20px 60px rgba(0,0,0,0.15); }}
        .header {{ text-align: center; border-bottom: 5px solid #1a365d; padding-bottom: 50px; margin-bottom: 60px; }}
        .header h1 {{ color: #1a365d; margin: 0; font-size: 48px; font-weight: 800; }}
        .status {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(320px, 1fr)); gap: 35px; margin-bottom: 60px; }}
        .status-card {{ background: linear-gradient(135deg, #f8fafc, #e2e8f0); padding: 35px; border-radius: 18px; border-left: 6px solid #1a365d; box-shadow: 0 6px 20px rgba(0,0,0,0.08); }}
        .status-card h3 {{ margin: 0 0 18px 0; color: #1a365d; font-weight: 700; font-size: 20px; }}
        .action-button {{ background: linear-gradient(135deg, #1a365d, #2d5a87); color: white; padding: 22px 40px; border: none; border-radius: 15px; font-size: 20px; cursor: pointer; margin: 20px; font-weight: 700; box-shadow: 0 8px 25px rgba(26, 54, 93, 0.4); transition: all 0.3s; }}
        .action-button:hover {{ transform: translateY(-3px); box-shadow: 0 12px 35px rgba(26, 54, 93, 0.5); }}
        .action-button:disabled {{ background: #6c757d; cursor: not-allowed; transform: none; }}
        .online {{ color: #28a745; font-weight: 700; }}
        .success {{ color: #28a745; font-weight: 700; }}
        .error {{ color: #dc3545; font-weight: 700; }}
        .warning {{ color: #ffc107; font-weight: 700; }}
        .refined-alert {{ background: linear-gradient(135deg, #e3f2fd, #bbdefb); padding: 35px; border-radius: 18px; margin: 35px 0; border: 1px solid #90caf9; box-shadow: 0 6px 20px rgba(0,0,0,0.08); }}
    </style>
    <script>
        async function collectRefinedNews() {{
            const button = document.getElementById('newsBtn');
            const status = document.getElementById('newsStatus');
            
            button.disabled = true;
            button.textContent = 'Coletando Especificamente...';
            status.innerHTML = '🎯 <span style="color: #1a365d;">Executando coleta refinada focada em consultoria...</span>';
            
            try {{
                const response = await fetch('/api/collect-refined-consulting');
                const result = await response.json();
                
                if (result.status === 'success') {{
                    status.innerHTML = '✅ <strong class="success">COLETA REFINADA CONCLUÍDA!</strong><br>' + result.message;
                    alert('✅ RELATÓRIO REFINADO ENVIADO! Apenas notícias específicas de consultoria.');
                }} else if (result.status === 'info') {{
                    status.innerHTML = '📰 <strong style="color: #1a365d;">INFO:</strong> ' + result.message;
                }} else {{
                    status.innerHTML = '❌ <strong class="error">Erro:</strong> ' + result.message;
                }}
            }} catch (error) {{
                status.innerHTML = '❌ <strong class="error">Erro de conexão:</strong> ' + error.message;
            }}
            
            button.disabled = false;
            button.textContent = '🎯 Coletar Especificamente';
        }}
    </script>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎯 Peers Refined Consulting Monitor</h1>
            <h2>Foco Específico - Apenas Consultoria</h2>
            <p>Filtros Refinados • Fontes Especializadas • Threshold Alto</p>
        </div>
        
        <div class="refined-alert">
            <h3 style="color: #1565c0; margin: 0 0 25px 0; font-size: 24px;">🎯 SISTEMA REFINADO PARA CONSULTORIA!</h3>
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(320px, 1fr)); gap: 30px;">
                <div>
                    <p style="margin: 12px 0; color: #1565c0; font-weight: 700;">🏢 Foco Específico:</p>
                    <p style="margin: 6px 0; color: #666; font-size: 15px;">Apenas notícias sobre consultorias específicas, não economia geral</p>
                </div>
                <div>
                    <p style="margin: 12px 0; color: #1565c0; font-weight: 700;">🎯 Filtros Avançados:</p>
                    <p style="margin: 6px 0; color: #666; font-size: 15px;">Exclusão de termos econômicos gerais, foco em atividades de consultoria</p>
                </div>
                <div>
                    <p style="margin: 12px 0; color: #1565c0; font-weight: 700;">📡 Fontes Especializadas:</p>
                    <p style="margin: 6px 0; color: #666; font-size: 15px;">Consultancy.org, Management Consulted, sites das próprias firmas</p>
                </div>
                <div>
                    <p style="margin: 12px 0; color: #1565c0; font-weight: 700;">🔍 Threshold Alto:</p>
                    <p style="margin: 6px 0; color: #666; font-size: 15px;">Score mínimo 70+ para garantir relevância específica</p>
                </div>
            </div>
        </div>
        
        <div class="status">
            <div class="status-card">
                <h3>📊 Status do Sistema</h3>
                <div class="online">✅ Online & Healthcheck OK</div>
            </div>
            <div class="status-card">
                <h3>📧 Configuração Email</h3>
                <div class="{'online' if api_configured else 'error'}">
                    {'✅ Resend API Ativo' if api_configured else '❌ API Key Necessária'}
                </div>
            </div>
            <div class="status-card">
                <h3>⏰ Agendamento</h3>
                <div class="{'online' if schedule else 'warning'}">
                    {'✅ ' + next_run if schedule else '⚠️ Schedule não disponível'}
                </div>
            </div>
            <div class="status-card">
                <h3>🎯 Sistema Refinado</h3>
                <div class="online">✅ Filtros Específicos</div>
            </div>
            <div class="status-card">
                <h3>🏢 Fontes Consultoria</h3>
                <div class="online">✅ {total_sources} Especializadas</div>
            </div>
            <div class="status-card">
                <h3>👥 Destinatários</h3>
                <div class="warning">⚠️ {len(refined_news_monitor.active_recipients)}/{len(refined_news_monitor.all_recipients)} ativos</div>
                <small>Carlos: domínio necessário</small>
            </div>
        </div>
        
        <div style="text-align: center; margin: 60px 0;">
            <button id="newsBtn" class="action-button" onclick="collectRefinedNews()">🎯 Coletar Especificamente</button>
            <div id="newsStatus" style="margin-top: 30px; font-size: 20px;"></div>
        </div>
        
        <div style="background: linear-gradient(135deg, #e3f2fd, #bbdefb); padding: 30px; border-radius: 18px; margin-top: 35px; border: 1px solid #90caf9;">
            <h4>🎯 Sistema Refinado para Consultoria</h4>
            <p>✅ <strong>Foco específico:</strong> Apenas notícias sobre consultorias, não economia geral</p>
            <p>✅ <strong>Filtros avançados:</strong> Exclusão de termos econômicos, foco em atividades de consultoria</p>
            <p>✅ <strong>Fontes especializadas:</strong> Consultancy.org, Management Consulted, sites das firmas</p>
            <p>✅ <strong>Threshold alto:</strong> Score mínimo 70+ para garantir relevância específica</p>
            <p>✅ <strong>Priorização:</strong> Fontes especializadas têm prioridade sobre mídia geral</p>
        </div>
    </div>
</body>
</html>
        """
        
        return render_template_string(html_template)
    except Exception as e:
        logger.error(f"Dashboard error: {e}")
        return f"Dashboard error: {e}", 500

@app.route('/api/collect-refined-consulting')
def api_collect_refined_consulting():
    """API endpoint para coleta refinada de consultoria"""
    try:
        logger.info("🎯 Iniciando coleta refinada específica para consultoria...")
        
        # Coletar notícias refinadas
        news_items = refined_news_monitor.collect_fresh_consulting_news()
        
        if not news_items:
            return jsonify({
                'status': 'info',
                'message': 'Nenhuma notícia nova específica de consultoria encontrada (filtros refinados funcionando)',
                'news_count': 0,
                'timestamp': datetime.now().isoformat()
            })
        
        # Enviar relatório
        success, message = refined_news_monitor.send_refined_consulting_report(news_items)
        
        if success:
            countries = list(set(item.get('country', 'Global') for item in news_items))
            sources = list(set(item.get('source', 'Unknown') for item in news_items))
            high_priority = len([item for item in news_items if item.get('priority') == 'high'])
            avg_score = sum(item['relevance_score'] for item in news_items) / len(news_items) if news_items else 0
            
            logger.info("✅ Relatório refinado de consultoria enviado!")
            return jsonify({
                'status': 'success',
                'message': message,
                'news_count': len(news_items),
                'high_priority_count': high_priority,
                'countries': len(countries),
                'sources': len(sources),
                'avg_score': round(avg_score, 1),
                'recipients': len(refined_news_monitor.active_recipients),
                'refined_filtering': True,
                'consulting_focused': True,
                'timestamp': datetime.now().isoformat()
            })
        else:
            logger.error(f"❌ Falha no envio refinado: {message}")
            return jsonify({
                'status': 'error',
                'message': f'Falha no envio refinado: {message}',
                'timestamp': datetime.now().isoformat()
            }), 500
            
    except Exception as e:
        logger.error(f"❌ Erro na coleta refinada: {e}")
        return jsonify({
            'status': 'error',
            'message': f'Erro interno na coleta refinada: {str(e)}',
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/health')
def health():
    """Health check endpoint alternativo"""
    return jsonify({
        'status': 'healthy',
        'service': 'peers_refined_consulting_monitor',
        'timestamp': datetime.now().isoformat()
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    logger.info(f"🎯 Starting REFINED CONSULTING MONITOR server on port {port}")
    app.run(host='0.0.0.0', port=port, debug=False)
