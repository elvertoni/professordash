# Aula 07 — JavaScript: Variáveis, tipos e operadores

O HTML e o CSS que você aprendeu até aqui são linguagens de marcação e estilo — elas descrevem conteúdo e aparência, mas não executam lógica. Para dar vida a uma página, precisamos de uma linguagem de programação de verdade. O JavaScript é a linguagem que roda no navegador e permite criar desde animações simples até aplicações web completas. Nesta aula conceitual, vamos conhecer os blocos fundamentais da linguagem: variáveis, tipos de dados e operadores.

## O que são variáveis?

Variáveis são como caixinhas nomeadas na memória do computador onde você guarda valores. Em JavaScript, você pode declarar variáveis de três formas: `var`, `let` e `const`.

:::conceito Declaração de variáveis
var: forma antiga, escopo de função, evite usar. let: escopo de bloco,
pode ser reatribuída. const: escopo de bloco, não pode ser reatribuída
(obrigatória para valores que não vão mudar). A regra prática: use
const por padrão e let só quando precisar reatribuir.
:::

```js
const nome = "Ana";      // string - não pode reatribuir
let idade = 17;           // number - pode mudar
var antigo = "evite";     // forma desencorajada
```

:::importante const não torna o valor imutável
Com const, a variável não pode ser reatribuída, mas o conteúdo de
objetos e arrays declarados com const pode ser modificado.
Exemplo: const lista = [1,2,3]; lista.push(4) funciona normalmente.
O que não pode é fazer lista = [4,5,6].
:::

## Tipos primitivos

JavaScript tem 7 tipos primitivos: string, number, boolean, null, undefined, symbol e bigint. Os 5 primeiros são os que você mais usará no começo.

:::exemplo Tipos primitivos na prática
```js
const texto = "Olá, mundo";       // string
const numero = 42;                 // number
const decimal = 3.14;              // number (não existe float separado)
const verdadeiro = true;           // boolean
const nulo = null;                 // null (ausência intencional de valor)
const indefinido = undefined;       // undefined (valor não atribuído)
```
:::

Uma curiosidade peculiar do JavaScript: `typeof null` retorna `"object"` — isso é um erro histórico da linguagem que nunca foi corrigido por questões de compatibilidade.

:::curiosidade Type coercion — conversão automática
JavaScript tenta converter tipos automaticamente em operações.
"5" - 2 resulta em 3 (string vira number), mas "5" + 2 resulta
em "52" (number vira string). Esse comportamento é chamado de
coerção de tipo e é fonte frequente de bugs — use Number() e
String() para conversões explícitas.
:::

## Operadores

JavaScript oferece operadores para fazer contas, comparar valores, combinar lógica e muito mais.

:::conceito Operadores — aritméticos, comparação e lógicos
Aritméticos: + - * / % (resto) ** (potência)
Comparação: == (valor), === (valor e tipo), !=, !==, , =
Lógicos: && (E), || (OU), ! (NÃO)
:::

A diferença entre `==` e `===` é crucial: `==` compara apenas o valor após converter os tipos (5 == "5" dá true), enquanto `===` compara valor e tipo sem conversão (5 === "5" dá false). A recomendação é sempre usar `===`.

```js
const a = 10;
const b = "10";
console.log(a == b);   // true  (coerção)
console.log(a === b);  // false (tipos diferentes)
console.log(a + Number(b)); // 20 (conversão explícita)
```

## Template strings e interpolação

Desde o ES6 (2015), JavaScript permite interpolar variáveis dentro de strings usando template literals (crases).

:::exemplo Template strings
```js
const nome = "Maria";
const idade = 16;
// Sem template string (concatenação antiga)
console.log("Olá, " + nome + ", você tem " + idade + " anos.");
// Com template string (moderna)
console.log(`Olá, ${nome}, você tem ${idade} anos.`);
```
:::

Template literals também respeitam quebras de linha, o que facilita criar strings multilinha sem precisar de `\n`.

## Questões de fixação

:::questao Qual a diferença entre let e const no JavaScript?
a) let declara números e const declara textos
b) const não pode ser reatribuída, let pode *
c) let só funciona dentro de funções
d) const é a versão antiga e não deve mais ser usada
> const não permite reatribuição da variável — uma vez declarada,
> não pode receber outro valor com =. let permite reatribuição
> normalmente. Ambos têm escopo de bloco. A regra prática é usar
> const como padrão e let apenas quando precisar reatribuir.
:::

:::questao Qual expressão NÃO resulta em um erro no JavaScript?
a) const nome; nome = "João"
d) let idade = 15; idade = 16 *
b) 10 === "10"
c) const lista = [1,2]; lista = [3,4]
> A única opção válida é a B: let permite reatribuição. const exige
> valor inicial (A dá erro de sintaxe). 10 === "10" retorna false
> (não erro), mas a expressão em si é válida. const não permite
> reatribuição, então D dá erro em lista = [3,4].
:::

## Atividade prática

Abra o console do navegador (F12 > Console) e declare variáveis com seu nome, idade, altura e se é estudante. Use `const` para dados fixos e `let` para mutáveis. Use `console.log` com template string para exibir uma frase: "Olá, [nome]. Você tem [idade] anos e [altura]m de altura."

:::objetivo Entrega
Screenshots do console do navegador mostrando as declarações e a
frase gerada com template string. Cole os comandos usados em um
arquivo .txt ou .js.
:::

:::roteiro
Pessoal, abram o console agora mesmo e digitem. Não precisa de
editor, não precisa de arquivo. Só F12, clique em Console, e
comecem a digitar JavaScript. O navegador é o melhor ambiente
para testar JS — é instantâneo.
:::

## Fechamento

:::resumo
- Variáveis guardam valores na memória: const (padrão), let (reatribuição)
- Tipos primitivos principais: string, number, boolean, null, undefined
- === compara valor e tipo; == compara apenas valor (evite)
- Template strings com crase permitem interpolação `${variavel}`
- typeof revela o tipo de um valor em tempo de execução
- Próxima aula: controle de fluxo e funções — escrevendo lógica com if, for e funções
:::
