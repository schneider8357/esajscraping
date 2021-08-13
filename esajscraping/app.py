from collections import deque
from datetime import datetime, timedelta

from flask import Flask, request, jsonify

from scrap import get_dados_processo


app = Flask(__name__)
app.clients = dict()

@app.route("/captura/processo/esaj", methods=["POST"])
def captura_processo_esaj():
    for ip in request.access_route:
        if ip in app.clients:
            now = datetime.now()
            if len(app.clients[ip]["requests"]) >= 10 and (now - app.clients[ip]["requests"][0]) < timedelta(seconds=60):
                return jsonify(dict(codigo=3, mensagem="Numero maximo de requests por minuto atingido")), 400
            app.clients[ip]["requests"].append(now)
        else:
            app.clients[ip] = {"requests": deque([datetime.now()], 10)}
    data = request.get_json()
    if data is None or data.get("numeroProcesso") is None:
        return jsonify(dict(codigo=4, mensagem="Numero nao informado")), 400
    resultado = get_dados_processo(data["numeroProcesso"])
    if resultado is None:
        return jsonify(dict(codigo=2, mensagem="Processo nao existe")), 404
    return jsonify(dict(codigo=1, mensagem="Sucesso", data=resultado)), 200

if __name__ == "__main__":
    app.run()
