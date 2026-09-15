import requests

url = "https://www.clubedaliga.com.br/api/cardsearch?tcg=1"

params = {
    "query": "Kit Inicial",
    "maintype": "1"
}
headers = {
    "User-Agent": "Mozilla/5.0",
    "Accept": "application/json, text/plain, */*"
}

resposta = requests.get(
    url,
    params=params,
    headers=headers,
    timeout=20
)

print("STATUS:", resposta.status_code)
print("URL FINAL:", resposta.url)
print("CONTENT-TYPE:", resposta.headers.get("Content-Type"))
print()
print(resposta.text[:10000])