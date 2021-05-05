import re

class Traduzir():

    def traduzir_palavras(self, texto):
      rep_dict = {'deals':'causa<b>', 'damage':'</b>dano', 'Water':'Água', 'Grass':'Grama', 'Electric':'Elétrico', 'Steel':'Aço', 'Fire':'Fogo', 'Ice':'Gelo', 'Fairy':'Fada', 'Poison':'Venenoso', 'Dark':'Sombrio', 'Bug':'Inseto', 'Dragon':'Dragão', 'Flying':'Voador', 'Ground':'Terrestre', 'Rock':'Pedra', 'Fighting':'Lutador', 'Psychic':'Psiquico', 'Ghost':'Fantasma'}
      pattern = re.compile("|".join([re.escape(k) for k in sorted(rep_dict,key=len,reverse=True)]), flags=re.DOTALL)
      
      return pattern.sub(lambda x: rep_dict[x.group(0)], texto)
