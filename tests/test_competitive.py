from app.analyzers.competitive import CompetitiveAnalyzer
from app.analyzers.opportunity_score import OpportunityScoreAnalyzer


def test_competitive_analyzer_flags_weaker_local_presence() -> None:
    lead = {
        "id": "lead-1",
        "name": "Clinica Nova",
        "rating": 3.8,
        "review_count": 4,
        "website": None,
        "phone": None,
    }
    competitors = [
        {
            "id": "lead-2",
            "name": "Clinica Forte",
            "rating": 4.7,
            "review_count": 80,
            "website": "https://example.com",
            "phone": "123",
        },
        {
            "id": "lead-3",
            "name": "Clinica Media",
            "rating": 4.2,
            "review_count": 20,
            "website": "https://example.org",
            "phone": "456",
        },
    ]

    result = CompetitiveAnalyzer().compare(lead, competitors)

    assert result["status"] == "compared"
    assert result["benchmarks"]["average_rating"] == 4.45
    assert "Nota abaixo da media dos concorrentes" in result["issues"]
    assert "Concorrentes possuem site com mais frequencia" in result["issues"]


def test_opportunity_score_uses_competitive_disadvantages() -> None:
    result = OpportunityScoreAnalyzer().calculate(
        {
            "digital_presence": {"signals": {"has_website": True, "has_phone": True, "rating": 4.5, "review_count": 60}},
            "seo": {"status": "checked", "issues": []},
            "competitive": {"status": "compared", "issues": ["Volume de avaliacoes abaixo da media local"]},
        }
    )

    assert result["score"] == 5
    assert "Desvantagens frente a concorrentes locais" in result["reasons"]
