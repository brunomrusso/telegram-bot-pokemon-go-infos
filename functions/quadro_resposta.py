import os
#Classes utulizadas
from functions.tradutor import Traduzir

class Quadro():

    def montar_string_resposta(self, soup):

      traducao = Traduzir()
      try:      
        stats = self.stats_base(soup)
        tipagem = self.tipo_pokemon(soup) #Tipo do pokemon
        vulneravel = self.vulnerabilidade(soup)
        resiste = self.resistencia(soup)      

        quadro_resposta = f'<b><u>SOBRE</u></b>{os.linesep}{stats[3]}{os.linesep}<b><u>TIPAGEM</u></b>{os.linesep}{tipagem}{os.linesep}<b><u>VULNERAVEL A</u></b>{os.linesep}{os.linesep}{vulneravel}{os.linesep}<b><u>RESISTENTE A</u></b>{os.linesep}{os.linesep}{resiste}{os.linesep}<b><u>ATRIBUTOS BASE</u></b>{os.linesep}{os.linesep}ATAQUE   -> <b>{stats[0]}</b>{os.linesep}DEFESA   -> <b>{stats[1]}</b>{os.linesep}STAMINA -> <b>{stats[2]}</b>'
        #print(quadro)

        quadro_resposta = traducao.traduzir_palavras(quadro_resposta)

      except:
        quadro_resposta = 'Informações não disponiveis para esse Pokemon.'
      return quadro_resposta

    def stats_base(self, soup):
        
      #Lista com todas as variaveis de resposta
      stats = []
      #Ataque #1
      stats.append(soup.find_all('div', {'class': 'togglable'})[1].find_all('td')[2].text)
      #Defesa #2
      stats.append(soup.find_all('div', {'class': 'togglable'})[1].find_all('td')[5].text)
      #Stamina #3
      stats.append(soup.find_all('div', {'class': 'togglable'})[1].find_all('td')[8].text)
      #Sobre o pokemon
      stats.append(soup.find('p', {'class': 'description'}).text)

      return stats  

    def tipo_pokemon(self, soup):

      tipagens = soup.find_all('div', {'class': 'large-type'})
      tipos = []
      for tipo in tipagens:
        tipos.append(tipo.text)
      #Loop de tipagem  
      for i in range(len(tipos)):
        #print(i)
        if i == 0:
          tipagem = tipos[i]
        else:
          tipagem = f'{tipagem},{tipos[i]}'

      return tipagem    

    def vulnerabilidade(self, soup):

      #Vulneravel a:
      vulnerabilidades = soup.find_all('table', {'class': 'weaknesses weak'})[0].find_all('td')
      lst_vul = []
      for vul in vulnerabilidades:
        texto = vul.text
        lst_vul.append(texto.replace('\n', '').replace('\t', ''))
      vulneravel = ''  
      for i in range(len(lst_vul)):  
        if i % 2 == 0:
          vulneravel = vulneravel + '<b>' + lst_vul[i] + </b>
        else:
          vulneravel = vulneravel + ' ' + lst_vul[i] + '\n'

      return vulneravel

    def resistencia(self, soup):

        #Resistente a:
      resistencias = soup.find_all('table', {'class': 'weaknesses res'})[0].find_all('td')
      lst_res = []
      for res in resistencias:
        texto = res.text
        lst_res.append(texto.replace('\n', '').replace('\t', ''))
      resiste = ''  
      for i in range(len(lst_res)):  
        if i % 2 == 0:
          resiste = resiste + '<b>' + lst_res[i] + </b>
        else:
          resiste = resiste + ' ' + lst_res[i] + '\n'

      return resiste            
