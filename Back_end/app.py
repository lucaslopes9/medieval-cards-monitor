import os
import re

from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv
import requests


# ============================================================
# CONFIGURAÇÃO
# ============================================================

dotenv_path = os.path.expanduser("~/.env.local")
load_dotenv(dotenv_path=dotenv_path)

app = Flask(__name__)

CORS(app)


DATABASE_URL = os.getenv("DATABASE_URL") or os.getenv("SQLALCHEMY_DATABASE_URI")

print("DEBUG DATABASE_URL:", bool(os.getenv("DATABASE_URL")))
print("DEBUG SQLALCHEMY_DATABASE_URI:", bool(os.getenv("SQLALCHEMY_DATABASE_URI")))
print("DEBUG DATABASE_URL_RESOLVIDA:", bool(DATABASE_URL))



if not DATABASE_URL:
    raise RuntimeError(
        "DATABASE_URL não foi encontrada nas variáveis de ambiente."
    )

# Compatibilidade com URLs postgres:// antigas
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace(
        "postgres://",
        "postgresql://",
        1
    )

app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URL
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)


# ============================================================
# MODELOS
# ============================================================

class User(db.Model):

    __tablename__ = "users"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    nome = db.Column(
        db.String(100),
        nullable=False
    )

    email = db.Column(
        db.String(120),
        unique=True,
        nullable=False
    )

    senha = db.Column(
        db.String(255),
        nullable=False
    )

    created_at = db.Column(
        db.DateTime,
        server_default=db.func.now()
    )


class SealedProduct(db.Model):

    __tablename__ = "sealed_products"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    nome = db.Column(
        db.String(150),
        nullable=False
    )

    edicao = db.Column(
        db.String(100),
        nullable=False
    )

    jogo = db.Column(
        db.String(50),
        nullable=False
    )

    tipo_produto = db.Column(
        db.String(80),
        nullable=False
    )

    preco_loja = db.Column(
        db.Numeric(10, 2),
        nullable=False
    )

    preco_concorrencia = db.Column(
        db.Numeric(10, 2),
        nullable=False
    )

    status = db.Column(
        db.String(80),
        nullable=False
    )

    created_at = db.Column(
        db.DateTime,
        server_default=db.func.now()
    )


# ============================================================
# CRIAÇÃO DAS TABELAS
# ============================================================

with app.app_context():
    db.create_all()


# ============================================================
# CADASTRO
# ============================================================

@app.route("/register", methods=["POST"])
def register():

    dados = request.get_json()

    if not dados:
        return jsonify({
            "sucesso": False,
            "mensagem": "Dados não enviados."
        }), 400

    nome = dados.get("nome")
    email = dados.get("email")
    senha = dados.get("senha")

    if not nome or not email or not senha:
        return jsonify({
            "sucesso": False,
            "mensagem": "Preencha todos os campos!"
        }), 400

    usuario_existente = User.query.filter_by(
        email=email
    ).first()

    if usuario_existente:
        return jsonify({
            "sucesso": False,
            "mensagem": "E-mail já cadastrado!"
        }), 400

    try:

        senha_criptografada = generate_password_hash(
            senha
        )

        novo_usuario = User(
            nome=nome,
            email=email,
            senha=senha_criptografada
        )

        db.session.add(novo_usuario)
        db.session.commit()

        return jsonify({
            "sucesso": True,
            "mensagem": "Usuário cadastrado com sucesso!"
        }), 201

    except Exception as erro:

        db.session.rollback()

        print(
            "Erro no cadastro:",
            erro
        )

        return jsonify({
            "sucesso": False,
            "mensagem": "Erro ao cadastrar usuário."
        }), 500


# ============================================================
# LOGIN
# ============================================================

@app.route("/login", methods=["POST"])
def login():

    dados = request.get_json()

    if not dados:
        return jsonify({
            "sucesso": False,
            "mensagem": "Dados não enviados."
        }), 400

    email = dados.get("email")
    senha = dados.get("senha")

    if not email or not senha:
        return jsonify({
            "sucesso": False,
            "mensagem": "Informe e-mail e senha."
        }), 400

    usuario = User.query.filter_by(
        email=email
    ).first()

    if usuario and check_password_hash(
        usuario.senha,
        senha
    ):

        return jsonify({
            "sucesso": True,
            "mensagem": "Login realizado com sucesso!",
            "usuario": {
                "id": usuario.id,
                "nome": usuario.nome,
                "email": usuario.email
            }
        }), 200

    return jsonify({
        "sucesso": False,
        "mensagem": "E-mail ou senha incorretos!"
    }), 401


# ============================================================
# NORMALIZAÇÃO
# ============================================================

def normalizar(texto):

    return re.sub(
        r"[^a-z0-9]+",
        " ",
        str(texto).lower()
    ).strip()


# ============================================================
# VERIFICAÇÃO EXATA DO TIPO DE PRODUTO
# ============================================================

def tipo_compativel(
    nome_produto,
    tipo_solicitado
):

    if not tipo_solicitado:
        return True

    produto = normalizar(
        nome_produto
    )

    tipo = normalizar(
        tipo_solicitado
    )

    if tipo == "booster box":

        if "booster box case" in produto:
            return False

        return "booster box" in produto

    if tipo == "booster box case":

        return "booster box case" in produto

    if tipo == "booster pack":

        if "sleeved booster pack" in produto:
            return False

        if "booster box" in produto:
            return False

        if "booster box case" in produto:
            return False

        return "booster pack" in produto

    if tipo == "sleeved booster pack":

        return "sleeved booster pack" in produto

    if tipo == "starter deck":

        return "starter deck" in produto

    if tipo == "starter kit":

        return "starter kit" in produto

    if tipo == "elite trainer box":

        return "elite trainer box" in produto

    if tipo == "bundle":

        return "bundle" in produto

    if tipo == "commander deck":

        return "commander deck" in produto

    return tipo in produto


# ============================================================
# VERIFICAR SE LISTING É LACRADO
# ============================================================

def listing_lacrado(listing):

    condition = normalizar(
        listing.get(
            "condition",
            ""
        )
    )

    # Se não veio condição, não descartamos o anúncio.
    if not condition:
        return True

    condicoes_lacradas = [
        "unopened",
        "sealed",
        "new",
        "factory sealed",
        "lacrado"
    ]

    for condicao in condicoes_lacradas:

        if normalizar(condicao) in condition:

            return True

    return False


# ============================================================
# BUSCAR PRODUTO NO TCGPLAYER
# ============================================================

def buscar_produto_tcgplayer(
    nome,
    edicao="",
    tipo_produto=""
):

    url = (
        "https://mp-search-api.tcgplayer.com/"
        "v1/search/request"
    )

    termo_busca = nome

    if edicao:

        termo_busca = (
            f"{nome} {edicao}"
        )

    payload = {

        "q": termo_busca,

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
    print("BUSCA TCGPLAYER")
    print("TERMO:", termo_busca)
    print("TIPO SOLICITADO:", tipo_produto)
    print("=" * 70)

    response = requests.post(

        url,

        json=payload,

        headers=headers,

        timeout=30

    )

    print(
        "STATUS TCGPLAYER:",
        response.status_code
    )

    if response.status_code != 200:

        print("ERRO TCGPLAYER:")
        print(response.text)

        return None

    data = response.json()

    resultados = data.get(
        "results",
        []
    )

    if not resultados:

        print(
            "Nenhum bloco de resultado."
        )

        return None

    produtos = resultados[0].get(
        "results",
        []
    )

    print(
        "PRODUTOS SELADOS RETORNADOS:",
        len(produtos)
    )

    if not produtos:

        print(
            "Nenhum produto selado encontrado."
        )

        return None

    # ========================================================
    # FILTRO OBRIGATÓRIO DE TIPO
    # ========================================================

    produtos_compativeis = []

    for produto in produtos:

        product_name = produto.get(
            "productName",
            ""
        )

        if tipo_compativel(
            product_name,
            tipo_produto
        ):

            produtos_compativeis.append(
                produto
            )

    print(
        "PRODUTOS COMPATÍVEIS COM O TIPO:",
        len(produtos_compativeis)
    )

    if not produtos_compativeis:

        print(
            "NENHUM PRODUTO COM O TIPO SOLICITADO."
        )

        return None

    # ========================================================
    # NORMALIZAÇÃO DOS DADOS DE BUSCA
    # ========================================================

    nome_normalizado = normalizar(
        nome
    )

    edicao_normalizada = normalizar(
        edicao
    )

    candidatos = []

    # ========================================================
    # ANALISA SOMENTE OS PRODUTOS DO TIPO CORRETO
    # ========================================================

    for produto in produtos_compativeis:

        product_name = produto.get(
            "productName",
            ""
        )

        product_name_normalizado = normalizar(
            product_name
        )

        score = 0

        # ----------------------------------------------------
        # NOME
        # ----------------------------------------------------

        if (
            product_name_normalizado
            == nome_normalizado
        ):

            score += 100

        elif (
            nome_normalizado
            in product_name_normalizado
        ):

            score += 70

        else:

            palavras = [

                palavra

                for palavra
                in nome_normalizado.split()

                if len(palavra) > 2

            ]

            encontradas = sum(

                1

                for palavra
                in palavras

                if palavra
                in product_name_normalizado

            )

            if palavras:

                percentual = (
                    encontradas
                    / len(palavras)
                )

                if percentual >= 0.8:

                    score += 60

                elif percentual >= 0.5:

                    score += 30

        # ----------------------------------------------------
        # EDIÇÃO
        # ----------------------------------------------------

        if edicao_normalizada:

            set_name = normalizar(
                produto.get(
                    "setName",
                    ""
                )
            )

            if (
                edicao_normalizada
                in set_name
            ):

                score += 30

            if (
                edicao_normalizada
                in product_name_normalizado
            ):

                score += 30

        candidatos.append(
            (
                score,
                produto
            )
        )

    # ========================================================
    # ORDENA OS CANDIDATOS
    # ========================================================

    candidatos.sort(
        key=lambda item: item[0],
        reverse=True
    )

    print("\nCANDIDATOS TCGPLAYER:")

    for score, produto in candidatos:

        print(
            "SCORE:",
            score,
            "|",
            produto.get(
                "productName"
            )
        )

    # ========================================================
    # ESCOLHE O MELHOR PRODUTO
    # ========================================================

    melhor_score, melhor_produto = (
        candidatos[0]
    )

    print("\nPRODUTO ESCOLHIDO:")

    print(
        melhor_produto.get(
            "productName"
        )
    )

    print(
        "PRODUCT ID:",
        melhor_produto.get(
            "productId"
        )
    )

    print(
        "SCORE:",
        melhor_score
    )

    # ========================================================
    # LISTINGS INDIVIDUAIS
    # ========================================================

    listings = melhor_produto.get(
        "listings",
        []
    )

    print("\nLISTINGS TOTAIS:")
    print(
        "QUANTIDADE:",
        len(listings)
    )

    ofertas = []

    for i, listing in enumerate(
        listings,
        start=1
    ):

        preco = listing.get(
            "price"
        )

        if preco is None:
            continue

        try:

            preco = float(
                preco
            )

        except (
            ValueError,
            TypeError
        ):

            continue

        if not listing_lacrado(
            listing
        ):

            continue

        vendedor = listing.get(
            "sellerName"
        )

        seller_price = listing.get(
            "sellerPrice"
        )

        frete = listing.get(
            "shippingPrice"
        )

        condicao = listing.get(
            "condition"
        )

        idioma = listing.get(
            "language"
        )

        quantidade = listing.get(
            "quantity"
        )

        oferta = {

            "vendedor": vendedor,

            "preco": preco,

            "seller_price": seller_price,

            "frete": frete,

            "condicao": condicao,

            "idioma": idioma,

            "quantidade": quantidade

        }

        ofertas.append(
            oferta
        )

        print(
            i,
            "| vendedor:",
            vendedor,
            "| preço:",
            preco,
            "| sellerPrice:",
            seller_price,
            "| frete:",
            frete,
            "| condição:",
            condicao,
            "| idioma:",
            idioma,
            "| quantidade:",
            quantidade
        )

    # ========================================================
    # ORDENA VENDEDORES PELO MENOR PREÇO
    # ========================================================

    ofertas.sort(
        key=lambda oferta: oferta["preco"]
    )

    print(
        "\nOFERTAS VÁLIDAS:",
        len(ofertas)
    )

    # ========================================================
    # MENOR PREÇO
    # ========================================================

    market_price = melhor_produto.get(
        "marketPrice"
    )

    if ofertas:

        lowest_price = ofertas[0][
            "preco"
        ]

    else:

        lowest_price = melhor_produto.get(
            "lowestPrice"
        )

    if lowest_price is None:

        lowest_price = market_price

    print(
        "MENOR PREÇO:",
        lowest_price
    )

    print(
        "MARKET PRICE:",
        market_price
    )

    # ========================================================
    # RETORNO
    # ========================================================

    return {

        "product_id":
            melhor_produto.get(
                "productId"
            ),

        "nome":
            melhor_produto.get(
                "productName"
            ),

        "edicao":
            melhor_produto.get(
                "setName"
            ),

        "jogo":
            melhor_produto.get(
                "productLineName"
            ),

        "tipo_produto":
            tipo_produto,

        "preco_tcgplayer":
            lowest_price,

        "market_price":
            market_price,

        "total_listings":
            melhor_produto.get(
                "totalListings"
            ),

        "ofertas":
            ofertas

    }


# ============================================================
# BUSCAR PREÇO / PRODUTO
# ============================================================

@app.route(
    "/buscar-preco",
    methods=["POST", "OPTIONS"],
    strict_slashes=False
)
def buscar_preco():

    # --------------------------------------------------------
    # CORS / PREFLIGHT
    # --------------------------------------------------------

    if request.method == "OPTIONS":

        return jsonify({
            "sucesso": True
        }), 200

    # --------------------------------------------------------
    # RECEBE DADOS
    # --------------------------------------------------------

    dados = request.get_json()

    if not dados:

        return jsonify({
            "sucesso": False,
            "mensagem": "Dados não enviados."
        }), 400

    jogo = dados.get("jogo")

    nome = dados.get("nome")

    edicao = dados.get(
        "edicao",
        ""
    )

    tipo_produto = dados.get(
        "tipo_produto",
        ""
    )

    if not jogo or not nome:

        return jsonify({
            "sucesso": False,
            "mensagem": (
                "Informe o jogo "
                "e o nome do produto."
            )
        }), 400

    # --------------------------------------------------------
    # BUSCA NO TCGPLAYER
    # --------------------------------------------------------

    try:

        produto_tcgplayer = (
            buscar_produto_tcgplayer(

                nome=nome,

                edicao=edicao,

                tipo_produto=tipo_produto

            )
        )

        # ----------------------------------------------------
        # PRODUTO NÃO ENCONTRADO
        # ----------------------------------------------------

        if not produto_tcgplayer:

            return jsonify({

                "sucesso": False,

                "mensagem": (
                    "Produto selado "
                    "com o tipo solicitado "
                    "não encontrado "
                    "no TCGplayer."
                )

            }), 404

        # ----------------------------------------------------
        # MENOR PREÇO
        # ----------------------------------------------------

        preco_tcgplayer = (
            produto_tcgplayer.get(
                "preco_tcgplayer"
            )
        )

        # ----------------------------------------------------
        # RESPOSTA
        # ----------------------------------------------------

        return jsonify({

            "sucesso": True,

            "nome":
                produto_tcgplayer.get(
                    "nome"
                ),

            "edicao":
                produto_tcgplayer.get(
                    "edicao"
                ) or edicao,

            "jogo":
                produto_tcgplayer.get(
                    "jogo"
                ) or jogo,

            "tipo_produto":
                produto_tcgplayer.get(
                    "tipo_produto"
                ) or tipo_produto,

            "product_id":
                produto_tcgplayer.get(
                    "product_id"
                ),

            "preco_tcgplayer":
                preco_tcgplayer,

            "market_price":
                produto_tcgplayer.get(
                    "market_price"
                ),

            "total_listings":
                produto_tcgplayer.get(
                    "total_listings"
                ),

            "ofertas":
                produto_tcgplayer.get(
                    "ofertas",
                    []
                )

        }), 200

    # --------------------------------------------------------
    # ERRO DE CONEXÃO
    # --------------------------------------------------------

    except requests.RequestException as erro:

        print(
            "Erro de conexão com TCGplayer:",
            erro
        )

        return jsonify({

            "sucesso": False,

            "mensagem": (
                "Erro de conexão "
                "com o TCGplayer."
            )

        }), 502

    # --------------------------------------------------------
    # ERRO INTERNO
    # --------------------------------------------------------

    except Exception as erro:

        print(
            "Erro interno:",
            erro
        )

        return jsonify({

            "sucesso": False,

            "mensagem": (
                "Erro interno "
                "ao processar a busca."
            )

        }), 500


# ============================================================
# INICIALIZAÇÃO
# ============================================================

if __name__ == "__main__":

    app.run(
        debug=True,
        port=5000
    )