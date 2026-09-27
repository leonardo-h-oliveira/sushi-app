# Publicação do ambiente de staging

O staging é uma cópia de teste do sistema. Ele deve ser validado antes de
qualquer publicação para clientes.

## 1. Banco PostgreSQL no Neon

1. Crie uma conta gratuita no Neon e um projeto chamado `sushi-staging`.
2. Escolha uma região próxima do backend, preferencialmente AWS US East
   (Ohio), quando essa opção estiver disponível.
3. Na tela **Connect**, copie a connection string do PostgreSQL. Use a URL com
   SSL e mantenha-a em segredo.
4. Não salve a URL em arquivos do projeto, mensagens públicas ou commits.

O Neon é utilizado somente como PostgreSQL. A aplicação continua responsável
por autenticação, regras de negócio e API.

## 2. Backend no Render

1. No Render, crie um Blueprint usando este repositório e o arquivo
   `render.yaml`.
2. Revise o recurso antes de confirmar. O Blueprint propõe somente um serviço
   web no plano gratuito.
3. Preencha as variáveis solicitadas:
   - `DATABASE_URL`: connection string copiada do Neon;
   - `ADMIN_USERNAME`: usuário exclusivo da equipe;
   - `ADMIN_PASSWORD`: senha longa e exclusiva;
   - `CORS_ORIGINS`: endereço HTTPS do frontend na Vercel.
4. Aguarde a implantação e confira `https://<api>.onrender.com/health`.

As migrações do Alembic são executadas automaticamente antes de cada início da
API. O Render executa o seed idempotente automaticamente como hook da primeira
implantação do serviço; publicações seguintes não sobrescrevem o cardápio
administrado pelo restaurante.

> Os planos gratuitos são adequados somente para staging. Antes do uso real,
> defina hospedagem comercial e uma política de backup testada.

## 3. Frontend na Vercel

1. Importe o mesmo repositório na Vercel.
2. Defina `frontend` como **Root Directory**.
3. Cadastre estas variáveis no ambiente Preview:
   - `API_URL=https://<api>.onrender.com`
   - `NEXT_PUBLIC_API_URL=https://<api>.onrender.com`
4. Faça o deploy e copie o endereço HTTPS gerado.
5. Volte ao Render e defina `CORS_ORIGINS` com esse endereço, sem barra final.

`API_URL` é usada durante a renderização no servidor. `NEXT_PUBLIC_API_URL` é
exposta ao navegador e permite que carrinho, checkout e painel conversem com a
API.

## 4. Validação

Execute todos os itens de `docs/release-checklist.md`. Registre como evidência:

- URL do frontend e da API;
- commit implantado;
- resultado da CI;
- celular ou simulador utilizado;
- problemas encontrados e decisão tomada.

Não promova o ambiente para produção nem crie `v0.1.0` enquanto os itens
obrigatórios do checklist estiverem pendentes.

