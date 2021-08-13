import json
import re
import sys

import requests


def get_dados_processo(valorConsultaNuUnificado: str) -> dict:
  num_proc = valorConsultaNuUnificado.split(".")
  numeroDigitoAnoUnificado = f"{num_proc[0]}.{num_proc[1]}"
  foroNumeroUnificado = num_proc[4]

  url = f"https://www2.tjal.jus.br/cpopg/search.do?conversationId=&cbPesquisa=NUMPROC&numeroDigitoAnoUnificado={numeroDigitoAnoUnificado}&foroNumeroUnificado={foroNumeroUnificado}&dadosConsulta.valorConsultaNuUnificado={valorConsultaNuUnificado}&dadosConsulta.valorConsultaNuUnificado=UNIFICADO&dadosConsulta.valorConsulta=&dadosConsulta.tipoNuProcesso=UNIFICADO&uuidCaptcha="
  resp = requests.get(url)
  if "<!-- BEGIN MESSAGE -->" in resp.text:
    return None
  document = re.sub(r"&nbsp;|\n", " ", resp.text)
  dados_processo = dict(numeroProcesso=valorConsultaNuUnificado)

  # Dados main
  pattern_dados_main = r'(<span id="%s"[^>]*>)((.|\s)+?)(\<\/span\>)'
  for s in ("classeProcesso", "assuntoProcesso", "foroProcesso", "varaProcesso", "juizProcesso"):
      dados_processo[s] = re.search(pattern_dados_main%s, document).group(2)

  # Dados collapse
  pattern_dados_collapse = r'(<div id="%s"[^>]*>)((.|\s)+?)(\<\/div\>)'
  for s in ("dataHoraDistribuicaoProcesso", "numeroControleProcesso", "valorAcaoProcesso"):
      dados_processo[s] =  re.sub(r"\s\s+","", re.search(pattern_dados_collapse%s, document).group(2))

  s = "areaProcesso"
  area = re.search(pattern_dados_collapse%s, document).group(2)
  dados_processo[s] = re.search(r"(<span[^>]*>)((.|\s)+?)(\<\/span\>)", area).group(2)

  # Partes
  partes = list()
  pattern_table_partes = r'(<table id="tableTodasPartes"[^>]*>)((.|\s)+?)(\<\/table\>)'
  table_partes = re.search(pattern_table_partes, document).group(2)
  pattern_dados_partes = r'(<tr class="fundoClaro"[^>]*>)((.|\s)+?)(\<\/tr\>)'
  for td in re.findall(pattern_dados_partes, table_partes):
    pattern_tipo_participacao = r'(<span class="mensagemExibindo tipoDeParticipacao"[^>]*>)((.|\s)+?)(\<\/span\>)'
    pattern_nome = r'(<td class="nomeParteEAdvogado"[^>]*>)((.|\s)+?)(\<\/td\>)'
    tipo_participacao = re.search(pattern_tipo_participacao, td[1])
    nome = re.search(pattern_nome, td[1])
    nome = re.sub(r"\s\s+","", nome.group(2))
    tags = re.search(r'(\<(.|\s)+)', nome)
    nova_parte = dict(nome=nome, tipoDeParticipacao=tipo_participacao.group(2))
    if tags:
      nova_parte["nome"] = nome.replace(tags.group(0), "")
      pattern_advogado = r'(<span.*>)((.|\s)+?)(\<\/span\>)((.|\s)+)'
      advogado = re.search(pattern_advogado, tags.group(0))
      nova_parte["advogado"] = dict(nome=advogado.group(5), tipoDeParticipacao=advogado.group(2))
    partes.append(nova_parte)
  dados_processo["partes"] = partes

  return dados_processo

if __name__ == "__main__":
  print(get_dados_processo(sys.argv[1]))