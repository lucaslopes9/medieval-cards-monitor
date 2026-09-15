import requests
import json

URL = "https://mp-search-api.tcgplayer.com/v1/search/request"

# Payload estruturado para buscar o termo e filtrar especificamente por produtos selados
payload = {
    "q": "Carrying On His",
    "size": 50,
    "from": 0,
    "filters": {
        "term": {
            "productTypeName": [
                "Sealed Products"
            ]
        }
    }
}

headers = {
    "Content-Type": "application/json",
    "User-Agent": "Mozilla/5.0"
}

print("=" * 70)
print("TESTE TCGPLAYER - FILTRANDO APENAS SELADOS")
print("=" * 70)

response = requests.post(
    URL,
    json=payload,
    headers=headers,
    timeout=30
)

print("STATUS:", response.status_code)

if response.status_code != 200:
    print("\nERRO:")
    print(response.text)
    exit()

data = response.json()
resultados = data.get("results", [])

if not resultados:
    print("Nenhum resultado encontrado.")
    exit()

produtos = resultados[0].get("results", [])

print(f"Quantidade de produtos selados retornados: {len(produtos)}\n")

for contador, produto in enumerate(produtos, start=1):
    product_id = produto.get("productId")
    product_name = produto.get("productName")
    market_price = produto.get("marketPrice")
    product_type = produto.get("productTypeName")
    
    print(f"[{contador}] ID: {product_id} | Nome: {product_name} | Tipo: {product_type} | Preço: ${market_price}")

print("\n" + "=" * 70)
print("FIM DO TESTE")
print("=" * 70)