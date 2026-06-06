# Aula 10 — Formulários HTML e validação

Formulários são a principal forma de coletar dados do usuário na web — desde um simples campo de busca até um cadastro completo com dezenas de campos. Nesta aula prática, você vai construir um formulário de cadastro completo com validação nativa do HTML5, validação customizada em JavaScript e captura de dados com FormData.

## O que vamos construir

Um formulário de cadastro de usuário com nome, e-mail, senha, confirmação de senha e data de nascimento. O HTML5 valida campos obrigatórios e formato de e-mail, e o JavaScript adiciona validação de senha forte, confirmação de senha igual e feedback visual em tempo real.

:::objetivo Resultado final
Um formulário estilizado que mostra erros em vermelho abaixo dos
campos, impede o envio com dados inválidos e exibe os dados
capturados em um card ao lado do formulário.
:::

## Pré-requisitos

:::dica Para esta aula você precisa de
Conhecimento de HTML (input, label, form), CSS (seletores, classes),
JavaScript (DOM, addEventListener, funções). Arquivos index.html e
script.js criados.
:::

## Passo a passo

1. **Criar a estrutura HTML do formulário** — Use inputs com tipos específicos e labels corretas.

```html
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Cadastro</title>
    <link rel="stylesheet" href="style.css">
</head>
<body>
    <div class="container">
        <form id="formCadastro">
            <h1>Cadastro</h1>
            
            <div class="campo">
                <label for="nome">Nome completo</label>
                <input type="text" id="nome" name="nome" required minlength="3">
                <span class="erro" id="erroNome"></span>
            </div>

            <div class="campo">
                <label for="email">E-mail</label>
                <input type="email" id="email" name="email" required>
                <span class="erro" id="erroEmail"></span>
            </div>

            <div class="campo">
                <label for="senha">Senha</label>
                <input type="password" id="senha" name="senha" required minlength="8">
                <span class="erro" id="erroSenha"></span>
            </div>

            <div class="campo">
                <label for="confirmarSenha">Confirmar senha</label>
                <input type="password" id="confirmarSenha" name="confirmarSenha" required>
                <span class="erro" id="erroConfirmar"></span>
            </div>

            <div class="campo">
                <label for="nascimento">Data de nascimento</label>
                <input type="date" id="nascimento" name="nascimento" required>
                <span class="erro" id="erroNascimento"></span>
            </div>

            <button type="submit">Cadastrar</button>
        </form>
        <div id="resultado"></div>
    </div>
    <script src="script.js"></script>
</body>
</html>
```

2. **Estilizar o formulário** — Crie um visual limpo com feedback visual de erro.

```css
* { margin: 0; padding: 0; box-sizing: border-box; }
body { font-family: Arial, sans-serif; background: #f0f2f5; padding: 40px 20px; }
.container { max-width: 800px; margin: 0 auto; display: grid; grid-template-columns: 1fr 1fr; gap: 40px; }
h1 { margin-bottom: 24px; color: #1a1a2e; }
.campo { margin-bottom: 16px; }
label { display: block; margin-bottom: 4px; font-weight: bold; color: #333; }
input {
    width: 100%; padding: 10px; border: 2px solid #ddd;
    border-radius: 6px; font-size: 1rem; transition: border-color 0.2s;
}
input:focus { outline: none; border-color: #2a9d8f; }
input.invalido { border-color: #e63946; }
.erro { color: #e63946; font-size: 0.85rem; margin-top: 4px; display: block; min-height: 20px; }
button {
    background: #2a9d8f; color: white; border: none;
    padding: 12px 24px; border-radius: 6px; cursor: pointer;
    font-size: 1rem; width: 100%;
}
button:hover { background: #21867a; }
#resultado { background: white; border-radius: 6px; padding: 20px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }
```

3. **Capturar dados com FormData** — No JavaScript, impeça o envio padrão e capture os dados.

```js
const form = document.querySelector('#formCadastro');
const resultado = document.querySelector('#resultado');

form.addEventListener('submit', function(event) {
    event.preventDefault();
    
    if (!validarFormulario()) {
        return;
    }
    
    const formData = new FormData(form);
    const dados = Object.fromEntries(formData);
    
    exibirDados(dados);
});
```

4. **Validar senha forte** — Crie uma função que verifica requisitos mínimos.

```js
function validarSenhaForte(senha) {
    const temMinimo = senha.length >= 8;
    const temMaiuscula = /[A-Z]/.test(senha);
    const temNumero = /[0-9]/.test(senha);
    return temMinimo && temMaiuscula && temNumero;
}
```

5. **Criar validação completa** — Verifique todos os campos e mostre erros.

```js
function validarFormulario() {
    let valido = true;
    
    const nome = document.querySelector('#nome');
    const erroNome = document.querySelector('#erroNome');
    if (nome.value.trim().length < 3) {
        erroNome.textContent = 'Nome deve ter pelo menos 3 caracteres.';
        nome.classList.add('invalido');
        valido = false;
    } else {
        erroNome.textContent = '';
        nome.classList.remove('invalido');
    }
    
    const senha = document.querySelector('#senha');
    const erroSenha = document.querySelector('#erroSenha');
    if (!validarSenhaForte(senha.value)) {
        erroSenha.textContent = 'Senha deve ter 8+ caracteres, 1 maiúscula e 1 número.';
        senha.classList.add('invalido');
        valido = false;
    } else {
        erroSenha.textContent = '';
        senha.classList.remove('invalido');
    }
    
    const confirmar = document.querySelector('#confirmarSenha');
    const erroConfirmar = document.querySelector('#erroConfirmar');
    if (confirmar.value !== senha.value) {
        erroConfirmar.textContent = 'Senhas não conferem.';
        confirmar.classList.add('invalido');
        valido = false;
    } else {
        erroConfirmar.textContent = '';
        confirmar.classList.remove('invalido');
    }
    
    return valido;
}
```

6. **Exibir dados capturados** — Mostre um card com as informações.

```js
function exibirDados(dados) {
    resultado.innerHTML = `
        <h2>Dados capturados</h2>
        <p><strong>Nome:</strong> ${dados.nome}</p>
        <p><strong>E-mail:</strong> ${dados.email}</p>
        <p><strong>Nascimento:</strong> ${dados.nascimento}</p>
        <p style="color: green;">✅ Cadastro validado com sucesso!</p>
    `;
}
```

## Checkpoint

:::objetivo Você está no caminho certo se
Ao submeter com dados inválidos, os erros aparecem nos campos
específicos. Ao submeter com dados válidos, o card de resultado
aparece com os dados corretos. A página não recarrega.
:::

## Erros comuns

:::atencao Sintoma: a página recarrega ao submeter
Causa: o event.preventDefault() está faltando ou foi colocado
depois de um return. A primeira linha do submit handler deve
ser event.preventDefault().
:::

:::atencao Sintoma: FormData retorna objeto vazio
Causa: os inputs não têm atributo name. O FormData usa o name
do input, não o id. Verifique se cada input tem name definido.
:::

## Desafio

Adicione validação em tempo real (keyup) que remove a classe de erro assim que o usuário começa a digitar corretamente, sem precisar submeter.

:::importante Desafio extra
Para quem terminar primeiro: adicione um campo de telefone com
máscara de entrada (formato (XX) XXXXX-XXXX) usando apenas
JavaScript puro, sem bibliotecas.
:::

## Código completo

```html
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Cadastro</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: Arial, sans-serif; background: #f0f2f5; padding: 40px 20px; }
        .container { max-width: 800px; margin: 0 auto; display: grid; grid-template-columns: 1fr 1fr; gap: 40px; }
        h1 { margin-bottom: 24px; color: #1a1a2e; font-size: 1.5rem; }
        .campo { margin-bottom: 16px; }
        label { display: block; margin-bottom: 4px; font-weight: bold; color: #333; }
        input { width: 100%; padding: 10px; border: 2px solid #ddd; border-radius: 6px; font-size: 1rem; }
        input:focus { outline: none; border-color: #2a9d8f; }
        input.invalido { border-color: #e63946; }
        .erro { color: #e63946; font-size: 0.85rem; margin-top: 4px; min-height: 20px; }
        button { background: #2a9d8f; color: white; border: none; padding: 12px 24px; border-radius: 6px; cursor: pointer; font-size: 1rem; width: 100%; }
        button:hover { background: #21867a; }
        #resultado { background: white; border-radius: 6px; padding: 20px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }
        #resultado h2 { margin-bottom: 12px; color: #1a1a2e; }
        #resultado p { margin-bottom: 8px; }
    </style>
</head>
<body>
    <div class="container">
        <form id="formCadastro">
            <h1>Cadastro</h1>
            <div class="campo">
                <label for="nome">Nome completo</label>
                <input type="text" id="nome" name="nome" required minlength="3">
                <span class="erro" id="erroNome"></span>
            </div>
            <div class="campo">
                <label for="email">E-mail</label>
                <input type="email" id="email" name="email" required>
                <span class="erro" id="erroEmail"></span>
            </div>
            <div class="campo">
                <label for="senha">Senha</label>
                <input type="password" id="senha" name="senha" required minlength="8">
                <span class="erro" id="erroSenha"></span>
            </div>
            <div class="campo">
                <label for="confirmarSenha">Confirmar senha</label>
                <input type="password" id="confirmarSenha" name="confirmarSenha" required>
                <span class="erro" id="erroConfirmar"></span>
            </div>
            <div class="campo">
                <label for="nascimento">Data de nascimento</label>
                <input type="date" id="nascimento" name="nascimento" required>
                <span class="erro" id="erroNascimento"></span>
            </div>
            <button type="submit">Cadastrar</button>
        </form>
        <div id="resultado">
            <p>Preencha o formulário para ver os dados aqui.</p>
        </div>
    </div>
    <script>
        const form = document.querySelector('#formCadastro');
        const resultado = document.querySelector('#resultado');

        function validarSenhaForte(senha) {
            return senha.length >= 8 && /[A-Z]/.test(senha) && /[0-9]/.test(senha);
        }

        function validarFormulario() {
            let valido = true;
            
            const nome = document.querySelector('#nome');
            const erroNome = document.querySelector('#erroNome');
            if (nome.value.trim().length < 3) {
                erroNome.textContent = 'Nome deve ter pelo menos 3 caracteres.';
                nome.classList.add('invalido');
                valido = false;
            } else {
                erroNome.textContent = '';
                nome.classList.remove('invalido');
            }
            
            const senha = document.querySelector('#senha');
            const erroSenha = document.querySelector('#erroSenha');
            if (!validarSenhaForte(senha.value)) {
                erroSenha.textContent = 'Senha: 8+ caracteres, 1 maiúscula, 1 número.';
                senha.classList.add('invalido');
                valido = false;
            } else {
                erroSenha.textContent = '';
                senha.classList.remove('invalido');
            }
            
            const confirmar = document.querySelector('#confirmarSenha');
            const erroConfirmar = document.querySelector('#erroConfirmar');
            if (confirmar.value !== senha.value) {
                erroConfirmar.textContent = 'Senhas não conferem.';
                confirmar.classList.add('invalido');
                valido = false;
            } else {
                erroConfirmar.textContent = '';
                confirmar.classList.remove('invalido');
            }
            
            return valido;
        }

        function exibirDados(dados) {
            resultado.innerHTML = `
                <h2>Dados capturados</h2>
                <p><strong>Nome:</strong> ${dados.nome}</p>
                <p><strong>E-mail:</strong> ${dados.email}</p>
                <p><strong>Nascimento:</strong> ${dados.nascimento}</p>
                <p style="color: green;">✅ Cadastro validado com sucesso!</p>
            `;
        }

        form.addEventListener('submit', function(event) {
            event.preventDefault();
            if (!validarFormulario()) return;
            const formData = new FormData(form);
            const dados = Object.fromEntries(formData);
            exibirDados(dados);
        });
    </script>
</body>
</html>
```

## Fechamento

:::resumo
- Formulários HTML usam input, label, button e atributos como required, minlength, type
- event.preventDefault() impede o recarregamento padrão da página
- FormData captura todos os campos name do formulário em pares chave-valor
- Validação customizada em JS complementa a validação nativa do HTML5
- Feedback visual (classe invalido, mensagens de erro) melhora a experiência do usuário
- Próxima aula: LocalStorage e persistência no navegador
:::
