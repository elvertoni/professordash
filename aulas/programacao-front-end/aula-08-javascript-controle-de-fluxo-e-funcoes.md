# Aula 08 — JavaScript: Controle de fluxo e funções

Agora que você já sabe declarar variáveis e conhece os tipos de dados do JavaScript, chegou a hora de fazer o código tomar decisões, repetir tarefas e se organizar em blocos reutilizáveis. Nesta aula prática, vamos construir uma calculadora de médias escolares usando estruturas condicionais, loops e funções — os três pilares da lógica de programação.

## O que vamos construir

Uma calculadora que recebe 4 notas, calcula a média, diz se o aluno foi aprovado ou reprovado e mostra quantos alunos passaram na turma. Tudo no console do navegador, mas organizado em funções reutilizáveis.

:::objetivo Resultado final
Um script JavaScript que, ao ser executado no console, processa
um array de notas, calcula médias e exibe no console: "Aluno:
7.5 - Aprovado" para cada aluno e um resumo final.
:::

## Pré-requisitos

:::dica Para esta aula você precisa de
Navegador moderno (Chrome ou Firefox) com console do desenvolvedor
(F12). Entender variáveis, tipos e template strings da aula 07.
:::

## Passo a passo

1. **Criar a estrutura condicional com if/else** — Comece declarando notas e calculando a média.

Abra o console do navegador e digite:

```js
const nota1 = 8;
const nota2 = 7;
const nota3 = 9;
const nota4 = 6;

const media = (nota1 + nota2 + nota3 + nota4) / 4;

if (media >= 7) {
    console.log(`Média: ${media} - Aprovado`);
} else if (media >= 5) {
    console.log(`Média: ${media} - Recuperação`);
} else {
    console.log(`Média: ${media} - Reprovado`);
}
```

2. **Criar uma função para encapsular a lógica** — Em vez de repetir o código para cada aluno, crie uma função.

```js
function calcularMedia(notas) {
    let soma = 0;
    for (let i = 0; i < notas.length; i++) {
        soma = soma + notas[i];
    }
    return soma / notas.length;
}
```

A função `calcularMedia` recebe um array de notas, percorre cada uma com um loop `for` e retorna a média.

3. **Usar for...of para simplificar o loop** — O JavaScript moderno oferece uma sintaxe mais limpa para percorrer arrays.

```js
function calcularMedia(notas) {
    let soma = 0;
    for (const nota of notas) {
        soma += nota;
    }
    return soma / notas.length;
}
```

O `for...of` percorre cada elemento diretamente, sem precisar de índice.

4. **Criar função de classificação** — Use condicionais dentro de outra função.

```js
function classificar(media) {
    if (media >= 7) {
        return "Aprovado";
    } else if (media >= 5) {
        return "Recuperação";
    } else {
        return "Reprovado";
    }
}
```

5. **Compor as funções para processar vários alunos** — Crie uma função que recebe um array de alunos e processa cada um.

```js
function processarTurma(alunos) {
    let aprovados = 0;
    for (const aluno of alunos) {
        const media = calcularMedia(aluno.notas);
        const situacao = classificar(media);
        console.log(`${aluno.nome}: ${media.toFixed(1)} - ${situacao}`);
        if (situacao === "Aprovado") {
            aprovados++;
        }
    }
    console.log(`---`);
    console.log(`Total de aprovados: ${aprovados} de ${alunos.length}`);
}
```

6. **Executar com dados reais** — Teste o sistema completo.

```js
const turma = [
    { nome: "Ana",    notas: [8, 7, 9, 6] },
    { nome: "Bruno",  notas: [5, 6, 4, 7] },
    { nome: "Carla",  notas: [10, 9, 8, 9] },
    { nome: "Daniel", notas: [3, 5, 4, 4] },
];

processarTurma(turma);
```

## Checkpoint

:::objetivo Você está no caminho certo se
Ao executar processarTurma(turma) no console, você vê a saída:
Ana: 7.5 - Aprovado
Bruno: 5.5 - Recuperação
Carla: 9.0 - Aprovado
Daniel: 4.0 - Reprovado
---
Total de aprovados: 2 de 4
:::

## Erros comuns

:::atencao Sintoma: o loop for executa para sempre (loop infinito)
Causa: esqueceu de incrementar o contador (i++).
Correção: a estrutura correta é for (let i = 0; i < arr.length; i++).
O terceiro termo é obrigatório para o loop progredir.
:::

:::atencao Sintoma: a função retorna undefined
Causa: a função não tem return ou o return está fora do lugar.
Correção: toda função que deve produzir um valor precisa de return
explícito. Sem return, a função retorna undefined por padrão.
:::

## Desafio

Adicione uma função `calcularMenorNota(notas)` que encontra a menor nota do aluno e, se ela for menor que 2, reprova automaticamente independente da média.

:::importante Desafio extra
Para quem terminar primeiro: transforme o array de alunos em
um array de objetos com nome, media e situacao usando o método
map() — pesquise como ele funciona. Exiba o array resultante.
:::

## Código completo

```js
function calcularMedia(notas) {
    let soma = 0;
    for (const nota of notas) {
        soma += nota;
    }
    return soma / notas.length;
}

function classificar(media) {
    if (media >= 7) {
        return "Aprovado";
    } else if (media >= 5) {
        return "Recuperação";
    } else {
        return "Reprovado";
    }
}

function processarTurma(alunos) {
    let aprovados = 0;
    for (const aluno of alunos) {
        const media = calcularMedia(aluno.notas);
        const situacao = classificar(media);
        console.log(`${aluno.nome}: ${media.toFixed(1)} - ${situacao}`);
        if (situacao === "Aprovado") {
            aprovados++;
        }
    }
    console.log(`---`);
    console.log(`Total de aprovados: ${aprovados} de ${alunos.length}`);
}

const turma = [
    { nome: "Ana",    notas: [8, 7, 9, 6] },
    { nome: "Bruno",  notas: [5, 6, 4, 7] },
    { nome: "Carla",  notas: [10, 9, 8, 9] },
    { nome: "Daniel", notas: [3, 5, 4, 4] },
];

processarTurma(turma);
```

## Fechamento

:::resumo
- if/else if/else permite que o código tome decisões
- for e for...of repetem blocos de código para cada item
- Funções encapsulam lógica com function nome(parametros) { }
- return envia um valor de volta para quem chamou a função
- Paremetros permitem que a função receba dados externos
- Próxima aula: DOM — manipulando a página com JavaScript
:::
