import requests

BASE_URL = "https://pokeapi.co/api/v2"

TYPE_TRANSLATIONS = {
    "normal": "Normal",
    "fire": "Fogo",
    "water": "Água",
    "electric": "Elétrico",
    "grass": "Grama",
    "ice": "Gelo",
    "fighting": "Lutador",
    "poison": "Venenoso",
    "ground": "Terrestre",
    "flying": "Voador",
    "psychic": "Psíquico",
    "bug": "Inseto",
    "rock": "Pedra",
    "ghost": "Fantasma",
    "dragon": "Dragão",
    "dark": "Sombrio",
    "steel": "Aço",
    "fairy": "Fada",
}


def _get(path):
    response = requests.get(f"{BASE_URL}{path}", timeout=30)
    response.raise_for_status()
    return response.json()


def get_pokemon_data(name_or_id):
    """Busca dados básicos do Pokémon na PokeAPI."""
    data = _get(f"/pokemon/{name_or_id}")

    types = [t["type"]["name"] for t in data["types"]]
    types_pt = [TYPE_TRANSLATIONS.get(t, t.capitalize()) for t in types]

    stats = {s["stat"]["name"]: s["base_stat"] for s in data["stats"]}

    sprites = data.get("sprites", {})
    other = sprites.get("other", {})
    official = other.get("official-artwork", {})

    return {
        "id": data["id"],
        "name": data["name"].capitalize(),
        "types": types_pt,
        "hp": stats.get("hp", "?"),
        "attack": stats.get("attack", "?"),
        "defense": stats.get("defense", "?"),
        "height": data.get("height", 0) / 10.0,
        "weight": data.get("weight", 0) / 10.0,
        "sprite_normal": official.get("front_default") or sprites.get("front_default"),
        "sprite_shiny": official.get("front_shiny") or sprites.get("front_shiny"),
    }


def get_description(pokemon_id):
    """Busca a descrição mais recente do Pokémon em português, espanhol ou inglês."""
    try:
        species = _get(f"/pokemon-species/{pokemon_id}")
    except requests.HTTPError:
        return None

    entries = species.get("flavor_text_entries", [])

    for lang_priority in ["pt", "es", "en"]:
        for entry in reversed(entries):
            if entry["language"]["name"] == lang_priority:
                text = entry["flavor_text"].replace("\n", " ").replace("\f", " ")
                return text

    return None
