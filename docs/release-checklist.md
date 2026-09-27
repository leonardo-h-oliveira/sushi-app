# Checklist de lançamento do MVP

Este checklist define quando o Sushi App pode ser chamado de MVP concluído. Cada item deve possuir uma evidência verificável, como uma execução de CI, um link do ambiente publicado ou o registro de um teste.

## Código e revisão

- [ ] As branches de funcionalidade foram integradas por Pull Request.
- [ ] A CI do último commit da `main` foi aprovada.
- [ ] Não há mudanças locais ou branches obrigatórias fora da `main`.
- [ ] O README descreve o estado real da versão.

## Segurança e privacidade

- [ ] `.env`, credenciais e bancos locais não estão versionados.
- [ ] As credenciais de produção são diferentes dos valores de exemplo.
- [ ] Rotas administrativas rejeitam usuários sem autenticação.
- [ ] A consulta pública de pedido não expõe telefone ou endereço.
- [ ] CORS permite somente os endereços utilizados em produção.

## Critérios de aceite do MVP

- [ ] O cliente abre o cardápio em um celular.
- [ ] O cliente seleciona produto, variação, adicional, quantidade e observação.
- [ ] O carrinho permite alterar quantidade e remover item.
- [ ] Entrega calcula a taxa e exige endereço.
- [ ] Retirada não exige endereço nem cobra taxa.
- [ ] PIX, cartão na entrega e dinheiro podem ser selecionados.
- [ ] O pedido é criado e recebe um número.
- [ ] O pedido aparece no painel do restaurante com todos os dados operacionais.
- [ ] O restaurante percorre os estados até concluir o pedido.
- [ ] O cliente visualiza o novo status na página de acompanhamento.
- [ ] Produtos, preços, imagens, categorias e disponibilidade podem ser administrados.

## Qualidade

- [ ] Testes de backend, frontend, lint e build passam localmente e na CI.
- [ ] Um teste ponta a ponta cobre o fluxo principal.
- [ ] Estados de carregamento, vazio e erro foram conferidos.
- [ ] O layout foi testado em Android e iPhone, ou em equivalentes simulados.
- [ ] A instalação como PWA foi conferida em produção.
- [ ] Não há erros relevantes no console do navegador.

## Publicação

- [ ] Banco PostgreSQL e migrações foram configurados no ambiente de staging.
- [ ] Frontend e backend de staging estão conectados por HTTPS.
- [ ] O fluxo completo foi aprovado em staging.
- [ ] Foi definida uma rotina de backup do banco.
- [ ] A versão `v0.1.0` foi criada somente após a aprovação dos itens obrigatórios.

## Evidência final

Registrar na release: commit publicado, endereço da aplicação, resultado da CI, dispositivos testados, data da validação e problemas conhecidos aceitos.
