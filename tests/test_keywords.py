from app.analyzers.keywords import KeywordResearchAnalyzer
from app.providers.google_suggest import GoogleSuggestProvider


def test_keyword_research_generates_local_commercial_terms() -> None:
    result = KeywordResearchAnalyzer().analyze("dentistas", "Curitiba")

    keywords = [item["keyword"] for item in result["terms"]]
    intents = [item["intent"] for item in result["terms"]]

    assert "dentistas em Curitiba" in keywords
    assert "orcamento dentistas Curitiba" in keywords
    assert "high" in intents
    assert "transactional" in intents


def test_keyword_research_merges_suggestions_without_duplicates() -> None:
    result = KeywordResearchAnalyzer().analyze(
        "dentistas",
        "Curitiba",
        suggestions=["dentistas em Curitiba", "dentistas preco Curitiba"],
    )

    terms = result["terms"]
    keywords = [item["keyword"] for item in terms]
    suggest_terms = [item for item in terms if item["source"] == "suggest"]

    assert keywords.count("dentistas em Curitiba") == 1
    assert suggest_terms[0]["keyword"] == "dentistas preco Curitiba"
    assert suggest_terms[0]["intent"] == "transactional"


def test_google_suggest_dedupes_and_normalizes_terms() -> None:
    result = GoogleSuggestProvider._dedupe([" dentista curitiba ", "Dentista Curitiba", ""])

    assert result == ["dentista curitiba"]
