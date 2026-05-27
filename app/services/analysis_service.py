from app.analyzers.digital_presence import DigitalPresenceAnalyzer
from app.analyzers.opportunity_score import OpportunityScoreAnalyzer
from app.analyzers.seo import SeoAnalyzer


class AnalysisService:
    def __init__(self) -> None:
        self.digital_presence = DigitalPresenceAnalyzer()
        self.seo = SeoAnalyzer()
        self.opportunity_score = OpportunityScoreAnalyzer()
