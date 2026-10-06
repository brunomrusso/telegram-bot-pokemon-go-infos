"""
Criado por Bruno Martinez Russo
Abril/2021 | Refatorado em Outubro/2026
"""
import json
import os
import requests

from functions.quadro_resposta import Quadro
from table.info_json import TableInfo


class TelegramBot:
    def __init__(self):
        self.token = os.environ.get("TOKEN")
        if not self.token:
            raise RuntimeError("Variável de ambiente TOKEN não configurada.")

        self.url_base = f"https://api.telegram.org/bot{self.token}/"
        self.info_json = TableInfo()
        self.quadro = Quadro()

    def main(self):
        update_id = None
        print("Bot iniciado. Aguardando mensagens...")
        while True:
            try:
                atualizacao = self.obter_mensagens(update_id)
                mensagens = atualizacao.get("result", [])
                if mensagens:
                    for mensagem in mensagens:
                        update_id = mensagem["update_id"]
                        chat_id = mensagem["message"]["from"]["id"]
                        eh_primeira_msg = mensagem["message"]["message_id"] == 1
                        resposta = self.criar_resposta(mensagem, eh_primeira_msg, chat_id)
                        self.responder(resposta, chat_id)
            except Exception as exc:
                print(f"Aconteceu algo errado: {exc}")

    def obter_mensagens(self, update_id):
        link_requisicao = f"{self.url_base}getUpdates?timeout=400"
        if update_id:
            link_requisicao = f"{link_requisicao}&offset={update_id + 1}"
        resultado = requests.get(link_requisicao, timeout=60)
        resultado.raise_for_status()
        return resultado.json()

    def criar_resposta(self, mensagem, eh_primeira_msg, chat_id):
        texto = mensagem["message"].get("text", "")
        print(f"Mensagem recebida: {texto}")

        if eh_primeira_msg or texto.lower() in ["ajuda", "/start", "help"]:
            return (
                "Olá! Bem-vindo ao PokeInfo bot em Português.\n"
                "Digite o número da Pokédex ou o nome do Pokémon (em inglês) "
                "para saber mais informações sobre ele :)\n"
                "Fonte: PokeAPI"
            )

        termo = texto.lower().strip()
        pokedex, nome = self.buscar_pokemon(termo)

        # Se a tabela local não encontrou, tenta o termo digitado direto na PokeAPI.
        identificador = nome.lower() if nome else termo

        pokemon, info_texto = self.quadro.montar_resposta(identificador)

        if pokemon is None:
            return "Pokémon não encontrado, tente novamente!"

        url_envio_foto = f"{self.url_base}sendPhoto"
        self.enviar_foto(pokemon["sprite_normal"], f"{pokemon['id']} - {pokemon['name']}", chat_id, url_envio_foto)

        emoji = "\u2728"
        self.enviar_foto(
            pokemon["sprite_shiny"],
            f"{pokemon['id']} - {pokemon['name']} - Shiny {emoji}",
            chat_id,
            url_envio_foto,
        )

        return info_texto

    def enviar_foto(self, url_imagem, caption, chat_id, url):
        if not url_imagem:
            print("URL da imagem não disponível.")
            return

        payload = {"chat_id": chat_id, "photo": url_imagem, "caption": caption}
        try:
            response = requests.post(url, data=payload, timeout=60)
            response.raise_for_status()
            print(f"Foto enviada: {response.status_code}")
        except requests.RequestException as exc:
            print(f"Erro ao enviar foto: {exc}")

    def responder(self, resposta, chat_id):
        link_de_envio = (
            f"{self.url_base}sendMessage"
            f"?chat_id={chat_id}"
            f"&text={requests.utils.quote(resposta)}"
            f"&parse_mode=html"
        )
        try:
            requests.get(link_de_envio, timeout=60)
        except requests.RequestException as exc:
            print(f"Erro ao enviar mensagem: {exc}")

    def buscar_pokemon(self, palavra, pokedex=None, nome=None):
        x = self.info_json.json_dados(palavra)

        num_row = len(x["items"])
        for row in range(num_row):
            num_busca = len(x["items"][row]["busca"])
            for i in range(num_busca):
                if x["items"][row]["busca"][i].lower() == palavra:
                    pokedex = x["items"][row]["pokedex"]
                    nome = x["items"][row]["busca"][1]

                if pokedex is None and i == 1:
                    if palavra in x["items"][row]["busca"][i].lower():
                        pokedex = x["items"][row]["pokedex"]
                        nome = x["items"][row]["busca"][1]

        return pokedex, nome


if __name__ == "__main__":
    TelegramBot().main()
