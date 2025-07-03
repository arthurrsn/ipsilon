# 💬 Fórum Ípsilon

O **Fórum Ípsilon** é uma aplicação web completa desenvolvida como projeto de TCC do Ensino Médio Técnico, simulando um fórum de discussões com funcionalidades de autenticação, posts, comentários e upload de mídias.

## 📖 Sobre o Projeto

Este projeto foi criado para ser uma plataforma de comunicação segura e privada, onde usuários pré-aprovados podem interagir, compartilhar ideias em tópicos, comentar em publicações e enriquecer as conversas com o upload de imagens.

A aplicação foi construída com um back-end em **Python** utilizando o micro-framework **Flask** e integrada com os serviços do **Google Firebase** para persistência de dados e armazenamento de arquivos.

## ✨ Funcionalidades Principais

- 🔐 **Sistema de Autenticação**: Acesso à plataforma controlado por login e senha, com os dados dos usuários armazenados de forma segura no Firestore.
- 📝 **Criação de Posts**: Usuários autenticados podem criar novos posts, definindo um tópico e o conteúdo da mensagem.
- 🖼️ **Upload de Imagens**: Funcionalidade para anexar uma imagem a um post no momento da sua criação. As imagens são armazenadas no Firebase Storage e o link público é associado à mensagem.
- 💬 **Sistema de Comentários**: Possibilidade de adicionar comentários a posts existentes, criando threads de discussão.
- 🔒 **Controle de Acesso**: Implementação de um sistema de solicitação de acesso e uma verificação de "termos de uso" para novos usuários.
- 👤 **Gerenciamento de Sessão**: Controle de estado do usuário (logado/deslogado) utilizando o sistema de sessões do Flask.

## 🛠️ Tecnologias Utilizadas

- **Back-end**: Python  
- **Framework Web**: Flask  
- **Banco de Dados NoSQL**: Google Firestore (para armazenar usuários, posts e comentários)  
- **Armazenamento de Arquivos**: Google Cloud Storage (via Firebase Storage para upload de imagens)  
- **Front-end**: HTML, CSS (utilizando o sistema de templates do Flask com Jinja2)

## 🚀 Como Executar o Projeto Localmente

Siga os passos abaixo para configurar e executar a aplicação em seu ambiente local.

### Pré-requisitos

- Python 3.9 ou superior instalado.
- Uma conta no Google e um projeto criado no Firebase.

### 1. Clone o Repositório

```bash
git clone https://github.com/arthurrsn/ipsilon.git
cd ipsilon
```
### 2. Configure o Ambiente Virtual

É uma boa prática criar um ambiente virtual para isolar as dependências do projeto.

```bash
# Criar o ambiente virtual
python -m venv venv

# Ativar o ambiente (Windows)
.\venv\Scripts\activate

# Ativar o ambiente (Linux/Mac)
source venv/bin/activate
```
### 3. Instale as Dependências

Com o ambiente ativado, instale as bibliotecas necessárias:

```bash
pip install Flask firebase-admin werkzeug
```
### 4. Configure o Firebase

Siga os passos abaixo para conectar a aplicação com os serviços do Firebase:

1. No console do Firebase, vá em **Configurações do Projeto > Contas de Serviço**
2. Clique em **"Gerar nova chave privada"** e faça o download do arquivo `.json`
3. Renomeie esse arquivo para `firebase_config.json` e coloque-o na **raiz do projeto**
4. No menu lateral do Firebase, vá em **"Storage"** e **habilite** o serviço de armazenamento
   
### 5. Execute a Aplicação

Com tudo configurado, inicie o servidor Flask com o seguinte comando:

```bash
python app.py
```

A aplicação estará disponível em:  
[http://127.0.0.1:5000](http://127.0.0.1:5000)


