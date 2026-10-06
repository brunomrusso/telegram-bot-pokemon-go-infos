# PokeInfo Bot para Telegram

Bot para Telegram que responde com a imagem normal, a imagem shiny e informações básicas de um Pokémon.

## O que mudou

O bot foi refatorado para usar a [PokeAPI](https://pokeapi.co) como fonte de dados, substituindo as URLs e o scraping do `pokemon.gameinfo.io` e `pokemongohub.net`, que pararam de funcionar ao longo dos anos.

## Funcionalidades

- Recebe o **número da Pokédex** ou o **nome do Pokémon em inglês**.
- Responde com a foto oficial do Pokémon.
- Responde com a foto shiny do Pokémon.
- Envia um texto com:
  - Descrição
  - Tipos (em português)
  - Atributos base (Ataque, Defesa, Stamina/HP)
  - Altura e peso

## Requisitos

- Python 3.8+
- Um token de bot do Telegram (obtenha com o [@BotFather](https://t.me/BotFather))

## Configuração

1. Clone o repositório e entre na pasta.
2. Crie um ambiente virtual (recomendado):

```bash
python -m venv venv
source venv/bin/activate  # Linux/macOS
# ou venv\Scripts\activate  # Windows
```

3. Instale as dependências:

```bash
pip install -r requirements.txt
```

4. Configure o token do bot:

```bash
export TOKEN="SEU_TOKEN_AQUI"  # Linux/macOS
# ou set TOKEN=SEU_TOKEN_AQUI  # Windows
```

## Executando localmente

```bash
python bot.py
```

## Publicando no Heroku

O arquivo `Procfile` está configurado para rodar o bot como um worker:

```
worker: python bot.py
```

Configure a variável de ambiente `TOKEN` no dashboard do Heroku e inicie o dyno worker.

## Exemplo de uso

No Telegram, envie para o bot:

```
pikachu
```

ou

```
25
```

O bot responde com as imagens e as informações do Pikachu.
