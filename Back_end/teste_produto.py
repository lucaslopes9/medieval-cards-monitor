import requests
import re
import json
import os

# ============================================================
# CONFIGURAÇÃO
# ============================================================

url = "https://www.ligamagic.com.br/"

params = {
    "view": "cards/card",
    "card": "Starter Kit - Assassin's Creed",
    "tipo": "1"
}

headers = {
    "User-Agent": "Mozilla/5.0"
}


# ============================================================
# ACESSAR LIGAMAGIC
# ============================================================

response = requests.get(
    url,
    params=params,
    headers=headers,
    timeout=15
)

print("STATUS:", response.status_code)
print("URL:", response.url)
print("TAMANHO:", len(response.text))

with open(
    "debug_cards.html",
    "w",
    encoding="utf-8"
) as f:
    f.write(response.text)

print("HTML salvo em debug_cards.html")


# ============================================================
# PROD_AVG
# ============================================================

match_avg = re.search(
    r'var\s+prod_avg\s*=\s*(\{.*?\});',
    response.text
)

if match_avg:
    print("\n========================================")
    print("PROD_AVG")
    print("========================================")
    print(match_avg.group(1))
else:
    print("\nprod_avg NÃO ENCONTRADO")


# ============================================================
# PROD_STOCK
# ============================================================

match_stock = re.search(
    r'var\s+prod_stock\s*=\s*(\[.*?\]);',
    response.text,
    re.DOTALL
)

if not match_stock:
    print("\nprod_stock NÃO ENCONTRADO")
    exit()

estoque = json.loads(
    match_stock.group(1)
)

print("\n========================================")
print("QUANTIDADE DE OFERTAS")
print("========================================")
print(
    "Total:",
    len(estoque)
)


# ============================================================
# MOSTRAR OFERTAS
# ============================================================

print("\n========================================")
print("OFERTAS INDIVIDUAIS")
print("========================================")

for oferta in estoque:
    print("\n----------------------------------------")
    print(
        "ID DA OFERTA:",
        oferta.get("id")
    )
    print(
        "LOJA ID:",
        oferta.get("lj_id")
    )
    print(
        "CONDIÇÃO:",
        oferta.get("qualid")
    )
    print(
        "IDIOMA:",
        oferta.get("idioma")
    )
    print(
        "PRECO CSS:"
    )
    print(
        oferta.get("precoCss")
    )


# ============================================================
# PEGAR TODAS AS CLASSES DE PREÇO
# ============================================================

classes_precos = set()

for oferta in estoque:
    preco_css = oferta.get(
        "precoCss",
        ""
    )

    for bloco in preco_css.split(";"):
        for classe in bloco.split():
            if classe != "V":
                classes_precos.add(
                    classe
                )

print("\n========================================")
print("CLASSES DE PREÇO")
print("========================================")

for classe in sorted(classes_precos):
    print(
        classe
    )


# ============================================================
# ENCONTRAR DEFINIÇÕES CSS
# ============================================================

print("\n========================================")
print("POSIÇÕES DO SPRITE")
print("========================================")

posicoes = {}

for classe in sorted(classes_precos):
    padrao = (
        r'\.'
        + re.escape(classe)
        + r'\s*\{'
        r'([^}]*)'
        r'\}'
    )

    resultado = re.findall(
        padrao,
        response.text
    )

    if not resultado:
        print(
            classe,
            "→ definição não encontrada"
        )
        continue

    css = resultado[0]

    match_position = re.search(
        r'background-position\s*:\s*'
        r'(-?\d+)px\s+(-?\d+)px',
        css
    )

    if match_position:
        x = int(
            match_position.group(1)
        )
        y = int(
            match_position.group(2)
        )

        posicoes[classe] = (
            x,
            y
        )

        print(
            f"{classe} → X={x}, Y={y}"
        )
    else:
        print(
            classe,
            "→ sem background-position"
        )


# ============================================================
# DESCOBRIR URL DO SPRITE
# ============================================================

print("\n========================================")
print("SPRITE")
print("========================================")

match_sprite = re.search(
    r'background-image\s*:\s*url\(([^)]+)\)',
    response.text
)

if not match_sprite:
    print(
        "URL DO SPRITE NÃO ENCONTRADA"
    )
    exit()

sprite_url = match_sprite.group(1)
sprite_url = sprite_url.strip(
    "'\""
)

if sprite_url.startswith("//"):
    sprite_url = (
        "https:"
        + sprite_url
    )
elif sprite_url.startswith("/"):
    sprite_url = (
        "https://www.ligamagic.com.br"
        + sprite_url
    )

print(
    "URL DO SPRITE:",
    sprite_url
)


# ============================================================
# BAIXAR SPRITE
# ============================================================

print("\n========================================")
print("BAIXANDO SPRITE")
print("========================================")

sprite_response = requests.get(
    sprite_url,
    headers=headers,
    timeout=15
)

print(
    "STATUS SPRITE:",
    sprite_response.status_code
)
print(
    "TAMANHO SPRITE:",
    len(sprite_response.content)
)

if sprite_response.status_code != 200:
    print(
        "Não foi possível baixar o sprite."
    )
    exit()

sprite_path = "ligamagic_sprite.jpg"

with open(
    sprite_path,
    "wb"
) as f:
    f.write(
        sprite_response.content
    )

print(
    "Sprite salvo em:",
    sprite_path
)


# ============================================================
# TENTAR USAR PILLOW
# ============================================================

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    print("\n========================================")
    print("PILLOW NÃO INSTALADO")
    print("========================================")
    print(
        "Instale com:"
    )
    print(
        "pip install pillow"
    )
    print(
        "\nO sprite já foi baixado."
    )
    exit()


# ============================================================
# ABRIR SPRITE
# ============================================================

print("\n========================================")
print("ANALISANDO SPRITE")
print("========================================")

imagem = Image.open(
    sprite_path
)

print(
    "TAMANHO DA IMAGEM:",
    imagem.size
)


# ============================================================
# CRIAR PASTA DOS RECORTES
# ============================================================

pasta_recortes = "sprite_recortes"

os.makedirs(
    pasta_recortes,
    exist_ok=True
)


# ============================================================
# RECORTAR CADA CARACTERE
# ============================================================

print("\n========================================")
print("RECORTANDO CARACTERES")
print("========================================")

recortes = []

for classe, (
    x,
    y
) in sorted(posicoes.items()):
    left = abs(x)
    top = abs(y)

    right = left + 7
    bottom = top + 15

    if (
        right > imagem.width
        or bottom > imagem.height
    ):
        print(
            f"{classe} → posição fora da imagem"
        )
        continue

    recorte = imagem.crop(
        (
            left,
            top,
            right,
            bottom
        )
    )

    recorte_grande = recorte.resize(
        (
            70,
            150
        )
    )

    caminho = os.path.join(
        pasta_recortes,
        f"{classe}.png"
    )

    recorte_grande.save(
        caminho
    )

    recortes.append(
        (
            classe,
            recorte_grande
        )
    )

    print(
        f"{classe} → salvo em {caminho}"
    )


# ============================================================
# CRIAR PAINEL COM TODOS OS CARACTERES
# ============================================================

print("\n========================================")
print("CRIANDO PAINEL DOS CARACTERES")
print("========================================")

largura_item = 100
altura_item = 190

quantidade = len(
    recortes
)

colunas = 4

linhas = (
    quantidade + colunas - 1
) // colunas

painel = Image.new(
    "RGB",
    (
        colunas * largura_item,
        linhas * altura_item
    ),
    "white"
)

draw = ImageDraw.Draw(
    painel
)


# ============================================================
# COLOCAR RECORTES NO PAINEL
# ============================================================

for indice, (
    classe,
    recorte
) in enumerate(recortes):
    coluna = (
        indice % colunas
    )

    linha = (
        indice // colunas
    )

    x = (
        coluna * largura_item
        + 15
    )

    y = (
        linha * altura_item
        + 25
    )

    painel.paste(
        recorte,
        (
            x,
            y
        )
    )

    draw.text(
        (
            x,
            5 + linha * altura_item
        ),
        classe,
        fill="black"
    )


# ============================================================
# SALVAR PAINEL
# ============================================================

painel_path = (
    "sprite_caracteres.png"
)

painel.save(
    painel_path
)

print(
    "Painel salvo em:",
    painel_path
)


# ============================================================
# MAPA DOS CARACTERES
# ============================================================

MAPA_DIGITOS = {
    "gBeEt": "0",
    "gPbIk": "1",
    "wMjFj": "2",
    "yQdHw": "6",
    "aGaLw": "7",
    "jUlHs": "8",
    "pAdTk": "9",
}

# ============================================================
# DECODIFICAR PREÇO
# ============================================================

def decodificar_preco(preco_css):
    partes = preco_css.split(";")
    resultado = ""

    for parte in partes:
        parte = parte.strip()

        if parte == "V":
            resultado += ","
            continue

        digito = None

        for classe in parte.split():
            if classe in MAPA_DIGITOS:
                digito = MAPA_DIGITOS[classe]
                break

        if digito is None:
            resultado += "?"
        else:
            resultado += digito

    return resultado


# ============================================================
# TESTAR DECODIFICAÇÃO
# ============================================================

print("\n========================================")
print("PREÇOS DECODIFICADOS")
print("========================================")

for oferta in estoque:
    preco_css = oferta.get("precoCss", "")
    preco = decodificar_preco(preco_css)

    print(
        f"Oferta {oferta.get('id')} "
        f"| Condição {oferta.get('qualid')} "
        f"| Preço: R$ {preco}"
    )


# ============================================================
# RESUMO
# ============================================================

print("\n========================================")
print("FINALIZADO")
print("========================================")
print(
    "Sprite:",
    sprite_path
)
print(
    "Pasta dos recortes:",
    pasta_recortes
)
print(
    "Painel:",
    painel_path
)