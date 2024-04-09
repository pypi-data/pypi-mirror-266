## Índice
1. [Introdução](#introdução)
2. [Pré-Requisitos](#pré-requisitos)
3. [Instalação do PostgreSQL](#instalação-do-postgresql)
4. [Configuração de Bancos de Dados e Usuários](#configuração-de-bancos-de-dados-e-usuários)
    - [Marketplace](#marketplace)
    - [RapidPro](#rapidpro)
5. [Configuração de Acesso Remoto](#configuração-de-acesso-remoto)
6. [Conexão com o pgAdmin](#conexão-com-o-pgadmin)
7. [Restauração de Backups](#restauração-de-backups)
8. [Permissões no PostgreSQL](#permissões-no-postgresql)
9. [Conclusão](#conclusão)

## Introdução
Este documento fornece um guia passo a passo para configurar o PostgreSQL no Windows Subsystem for Linux (WSL), com foco em preparar o ambiente para as aplicações RapidPro e Marketplace.

## Pré-Requisitos
- Windows Subsystem for Linux (WSL) instalado.
- PostgreSQL instalado no WSL.
- pgAdmin instalado no Windows.
- Conexão de rede entre o WSL e o Windows configurada.

## Instalação do PostgreSQL
1. Abra o terminal do WSL e atualize os pacotes:
    ```bash
    sudo apt update && sudo apt upgrade
    ```
2. Instale o PostgreSQL:
    ```bash
    sudo apt install postgresql postgresql-contrib
    ```

## Configuração de Bancos de Dados e Usuários

### Marketplace
1. Conecte-se ao PostgreSQL:
    ```bash
    sudo -u postgres psql
    ```
2. Crie o usuário e o banco de dados para o Marketplace:
    ```sql
    CREATE USER marketplace WITH PASSWORD 'marketplace';
    CREATE DATABASE marketplace WITH OWNER = marketplace;
    \q
    ```

### RapidPro
1. Conecte-se ao PostgreSQL novamente:
    ```bash
    sudo -u postgres psql
    ```
2. Crie o usuário e o banco de dados para o RapidPro:
    ```sql
    CREATE USER rapidpro WITH PASSWORD 'rapidpro';
    CREATE DATABASE rapidpro WITH OWNER = rapidpro;
    \q
    ```
Agora você tem dois usuários e dois bancos de dados configurados no mesmo servidor PostgreSQL.

<!-- ## Configuração de Acesso Remoto
1. Descubra o endereço IP do seu WSL:
    ```bash
    hostname -I #172.31.115.79
    ```
2. Edite o arquivo pg_hba.conf para permitir conexões remotas:
    ```bash
    sudo nano /etc/postgresql/12/main/pg_hba.conf
    ```
3. Adicione a seguinte linha, substituindo 172.31.115.79 pelo endereço IP do seu WSL:
    ```css
    host all all 172.31.115.79/32 md5
    ```
4. Salve e saia, depois reinicie o PostgreSQL:
    ```bash
    sudo service postgresql restart
    ``` -->
## Configuração do Túnel SSH
1. Certifique-se de que o serviço SSH está rodando no WSL:
```bash
Copy code
sudo service ssh status
```
Se não estiver, inicie o serviço:

```bash
Copy code
sudo service ssh start
```
2. Edite o arquivo de configuração do SSH para permitir autenticação por senha:
```bash
Copy code
sudo nano /etc/ssh/sshd_config
```
Encontre a linha #PasswordAuthentication yes e mude para PasswordAuthentication yes.
Reinicie o serviço SSH:
```bash
Copy code
sudo service ssh restart
```
Descubra o nome do seu usuário no WSL:
```bash
Copy code
whoami
```
No terminal do Windows, crie um túnel SSH substituindo SEU_USUARIO_NO_WSL pelo seu nome de usuário no WSL:
```powershell
Copy code
ssh -L 5433:localhost:5432 SEU_USUARIO_NO_WSL@localhost -p 22
```
Quando solicitado, insira a senha do seu usuário no WSL.

## Restauração de Backups
Para restaurar backups, você pode usar o comando psql ou pg_restore, dependendo do formato do seu backup. Por exemplo:
```bash
psql -U rapidpro -d rapidpro -f /caminho/para/seu/backup.sql
```

## Permissões no PostgreSQL
Para garantir que o usuário postgres tenha acesso total aos bancos de dados, você pode executar os seguintes comandos:
```sql
GRANT ALL PRIVILEGES ON DATABASE rapidpro TO postgres;
\c rapidpro
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO postgres;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO postgres;
GRANT ALL PRIVILEGES ON ALL FUNCTIONS IN SCHEMA public TO postgres;
```

## Conexão com o pgAdmin
1. Abra o pgAdmin no Windows.
2. Crie uma nova conexão com o servidor PostgreSQL no WSL:
	Host: localhost
	Port: 5433
	Maintenace db: postgres
	Username: postgres
3. Conecte-se ao server:
	Password: senha que você configurou para o usuário no PostgreSQL
	
## Conclusão
Importante testar se tudo funcionou corretamente 