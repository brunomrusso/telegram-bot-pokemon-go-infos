import os
from functions.pokeapi import (
    get_pokemon_data,
    get_description,
    get_species_data,
    get_evolution_chain,
    get_damage_chart,
    format_types,
    emoji_for_type,
)


class Quadro:

    def montar_resposta(self, pokemon_id_or_name):
        try:
            pokemon = get_pokemon_data(pokemon_id_or_name)
        except Exception as exc:
            return None, f"Pokémon não encontrado: {exc}"

        species = get_species_data(pokemon["id"])
        description = get_description(pokemon["id"]) or "Descrição não disponível."
        evolution = get_evolution_chain(species.get("evolution_chain_url"))
        damage_chart = get_damage_chart(pokemon["types"])

        linha = os.linesep

        # Emoji principal baseado no primeiro tipo
        emoji_principal = emoji_for_type(pokemon["types"][0]) if pokemon["types"] else ""

        header = (
            f"{emoji_principal} <b>{pokemon['name']} #{pokemon['id']}</b>{linha}"
            f"Tipo: {format_types(pokemon['types'])}{linha}"
            f"Categoria: {species['category']} | Geração: {species['generation']}"
        )

        atributos = (
            f"<b><u>ATRIBUTOS BASE</u></b>{linha}"
            f"ATAQUE   -> <b>{pokemon['attack']}</b>{linha}"
            f"DEFESA   -> <b>{pokemon['defense']}</b>{linha}"
            f"STAMINA  -> <b>{pokemon['hp']}</b>{linha}{linha}"
            f"ALTURA   -> {pokemon['height']} m{linha}"
            f"PESO     -> {pokemon['weight']} kg"
        )

        fraquezas = self._format_damage_chart(damage_chart, linha)

        evolucao = ""
        if evolution:
            evolucao = f"{linha}{linha}<b><u>EVOLUÇÃO</u></b>{linha}{evolution}"

        texto = (
            f"{header}{linha}{linha}"
            f"<b><u>SOBRE</u></b>{linha}"
            f"{description}{linha}{linha}"
            f"{fraquezas}{linha}{linha}"
            f"{atributos}"
            f"{evolucao}"
        )

        return pokemon, texto

    def _format_damage_chart(self, damage_chart, linha):
        ordem = ["4×", "2×", "1×", "½×", "¼×", "0×"]
        partes = []

        for key in ordem:
            if key in damage_chart and damage_chart[key]:
                nomes = ", ".join(
                    f"{emoji_for_type(t)} {format_single_type(t)}"
                    for t in damage_chart[key]
                )
                partes.append(f"<b>{key}</b>: {nomes}")

        if not partes:
            return "<b><u>EFETIVIDADE</u></b>\nNenhuma informação disponível."

        return f"<b><u>EFETIVIDADE DE ATAQUES</u></b>{linha}" + f"{linha}".join(partes)


def format_single_type(type_name):
    from functions.pokeapi import translate_type
    return translate_type(type_name)
