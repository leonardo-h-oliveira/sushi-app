# ADR 001 Arquitetura do backend

## Status

Aceita

## Contexto

O escopo inicial citava Supabase e PostgreSQL. Durante a implementação, o projeto adotou uma API própria com FastAPI, SQLAlchemy e Alembic, usando SQLite no desenvolvimento e mantendo compatibilidade com PostgreSQL.

## Decisão

Manter o backend próprio como a arquitetura oficial do MVP. O frontend acessa somente a API HTTP. A API concentra autenticação administrativa, regras de preço, pedidos e persistência. PostgreSQL será usado nos ambientes publicados, e SQLite continuará restrito ao desenvolvimento local e aos testes.

## Consequências

- As regras de negócio ficam explícitas e testáveis no backend.
- O projeto precisa publicar e operar dois serviços, frontend e API.
- Migrações, credenciais, CORS, logs, backup e disponibilidade do banco passam a ser responsabilidades do projeto.
- Uma migração futura para Supabase só deverá ocorrer após nova decisão arquitetural.
