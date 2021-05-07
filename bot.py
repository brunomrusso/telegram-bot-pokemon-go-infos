"""
Criado por Bruno Martinez Russo
Abril/2021
"""
import requests
import json
import os
import io
import bs4
#Classes utulizadas
from table.info_json import TableInfo
from functions.quadro_resposta import Quadro

class TelegramBot():
  def __init__(self):
    TOKEN = os.environ['TOKEN']
    self.url_base = f'https://api.telegram.org/bot{TOKEN}/'
    self.info_json = TableInfo()

  #iniciar Bot
  def main(self):
    update_id = None
    while True:
      __atualizacao = self.obter_mensagens(update_id)
      __mensagens = __atualizacao['result']
      if __mensagens:
        for mensagem in __mensagens:
          try:
            update_id = mensagem['update_id']
            chat_id = mensagem['message']['from']['id']
            eh_primeira_msg = mensagem['message']['message_id'] == 1
            resposta = self.criar_resposta(mensagem, eh_primeira_msg, chat_id)
            self.responder(resposta, chat_id)
          except:
            print("Aconteceu algo errado :(")

 #Obter mensagens
  def obter_mensagens(self, update_id):
    link_requisicao = f'{self.url_base}getUpdates?timeout=400'
    if update_id:
      link_requisicao = f'{link_requisicao}&offset={update_id + 1}'
    resultado = requests.get(link_requisicao)
    return json.loads(resultado.content)

  #criando respostas para o usuario 
  def criar_resposta(self,mensagem, eh_primeira_msg, chat_id):
    
    mensagem = mensagem['message']['text']
    print(mensagem)
    if eh_primeira_msg == True or mensagem.lower() in ['ajuda', '/start']:
      resposta = f'''Olá bem vindo ao PokeInfo bot em Português.{os.linesep}Digite o número da pokedex ou nome do Pokemon para saber mais informações sobre ele :){os.linesep}Fonte: pokemongohub.net'''
      print(resposta)
    else:
        
      #Buscar pokemon buscado
      __link_default ="https://db.pokemongohub.net/images/official/full/"
      __link_shiny = "https://db.pokemongohub.net/images/ingame/normal/pokemon_icon_"
      pokedex, nome = self.buscar_pokemon(mensagem.lower())

      url = f'{self.url_base}sendPhoto';
      #Enviando imagem do pokemon normal
      r1 = self.montar_imagem(f'''{__link_default}{pokedex}.webp''', f'''{pokedex} - {nome} ''', chat_id, url)
      #Enviando imagem do pokemon shiny
      r2 = self.montar_imagem(f'''{__link_shiny}{pokedex}_00_shiny.png''', f'''{pokedex} - {nome} - Shiny \U+2728''', chat_id, url)
      
      #Tratando respostas de erro ao usuário
      if r1.status_code == 200 or r2.status_code == 200:
        resposta = self.montar_quadro_stats(pokedex)
      else:
        resposta = 'Pokemon não encontrado, tente novamente!'  
      #print(r1.status_code)
        print(resposta)
    print(r1.status_code, r1.reason, r1.content)  
    print(r2.status_code, r2.reason, r2.content)

    return resposta
  
  def montar_imagem(self, link, caption, chat_id, url):
    
      remote_image = requests.get(link)
      photo = io.BytesIO(remote_image.content)
      photo.name = "pokemon"
      files = {'photo': photo}
      data = {'chat_id' : chat_id, 'caption':  caption}
      r = requests.post(url, files=files, data=data)
      print(r)
      return r 

  def responder(self, resposta, chat_id):
      #enviar a mensagem
      link_de_envio = f'{self.url_base}sendMessage?chat_id={chat_id}&text={resposta}&parse_mode=html'
      requests.get(link_de_envio)

  def montar_quadro_stats(self, num_dex):

      quadro = Quadro()
      __http = f'https://pokemon.gameinfo.io/pt-br/pokemon/{num_dex}'
      __r = requests.get(__http)
      __soup = bs4.BeautifulSoup(__r.text, "lxml")      
      quadro_resposta = quadro.montar_string_resposta(__soup)
      return quadro_resposta

  def buscar_pokemon(self, palavra, pokedex=None, nome=None):

    #Buscar pokemon no json
    x = self.info_json.json_dados(palavra)  

    num_row = len(x["items"]) 
    for row in range(num_row):
        #print(x["items"][row]['busca'])
        num_busca = len(x["items"][row]['busca'])
        #Buscando o pokemon pela palavra/numero digitado elo usuario
        for i in range(num_busca):
            if x["items"][row]['busca'][i].lower() == palavra:
                pokedex = x["items"][row]['pokedex']
                nome = x["items"][row]['busca'][1]
            #Quando ele não encontrar o pokemon na busca acima
             #Ele tenta fazer uma busca pela subtring da palavra digitada    
            if pokedex == None and i == 1:
              if x["items"][row]['busca'][i].lower().find(palavra) != -1:
                pokedex = x["items"][row]['pokedex']
                nome = x["items"][row]['busca'][1]
    return pokedex, nome

if __name__ == '__main__':
    TelegramBot().main()

