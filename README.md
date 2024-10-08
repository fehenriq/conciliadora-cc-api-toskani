# API

A API foi desenhada para gerir usuários, imagens e apps do Grupo Gimi.

## ✔️ Tecnologias usadas
- Python
- Django
- Django Ninja
- Pydantic
- PostgreSQL
- Python Jose
- Vercel

## 📁 Acesso ao deploy

[![Deploy with Vercel](https://vercel.com/button)](https://engenhadev.com.br/)

## 🔨 Funcionalidades

- **Gestão de Usuários**: Administração de usuários que podem acessar a API.
- **Autenticação**: Sistema de tokens para acesso seguro à API.

## 📌 Uso

A API segue os princípios REST para comunicação. Os seguintes endpoints estão disponíveis:

### /users
- Gerenciar usuários e realizar operações CRUD.

## 🔐 Autenticação

A autenticação é realizada através de JWT. Utilize a rota `/auth/login` para obter um token de acesso, enviando as credenciais do usuário. Utilize este token nas requisições subsequentes para autenticar e para ter acesso aos dados do usuário autenticado utilize a rota `/auth/me`.

## 🛠️ Abrindo e rodando o projeto

Para configurar a API em seu ambiente, siga estas etapas:

1. Clone o repositório do projeto para sua máquina local.
2. Configure o ambiente virtual para Python e ative-o.
3. Instale as dependências do projeto
```bash
pip install -r requirements.txt
```
1. Configure as variáveis de ambiente necessárias para a conexão com o banco de dados e outras configurações de sistema.
2. Execute as migrações do banco de dados
```bash
python manage.py migrate
```
1. Crie um super usuário para ter acesso a `/admin/`
```bash
python manage.py createsuperuser
```
1. Inicie o servidor de desenvolvimento
```bash
python manage.py runserver
```