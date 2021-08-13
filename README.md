# esajscraping

## Instalação

```bash
git clone https://github.com/schneider8357/esajscraping
cd esajscraping
pip install -U flask requests
```

## Execução

Para executar a app Flask:

```bash
python3 esajscraping/app.py
```

## Consultando a app

```bash
curl -X POST -H "Content-type: application/json" -d '{"numeroProcesso": "0705677-72.2019.8.02.0001"}' http://127.0.0.1:5000/captura/processo/esaj
```

