def geocoding_key(location: str) -> str:
    return f"geocoding:v1:{location.lower().strip()}"


def places_search_key(niche: str, location: str, radius_meters: int) -> str:
    return f"places_search:v1:{niche.lower().strip()}:{location.lower().strip()}:{radius_meters}"


def place_details_key(place_id: str) -> str:
    return f"place_details:v1:{place_id}"


def seo_key(url: str) -> str:
    return f"seo:v1:{url.lower().strip()}"
