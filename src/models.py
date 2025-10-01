"""
Data models for Consultancy News Agent
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import List, Optional, Dict, Any
import json

class Region(Enum):
    """Geographic regions"""
    US = "United States"
    EUROPE = "Europe"
    GLOBAL = "Global"

class ConsultancyType(Enum):
    """Types of consultancy firms"""
    BIG4 = "Big 4"
    MBB = "MBB"
    GLOBAL = "Global"
    REGIONAL = "Regional"
    BOUTIQUE = "Boutique"

class NewsCategory(Enum):
    """Categories of news"""
    EXECUTIVE_MOVE = "Executive Movement"
    CORPORATE_CHANGE = "Corporate Change"
    CONTRACT_WIN = "Contract Win"
    PARTNERSHIP = "Partnership"
    AWARD = "Award"
    EXPANSION = "Expansion"
    ACQUISITION = "Acquisition"
    OTHER = "Other"

@dataclass
class ConsultancyFirm:
    """Represents a consultancy firm"""
    name: str
    type: ConsultancyType
    region: Region
    aliases: List[str] = field(default_factory=list)
    website: Optional[str] = None
    headquarters: Optional[str] = None
    
    def matches(self, text: str) -> bool:
        """Check if text mentions this firm"""
        text_lower = text.lower()
        
        # Check main name
        if self.name.lower() in text_lower:
            return True
        
        # Check aliases
        for alias in self.aliases:
            if alias.lower() in text_lower:
                return True
        
        return False

@dataclass
class NewsArticle:
    """Represents a news article about consultancy"""
    title: str
    url: str
    source: str
    summary: Optional[str] = None
    content: Optional[str] = None
    date_published: Optional[datetime] = None
    date_collected: datetime = field(default_factory=datetime.now)
    
    # Analysis fields
    relevance_score: float = 0.0
    category: Optional[NewsCategory] = None
    firms_mentioned: List[str] = field(default_factory=list)
    region: Optional[Region] = None
    
    # Metadata
    source_priority: str = "medium"
    language: str = "en"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            'title': self.title,
            'url': self.url,
            'source': self.source,
            'summary': self.summary,
            'content': self.content,
            'date_published': self.date_published.isoformat() if self.date_published else None,
            'date_collected': self.date_collected.isoformat(),
            'relevance_score': self.relevance_score,
            'category': self.category.value if self.category else None,
            'firms_mentioned': self.firms_mentioned,
            'region': self.region.value if self.region else None,
            'source_priority': self.source_priority,
            'language': self.language
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'NewsArticle':
        """Create from dictionary"""
        article = cls(
            title=data['title'],
            url=data['url'],
            source=data['source'],
            summary=data.get('summary'),
            content=data.get('content'),
            date_published=datetime.fromisoformat(data['date_published']) if data.get('date_published') else None,
            date_collected=datetime.fromisoformat(data['date_collected']) if data.get('date_collected') else datetime.now(),
            relevance_score=data.get('relevance_score', 0.0),
            firms_mentioned=data.get('firms_mentioned', []),
            source_priority=data.get('source_priority', 'medium'),
            language=data.get('language', 'en')
        )
        
        # Set enums
        if data.get('category'):
            try:
                article.category = NewsCategory(data['category'])
            except ValueError:
                article.category = NewsCategory.OTHER
        
        if data.get('region'):
            try:
                article.region = Region(data['region'])
            except ValueError:
                article.region = None
        
        return article

@dataclass
class DailyReport:
    """Daily report containing analyzed articles"""
    date: str
    total_articles: int
    high_relevance_articles: int
    articles_by_region: Dict[str, int]
    articles_by_firm: Dict[str, int]
    articles_by_category: Dict[str, int]
    top_articles: List[NewsArticle]
    summary: str
    
    # Metadata
    collection_time: datetime = field(default_factory=datetime.now)
    analysis_criteria: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            'date': self.date,
            'total_articles': self.total_articles,
            'high_relevance_articles': self.high_relevance_articles,
            'articles_by_region': self.articles_by_region,
            'articles_by_firm': self.articles_by_firm,
            'articles_by_category': self.articles_by_category,
            'top_articles': [article.to_dict() for article in self.top_articles],
            'summary': self.summary,
            'collection_time': self.collection_time.isoformat(),
            'analysis_criteria': self.analysis_criteria
        }
    
    def to_json(self) -> str:
        """Convert to JSON string"""
        return json.dumps(self.to_dict(), indent=2, ensure_ascii=False)

# Predefined consultancy firms
CONSULTANCY_FIRMS = [
    # BIG 4
    ConsultancyFirm(
        name="Deloitte",
        type=ConsultancyType.BIG4,
        region=Region.GLOBAL,
        aliases=["Deloitte Consulting", "Deloitte & Touche", "DTT"],
        website="https://www2.deloitte.com"
    ),
    ConsultancyFirm(
        name="PwC",
        type=ConsultancyType.BIG4,
        region=Region.GLOBAL,
        aliases=["PricewaterhouseCoopers", "PwC Consulting", "Price Waterhouse"],
        website="https://www.pwc.com"
    ),
    ConsultancyFirm(
        name="EY",
        type=ConsultancyType.BIG4,
        region=Region.GLOBAL,
        aliases=["Ernst & Young", "EY Consulting", "Ernst and Young"],
        website="https://www.ey.com"
    ),
    ConsultancyFirm(
        name="KPMG",
        type=ConsultancyType.BIG4,
        region=Region.GLOBAL,
        aliases=["KPMG Consulting", "KPMG Advisory"],
        website="https://home.kpmg"
    ),
    
    # MBB
    ConsultancyFirm(
        name="McKinsey & Company",
        type=ConsultancyType.MBB,
        region=Region.GLOBAL,
        aliases=["McKinsey", "McK"],
        website="https://www.mckinsey.com"
    ),
    ConsultancyFirm(
        name="Boston Consulting Group",
        type=ConsultancyType.MBB,
        region=Region.GLOBAL,
        aliases=["BCG", "Boston Consulting"],
        website="https://www.bcg.com"
    ),
    ConsultancyFirm(
        name="Bain & Company",
        type=ConsultancyType.MBB,
        region=Region.GLOBAL,
        aliases=["Bain", "Bain Consulting"],
        website="https://www.bain.com"
    ),
    
    # Global Consultancies
    ConsultancyFirm(
        name="Accenture",
        type=ConsultancyType.GLOBAL,
        region=Region.GLOBAL,
        aliases=["Accenture Consulting", "ACN"],
        website="https://www.accenture.com"
    ),
    ConsultancyFirm(
        name="IBM Consulting",
        type=ConsultancyType.GLOBAL,
        region=Region.GLOBAL,
        aliases=["IBM", "IBM Global Services", "IBM Business Consulting"],
        website="https://www.ibm.com/consulting"
    ),
    ConsultancyFirm(
        name="Capgemini",
        type=ConsultancyType.GLOBAL,
        region=Region.GLOBAL,
        aliases=["Capgemini Consulting", "Cap Gemini"],
        website="https://www.capgemini.com"
    ),
    
    # Regional Consultancies
    ConsultancyFirm(
        name="Oliver Wyman",
        type=ConsultancyType.REGIONAL,
        region=Region.GLOBAL,
        aliases=["Oliver Wyman Group"],
        website="https://www.oliverwyman.com"
    ),
    ConsultancyFirm(
        name="Roland Berger",
        type=ConsultancyType.REGIONAL,
        region=Region.EUROPE,
        aliases=["Roland Berger Strategy Consultants"],
        website="https://www.rolandberger.com"
    ),
    ConsultancyFirm(
        name="A.T. Kearney",
        type=ConsultancyType.REGIONAL,
        region=Region.GLOBAL,
        aliases=["AT Kearney", "Kearney"],
        website="https://www.kearney.com"
    ),
    ConsultancyFirm(
        name="Booz Allen Hamilton",
        type=ConsultancyType.REGIONAL,
        region=Region.US,
        aliases=["Booz Allen", "BAH"],
        website="https://www.boozallen.com"
    ),
    ConsultancyFirm(
        name="L.E.K. Consulting",
        type=ConsultancyType.REGIONAL,
        region=Region.GLOBAL,
        aliases=["LEK", "L.E.K."],
        website="https://www.lek.com"
    ),
    ConsultancyFirm(
        name="Strategy&",
        type=ConsultancyType.REGIONAL,
        region=Region.GLOBAL,
        aliases=["Strategy and", "PwC Strategy&", "Booz & Company"],
        website="https://www.strategyand.pwc.com"
    )
]

def get_firm_by_name(name: str) -> Optional[ConsultancyFirm]:
    """Get consultancy firm by name or alias"""
    name_lower = name.lower()
    
    for firm in CONSULTANCY_FIRMS:
        if firm.name.lower() == name_lower:
            return firm
        
        for alias in firm.aliases:
            if alias.lower() == name_lower:
                return firm
    
    return None

def identify_firms_in_text(text: str) -> List[ConsultancyFirm]:
    """Identify consultancy firms mentioned in text"""
    mentioned_firms = []
    text_lower = text.lower()
    
    for firm in CONSULTANCY_FIRMS:
        if firm.matches(text):
            mentioned_firms.append(firm)
    
    return mentioned_firms

