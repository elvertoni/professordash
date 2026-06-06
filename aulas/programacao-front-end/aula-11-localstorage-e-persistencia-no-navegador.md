# Aula 11 — LocalStorage e persistência no navegador

Você já notou como alguns sites lembram sua preferência de tema (claro/escuro) mesmo depois de você fechar e reabrir o navegador? Ou como o carrinho de compras de uma loja mantém os itens que você adicionou, mesmo sem fazer login? Isso é possível graças ao localStorage, uma API do navegador que permite armazenar dados de forma persistente no computador do usuário. Nesta aula, vamos entender como funciona, quando usar e quais são os limites dessa abordagem.

## O que é localStorage?

O `localStorage` é um mecanismo de armazenamento chave-valor fornecido pelo navegador. Os dados ficam salvos no disco do usuário e sobrevivem ao fechamento do navegador, reinicialização do computador e até mesmo à troca de páginas no mesmo domínio.

:::conceito localStorage vs sessionStorage
localStorage: dados persistem mesmo após fechar o navegador.
Só são removidos via código JavaScript (removeItem, clear) ou
limpeza manual dos dados do navegador pelo usuário.
sessionStorage: dados persistem apenas durante a sessão da aba.
Ao fechar a aba ou o navegador, os dados são automaticamente
removidos.
:::

A API é extremamente simples: `localStorage.setItem(chave, valor)` para salvar, `localStorage.getItem(chave)` para ler, `localStorage.removeItem(chave)` para remover um item específico e `localStorage.clear()` para limpar tudo.

## Limitações e características importantes

O localStorage não é um banco de dados relacional — ele tem limitações importantes que você precisa conhecer antes de usá-lo em projetos reais.

:::importante Limitações do localStorage
Capacidade máxima: cerca de 5MB por domínio (pode variar entre
navegadores). Só armazena strings — objetos e arrays precisam
ser convertidos com JSON.stringify e JSON.parse. Os dados ficam
no computador do usuário e não são enviados ao servidor
automaticamente. O acesso é síncrono, o que pode travar a página
em operações com muitos dados.
:::

A limitação de 5MB é generosa para textos e configurações, mas inviável para imagens, vídeos ou grandes volumes de dados estruturados. Para esses casos, existem alternativas como IndexedDB ou, claro, um banco de dados no servidor.

## JSON.stringify e JSON.parse — a ponte para objetos

Como o localStorage só aceita strings, precisamos de uma forma de converter objetos em texto e vice-versa. É aí que entra o JSON.

:::exemplo Salvando e lendo objetos
```js
const usuario = {
    nome: "Ana",
    idade: 17,
    hobbies: ["ler", "programar"]
};

// Salvar: objeto → string
localStorage.setItem("usuario", JSON.stringify(usuario));

// Ler: string → objeto
const dados = JSON.parse(localStorage.getItem("usuario"));
console.log(dados.nome); // "Ana"
```
:::

Se você tentar salvar um objeto sem usar `JSON.stringify`, o JavaScript vai chamar o método `toString()` do objeto e salvar `"[object Object]"` — um erro clássico de quem está começando.

## Quando usar localStorage?

O localStorage é ideal para cenários onde os dados são do usuário, não precisam de segurança crítica e não precisam estar disponíveis em múltiplos dispositivos.

:::exemplo Casos de uso reais
- Preferências de tema (claro/escuro) e idioma
- Carrinho de compras em lojas virtuais
- Rascunhos de formulários (salvar antes de enviar)
- Histórico de busca local
- Estado de tutorial ou onboarding (já foi visto / não mostrar de novo)
- Jogos offline com progresso salvo localmente
:::

:::importante O que NÃO armazenar no localStorage
- Senhas, tokens de autenticação ou dados sensíveis
- Informações que precisam estar no servidor
- Dados que o usuário não pode perder (não há backup automático)
- Grandes volumes de dados (acima de 500KB)
:::

O localStorage é acessível por qualquer JavaScript executado no mesmo domínio, incluindo scripts de terceiros (anúncios, analytics). Por isso, dados sensíveis nunca devem ficar no localStorage.

## Questões de fixação

:::questao Qual método remove um item específico do localStorage?
a) localStorage.delete("chave")
b) localStorage.removeItem("chave") *
c) localStorage.remove("chave")
d) delete localStorage["chave"]
> O método correto é removeItem(). delete() não existe na API.
> remove() também não é um método do localStorage. O operador
> delete funciona em alguns navegadores mas não é padronizado —
> a forma correta e compatível é removeItem().
:::

:::questao Por que objetos precisam de JSON.stringify antes de serem salvos no localStorage?
a) Porque o localStorage só aceita strings como valor *
b) Porque JSON.stringify criptografa os dados para segurança
c) Porque objetos ocupam menos espaço depois de converter
d) Porque o navegador não entende a linguagem JavaScript
> O localStorage armazena exclusivamente strings. Objetos JavaScript
> são convertidos para "[object Object]" pelo toString() se não
> forem serializados. JSON.stringify transforma o objeto em uma
> string JSON válida, e JSON.parse recupera o objeto original.
> Não há criptografia envolvida no processo.
:::

## Atividade prática

Crie uma página HTML com um formulário de contato (nome, email, mensagem) e um botão "Salvar rascunho". Ao clicar, os dados do formulário são salvos no localStorage. Ao recarregar a página, os campos devem ser preenchidos automaticamente com os dados salvos. Adicione também um botão "Limpar rascunho" que remove os dados.

:::objetivo Entrega
Arquivo rascunho.html funcional. Teste: preencha o formulário,
clique em Salvar Rascunho, feche e reabra a página — os campos
devem aparecer preenchidos. Entregue o código completo via
repositório ou arquivo zipado.
:::

:::roteiro
Pessoal, testem o seguinte: abram o formulário, preencham, salvem
o rascunho. Depois fechem o navegador COMPLETAMENTE — não só a
aba — e abram de novo. O rascunho ainda está lá. Isso é persistência
de dados no navegador, e é muito poderoso para a experiência do
usuário.
:::

## Fechamento

:::resumo
- localStorage persiste dados no navegador mesmo após fechar o programa
- Armazena pares chave-valor com limite de ~5MB por domínio
- Só aceita strings: use JSON.stringify para salvar objetos e JSON.parse para ler
- sessionStorage é similar mas os dados duram apenas uma sessão
- Não armazene dados sensíveis (senhas, tokens) no localStorage
- Próxima aula: projeto final — mini e-commerce front-end integrando tudo
:::
