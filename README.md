# Conciliadora CC API

A Conciliadora CC API é uma ferramenta desenvolvida para gerenciar usuários, contas e transações relacionadas aos cartões de crédito, débito e PIX, com integração direta às APIs da Omie e Pagar.Me.

## ✔️ Tecnologias usadas
- Python
- Django
- Django Ninja
- Pydantic
- PostgreSQL
- Python Jose
- Vercel
- Omie API
- Pagar.Me API

## 📁 Acesso ao Deploy

[![Deploy with Vercel](https://vercel.com/button)](https://conciliadora-cc-api.vercel.app/api/docs)

## 🔨 Funcionalidades

- **Gestão de Usuários**: Administração de usuários que têm acesso à API e aos dados de transações.
- **Autenticação**: Utiliza JWT para acesso seguro, com rotas específicas para login e verificação de tokens.
- **Gestão de Contas e Parcelas**: Criação, edição e remoção de contas e gerenciamento de parcelas de transações.
- **Sincronização com APIs Externas**: Integração com Omie e Pagar.Me para sincronização e atualização de dados de contas e transações.

## 📌 Endpoints

A Conciliadora CC API adota os princípios REST e oferece as seguintes rotas principais:

### Autenticação

- `POST /api/auth/login`: Realiza o login e gera um token de autenticação.
- `GET /api/auth/me`: Retorna as informações do usuário autenticado.

### Usuários

- `GET /api/users/{user_id}`: Recupera as informações de um usuário específico.
- `POST /api/users/{user_id}/change-password`: Permite ao usuário alterar sua senha.

### Contas

- `POST /api/accounts`: Cria uma nova conta.
- `GET /api/accounts`: Lista todas as contas cadastradas.
- `POST /api/accounts/omie`: Sincroniza as contas com os dados da API Omie.
- `GET /api/accounts/omie`: Lista as contas sincronizadas com a Omie.
- `PATCH /api/accounts/{account_id}`: Atualiza as informações de uma conta específica.
- `DELETE /api/accounts/{account_id}`: Remove uma conta do sistema.
- `POST /api/accounts/{account_id}/installments`: Adiciona parcelas a uma conta.
- `PATCH /api/accounts/{account_id}/installments/{installment_number}`: Atualiza uma parcela específica.
- `DELETE /api/accounts/{account_id}/installments/{installment_number}`: Remove uma parcela específica de uma conta.

### Transações

- `GET /api/transactions`: Lista todas as transações registradas.
- `POST /api/transactions/omie`: Sincroniza transações utilizando a API Omie.
- `PATCH /api/transactions/pagarme`: Sincroniza transações com a API Pagar.Me.

## 🔐 Autenticação

A autenticação é realizada através de JWT. Para obter o token de acesso, utilize a rota `/api/auth/login`, enviando as credenciais do usuário. Para acessar informações do usuário autenticado, use a rota `/api/auth/me` e inclua o token no cabeçalho das requisições.

## 🛠️ Configuração e Execução

Para configurar a Conciliadora CC API em seu ambiente de desenvolvimento local, siga as etapas abaixo:

1. Crie e ative um ambiente virtual para Python:
   ```bash
   python -m venv venv
   source venv/bin/activate  # No Windows, use `venv\Scripts\activate`
   ```
2. Instale as dependências do projeto:
   ```bash
   pip install -r requirements.txt
   ```
3. Configure as variáveis de ambiente para conexão com o banco de dados e outras credenciais necessárias.
4. Aplique as migrações do banco de dados:
   ```bash
   python manage.py migrate
   ```
5. Crie um superusuário para acessar o painel administrativo:
   ```bash
   python manage.py createsuperuser
   ```
6. Inicie o servidor de desenvolvimento:
   ```bash
   python manage.py runserver
   ```