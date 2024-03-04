# App Financeiro

O App Financeiro é uma aplicação web simples desenvolvida em Flask, uma framework web em Python. 
Esta aplicação permite aos usuários gerenciar suas finanças, incluindo o registro de contas a pagar, contas pagas e a configuração de sua renda total.

## Funcionalidades

- Adicionar contas a pagar, incluindo descrição e valor
- Registrar contas pagas, removendo-as da lista de contas a pagar
- Configurar a renda total

Necessário ter o Pyhton instalado.
## Como usar
1. Clone este repositório:
  git clone https://github.com/paulogeraldo1/prj-eng-software
2. Navegue até o diretório do projeto
3. Instale as dependências usando o pip:
  pip install -r requirements.txt
4. Inicie a aplicação:
  pyhton app.py
5. Abra seu navegador e acesse http://localhost:5000 para visualizar a aplicação.

## Como usar em docker
Basta executar o docker compose, e a aplicação estará rodando na sua porta 85
Obs: verificar a última versão no DockerHub: https://hub.docker.com/r/pgls/prjengsoftware

docker-compose up -d 
ou
docker run -p 85:8000 pgls/prjengsoftware:1.2

Usuário: user
Senha: 1234