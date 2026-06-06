# Aula 03 — HTML Semântico e boas práticas

Você já sabe criar uma página HTML com headings, parágrafos e listas. Mas será que um programa de computador consegue entender o significado do seu conteúdo? Um leitor de tela para pessoas cegas consegue navegar por ela? E o Google, entende qual parte é o menu, qual é o conteúdo principal e qual é o rodapé? Nesta aula, vamos aprender HTML semântico — tags que carregam significado, não apenas estilo — e por que ele é essencial para acessibilidade, SEO e manutenção de código.

## O que é HTML semântico?

HTML semântico significa usar a tag certa para cada tipo de conteúdo. Em vez de encher a página de `` — que não tem significado algum — usamos tags como ``, ``, ``, `` e `` que descrevem claramente a função de cada parte da página.

:::conceito Tags Semânticas
Tags HTML que comunicam o significado do conteúdo que envolvem,
não apenas a aparência. Exemplos: ``, ``,
``, ``, ``, ``, ``.
:::

O HTML semântico não muda o visual da página — uma `` e um `` aparecem iguais no navegador. A diferença está no código: humanos e máquinas (leitores de tela, robôs de busca) conseguem interpretar a estrutura com muito mais precisão.

## Por que semântica importa?

Acessibilidade, SEO e manutenibilidade são os três pilares que justificam o uso de HTML semântico.

:::importante Acessibilidade vs SEO vs Manutenibilidade
Acessibilidade: leitores de tela como JAWS e NVDA usam tags
semânticas para permitir navegação por atalhos (pular para o main,
navegar por headings). SEO: o Google ranqueia melhor páginas com
estrutura semântica clara, especialmente o uso correto de h1 a h6.
Manutenibilidade: `` é mais fácil de achar no código do que
``.
:::

Um dado importante: cerca de 3% da população brasileira tem deficiência visual severa. Isso significa que, em uma turma de 35 alunos, estatisticamente um deles pode depender de tecnologia assistiva para navegar na web.

## Tags semânticas principais do HTML5

O HTML5 introduziu diversas tags semânticas que hoje são padrão da web.

:::exemplo Estrutura semântica de uma página
```
        — cabeçalho da página ou seção
           — navegação principal
          — conteúdo principal (único por página)
       — conteúdo independente (post, notícia)
       — agrupamento temático
         — conteúdo complementar (sidebar)
        — rodapé com informações de contato
```
:::

Além dessa estrutura, tags como `` e `` agrupam imagens com legendas, `` marca datas e horários de forma legível para máquinas, e `` identifica informações de contato.

:::curiosidade A origem do HTML semântico
O HTML foi criado por Tim Berners-Lee em 1991 como uma linguagem
para compartilhar documentos científicos. As tags semânticas faziam
parte da visão original da web como um espaço de documentos
interligados com significado. O HTML5, lançado em 2014, resgatou
essa visão com as tags semânticas modernas.
:::

## Boas práticas e erros comuns

Usar HTML semântico não é só escolher a tag bonita — é seguir uma hierarquia e evitar armadilhas.

:::importante Hierarquia correta de headings
A regra de ouro: um único `` por página (o título principal),
seguido de ``, `` e assim por diante, sem pular níveis.
Nunca use `` para logotipo ou `` para destaque visual
que não representa subseção. Headings são hierarquia de conteúdo,
não de tamanho de fonte.
:::

Outra prática fundamental é usar `` com um heading dentro. Uma `` sem heading perde o sentido semântico. E lembre-se: `` continua útil para agrupamentos puramente visuais — o que muda é que, quando a tag certa existe, use-a.

## Questões de fixação

:::questao Qual tag HTML5 representa o conteúdo principal e único de uma página?
b) ``
a) `` *
d) ``
> A tag `` envolve o conteúdo principal e único da página. Deve
> haver apenas um `` por documento. `` contém tudo, ``
> agrupa conteúdo temático e `` representa conteúdo independente.
:::

:::questao Qual opção NÃO é um benefício do HTML semântico?
a) Melhora a acessibilidade para leitores de tela
b) Ajuda o Google a entender a estrutura da página
c) Torna as fontes automaticamente maiores e mais bonitas *
d) Facilita a manutenção do código por outros desenvolvedores
> HTML semântico não afeta o estilo visual — as tags semânticas
> aparecem iguais às não-semânticas no navegador. Os benefícios são
> para acessibilidade, SEO e organização do código, não para aparência.
:::

## Atividade prática

Refatore a página HTML que você criou na aula 02 (sua página pessoal) substituindo as `` por tags semânticas: `` para o cabeçalho, `` para o conteúdo, `` para agrupar hobbies e metas, e `` com uma linha de crédito.

:::objetivo Entrega
Arquivo index-semantico.html com a estrutura completa usando pelo
menos 6 tags semânticas diferentes (header, main, section, nav,
article, footer). O conteúdo visual deve ser idêntico ao da aula 2.
:::

:::roteiro
Pessoal, pensem no seguinte: se um robô do Google ler sua página,
ele consegue identificar onde termina o cabeçalho e começa o conteúdo?
Consegue achar o artigo principal? É exatamente isso que as tags
semânticas fazem — elas são etiquetas que organizam o conteúdo para
quem não enxerga a página, literalmente.
:::

## Fechamento

:::resumo
- HTML semântico usa tags com significado, não apenas divs genéricas
- header, nav, main, article, section, aside e footer são as principais
- Acessibilidade, SEO e manutenibilidade são os três benefícios-chave
- A hierarquia de headings (h1 a h6) deve refletir a estrutura do conteúdo
- Próxima aula: CSS — seletores e estilização básica para deixar sua página bonita
:::
