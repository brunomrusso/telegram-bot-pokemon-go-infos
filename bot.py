"""
Criado por Bruno Martinez Russo
Abril/2021
"""
import requests
import json
import os
import io
import bs4
import re
#Classes utulizadas
from table.info_json import TableInfo

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
      r2 = self.montar_imagem(f'''{__link_shiny}{pokedex}_00_shiny.png''', f'''{pokedex} - {nome} - Shiny ''', chat_id, url)
      
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

      __http = f'https://pokemon.gameinfo.io/pt-br/pokemon/{num_dex}'
      __r = requests.get(__http)
      __soup = bs4.BeautifulSoup(__r.text, "lxml")      
      quadro_resposta = self.montar_string_resposta(__soup)
      return quadro_resposta

  def montar_string_resposta(self, soup):
      
      #Lista com todas as variaveis de resposta
      resposta = []
      try:
        #Ataque #1
        resposta.append(soup.find_all('div', {'class': 'togglable'})[1].find_all('td')[2].text)
        #Defesa #2
        resposta.append(soup.find_all('div', {'class': 'togglable'})[1].find_all('td')[5].text)
        #Stamina #3
        resposta.append(soup.find_all('div', {'class': 'togglable'})[1].find_all('td')[8].text)
        #Sobre o pokemon
        resposta.append(soup.find('p', {'class': 'description'}).text)
        #Tipo do pokemon
        tipagens = soup.find_all('div', {'class': 'large-type'})
        tipos = []
        for tipo in tipagens:
          tipos.append(tipo.text)
        #Loop de tipagem  
        for i in range(len(tipos)):
          print(i)
          if i == 0:
            tipagem = tipos[i]
          else:
            tipagem = f'{tipagem},{tipos[i]}'
        #Vulneravel a:
        vulnerabilidades = soup.find_all('table', {'class': 'weaknesses weak'})[0].find_all('td')
        lst_vul = []
        for vul in vulnerabilidades:
          texto = vul.text
          lst_vul.append(texto.replace('\n', '').replace('\t', ''))
        vulneravel = ''  
        for i in range(len(lst_vul)):  
          if i % 2 == 0:
            vulneravel = vulneravel + lst_vul[i]
          else:
            vulneravel = vulneravel + ' ' + lst_vul[i] + '\n'  

         #Resistente a:
        resistencias = soup.find_all('table', {'class': 'weaknesses res'})[0].find_all('td')
        lst_res = []
        for res in resistencias:
          texto = res.text
          lst_res.append(texto.replace('\n', '').replace('\t', ''))
        resiste = ''  
        for i in range(len(lst_res)):  
          if i % 2 == 0:
            resiste = resiste + lst_res[i]
          else:
            resiste = resiste + ' ' + lst_res[i] + '\n'          


        quadro_resposta = f'<b><u>SOBRE</u></b>{os.linesep}{resposta[3]}{os.linesep}<b><u>TIPAGEM</u></b>{os.linesep}{tipagem}{os.linesep}<b><u>VULNERAVEL A</u></b>{os.linesep}{os.linesep}{vulneravel}{os.linesep}<b><u>RESISTENTE A</u></b>{os.linesep}{os.linesep}{resiste}{os.linesep}<b><u>ATRIBUTOS BASE</u></b>{os.linesep}{os.linesep}ATAQUE   -> {resposta[0]}{os.linesep}DEFESA   -> {resposta[1]}{os.linesep}STAMINA -> {resposta[2]}'
        #print(quadro)

        quadro_resposta = self.traduzir_palavras(quadro_resposta)
      except:
        quadro_resposta = 'Informações não disponiveis para esse Pokemon.'
      return quadro_resposta

  def traduzir_palavras(self, texto):
    rep_dict = {'deals':'causa', 'damage':'dano', 'Water':'Água', 'Grass':'Grama', 'Electric':'Elétrico', 'Steel':'Aço', 'Fire':'Fogo', 'Ice':'Gelo', 'Fairy':'Fada', 'Poison':'Venenoso', 'Dark':'Sombrio', 'Bug':'Inseto', 'Dragon':'Dragão', 'Flying':'Voador', 'Ground':'Terrestre', 'Rock':'Pedra', 'Fighting':'Lutador', 'Psychic':'Psiquico', 'Ghost':'Fantasma'}
    pattern = re.compile("|".join([re.escape(k) for k in sorted(rep_dict,key=len,reverse=True)]), flags=re.DOTALL)
    return pattern.sub(lambda x: rep_dict[x.group(0)], texto)


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

