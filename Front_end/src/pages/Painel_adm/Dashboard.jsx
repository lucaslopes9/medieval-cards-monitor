import { useState } from 'react';
import './Dashboard.css';

function Dashboard() {
  const [produtos, setProdutos] = useState([]);
  const [nomeCard, setNomeCard] = useState('');
  const [edicao, setEdicao] = useState('');
  const [jogo, setJogo] = useState('Magic');
  const [tipo, setTipo] = useState('Booster Box');
  const [precoLoja, setPrecoLoja] = useState('');

  const handleAddProduto = async (e) => {
    e.preventDefault();

    if (!nomeCard || !precoLoja) {
      alert('Preencha o nome do produto e o seu preço.');
      return;
    }

    try {
      const response = await fetch(
        'https://back-end-waf6.onrender.com/buscar-preco',
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            nome: nomeCard,
            edicao: edicao || 'Geral',
            jogo: jogo,
            tipo_produto: tipo
          })
        }
      );

      const resultado = await response.json();

      console.log(
        'RESPOSTA DO BACKEND:',
        resultado
      );

      if (!response.ok || !resultado.sucesso) {
        alert(
          resultado.mensagem ||
          resultado.erro ||
          'Não foi possível encontrar o produto no TCGplayer.'
        );

        return;
      }

      const novoItem = {
        id: Date.now(),

        nome:
          resultado.nome ||
          nomeCard,

        edicao:
          resultado.edicao ||
          edicao ||
          'Geral',

        jogo:
          resultado.jogo ||
          jogo,

        tipo:
          resultado.tipo_produto ||
          tipo,

        precoLoja:
          Number(precoLoja).toFixed(2),

        precoTCGPlayer:
          resultado.preco_tcgplayer !== undefined &&
          resultado.preco_tcgplayer !== null
            ? Number(
                resultado.preco_tcgplayer
              ).toFixed(2)
            : '0.00',

        marketPrice:
          resultado.market_price !== undefined &&
          resultado.market_price !== null
            ? Number(
                resultado.market_price
              ).toFixed(2)
            : '0.00',

        totalListings:
          resultado.total_listings || 0,

        ofertas:
          resultado.ofertas || []
      };

      setProdutos(
        (produtosAnteriores) => [
          ...produtosAnteriores,
          novoItem
        ]
      );

      setNomeCard('');
      setEdicao('');
      setPrecoLoja('');

    } catch (error) {
      console.error(
        'Erro ao conectar com o backend Python:',
        error
      );

      alert(
        'Erro ao conectar com o backend Python. ' +
        'Verifique se o servidor está rodando.'
      );
    }
  };

  return (
    <div className="dashboard-container">

      <main
        className="dashboard-content"
        style={{
          width: '100%',
          padding: '20px'
        }}
      >

        <header>

          <h1>
            Painel Administrativo – Medieval Cards
          </h1>

          <p>
            Gerencie seus produtos selados e acompanhe os preços do site
            TCGplayer.
          </p>

        </header>

        <section className="form-section">


          <form
            onSubmit={handleAddProduto}
            className="card-form-grid"
            style={{
              display: 'grid',
              gridTemplateColumns:
                'repeat(auto-fit, minmax(180px, 1fr))',
              gap: '12px',
              alignItems: 'center'
            }}
          >

            {/* NOME DO PRODUTO */}
            <div className="form-group">

              <label htmlFor="nomeCard">
                Nome do produto selado/fechado
              </label>

              <input
                id="nomeCard"
                type="text"
                placeholder="Nome do produto"
                value={nomeCard}
                onChange={(e) =>
                  setNomeCard(e.target.value)
                }
              />

            </div>

            {/* EDIÇÃO / SET */}
            <div className="form-group">

              <label htmlFor="edicao">
                Edição / Set
              </label>

              <input
                id="edicao"
                type="text"
                placeholder="Edição / Set"
                value={edicao}
                onChange={(e) =>
                  setEdicao(e.target.value)
                }
              />

            </div>

            {/* JOGO */}
            <div className="form-group">

              <label htmlFor="jogo">
                Jogo
              </label>

              <select
                id="jogo"
                value={jogo}
                onChange={(e) =>
                  setJogo(e.target.value)
                }
              >

                <option value="Magic">
                  Magic: The Gathering
                </option>

                <option value="Pokemon">
                  Pokémon TCG
                </option>

                <option value="Yugioh">
                  Yu-Gi-Oh!
                </option>

                <option value="One Piece Card Game">
                  One Piece Card Game
                </option>

              </select>

            </div>

            {/* TIPO DE EMBALAGEM */}
            <div className="form-group">

              <label htmlFor="tipo">
                Tipo de embalagem
              </label>

              <select
                id="tipo"
                value={tipo}
                onChange={(e) =>
                  setTipo(e.target.value)
                }
              >

                <option value="Booster Box">
                  Booster Box
                </option>

                <option value="Booster Pack">
                  Booster Pack
                </option>

                <option value="Sleeved Booster Pack">
                  Sleeved Booster Pack
                </option>

                <option value="Starter Deck">
                  Starter Deck
                </option>

                <option value="Starter Kit">
                  Starter Kit
                </option>

                <option value="Elite Trainer Box">
                  Elite Trainer Box (ETB)
                </option>

                <option value="Bundle">
                  Bundle
                </option>

                <option value="Commander Deck">
                  Commander Deck
                </option>

                <option value="Booster Box Case">
                  Booster Box Case
                </option>

              </select>

            </div>

            {/* PREÇO DE VENDA DA LOJA */}
            <div className="form-group">

              <label htmlFor="precoLoja">
                Preço de venda da sua loja
              </label>

              <input
                id="precoLoja"
                type="number"
                step="0.01"
                placeholder="Preço de venda (R$)"
                value={precoLoja}
                onChange={(e) =>
                  setPrecoLoja(e.target.value)
                }
              />

            </div>

            {/* BOTÃO */}
            <button
              type="submit"
              className="btn-cadastrar"
            >
              Pesquisar preços no TCGplayer
            </button>

          </form>

        </section>

        <section
          className="list-section"
          style={{
            marginTop: '30px'
          }}
        >

          <h3>
            Comparativo com TCGplayer
          </h3>

          <table
            style={{
              width: '100%',
              borderCollapse: 'collapse',
              marginTop: '10px'
            }}
          >

            <thead>

              <tr
                style={{
                  background: '#f4f4f4',
                  textAlign: 'left'
                }}
              >

                <th style={{ padding: '10px' }}>
                  Produto selado/fechado
                </th>

                <th style={{ padding: '10px' }}>
                  Edição / Set
                </th>

                <th style={{ padding: '10px' }}>
                  Jogo
                </th>

                <th style={{ padding: '10px' }}>
                  Tipo de embalagem
                </th>

                <th style={{ padding: '10px' }}>
                  Preço de venda da sua loja
                </th>

                <th style={{ padding: '10px' }}>
                  Menor preço do TCGplayer
                </th>

                <th style={{ padding: '10px' }}>
                  Market Price
                </th>

                <th style={{ padding: '10px' }}>
                  Ofertas de vendedores
                </th>

              </tr>

            </thead>

            <tbody>

              {produtos.map((item) => (

                <tr
                  key={item.id}
                  style={{
                    borderBottom:
                      '1px solid #ddd'
                  }}
                >

                  <td style={{ padding: '10px' }}>
                    <strong>
                      {item.nome}
                    </strong>
                  </td>

                  <td style={{ padding: '10px' }}>
                    {item.edicao}
                  </td>

                  <td style={{ padding: '10px' }}>
                    {item.jogo}
                  </td>

                  <td style={{ padding: '10px' }}>
                    {item.tipo}
                  </td>

                  <td style={{ padding: '10px' }}>
                    R$ {item.precoLoja}
                  </td>

                  <td style={{ padding: '10px' }}>
                    <strong>
                      US$ {item.precoTCGPlayer}
                    </strong>
                  </td>

                  <td style={{ padding: '10px' }}>
                    US$ {item.marketPrice}
                  </td>

                  <td style={{ padding: '10px' }}>

                    <strong>
                      {item.ofertas.length}
                    </strong>

                    {item.ofertas.length > 0 && (

                      <div
                        style={{
                          marginTop: '10px'
                        }}
                      >

                        {item.ofertas.map(
                          (oferta, index) => (

                            <div
                              key={index}
                              style={{
                                border:
                                  '1px solid #ddd',
                                borderRadius:
                                  '8px',
                                padding:
                                  '10px',
                                marginBottom:
                                  '8px',
                                background:
                                  index === 0
                                    ? '#f0fff0'
                                    : '#fff'
                              }}
                            >

                              <div>

                                <strong>

                                  {index === 0
                                    ? '🥇 '
                                    : ''
                                  }

                                  {oferta.vendedor ||
                                    'Vendedor não informado'
                                  }

                                </strong>

                              </div>

                              <div
                                style={{
                                  marginTop:
                                    '5px'
                                }}
                              >

                                <strong>
                                  US$ {
                                    Number(
                                      oferta.preco
                                    ).toFixed(2)
                                  }
                                </strong>

                              </div>

                              <div>
                                Frete: US$ {
                                  oferta.frete !==
                                  null &&
                                  oferta.frete !==
                                  undefined
                                    ? Number(
                                        oferta.frete
                                      ).toFixed(2)
                                    : '0.00'
                                }
                              </div>

                              <div>
                                Condição: {
                                  oferta.condicao ||
                                  'Não informado'
                                }
                              </div>

                              <div>
                                Idioma: {
                                  oferta.idioma ||
                                  'Não informado'
                                }
                              </div>

                              <div>
                                Quantidade: {
                                  oferta.quantidade ??
                                  'Não informado'
                                }
                              </div>

                            </div>

                          )
                        )}

                      </div>

                    )}

                  </td>

                </tr>

              ))}

            </tbody>

          </table>

        </section>

      </main>

    </div>
  );
}

export default Dashboard;