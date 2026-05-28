from app.analyzers.digital_presence import DigitalPresenceAnalyzer
from app.analyzers.opportunity_score import OpportunityScoreAnalyzer
from app.analyzers.seo import SeoAnalyzer


def test_analysis_prioritizes_lead_without_website_and_reviews() -> None:
    lead = {
        "name": "Clinica Exemplo",
        "website": None,
        "phone": None,
        "rating": 3.6,
        "review_count": 4,
    }

    digital_presence = DigitalPresenceAnalyzer().analyze(lead)
    seo = SeoAnalyzer().analyze(lead)
    opportunity = OpportunityScoreAnalyzer().calculate(
        {"digital_presence": digital_presence, "seo": seo}
    )

    assert digital_presence["presence_level"] == "weak"
    assert seo["status"] == "missing_website"
    assert opportunity["priority"] == "high"
    assert opportunity["score"] >= 70
