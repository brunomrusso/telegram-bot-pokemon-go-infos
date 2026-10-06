import requests
from collections import defaultdict

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

TYPE_EMOJIS = {
    "normal": "⚪",
    "fire": "🔥",
    "water": "💧",
    "electric": "⚡",
    "grass": "🌿",
    "ice": "❄️",
    "fighting": "🥊",
    "poison": "☠️",
    "ground": "🌍",
    "flying": "🪽",
    "psychic": "🔮",
    "bug": "🐛",
    "rock": "🪨",
    "ghost": "👻",
    "dragon": "🐉",
    "dark": "🌑",
    "steel": "⚙️",
    "fairy": "🧚",
}

GENERATION_TRANSLATIONS = {
    "generation-i": "Kanto",
    "generation-ii": "Johto",
    "generation-iii": "Hoenn",
    "generation-iv": "Sinnoh",
    "generation-v": "Unova",
    "generation-vi": "Kalos",
    "generation-vii": "Alola",
    "generation-viii": "Galar",
    "generation-ix": "Paldea",
}


def _get(path):
    response = requests.get(f"{BASE_URL}{path}", timeout=30)
    response.raise_for_status()
    return response.json()


def translate_type(name):
    return TYPE_TRANSLATIONS.get(name, name.capitalize())


def emoji_for_type(name):
    return TYPE_EMOJIS.get(name, "")


def format_types(types):
    return ", ".join(f"{emoji_for_type(t)} {translate_type(t)}" for t in types)


def get_pokemon_data(name_or_id):
    """Busca dados básicos do Pokémon na PokeAPI."""
    data = _get(f"/pokemon/{name_or_id}")

    types = [t["type"]["name"] for t in data["types"]]

    stats = {s["stat"]["name"]: s["base_stat"] for s in data["stats"]}

    sprites = data.get("sprites", {})
    other = sprites.get("other", {})
    official = other.get("official-artwork", {})

    return {
        "id": data["id"],
        "name": data["name"].capitalize(),
        "types": types,
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


def get_species_data(pokemon_id):
    """Busca dados da espécie: categoria, geração e URL da cadeia evolutiva."""
    species = _get(f"/pokemon-species/{pokemon_id}")

    category = "Normal"
    if species.get("is_baby"):
        category = "Bebê"
    elif species.get("is_legendary"):
        category = "Lendário"
    elif species.get("is_mythical"):
        category = "Mítico"

    generation = species.get("generation", {}).get("name", "")
    generation = GENERATION_TRANSLATIONS.get(generation, generation)

    evolution_chain_url = species.get("evolution_chain", {}).get("url")

    return {
        "category": category,
        "generation": generation,
        "evolution_chain_url": evolution_chain_url,
    }


def get_evolution_chain(evolution_chain_url):
    """Extrai a cadeia evolutiva em formato de texto linear."""
    if not evolution_chain_url:
        return None

    try:
        data = requests.get(evolution_chain_url, timeout=30).json()
    except Exception:
        return None

    chain = data.get("chain", {})
    if not chain:
        return None

    stages = []
    current = chain
    while current:
        species_name = current["species"]["name"].capitalize()
        stages.append(species_name)

        evolves_to = current.get("evolves_to", [])
        if not evolves_to:
            break

        # Pega o primeiro caminho de evolução para simplificar
        current = evolves_to[0]

    return " → ".join(stages) if len(stages) > 1 else None


def get_type_damage_relations(type_name):
    """Retorna dicionário com multiplicadores de dano recebido pelo tipo."""
    data = _get(f"/type/{type_name}")
    relations = data.get("damage_relations", {})

    multipliers = defaultdict(lambda: 1.0)

    for type_info in relations.get("double_damage_from", []):
        multipliers[type_info["name"]] *= 2.0

    for type_info in relations.get("half_damage_from", []):
        multipliers[type_info["name"]] *= 0.5

    for type_info in relations.get("no_damage_from", []):
        multipliers[type_info["name"]] = 0.0

    return multipliers


def get_damage_chart(types):
    """Calcula a efetividade de tipos ofensivos contra a combinação de tipos do Pokémon."""
    combined = defaultdict(lambda: 1.0)

    for type_name in types:
        relations = get_type_damage_relations(type_name)
        for attacker, multiplier in relations.items():
            if multiplier == 0.0:
                combined[attacker] = 0.0
            else:
                combined[attacker] *= multiplier

    chart = defaultdict(list)
    for attacker, multiplier in combined.items():
        # Agrupa por faixa de multiplicador
        if multiplier == 0.0:
            chart["0×"].append(attacker)
        elif multiplier <= 0.25:
            chart["¼×"].append(attacker)
        elif multiplier <= 0.5:
            chart["½×"].append(attacker)
        elif multiplier >= 4.0:
            chart["4×"].append(attacker)
        elif multiplier >= 2.0:
            chart["2×"].append(attacker)
        else:
            chart["1×"].append(attacker)

    # Ordena as listas para ficar consistente
    for key in chart:
        chart[key].sort()

    return chart
