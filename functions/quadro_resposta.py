import os
from functions.pokeapi import get_pokemon_data, get_description


class Quadro:

    def montar_resposta(self, pokemon_id_or_name):
        try:
            pokemon = get_pokemon_data(pokemon_id_or_name)
        except Exception as exc:
            return None, f"Pokemon não encontrado: {exc}"

        description = get_description(pokemon["id"]) or "Descrição não disponível."

        linha = os.linesep
        tipos = ", ".join(pokemon["types"])

        texto = (
            f"<b><u>SOBRE</u></b>{linha}"
            f"{description}{linha}{linha}"
            f"<b><u>TIPAGEM</u></b>{linha}"
            f"{tipos}{linha}{linha}"
            f"<b><u>ATRIBUTOS BASE</u></b>{linha}{linha}"
            f"ATAQUE   -> <b>{pokemon['attack']}</b>{linha}"
            f"DEFESA   -> <b>{pokemon['defense']}</b>{linha}"
            f"STAMINA  -> <b>{pokemon['hp']}</b>{linha}{linha}"
            f"ALTURA   -> {pokemon['height']} m{linha}"
            f"PESO     -> {pokemon['weight']} kg"
        )

        return pokemon, texto
