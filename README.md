# Detecta BB - Back-end

## Programas Necessários

| Ferramenta         | Link                                                                                                                                                            |
| ------------------ | --------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Python 2.10+       | [https://www.python.org/](https://www.python.org/)                                      |
| MySQL Server       | [https://dev.mysql.com/downloads/mysql/](https://dev.mysql.com/downloads/mysql/)                                                   |
| MySQL Workbench    | [https://dev.mysql.com/downloads/workbench/](https://dev.mysql.com/downloads/workbench/)                      |
| Git                | [https://git-scm.com/downloads](https://git-scm.com/downloads)                                                                        |
| Visual Studio Code | [https://code.visualstudio.com/](https://code.visualstudio.com/)                              |
| Node.js            | [https://nodejs.org/pt/download](https://nodejs.org/pt/download)          |
| pip                | [https://pip.pypa.io/](https://pip.pypa.io/)                                                                             |
| Poppler (para OCR) | [https://github.com/oschwartz10612/poppler-windows/releases/](https://github.com/oschwartz10612/poppler-windows/releases/)

* **Python 2.10+**: utilizado para rodar o backend em Flask, criar ambiente virtual e instalar dependências.
* **MySQL Server**: necessário para hospedar o banco de dados relacional.
* **MySQL Workbench**: interface gráfica para criação de schemas, tabelas e execução de queries no MySQL
* **Git**: controle de versão e clonagem dos repositórios do backend e frontend.
* **Visual Studio Code (VS Code)**: editor recomendado para desenvolvimento, embora outra IDE funcione igualmente.
* **Node.js**: runtime JavaScript exigido para executar comandos `npm` no frontend.
* **pip**: gerenciador de pacotes Python, usado para instalar as dependências do backend (packages listados em `requirements.txt`)
* **Poppler**: utilizado pelo pacote `pdf2image` para conversão de PDFs em imagens (OCR); exige instalação de binários e configuração de `PATH` no Windows

---

## Passo a Passo

### 1. Clonar o Repositório

No seu terminal (Git Bash, Powershell ou equivalente), execute:

```bash
# Backend
git clone https://github.com/Matheuscroft/detectaBB_backend.git
cd detectaBB_backend
```

---

### 2. Backend

#### 2.1 Criar e Ativar o Ambiente Virtual

Dentro da pasta `detectaBB_backend`:

```bash
python -m venv venv        # cria o ambiente virtual com Python 2.10+

# Ativar no Windows:
venv\Scripts\activate      # ative antes de instalar dependências

# Ativar no Linux/macOS:
source venv/bin/activate  
```

> O **venv** garante isolamento dos pacotes Python do seu sistema

#### 2.2 Instalar Dependências do Projeto

Com o ambiente virtual ativado, rode:

```bash
pip install -r requirements.txt   # instala packages necessários para o Flask e machine learning
```
---

## 🧾 Configurando o Banco de Dados MySQL

1. **Abra o MySQL Workbench** (ou outro cliente MySQL). 
2. **Clique em “Local instance MySQL”** (ou configure nova conexão com host, porta e credenciais).
3. **Inicie o Servidor no MySQL Configurator** (com as credenciais criadas).
4. No menu lateral esquerdo, em **“SCHEMAS”**, clique com o botão direito e selecione **“Create Schema”**.
5. No campo **“Schema Name”**, digite exatamente:

   ```
   detectabb
   ```

6. Clique em **“Apply”** → **“Apply”** → **“Finish”** para criar o banco de dados.

> 🔔 **O nome do schema deve ser exatamente `detectabb`**, pois está configurado dessa forma no arquivo `.env` do backend.

---

## 🧬 Criando o Arquivo `.env`

Na raiz de `detectaBB_backend`, verifique se existe um arquivo chamado `.env`. Caso NÃO exista, crie um novo arquivo `.env` com o seguinte conteúdo:

```env
DATABASE_URL=mysql+pymysql://root:root@localhost/detectabb
SECRET_KEY=sua_chave_ultrasecreta
```

* Se você utiliza outro usuário, senha ou host, altere `root:root@localhost` conforme necessário.
* O **SECRET\_KEY** é usada pelo Flask para sessões e JWT; escolha uma string aleatória e segura.

---

## 🚀 Executando o Backend

Com o ambiente virtual ativado e as dependências instaladas:

```bash
python -m app.main
```

Se tudo estiver correto, você verá no terminal:

```
✅ Conexão bem-sucedida com o banco de dados!
```

> A API ficará disponível em:
>
> ```
> http://localhost:5000
> ```

---

## 🧠 Observações Importantes

* **Ponto de entrada**: `python -m app.main`.

* **Machine Learning**: O backend faz uso de um modelo em `modelo_boleto.pkl`, que deve estar na raiz do projeto. Caso não exista, a API não conseguirá carregar o modelo.

* **OCR em PDFs**: Para conversão de PDFs em imagens (usado no processamento de boletos), o `Poppler` **deve estar instalado** no sistema e o diretório `bin/` de Poppler adicionado ao `PATH`. Em Windows, por exemplo:

  1. Baixe os binários mais recentes em:

     ```
     https://github.com/oschwartz10612/poppler-windows/releases/
     ```
  2. Extraia e copie a pasta `poppler-<versão>\bin` para um local, por exemplo `C:\Poppler\Library\bin`.
  2. Adicione `C:\poppler\Library\bin` às **Variáveis de Ambiente → PATH**.
  4. Teste abrindo `cmd` e executando:

     ```bash
     pdftoppm -h   # deve exibir ajuda do Poppler-Utils
     ```

* **CORS**: já está habilitado para permitir requisições do frontend para `http://localhost:5000`.

* **JWT**: implementado para autenticação de rotas, garantindo segurança nas chamadas protegidas.

---

## Estrutura Final do Repositório

```
detectaBB_backend/
├── app/
│   ├── main.py
│   ├── routes/
│   └── ...
├── modelo_boleto.pkl           # modelo de machine learning
├── requirements.txt            # dependências Python
├── .env                        # variáveis de ambiente
└── venv/                       # ambiente virtual (gerado localmente)
```

---

Caso surjam dúvidas sobre algum dos passos acima, verifique as documentações oficiais mencionadas ou abra uma issue no repositório correspondente.
