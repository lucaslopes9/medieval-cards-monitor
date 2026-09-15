import { useState } from "react";
import "./login.css";

import { Link } from "react-router-dom";

import { Eye, EyeOff } from "lucide-react";

function Login() {
  const [email, setEmail] = useState("");
  const [senha, setSenha] = useState("");
  const [erro, setErro] = useState("");

  const [mostrarSenha, setMostrarSenha] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setErro("");

    try {
      const resposta = await fetch("https://back-end-waf6.onrender.com/login", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ email, senha }),
      });

      const dados = await resposta.json();

      if (resposta.ok && dados.sucesso) {
        alert(dados.mensagem);
        localStorage.setItem("usuario", JSON.stringify(dados.usuario));
         window.location.href = "/dashboard";
      } else {
        setErro(dados.mensagem || "Erro ao fazer login.");
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
        <p>Portal Administrativo</p>

        {erro && <p style={{ color: "red", fontSize: "14px" }}>{erro}</p>}

        <form onSubmit={handleSubmit}>
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
     {mostrarSenha ? <EyeOff size={18} /> : <Eye size={18} />}
    </span>
  </div>
</div>

          <button type="submit">Entrar</button>
        </form>

        <div style={{ marginTop: "15px", display: "flex", justifyContent: "space-between", fontSize: "14px" }}>
          <a href="#">Esqueci minha senha</a>
          {/* Altere o href para a rota da sua página de cadastro */}
        <Link to="/register">Primeiro acesso? Cadastre-se</Link>
        </div>
      </div>
    </div>
  );
}

export default Login;
