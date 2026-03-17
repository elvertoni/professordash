# Portifa.md — Ajustes de Design para tonicoimbra.com

> Objetivo: alinhar o portfólio ao design system do **aulas.tonicoimbra.com** — fundo escuro
> roxo/preto, acento violeta, tipografia `#e4e4f0`, cards com borda `zinc-800`.

---

## 1. Design Tokens — O que muda

### Cores (Tailwind config)

| Token | **Atual** (portfólio) | **Alvo** (aulas) |
|---|---|---|
| `base` | `#0f172a` (slate-900 azul) | `#0d0d1a` (roxo profundo) |
| `surface` | `#141e33` (navy) | `#1a1a2e` (roxo escuro) |
| `primary` | `#2563eb` (blue-600) | `#7c3aed` (violet-700) |
| `primaryLight` | — | `#8b5cf6` (violet-500) |
| `primaryXLight` | — | `#a78bfa` (violet-400) |
| `secondary` | `#0d9488` (teal-600) | `#06b6d4` (cyan-500) — mantém |
| `accent` | `#06b6d4` (cyan-500) | `#22d3ee` (cyan-400) |
| `textMain` | `#f1f5f9` (slate-100) | `#e4e4f0` (ligeiramente lilás) |
| `textMuted` | `#94a3b8` (slate-400) | `#8b8ba7` (cinza-lilás) |
| `border` | `rgba(37,99,235,0.2)` | `#27272a` (zinc-800) |

### No `tailwind.config.js`

```js
// Substituir o bloco colors no extend:
colors: {
  base:      '#0d0d1a',   // era #0f172a
  surface:   '#1a1a2e',   // era #141e33
  primary:   '#7c3aed',   // era #2563eb
  secondary: '#06b6d4',   // mantém cyan
  accent:    '#22d3ee',   // levemente mais claro
  textMain:  '#e4e4f0',   // era #f1f5f9
  textMuted: '#8b8ba7',   // era #94a3b8
},
```

---

## 2. CSS Customizado (`assets/css/style.css`)

### Background com granulação roxa

```css
/* Trocar o gradiente de fundo da hero */
/* Era: azul/navy */
/* Novo: roxo profundo com glow violeta */

body {
  background-color: #0d0d1a;
}

/* Glow de fundo (elemento decorativo) */
.bg-glow {
  background: radial-gradient(
    ellipse 80% 50% at 50% -10%,
    rgba(139, 92, 246, 0.15),  /* violet */
    transparent
  );
}
```

### Scrollbar personalizada

```css
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: #0d0d1a; }
::-webkit-scrollbar-thumb { background: #3f3f5a; border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: #7c3aed; }
```

### Selection highlight

```css
/* Era azul, muda para violeta */
::selection {
  background-color: #7c3aed;
  color: #fff;
}
```

---

## 3. Navbar

**Atual:** `bg-base/80` com glow azul no link ativo
**Alvo:** mesmo fundo `bg-[#0d0d1a]/90`, border `border-zinc-800`, hover violeta

```html
<!-- Classes da nav atual → substituir -->
<nav class="bg-base/95 border-b border-white/5 ...">

<!-- Novo: -->
<nav class="bg-[#0d0d1a]/90 backdrop-blur-md border-b border-zinc-800 ...">

<!-- Links de navegação: trocar hover/active de azul para violeta -->
<!-- Atual: hover:text-accent  (cyan) -->
<!-- Novo:  hover:text-violet-400 -->

<!-- Link ativo: trocar border-primary → border-violet-500 -->
```

---

## 4. Hero Section

### Ponto decorativo no nome ("Toni Coimbra**.**")

```html
<!-- Atual: text-accent (cyan) -->
<span class="text-accent">.</span>

<!-- Novo: violet -->
<span class="text-violet-400" style="text-shadow: 0 0 12px rgba(139,92,246,0.6)">.</span>
```

### Subtítulo destacado

```html
<!-- Atual: text-primary (blue) -->
<span class="text-primary font-semibold">soluções de automação...</span>

<!-- Novo: -->
<span class="text-violet-400 font-semibold">soluções de automação...</span>
```

### Botão primário ("Ver Projetos")

```html
<!-- Atual: bg-primary hover:shadow-blue -->
<a class="bg-primary hover:shadow-[0_0_15px_rgba(37,99,235,0.5)] ...">

<!-- Novo: -->
<a class="bg-violet-600 hover:bg-violet-700
           hover:shadow-[0_0_20px_rgba(139,92,246,0.4)]
           transition-all duration-300 ...">
```

### Botão secundário ("Fale Comigo")

```html
<!-- Atual: border-primary/30 hover:border-primary -->
<a class="border border-primary/30 hover:border-primary text-textMain ...">

<!-- Novo: -->
<a class="border border-violet-500/30 hover:border-violet-500/60
           text-[#e4e4f0] hover:text-violet-300
           hover:bg-violet-500/5 transition-all duration-300 ...">
```

### Glow decorativo de fundo (elemento blob)

```html
<!-- Atual: bg-primary/20 blur-[100px] -->
<div class="bg-primary/20 blur-[100px] ...">

<!-- Novo: -->
<div class="bg-violet-600/20 blur-[120px] rounded-full ...">
```

---

## 5. Seção "Sobre Mim"

### Linha decorativa vertical

```html
<!-- Atual: border-l-2 border-primary -->
<div class="border-l-2 border-primary pl-8">

<!-- Novo: -->
<div class="border-l-2 border-violet-500 pl-8">
```

### Badges de formação

```html
<!-- Atual: bg-primary/5 border-primary/10 text-primary -->
<span class="bg-primary/5 border border-primary/10 text-primary ...">

<!-- Novo: -->
<span class="bg-violet-500/10 border border-violet-500/20 text-violet-300 rounded-md px-3 py-1 text-sm ...">
```

---

## 6. Seção "Tech Stack"

### Cards de categoria

```html
<!-- Atual: bg-surface border-white/5 hover:border-primary/30 -->
<div class="bg-surface border border-white/5
            hover:border-primary/30 hover:shadow-[0_0_15px_rgba(37,99,235,0.3)] ...">

<!-- Novo: -->
<div class="bg-[#1a1a2e] border border-zinc-800
            hover:border-violet-500/40
            hover:shadow-[0_0_20px_rgba(139,92,246,0.1)]
            transition-all duration-300 rounded-xl p-6 ...">
```

### Ícone de categoria (header do card)

```html
<!-- Atual: bg-primary/20 text-primary -->
<div class="bg-primary/20 text-primary ...">

<!-- Novo: -->
<div class="bg-violet-500/10 border border-violet-500/20 text-violet-400 ...">
```

### Badges de tecnologia (tags)

```html
<!-- Atual: bg-surface/30 border-primary/10 text-textMuted -->
<span class="bg-surface/30 border border-primary/10 text-textMuted ...">

<!-- Novo: -->
<span class="bg-zinc-900/50 border border-zinc-800 text-[#8b8ba7]
             hover:border-violet-500/30 hover:text-violet-300
             transition-colors duration-200 rounded-md px-2 py-1 text-xs ...">
```

> **Dica:** para as outras categorias (Dados, Infra) use os accentos secundários como no aulas:
> - IA/ML → violeta (`violet-400`)
> - Automação → cyan (`cyan-400`)
> - Dados → emerald (`emerald-400`)
> - Infra → amber (`amber-400`)

---

## 7. Seção "Projetos em Destaque"

### Cards de projeto

```html
<!-- Atual: bg-surface border-white/5 hover:border-primary/40 -->
<div class="bg-surface border border-white/5
            hover:border-primary/40 hover:shadow-[0_0_15px_rgba(37,99,235,0.3)] ...">

<!-- Novo: -->
<div class="bg-[#1a1a2e] border border-zinc-800
            hover:border-violet-500/40
            hover:shadow-[0_0_20px_rgba(139,92,246,0.1)]
            transition-all duration-300 rounded-xl overflow-hidden ...">
```

### Badge de status (ex: "TJPR")

```html
<!-- Novo badge estilo aulas: -->
<span class="text-[10px] font-bold uppercase tracking-widest
             text-violet-400 bg-violet-400/10
             border border-violet-400/20
             px-2 py-0.5 rounded">TJPR</span>
```

### Tags de tecnologia no projeto

```html
<!-- Atual: bg-accent/10 text-accent  ou  bg-secondary/10 text-secondary -->

<!-- Novo — variar por tipo: -->
<!-- Python/IA:    --> <span class="bg-violet-500/10 text-violet-300 border border-violet-500/20 ...">
<!-- n8n/API:     --> <span class="bg-cyan-500/10 text-cyan-300 border border-cyan-500/20 ...">
<!-- DB/Dados:    --> <span class="bg-emerald-500/10 text-emerald-300 border border-emerald-500/20 ...">
<!-- Infra/DevOps:--> <span class="bg-amber-500/10 text-amber-300 border border-amber-500/20 ...">
```

### Link "Ver Projeto →"

```html
<!-- Atual: text-primary hover:text-accent -->
<a class="text-primary hover:text-accent ...">

<!-- Novo: -->
<a class="text-xs font-medium text-violet-400 hover:text-violet-300
           bg-violet-500/10 hover:bg-violet-500/20
           border border-violet-500/20
           px-3 py-1.5 rounded-lg transition-all ...">
  Ver Projeto &rarr;
</a>
```

---

## 8. Seção "Experiência Profissional"

### Timeline — linha vertical

```html
<!-- Atual: bg-primary/30 -->
<div class="bg-primary/30 ...">

<!-- Novo: -->
<div class="bg-violet-500/30 ...">
```

### Ponto da timeline

```html
<!-- Atual: bg-primary border-base -->
<div class="bg-primary border-4 border-base ...">

<!-- Novo: -->
<div class="bg-violet-500 border-4 border-[#0d0d1a]
             shadow-[0_0_10px_rgba(139,92,246,0.5)] ...">
```

### Card de experiência

```html
<!-- Atual: bg-surface/50 border-primary/20 -->
<div class="bg-surface/50 border border-primary/20 ...">

<!-- Novo: -->
<div class="bg-[#1a1a2e] border border-zinc-800
            hover:border-violet-500/30
            transition-all duration-200 rounded-xl p-6 ...">
```

### Badge de período ("Presente")

```html
<!-- Atual: bg-accent/20 text-accent -->
<span class="bg-accent/20 text-accent ...">

<!-- Novo: -->
<span class="text-xs font-bold uppercase tracking-widest
             text-emerald-400 bg-emerald-400/10
             border border-emerald-400/20
             px-2 py-0.5 rounded">Presente</span>
```

### Empresa/cargo destacado

```html
<!-- Atual: text-primary -->
<span class="text-primary font-semibold">TJPR</span>

<!-- Novo: -->
<span class="text-violet-400 font-semibold">TJPR</span>
```

---

## 9. Seção "Contato"

### Container principal

```html
<!-- Atual: bg-surface border-primary/20 -->
<div class="bg-surface border border-primary/20 ...">

<!-- Novo: -->
<div class="bg-[#1a1a2e] border border-zinc-800 rounded-xl p-8 ...">
```

### Inputs do formulário

```html
<!-- Atual: bg-base border-primary/20 focus:border-primary -->
<input class="bg-base border border-primary/20
              focus:border-primary focus:ring-1 focus:ring-primary ...">

<!-- Novo: -->
<input class="bg-[#0d0d1a] border border-zinc-800
              text-[#e4e4f0] placeholder-[#8b8ba7]/50
              focus:border-violet-500/60 focus:ring-1 focus:ring-violet-500/30
              focus:outline-none rounded-lg px-4 py-3
              transition-colors duration-200 ...">
```

### Botão "Enviar Mensagem"

```html
<!-- Atual: bg-gradient-brand (teal→cyan) -->
<button class="bg-gradient-brand ...">

<!-- Novo: -->
<button class="bg-violet-600 hover:bg-violet-700
               text-white font-medium
               shadow-lg shadow-violet-500/20
               hover:shadow-[0_0_20px_rgba(139,92,246,0.4)]
               transition-all duration-300
               px-6 py-3 rounded-lg ...">
  Enviar Mensagem
</button>
```

---

## 10. Footer

```html
<!-- Atual: border-t border-white/5 text-textMuted/70 -->
<footer class="border-t border-white/5 ...">

<!-- Novo: -->
<footer class="border-t border-zinc-800 py-8 text-center">
  <p class="text-[#8b8ba7] text-sm">
    © 2026 <span class="text-violet-400 font-medium">Toni Coimbra</span>.
    Construído com HTML, TailwindCSS &amp; Vanilla JS.
  </p>
</footer>
```

---

## 11. Tipografia

| Elemento | Atual | Novo |
|---|---|---|
| Headings (h1, h2) | `text-textMain` (`#f1f5f9`) | `text-[#e4e4f0]` |
| Subtítulos / label | `text-textMuted` (`#94a3b8`) | `text-[#8b8ba7]` |
| Destaque em parágrafo | `text-primary` (blue) | `text-violet-400` |
| Mono / tags | `font-mono text-accent` | `font-mono text-violet-400` |

---

## 12. Efeitos e Detalhes Finais

### Cursor glow (se houver)
```css
/* Trocar cor do cursor follower de azul para violeta */
.cursor-glow {
  background: radial-gradient(circle, rgba(139,92,246,0.15), transparent 60%);
}
```

### Animação de "Scroll" indicator
```html
<!-- Atual: text-textMuted/50 -->
<span class="text-[#8b8ba7]/50 animate-bounce ...">Scroll</span>
```

### Hover em ícones sociais (se houver)
```html
<!-- GitHub, LinkedIn etc. -->
<a class="text-[#8b8ba7] hover:text-violet-400
           hover:bg-violet-500/10
           border border-zinc-800 hover:border-violet-500/40
           transition-all duration-200 p-2 rounded-lg ...">
```

---

## 13. Resumo das Substituições Globais (sed/replace-all)

Para aplicar em lote no `assets/css/style.css` e `index.html`:

| Substituir | Por |
|---|---|
| `#2563eb` / `blue-600` / `primary` (azul) | `#7c3aed` / `violet-700` |
| `#0f172a` | `#0d0d1a` |
| `#141e33` | `#1a1a2e` |
| `#f1f5f9` | `#e4e4f0` |
| `#94a3b8` | `#8b8ba7` |
| `rgba(37,99,235,` | `rgba(139,92,246,` |
| `border-primary/` → borders genéricas | `border-zinc-800` ou `border-violet-500/20` |
| `shadow-[0_0_*_rgba(37,99,235` | `shadow-[0_0_*_rgba(139,92,246` |
| `bg-gradient-brand` | `bg-violet-600` |

---

## 14. Paleta Final de Referência

```
Fundo principal:  #0d0d1a  ████
Surface / cards:  #1a1a2e  ████
Borda padrão:     #27272a  ████  (zinc-800)
Violeta primário: #7c3aed  ████  (violet-700)
Violeta médio:    #8b5cf6  ████  (violet-500)
Violeta claro:    #a78bfa  ████  (violet-400)
Cyan accent:      #22d3ee  ████  (cyan-400)
Emerald:          #34d399  ████  (emerald-400)
Amber:            #fbbf24  ████  (amber-400)
Rose:             #fb7185  ████  (rose-400)
Texto principal:  #e4e4f0  ████
Texto secundário: #8b8ba7  ████
```
