# Publicação do ambiente de staging

O staging é uma cópia de teste do sistema. Ele deve ser validado antes de
qualquer publicação para clientes.

## 1. Backend e banco no Render

1. No Render, crie um Blueprint usando este repositório e o arquivo
   `render.yaml`.
2. Revise os recursos antes de confirmar. O Blueprint propõe um serviço web e
   um PostgreSQL no plano gratuito.
3. Preencha as variáveis solicitadas:
   - `ADMIN_USERNAME`: usuário exclusivo da equipe;
   - `ADMIN_PASSWORD`: senha longa e exclusiva;
   - `CORS_ORIGINS`: endereço HTTPS do frontend na Vercel.
4. Aguarde a implantação e confira `https://<api>.onrender.com/health`.
5. No Shell do serviço, execute uma única vez:

   ```bash
   python backend/seed.py
   ```

As migrações do Alembic são executadas automaticamente antes de cada início da
API. O seed é idempotente, mas não é automático para evitar que uma publicação
altere o cardápio administrado pelo restaurante.

> O PostgreSQL gratuito do Render é adequado apenas para staging: expira após
> 30 dias e não oferece backups. Produção exige um banco persistente e uma
> política de backup definida.

## 2. Frontend na Vercel

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

## 3. Validação

Execute todos os itens de `docs/release-checklist.md`. Registre como evidência:

- URL do frontend e da API;
- commit implantado;
- resultado da CI;
- celular ou simulador utilizado;
- problemas encontrados e decisão tomada.

Não promova o ambiente para produção nem crie `v0.1.0` enquanto os itens
obrigatórios do checklist estiverem pendentes.

