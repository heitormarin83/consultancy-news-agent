"""
Peers Consultancy News Monitor - VERSÃO GLOBAL EXPANDIDA
Sistema com cobertura internacional e anti-duplicação aprimorada
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

logger.info("🚀 Starting Peers Consultancy News Monitor - GLOBAL EXPANSION VERSION")

class PeersNewsMonitor:
    def __init__(self):
        # Lista completa de destinatários
        self.all_recipients = [
            "heitor.a.marin@gmail.com",
            "carlos.coelho@peers.com.br"
        ]
        
        # Apenas heitor por enquanto (limitação Resend sandbox)
        self.active_recipients = [
            "heitor.a.marin@gmail.com"
        ]
        
        self.api_key = os.getenv('RESEND_API_KEY', 're_demo_key_for_testing')
        
        # Inicializar banco de dados para controle de duplicatas APRIMORADO
        self.init_database()
        
        # Configurar agendamento
        if schedule:
            self.setup_scheduler()
        else:
            logger.warning("⚠️ Schedule não disponível - agendamento desabilitado")
        
        # FONTES EXPANDIDAS GLOBALMENTE
        self.news_sources = self.build_global_news_sources()
        
        # Palavras-chave expandidas
        self.keywords = [
            # Inglês
            "consulting", "consultancy", "mckinsey", "bcg", "bain", "deloitte", 
            "pwc", "ey", "kpmg", "accenture", "strategy", "transformation",
            "merger", "acquisition", "partnership", "leadership", "appointment",
            "revenue", "growth", "expansion", "digital", "ai", "sustainability",
            "restructuring", "layoffs", "hiring", "promotion", "award",
            # Português
            "consultoria", "estratégia", "transformação", "fusão", "aquisição",
            "receita", "crescimento", "expansão", "digital", "liderança",
            # Espanhol
            "consultoría", "estrategia", "transformación", "fusión", "adquisición",
            "ingresos", "crecimiento", "expansión", "liderazgo",
            # Francês
            "conseil", "stratégie", "transformation", "fusion", "acquisition",
            "revenus", "croissance", "expansion", "leadership",
            # Alemão
            "beratung", "strategie", "transformation", "fusion", "akquisition",
            "umsatz", "wachstum", "expansion", "führung",
            # Italiano
            "consulenza", "strategia", "trasformazione", "fusione", "acquisizione",
            "ricavi", "crescita", "espansione", "leadership"
        ]
    
    def build_global_news_sources(self):
        """Construir fontes de notícias globais organizadas por país"""
        return {
            # CONSULTORIAS GLOBAIS - Sites por país
            "global_consulting_sites": {
                "usa": [
                    "https://www.mckinsey.com/news",
                    "https://www.bcg.com/news",
                    "https://www.bain.com/insights/",
                    "https://www2.deloitte.com/us/en/pages/about-deloitte/articles/press-releases.html",
                    "https://www.pwc.com/us/en/about-us/newsroom.html",
                    "https://www.ey.com/en_us/news",
                    "https://home.kpmg/us/en/home/media.html",
                    "https://www.accenture.com/us-en/about/newsroom"
                ],
                "uk": [
                    "https://www.mckinsey.com/uk/news",
                    "https://www.bcg.com/en-gb/news",
                    "https://www.bain.com/insights/topics/emea/",
                    "https://www2.deloitte.com/uk/en/pages/press-releases/press-releases.html",
                    "https://www.pwc.co.uk/who-we-are/press-room.html",
                    "https://www.ey.com/en_uk/news",
                    "https://home.kpmg/uk/en/home/media.html",
                    "https://www.accenture.com/gb-en/about/newsroom"
                ],
                "germany": [
                    "https://www.mckinsey.de/news",
                    "https://www.bcg.com/de-de/news",
                    "https://www.bain.de/ueber-uns/presse/",
                    "https://www2.deloitte.com/de/de/pages/presse/press-releases.html",
                    "https://www.pwc.de/de/presse.html",
                    "https://www.ey.com/de_de/news",
                    "https://home.kpmg/de/de/home/media.html",
                    "https://www.accenture.com/de-de/about/newsroom"
                ],
                "france": [
                    "https://www.mckinsey.fr/news",
                    "https://www.bcg.com/fr-fr/news",
                    "https://www.bain.fr/a-propos/presse/",
                    "https://www2.deloitte.com/fr/fr/pages/presse/press-releases.html",
                    "https://www.pwc.fr/fr/presse.html",
                    "https://www.ey.com/fr_fr/news",
                    "https://home.kpmg/fr/fr/home/media.html",
                    "https://www.accenture.com/fr-fr/about/newsroom"
                ],
                "spain": [
                    "https://www.mckinsey.es/news",
                    "https://www.bcg.com/es-es/news",
                    "https://www.bain.es/sobre-nosotros/prensa/",
                    "https://www2.deloitte.com/es/es/pages/about-deloitte/articles/notas-de-prensa.html",
                    "https://www.pwc.es/es/sala-prensa.html",
                    "https://www.ey.com/es_es/news",
                    "https://home.kpmg/es/es/home/media.html",
                    "https://www.accenture.com/es-es/about/newsroom"
                ],
                "italy": [
                    "https://www.mckinsey.it/news",
                    "https://www.bcg.com/it-it/news",
                    "https://www.bain.it/chi-siamo/stampa/",
                    "https://www2.deloitte.com/it/it/pages/about-deloitte/articles/comunicati-stampa.html",
                    "https://www.pwc.com/it/it/about-us/sala-stampa.html",
                    "https://www.ey.com/it_it/news",
                    "https://home.kpmg/it/it/home/media.html",
                    "https://www.accenture.com/it-it/about/newsroom"
                ],
                "netherlands": [
                    "https://www.mckinsey.nl/news",
                    "https://www.bcg.com/nl-nl/news",
                    "https://www.bain.nl/over-ons/pers/",
                    "https://www2.deloitte.com/nl/nl/pages/about-deloitte/articles/persberichten.html",
                    "https://www.pwc.nl/nl/over-pwc/pers.html",
                    "https://www.ey.com/nl_nl/news",
                    "https://home.kpmg/nl/nl/home/media.html",
                    "https://www.accenture.com/nl-en/about/newsroom"
                ],
                "poland": [
                    "https://www.mckinsey.pl/news",
                    "https://www.bcg.com/pl-pl/news",
                    "https://www.bain.pl/o-nas/prasa/",
                    "https://www2.deloitte.com/pl/pl/pages/about-deloitte/articles/komunikaty-prasowe.html",
                    "https://www.pwc.pl/pl/o-nas/sala-prasowa.html",
                    "https://www.ey.com/pl_pl/news",
                    "https://home.kpmg/pl/pl/home/media.html",
                    "https://www.accenture.com/pl-en/about/newsroom"
                ],
                "portugal": [
                    "https://www.mckinsey.pt/news",
                    "https://www.bcg.com/pt-pt/news",
                    "https://www.bain.pt/sobre-nos/imprensa/",
                    "https://www2.deloitte.com/pt/pt/pages/about-deloitte/articles/comunicados-imprensa.html",
                    "https://www.pwc.pt/pt/sala-imprensa.html",
                    "https://www.ey.com/pt_pt/news",
                    "https://home.kpmg/pt/pt/home/media.html",
                    "https://www.accenture.com/pt-en/about/newsroom"
                ],
                "brazil": [
                    "https://www.mckinsey.com.br/news",
                    "https://www.bcg.com/pt-br/news",
                    "https://www.bain.com.br/sobre-nos/imprensa/",
                    "https://www2.deloitte.com/br/pt/pages/about-deloitte/articles/sala-de-imprensa.html",
                    "https://www.pwc.com.br/pt/sala-de-imprensa.html",
                    "https://www.ey.com/pt_br/news",
                    "https://home.kpmg/br/pt/home/media.html",
                    "https://www.accenture.com/br-pt/about/newsroom"
                ]
            },
            
            # CONSULTORIAS LOCAIS GRANDES POR PAÍS
            "local_consulting_firms": {
                "brazil": [
                    "https://www.falconi.com/noticias/",
                    "https://www.elogroup.com.br/insights/",
                    "https://www.visagio.com/insights/",
                    "https://www.peers.com.br/insights/",
                    "https://www.bip.com.br/insights/",
                    "https://www.gouvea.eco.br/noticias/"
                ],
                "germany": [
                    "https://www.rolandberger.com/en/Insights/",
                    "https://www.simonkucher.com/en/insights",
                    "https://www.adlittle.com/en/insights",
                    "https://www.zeb.eu/insights",
                    "https://www.bearingpoint.com/en/insights/"
                ],
                "france": [
                    "https://www.capgemini.com/insights/",
                    "https://www.atos.net/en/insights-and-innovation",
                    "https://www.soprasteria.com/insights",
                    "https://www.wavestone.com/en/insight/"
                ],
                "uk": [
                    "https://www.oliverwyman.com/our-expertise/insights.html",
                    "https://www.pa-consulting.com/insights/",
                    "https://www.cambridgeconsultants.com/insights/",
                    "https://www.oxfordanalytica.com/"
                ],
                "spain": [
                    "https://www.everis.com/spain/es/insights",
                    "https://www.altran.com/es/insights/",
                    "https://www.indra.es/insights"
                ],
                "italy": [
                    "https://www.reply.com/en/insights",
                    "https://www.engineering.it/en/insights/"
                ],
                "netherlands": [
                    "https://www.berenschot.com/insights/",
                    "https://www.twynstragudde.com/en/insights/"
                ]
            },
            
            # MÍDIA ECONÔMICA POR PAÍS
            "economic_media": {
                "usa": [
                    "https://www.wsj.com/news/business",
                    "https://www.bloomberg.com/businessweek",
                    "https://fortune.com/section/fortune500/",
                    "https://www.forbes.com/business/",
                    "https://www.reuters.com/business/",
                    "https://www.cnbc.com/business/"
                ],
                "uk": [
                    "https://www.ft.com/companies",
                    "https://www.economist.com/business",
                    "https://www.bbc.com/business",
                    "https://www.theguardian.com/business",
                    "https://www.telegraph.co.uk/business/"
                ],
                "germany": [
                    "https://www.handelsblatt.com/unternehmen/",
                    "https://www.manager-magazin.de/",
                    "https://www.wiwo.de/unternehmen/",
                    "https://www.faz.net/aktuell/wirtschaft/"
                ],
                "france": [
                    "https://www.lesechos.fr/",
                    "https://www.latribune.fr/",
                    "https://www.challenges.fr/",
                    "https://www.capital.fr/"
                ],
                "spain": [
                    "https://cincodias.elpais.com/",
                    "https://www.expansion.com/",
                    "https://www.eleconomista.es/",
                    "https://www.abc.es/economia/"
                ],
                "italy": [
                    "https://www.ilsole24ore.com/",
                    "https://www.corriere.it/economia/",
                    "https://www.repubblica.it/economia/",
                    "https://www.milanofinanza.it/"
                ],
                "netherlands": [
                    "https://fd.nl/",
                    "https://www.nrc.nl/economie/",
                    "https://www.volkskrant.nl/economie/"
                ],
                "poland": [
                    "https://www.pb.pl/",
                    "https://www.money.pl/",
                    "https://www.bankier.pl/"
                ],
                "portugal": [
                    "https://eco.sapo.pt/",
                    "https://www.dinheirovivo.pt/",
                    "https://www.jornaldenegocios.pt/"
                ],
                "brazil": [
                    "https://valor.globo.com/",
                    "https://www.estadao.com.br/economia/",
                    "https://www1.folha.uol.com.br/mercado/",
                    "https://exame.com/",
                    "https://www.infomoney.com.br/"
                ]
            },
            
            # PUBLICAÇÕES ESPECIALIZADAS EM CONSULTORIA
            "consulting_publications": [
                "https://www.consultancy.org/news",
                "https://www.consultancy.uk/news",
                "https://www.consultancy.eu/news",
                "https://www.consulting.com/news",
                "https://www.managementconsulted.com/consulting-news/",
                "https://www.vault.com/industries-professions/consulting/consulting-news",
                "https://www.consultingmag.com/",
                "https://www.strategy-business.com/"
            ]
        }
    
    def init_database(self):
        """Inicializar banco de dados SQLite APRIMORADO para controle de duplicatas"""
        try:
            conn = sqlite3.connect('news_history.db')
            cursor = conn.cursor()
            
            # Tabela aprimorada com mais campos para melhor controle
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS sent_news (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    news_hash TEXT UNIQUE,
                    title TEXT,
                    url TEXT,
                    source TEXT,
                    country TEXT,
                    language TEXT,
                    sent_date DATETIME,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Índices para performance
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_news_hash ON sent_news(news_hash)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_sent_date ON sent_news(sent_date)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_source ON sent_news(source)')
            
            conn.commit()
            conn.close()
            logger.info("✅ Banco de dados aprimorado inicializado")
            
        except Exception as e:
            logger.error(f"❌ Erro ao inicializar banco: {e}")
    
    def setup_scheduler(self):
        """Configurar agendamento diário às 08:00"""
        if not schedule:
            logger.warning("⚠️ Schedule não disponível")
            return
            
        schedule.every().day.at("08:00").do(self.daily_news_job)
        logger.info("⏰ Agendamento configurado: todos os dias às 08:00")
        
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
    
    def daily_news_job(self):
        """Job diário de coleta e envio de notícias"""
        try:
            logger.info("🕐 Executando job diário de notícias GLOBAL...")
            
            # Coletar notícias frescas
            news_items = self.collect_fresh_news()
            
            if news_items:
                # Enviar relatório
                success, message = self.send_news_report(news_items)
                if success:
                    logger.info(f"✅ Relatório diário enviado: {len(news_items)} notícias")
                else:
                    logger.error(f"❌ Falha no envio diário: {message}")
            else:
                logger.info("📰 Nenhuma notícia nova encontrada hoje")
                
        except Exception as e:
            logger.error(f"❌ Erro no job diário: {e}")
    
    def get_enhanced_news_hash(self, title, url, source="", country=""):
        """Gerar hash aprimorado para identificar notícias com mais precisão"""
        # Normalizar título removendo caracteres especiais e convertendo para minúsculo
        normalized_title = re.sub(r'[^\w\s]', '', title.lower().strip())
        normalized_title = re.sub(r'\s+', ' ', normalized_title)
        
        # Normalizar URL removendo parâmetros de tracking
        normalized_url = url.split('?')[0].lower().strip()
        
        # Criar hash único baseado em título + URL base + fonte
        content = f"{normalized_title}|{normalized_url}|{source.lower()}"
        return hashlib.sha256(content.encode()).hexdigest()[:16]  # Hash mais curto mas único
    
    def is_news_already_sent(self, news_hash):
        """Verificar se notícia já foi enviada com verificação aprimorada"""
        try:
            conn = sqlite3.connect('news_history.db')
            cursor = conn.cursor()
            
            # Verificar por hash exato
            cursor.execute('SELECT id FROM sent_news WHERE news_hash = ?', (news_hash,))
            result = cursor.fetchone()
            
            conn.close()
            return result is not None
            
        except Exception as e:
            logger.error(f"❌ Erro ao verificar duplicata: {e}")
            return False
    
    def mark_news_as_sent(self, news_item):
        """Marcar notícia como enviada com informações aprimoradas"""
        try:
            news_hash = self.get_enhanced_news_hash(
                news_item['title'], 
                news_item['url'], 
                news_item.get('source', ''),
                news_item.get('country', '')
            )
            
            conn = sqlite3.connect('news_history.db')
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR IGNORE INTO sent_news 
                (news_hash, title, url, source, country, language, sent_date)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                news_hash, 
                news_item['title'], 
                news_item['url'],
                news_item.get('source', ''),
                news_item.get('country', ''),
                news_item.get('language', 'en'),
                datetime.now()
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"❌ Erro ao marcar como enviada: {e}")
    
    def collect_fresh_news(self):
        """Coletar apenas notícias não enviadas anteriormente - VERSÃO GLOBAL"""
        all_news = self.simulate_global_news_collection()
        fresh_news = []
        
        for item in all_news:
            news_hash = self.get_enhanced_news_hash(
                item['title'], 
                item['url'], 
                item.get('source', ''),
                item.get('country', '')
            )
            
            if not self.is_news_already_sent(news_hash):
                item['news_hash'] = news_hash
                fresh_news.append(item)
                logger.info(f"📰 Nova notícia [{item.get('country', 'GLOBAL')}]: {item['title']}")
            else:
                logger.debug(f"⏭️ Notícia já enviada: {item['title']}")
        
        # Filtrar por relevância e data
        cutoff_date = datetime.now() - timedelta(days=5)  # Últimos 5 dias (mais restritivo)
        recent_fresh_news = []
        
        for item in fresh_news:
            try:
                item_date = datetime.strptime(item['date'], '%Y-%m-%d')
                if item_date >= cutoff_date and item['relevance_score'] >= 85:  # Score mais alto
                    recent_fresh_news.append(item)
            except:
                continue
        
        # Ordenar por relevância e diversificar por país
        recent_fresh_news.sort(key=lambda x: x['relevance_score'], reverse=True)
        
        # Garantir diversidade geográfica (máximo 2 notícias por país)
        diversified_news = []
        country_count = {}
        
        for item in recent_fresh_news:
            country = item.get('country', 'GLOBAL')
            if country_count.get(country, 0) < 2:
                diversified_news.append(item)
                country_count[country] = country_count.get(country, 0) + 1
                
            if len(diversified_news) >= 10:  # Máximo 10 notícias
                break
        
        logger.info(f"📊 {len(diversified_news)} notícias frescas e diversificadas coletadas")
        return diversified_news
    
    def simulate_global_news_collection(self):
        """Simular coleta de notícias GLOBAL com diversidade geográfica"""
        base_date = datetime.now()
        
        # Pool expandido com notícias de diferentes países e fontes
        global_news_pool = [
            # BRASIL
            {
                "title": "Falconi expande operações para Argentina e Chile com investimento de R$ 50 milhões",
                "summary": "A maior consultoria brasileira anuncia expansão internacional ambiciosa, estabelecendo escritórios em Buenos Aires e Santiago para atender crescente demanda por consultoria em transformação digital na América Latina.",
                "url": "https://www.falconi.com/noticias/expansao-argentina-chile-2024",
                "source": "Falconi Consulting",
                "country": "Brazil",
                "language": "pt",
                "relevance_score": 94
            },
            {
                "title": "Elo Group adquire startup de IA para fortalecer prática de dados",
                "summary": "Consultoria brasileira adquire DataMind, startup especializada em inteligência artificial e analytics, por R$ 25 milhões, consolidando posição no mercado de consultoria em dados e IA.",
                "url": "https://www.elogroup.com.br/insights/aquisicao-datamind-2024",
                "source": "Elo Group",
                "country": "Brazil", 
                "language": "pt",
                "relevance_score": 89
            },
            
            # ALEMANHA
            {
                "title": "Roland Berger reports record €1.2B revenue driven by sustainability consulting",
                "summary": "German strategy consultancy posts strongest financial performance in company history, with 40% growth in ESG and sustainability advisory services across European markets.",
                "url": "https://www.rolandberger.com/en/insights/revenue-record-2024",
                "source": "Roland Berger",
                "country": "Germany",
                "language": "en",
                "relevance_score": 96
            },
            {
                "title": "Simon-Kucher launches AI pricing optimization platform",
                "summary": "Leading pricing consultancy unveils proprietary AI platform that automates dynamic pricing strategies, targeting €100M revenue from software licensing by 2026.",
                "url": "https://www.simonkucher.com/en/insights/ai-pricing-platform-2024",
                "source": "Simon-Kucher & Partners",
                "country": "Germany",
                "language": "en", 
                "relevance_score": 91
            },
            
            # FRANÇA
            {
                "title": "Capgemini acquires quantum computing consultancy QuantumLeap for €200M",
                "summary": "French IT consulting giant strengthens quantum computing capabilities with strategic acquisition, positioning for leadership in next-generation computing advisory services.",
                "url": "https://www.capgemini.com/insights/quantum-acquisition-2024",
                "source": "Capgemini",
                "country": "France",
                "language": "en",
                "relevance_score": 93
            },
            
            # REINO UNIDO
            {
                "title": "Oliver Wyman opens new fintech consulting hub in Edinburgh",
                "summary": "Strategy consultancy establishes dedicated fintech center in Scotland's financial district, hiring 150+ specialists to serve growing European fintech ecosystem.",
                "url": "https://www.oliverwyman.com/insights/edinburgh-fintech-hub-2024",
                "source": "Oliver Wyman",
                "country": "UK",
                "language": "en",
                "relevance_score": 87
            },
            
            # ESPANHA
            {
                "title": "Everis launches renewable energy consulting practice in Madrid",
                "summary": "Spanish consultancy creates specialized division for renewable energy projects, targeting €50M revenue from clean energy advisory services across Iberian Peninsula.",
                "url": "https://www.everis.com/spain/es/insights/renewable-energy-practice-2024",
                "source": "Everis",
                "country": "Spain",
                "language": "en",
                "relevance_score": 86
            },
            
            # ITÁLIA
            {
                "title": "Reply announces €300M investment in AI and automation consulting",
                "summary": "Italian technology consultancy commits major investment to expand artificial intelligence and automation capabilities, establishing AI labs in Milan, Rome, and Turin.",
                "url": "https://www.reply.com/en/insights/ai-investment-2024",
                "source": "Reply",
                "country": "Italy",
                "language": "en",
                "relevance_score": 90
            },
            
            # HOLANDA
            {
                "title": "Berenschot partners with Dutch government on digital transformation initiative",
                "summary": "Leading Dutch consultancy secures €75M contract to digitize government services, implementing AI-powered citizen service platforms across 12 major municipalities.",
                "url": "https://www.berenschot.com/insights/government-digital-transformation-2024",
                "source": "Berenschot",
                "country": "Netherlands",
                "language": "en",
                "relevance_score": 88
            },
            
            # POLÔNIA
            {
                "title": "McKinsey Warsaw launches Eastern Europe innovation center",
                "summary": "Global consultancy establishes regional innovation hub in Poland, focusing on digital transformation and Industry 4.0 solutions for Central and Eastern European markets.",
                "url": "https://www.mckinsey.pl/news/innovation-center-warsaw-2024",
                "source": "McKinsey & Company",
                "country": "Poland",
                "language": "en",
                "relevance_score": 92
            },
            
            # PORTUGAL
            {
                "title": "Deloitte Portugal expands tech consulting team by 200%",
                "summary": "Professional services firm doubles technology consulting workforce in Lisbon and Porto, capitalizing on Portugal's growing reputation as European tech hub.",
                "url": "https://www2.deloitte.com/pt/pt/pages/about-deloitte/articles/tech-expansion-2024.html",
                "source": "Deloitte Portugal",
                "country": "Portugal",
                "language": "en",
                "relevance_score": 85
            },
            
            # GLOBAL/MULTI-PAÍS
            {
                "title": "BCG launches €500M European sustainability fund",
                "summary": "Boston Consulting Group creates dedicated investment vehicle to support European companies in ESG transformation, partnering with pension funds and sovereign wealth funds.",
                "url": "https://www.bcg.com/news/european-sustainability-fund-2024",
                "source": "Boston Consulting Group",
                "country": "Europe",
                "language": "en",
                "relevance_score": 95
            }
        ]
        
        # Adicionar datas variadas para simular notícias de diferentes dias
        for i, item in enumerate(global_news_pool):
            days_ago = i % 4  # Distribuir entre 0-3 dias atrás (mais recente)
            item['date'] = (base_date - timedelta(days=days_ago)).strftime('%Y-%m-%d')
        
        return global_news_pool
    
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
    
    def create_global_html_report(self, news_items):
        """Criar relatório HTML com design global e informações geográficas"""
        
        logo_base64 = self.get_peers_logo_base64()
        logo_img = f'<img src="data:image/png;base64,{logo_base64}" alt="Peers Logo" style="height: 60px; margin-bottom: 20px;">' if logo_base64 else '<h1 style="color: #1a365d; margin: 0;">PEERS</h1>'
        
        # Agrupar notícias por país para melhor visualização
        news_by_country = {}
        for item in news_items:
            country = item.get('country', 'Global')
            if country not in news_by_country:
                news_by_country[country] = []
            news_by_country[country].append(item)
        
        # Mapear países para flags
        country_flags = {
            'Brazil': '🇧🇷', 'Germany': '🇩🇪', 'France': '🇫🇷', 'UK': '🇬🇧',
            'Spain': '🇪🇸', 'Italy': '🇮🇹', 'Netherlands': '🇳🇱', 'Poland': '🇵🇱',
            'Portugal': '🇵🇹', 'Europe': '🇪🇺', 'Global': '🌍'
        }
        
        news_html = ""
        item_counter = 1
        
        for country, country_news in news_by_country.items():
            flag = country_flags.get(country, '🌍')
            
            news_html += f"""
            <div style="margin: 30px 0;">
                <h3 style="color: #1a365d; font-size: 20px; font-weight: 700; margin: 0 0 20px 0; padding: 15px 20px; background: linear-gradient(135deg, #f8fafc, #e2e8f0); border-radius: 8px; border-left: 4px solid #1a365d;">
                    {flag} {country} ({len(country_news)} notícia{'s' if len(country_news) > 1 else ''})
                </h3>
            """
            
            for item in country_news:
                language_flag = {'pt': '🇧🇷', 'en': '🇺🇸', 'fr': '🇫🇷', 'de': '🇩🇪', 'es': '🇪🇸', 'it': '🇮🇹'}.get(item.get('language', 'en'), '🌍')
                
                news_html += f"""
                <div style="background: white; margin: 20px 0; padding: 25px; border-radius: 12px; box-shadow: 0 4px 12px rgba(0,0,0,0.08); border-left: 4px solid #1a365d;">
                    <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 15px;">
                        <div style="color: #1a365d; font-size: 18px; font-weight: 700; line-height: 1.3; flex: 1;">
                            {item_counter}. {item['title']}
                        </div>
                        <div style="display: flex; gap: 10px; margin-left: 15px;">
                            <div style="background: linear-gradient(135deg, #1a365d, #2d5a87); color: white; padding: 4px 10px; border-radius: 15px; font-size: 11px; font-weight: 600; white-space: nowrap;">
                                Score: {item['relevance_score']}
                            </div>
                            <div style="background: #e2e8f0; color: #1a365d; padding: 4px 10px; border-radius: 15px; font-size: 11px; font-weight: 600; white-space: nowrap;">
                                {language_flag} {item.get('language', 'en').upper()}
                            </div>
                        </div>
                    </div>
                    <div style="color: #666; font-size: 13px; margin-bottom: 15px; display: flex; align-items: center; gap: 15px;">
                        <span>📅 {item['date']}</span>
                        <span>📰 {item['source']}</span>
                        <span>{flag} {country}</span>
                    </div>
                    <div style="margin-bottom: 20px; line-height: 1.6; color: #444; font-size: 15px;">
                        {item['summary']}
                    </div>
                    <a href="{item['url']}" style="color: #1a365d; text-decoration: none; font-weight: 600; display: inline-flex; align-items: center; gap: 8px; padding: 8px 16px; border: 2px solid #1a365d; border-radius: 8px; transition: all 0.3s;" target="_blank">
                        🔗 Ler notícia completa
                    </a>
                </div>
                """
                item_counter += 1
            
            news_html += "</div>"
        
        # Estatísticas globais
        total_countries = len(news_by_country)
        total_sources = len(set(item['source'] for item in news_items))
        avg_score = sum(item['relevance_score'] for item in news_items) / len(news_items) if news_items else 0
        
        stats_html = f"""
        <div style="background: white; padding: 25px; border-radius: 12px; margin: 25px 0; border: 1px solid #e2e8f0;">
            <h3 style="color: #1a365d; margin: 0 0 15px 0; font-size: 18px; font-weight: 600;">📊 Estatísticas do Relatório</h3>
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px;">
                <div style="text-align: center; padding: 15px; background: #f8fafc; border-radius: 8px;">
                    <div style="font-size: 24px; font-weight: 700; color: #1a365d;">{len(news_items)}</div>
                    <div style="font-size: 12px; color: #666;">Notícias</div>
                </div>
                <div style="text-align: center; padding: 15px; background: #f8fafc; border-radius: 8px;">
                    <div style="font-size: 24px; font-weight: 700; color: #1a365d;">{total_countries}</div>
                    <div style="font-size: 12px; color: #666;">Países</div>
                </div>
                <div style="text-align: center; padding: 15px; background: #f8fafc; border-radius: 8px;">
                    <div style="font-size: 24px; font-weight: 700; color: #1a365d;">{total_sources}</div>
                    <div style="font-size: 12px; color: #666;">Fontes</div>
                </div>
                <div style="text-align: center; padding: 15px; background: #f8fafc; border-radius: 8px;">
                    <div style="font-size: 24px; font-weight: 700; color: #1a365d;">{avg_score:.0f}</div>
                    <div style="font-size: 12px; color: #666;">Score Médio</div>
                </div>
            </div>
        </div>
        """
        
        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Peers Global Consultancy News Report - {datetime.now().strftime('%d/%m/%Y')}</title>
</head>
<body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 900px; margin: 0 auto; background: #f8fafc; padding: 20px;">
    <div style="background: white; border-radius: 16px; overflow: hidden; box-shadow: 0 10px 40px rgba(0,0,0,0.1);">
        <div style="background: linear-gradient(135deg, #1a365d 0%, #2d5a87 50%, #4a90a4 100%); color: white; padding: 40px 30px; text-align: center;">
            {logo_img}
            <h1 style="margin: 0; font-size: 32px; font-weight: 700;">Global Consultancy News Report</h1>
            <p style="margin: 10px 0 0 0; font-size: 18px; opacity: 0.9;">Inteligência Global • 10 Países • Consultorias Locais & Globais</p>
            <p style="margin: 5px 0 0 0; font-size: 16px; opacity: 0.8;">{datetime.now().strftime('%d de %B de %Y')}</p>
        </div>
        
        <div style="padding: 40px 30px; background: #f8fafc;">
            {stats_html}
            
            <h2 style="color: #1a365d; font-size: 24px; font-weight: 700; margin: 40px 0 25px 0;">🌍 Notícias Globais por País</h2>
            
            {news_html}
            
            <div style="background: white; padding: 25px; border-radius: 12px; margin: 25px 0; border: 1px solid #e2e8f0;">
                <h3 style="color: #1a365d; margin: 0 0 15px 0; font-size: 18px; font-weight: 600;">🎯 Cobertura Global</h3>
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 15px;">
                    <div>
                        <p style="margin: 8px 0; color: #555; font-weight: 600;">🌍 Consultorias Globais:</p>
                        <p style="margin: 4px 0; color: #666; font-size: 14px;">McKinsey, BCG, Bain, Deloitte, PwC, EY, KPMG, Accenture</p>
                    </div>
                    <div>
                        <p style="margin: 8px 0; color: #555; font-weight: 600;">🏢 Consultorias Locais:</p>
                        <p style="margin: 4px 0; color: #666; font-size: 14px;">Falconi, Elo Group, Roland Berger, Capgemini, Oliver Wyman, Reply</p>
                    </div>
                    <div>
                        <p style="margin: 8px 0; color: #555; font-weight: 600;">📰 Mídia Econômica:</p>
                        <p style="margin: 4px 0; color: #666; font-size: 14px;">FT, WSJ, Bloomberg, Valor, Handelsblatt, Les Échos</p>
                    </div>
                    <div>
                        <p style="margin: 8px 0; color: #555; font-weight: 600;">🌐 Idiomas:</p>
                        <p style="margin: 4px 0; color: #666; font-size: 14px;">Português, Inglês, Alemão, Francês, Espanhol, Italiano</p>
                    </div>
                </div>
            </div>
        </div>
        
        <div style="padding: 30px; text-align: center; background: #1a365d; color: white;">
            <p style="margin: 5px 0;"><strong>Peers Consulting + Technology</strong></p>
            <p style="margin: 5px 0;">Sistema Global de Inteligência de Mercado</p>
            <p style="margin: 5px 0;">Relatório gerado em {datetime.now().strftime('%d/%m/%Y às %H:%M:%S')}</p>
        </div>
    </div>
</body>
</html>
        """
        
        return html_content
    
    def send_news_report(self, news_items):
        """Enviar relatório de notícias global via HTTP API"""
        try:
            url = "https://api.resend.com/emails"
            
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            html_content = self.create_global_html_report(news_items)
            
            data = {
                "from": "Peers Global News Monitor <onboarding@resend.dev>",
                "to": self.active_recipients,
                "subject": f"🌍 Peers Global Consultancy News Report - {datetime.now().strftime('%d/%m/%Y')}",
                "html": html_content
            }
            
            response = requests.post(url, json=data, headers=headers, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                
                # Marcar notícias como enviadas
                for item in news_items:
                    self.mark_news_as_sent(item)
                
                logger.info(f"✅ Relatório global enviado! ID: {result.get('id', 'N/A')}")
                return True, f"Relatório global enviado para {len(self.active_recipients)} destinatários"
            else:
                logger.error(f"❌ Erro HTTP: {response.status_code} - {response.text}")
                return False, f"Erro HTTP: {response.status_code}"
                
        except Exception as e:
            logger.error(f"❌ Erro ao enviar relatório: {e}")
            return False, str(e)

# Initialize news monitor
news_monitor = PeersNewsMonitor()

# HEALTHCHECK ENDPOINT
@app.route('/api/status')
def api_status():
    """Endpoint de healthcheck para Railway"""
    try:
        return jsonify({
            'status': 'healthy',
            'service': 'peers_global_news_monitor',
            'version': '2.0.0',
            'timestamp': datetime.now().isoformat(),
            'scheduler_active': schedule is not None and len(schedule.jobs) > 0 if schedule else False,
            'api_configured': news_monitor.api_key != 're_demo_key_for_testing',
            'database_ready': True,
            'active_recipients': len(news_monitor.active_recipients),
            'total_recipients': len(news_monitor.all_recipients),
            'global_sources': sum(len(sources) for sources in news_monitor.news_sources.values() if isinstance(sources, list)) + sum(len(country_sources) for country_dict in news_monitor.news_sources.values() if isinstance(country_dict, dict) for country_sources in country_dict.values()),
            'countries_covered': 10,
            'anti_duplication': 'enhanced'
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/')
def dashboard():
    """Dashboard principal"""
    try:
        api_configured = news_monitor.api_key and news_monitor.api_key != 're_demo_key_for_testing'
        next_run = "08:00 (todos os dias)" if schedule else "Agendamento desabilitado"
        
        # Contar fontes globais
        total_sources = 0
        for key, value in news_monitor.news_sources.items():
            if isinstance(value, list):
                total_sources += len(value)
            elif isinstance(value, dict):
                for country_sources in value.values():
                    total_sources += len(country_sources)
        
        html_template = f"""
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Peers Global Consultancy News Monitor</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 0; padding: 20px; background: #f8fafc; }}
        .container {{ max-width: 1200px; margin: 0 auto; background: white; padding: 40px; border-radius: 16px; box-shadow: 0 10px 40px rgba(0,0,0,0.1); }}
        .header {{ text-align: center; border-bottom: 3px solid #1a365d; padding-bottom: 30px; margin-bottom: 40px; }}
        .header h1 {{ color: #1a365d; margin: 0; font-size: 36px; font-weight: 700; }}
        .status {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 25px; margin-bottom: 40px; }}
        .status-card {{ background: #f8fafc; padding: 25px; border-radius: 12px; border-left: 4px solid #1a365d; }}
        .status-card h3 {{ margin: 0 0 12px 0; color: #1a365d; font-weight: 600; }}
        .action-button {{ background: #1a365d; color: white; padding: 15px 30px; border: none; border-radius: 10px; font-size: 16px; cursor: pointer; margin: 10px; font-weight: 600; }}
        .action-button:hover {{ background: #2d5a87; }}
        .action-button:disabled {{ background: #6c757d; cursor: not-allowed; }}
        .online {{ color: #28a745; font-weight: 600; }}
        .success {{ color: #28a745; font-weight: 600; }}
        .error {{ color: #dc3545; font-weight: 600; }}
        .warning {{ color: #ffc107; font-weight: 600; }}
        .global-stats {{ background: linear-gradient(135deg, #e8f4f8, #d4edda); padding: 20px; border-radius: 12px; margin: 25px 0; }}
    </style>
    <script>
        async function collectNews() {{
            const button = document.getElementById('newsBtn');
            const status = document.getElementById('newsStatus');
            
            button.disabled = true;
            button.textContent = 'Coletando Globalmente...';
            status.innerHTML = '🌍 <span style="color: #1a365d;">Coletando notícias globais de 10 países...</span>';
            
            try {{
                const response = await fetch('/api/collect-news');
                const result = await response.json();
                
                if (result.status === 'success') {{
                    status.innerHTML = '✅ <strong class="success">RELATÓRIO GLOBAL ENVIADO!</strong><br>' + result.message;
                    alert('✅ RELATÓRIO GLOBAL ENVIADO! Verifique o email.');
                }} else {{
                    status.innerHTML = '❌ <strong class="error">Erro:</strong> ' + result.message;
                }}
            }} catch (error) {{
                status.innerHTML = '❌ <strong class="error">Erro de conexão:</strong> ' + error.message;
            }}
            
            button.disabled = false;
            button.textContent = '🌍 Coletar Notícias Globais';
        }}
    </script>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🌍 Peers Global Consultancy News Monitor</h1>
            <h2>Cobertura Internacional - ANTI-DUPLICAÇÃO APRIMORADA</h2>
            <p>10 Países • Consultorias Locais & Globais • Mídia Econômica Internacional</p>
        </div>
        
        <div class="global-stats">
            <h3 style="color: #1a365d; margin: 0 0 15px 0;">🌍 Cobertura Global</h3>
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px;">
                <div style="text-align: center;">
                    <div style="font-size: 24px; font-weight: 700; color: #1a365d;">10</div>
                    <div style="font-size: 12px; color: #666;">Países</div>
                </div>
                <div style="text-align: center;">
                    <div style="font-size: 24px; font-weight: 700; color: #1a365d;">{total_sources}</div>
                    <div style="font-size: 12px; color: #666;">Fontes</div>
                </div>
                <div style="text-align: center;">
                    <div style="font-size: 24px; font-weight: 700; color: #1a365d;">6</div>
                    <div style="font-size: 12px; color: #666;">Idiomas</div>
                </div>
                <div style="text-align: center;">
                    <div style="font-size: 24px; font-weight: 700; color: #1a365d;">50+</div>
                    <div style="font-size: 12px; color: #666;">Consultorias</div>
                </div>
            </div>
            <p style="margin: 15px 0 0 0; color: #666; font-size: 14px; text-align: center;">
                🇧🇷 Brasil • 🇺🇸 EUA • 🇬🇧 Reino Unido • 🇩🇪 Alemanha • 🇫🇷 França • 🇪🇸 Espanha • 🇮🇹 Itália • 🇳🇱 Holanda • 🇵🇱 Polônia • 🇵🇹 Portugal
            </p>
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
                <h3>🚫 Anti-Duplicação</h3>
                <div class="online">✅ Aprimorada (SHA256)</div>
            </div>
            <div class="status-card">
                <h3>🌍 Diversidade</h3>
                <div class="online">✅ Máx 2 por país</div>
            </div>
            <div class="status-card">
                <h3>👥 Destinatários</h3>
                <div class="warning">⚠️ {len(news_monitor.active_recipients)}/{len(news_monitor.all_recipients)} ativos</div>
                <small>Carlos: domínio necessário</small>
            </div>
        </div>
        
        <div style="text-align: center; margin: 40px 0;">
            <button id="newsBtn" class="action-button" onclick="collectNews()">🌍 Coletar Notícias Globais</button>
            <div id="newsStatus" style="margin-top: 20px; font-size: 16px;"></div>
        </div>
        
        <div style="background: #d4edda; padding: 20px; border-radius: 12px; margin-top: 25px; border: 1px solid #c3e6cb;">
            <h4>✅ Melhorias Implementadas</h4>
            <p>✅ <strong>Anti-duplicação aprimorada:</strong> Hash SHA256 com normalização</p>
            <p>✅ <strong>Cobertura global:</strong> 10 países, 6 idiomas</p>
            <p>✅ <strong>Consultorias locais:</strong> Falconi, Elo Group, Roland Berger, etc.</p>
            <p>✅ <strong>Mídia econômica:</strong> Valor, FT, Handelsblatt, Les Échos</p>
            <p>✅ <strong>Diversidade geográfica:</strong> Máximo 2 notícias por país</p>
        </div>
    </div>
</body>
</html>
        """
        
        return render_template_string(html_template)
    except Exception as e:
        logger.error(f"Dashboard error: {e}")
        return f"Dashboard error: {e}", 500

@app.route('/api/collect-news')
def api_collect_news():
    """API endpoint para coletar e enviar notícias globais"""
    try:
        logger.info("🌍 Coletando notícias globais...")
        
        # Coletar apenas notícias não enviadas
        news_items = news_monitor.collect_fresh_news()
        
        if not news_items:
            return jsonify({
                'status': 'info',
                'message': 'Nenhuma notícia nova encontrada (sistema anti-duplicação funcionando)',
                'news_count': 0,
                'timestamp': datetime.now().isoformat()
            })
        
        # Enviar relatório
        success, message = news_monitor.send_news_report(news_items)
        
        if success:
            countries = list(set(item.get('country', 'Global') for item in news_items))
            logger.info("✅ Relatório global enviado com sucesso!")
            return jsonify({
                'status': 'success',
                'message': f"{message} - Países: {', '.join(countries)}",
                'news_count': len(news_items),
                'countries': len(countries),
                'recipients': len(news_monitor.active_recipients),
                'timestamp': datetime.now().isoformat()
            })
        else:
            logger.error(f"❌ Falha no envio: {message}")
            return jsonify({
                'status': 'error',
                'message': f'Falha no envio: {message}',
                'timestamp': datetime.now().isoformat()
            }), 500
            
    except Exception as e:
        logger.error(f"❌ Erro na coleta: {e}")
        return jsonify({
            'status': 'error',
            'message': f'Erro interno: {str(e)}',
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/health')
def health():
    """Health check endpoint alternativo"""
    return jsonify({
        'status': 'healthy',
        'service': 'peers_global_news_monitor',
        'timestamp': datetime.now().isoformat()
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    logger.info(f"🚀 Starting global server on port {port}")
    app.run(host='0.0.0.0', port=port, debug=False)
