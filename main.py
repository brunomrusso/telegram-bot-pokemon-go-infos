import requests
import json
import os
import io
from info_json import TableInfo

class TelegramBot():
  def __init__(self):
    token ='1768676380:AAHpCcROVoPNv3Mtw5axQG1rv3oHGP65qas'
    self.url_base = f'https://api.telegram.org/bot{token}/'
    self.info_json = TableInfo()

  #iniciar Bot
  def Iniciar(self):
    update_id = None
    while True:
      atualizacao = self.obter_mensagens(update_id)
      mensagens = atualizacao['result']
      if mensagens:
        for mensagem in mensagens:
          update_id = mensagem['update_id']
          chat_id = mensagem['message']['from']['id']
          eh_primeira_msg = mensagem['message']['message_id'] == 1
          resposta = self.criar_resposta(mensagem, eh_primeira_msg, chat_id)
          self.responder(resposta, chat_id)

 #Obter mensagens
  def obter_mensagens(self, update_id):
    link_requisicao = f'{self.url_base}getUpdates?timeout=100'
    if update_id:
      link_requisicao = f'{link_requisicao}&offset={update_id + 1}'
    resultado = requests.get(link_requisicao)
    return json.loads(resultado.content)

  #criando respostas para o usuario 
  def criar_resposta(self,mensagem, eh_primeira_msg, chat_id):
    
    mensagem = mensagem['message']['text']
    print(mensagem)
    if eh_primeira_msg == True or mensagem.lower() in ['ajuda', '/start']:
      resposta = f'''Olá bem vindo ao PokeInfo bot em Portugues.{os.linesep}Digite o número da pokedex ou nome do Pokemon para saber mais informações sobre ele :)'''
      print(resposta)
    else:
        
      #Buscar pokemon buscado
      link_default ="https://db.pokemongohub.net/images/official/full/"
      link_shiny = "https://db.pokemongohub.net/images/ingame/normal/pokemon_icon_"
      pokedex, nome = self.buscar_pokemon(mensagem.lower())

      url = f'{self.url_base}sendPhoto';
      #Enviando imagem do pokemon normal
      remote_image = requests.get(f'''{link_default}{pokedex}.webp''')
      photo = io.BytesIO(remote_image.content)
      photo.name = "pokemon"
      files = {'photo': photo}
      data = {'chat_id' : chat_id, 'caption':  f'''{pokedex} - {nome} '''}
      r1 = requests.post(url, files=files, data=data)
      #Enviando imagem do pokemon shiny
      remote_image = requests.get(f'''{link_shiny}{pokedex}_00_shiny.png''')
      photo = io.BytesIO(remote_image.content)
      photo.name = "pokemon"
      files = {'photo': photo}
      data = {'chat_id' : chat_id, 'caption':  f'''{pokedex} - {nome} - Shiny '''}
      r2 = requests.post(url, files=files, data=data)
      #Tratando respostas de erro ao usuário
      print(r1)
      print(r2)
      if r1.status_code == 200 or r2.status_code == 200:
        resposta = ''
      else:
        resposta = 'Pokemon não encontrado, tente novamente!'  
      #print(r1.status_code)
        print(resposta)
    #print(r1.status_code, r1.reason, r1.content)  
    #print(r2.status_code, r2.reason, r2.content)

    return resposta     


  def responder(self, resposta, chat_id):
    #enviar a mensagem
    link_de_envio = f'{self.url_base}sendMessage?chat_id={chat_id}&text={resposta}'
    requests.get(link_de_envio)

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

bot = TelegramBot()
bot.Iniciar()    




    

