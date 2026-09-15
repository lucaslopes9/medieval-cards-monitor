import { useState } from "react";
import "./Register.css";

function Register() {
  const [nome, setNome] = useState("");
  const [email, setEmail] = useState("");
  const [senha, setSenha] = useState("");
  const [mostrarSenha, setMostrarSenha] = useState(false); // Estado para controlar a visibilidade da senha
  const [mensagem, setMensagem] = useState("");
  const [erro, setErro] = useState("");

  const handleSubmit = async (e) => {
    e.preventDefault();
    setErro("");
    setMensagem("");

    try {
      const resposta = await fetch("https://back-end-waf6.onrender.com/register", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ nome, email, senha }),
      });

      const dados = await resposta.json();

      if (resposta.ok && dados.sucesso) {
        setMensagem(dados.mensagem);
        setTimeout(() => {
          window.location.href = "/"; // Redireciona para o login após 2 segundos
        }, 2000);
      } else {
        setErro(dados.mensagem || "Erro ao cadastrar usuário.");
      }
    } catch (err) {
      console.error("Erro na requisição:", err);
      setErro("Não foi possível conectar ao servidor.");
    }
  };

  return (
    <div className="login-container">
      <div className="login-box">
        <h1>Price Monitor</h1>
        <p>Criar Nova Conta</p>

        {erro && <p style={{ color: "red", fontSize: "14px" }}>{erro}</p>}
        {mensagem && <p style={{ color: "green", fontSize: "14px" }}>{mensagem}</p>}

        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label htmlFor="nome">Nome</label>
            <input
              type="text"
              id="nome"
              placeholder="Digite seu nome"
              value={nome}
              onChange={(e) => setNome(e.target.value)}
              required
            />
          </div>

          <div className="form-group">
            <label htmlFor="email">E-mail</label>
            <input
              type="email"
              id="email"
              placeholder="Digite seu e-mail"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
            />
          </div>

          <div className="form-group">
            <label htmlFor="password">Senha</label>
            <div className="password-container" style={{ position: "relative" }}>
              <input
                type={mostrarSenha ? "text" : "password"}
                id="password"
                placeholder="Digite sua senha"
                value={senha}
                onChange={(e) => setSenha(e.target.value)}
                required
                style={{ width: "100%", paddingRight: "40px" }}
              />
              <span
                onClick={() => setMostrarSenha(!mostrarSenha)}
                style={{
                  position: "absolute",
                  right: "12px",
                  top: "50%",
                  transform: "translateY(-50%)",
                  cursor: "pointer",
                  userSelect: "none",
                  fontSize: "16px",
                }}
              >
                {mostrarSenha ? "👁️‍🗨️" : "👁️"}
              </span>
            </div>
          </div>

          <button type="submit">Cadastrar</button>
        </form>

        <div style={{ marginTop: "15px", textAlign: "center", fontSize: "14px" }}>
          <a href="/">Já tem uma conta? Entrar</a>
        </div>
      </div>
    </div>
  );
}

export default Register;