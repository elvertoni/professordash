# Como cadastrar alunos no ProfessorDash

Para que um aluno consiga fazer login com o Google no portal da turma, ele precisa
estar previamente cadastrado no sistema com o mesmo email da conta Google que
vai usar para entrar.

---

## Opcao 1 - Cadastrar um aluno individualmente

1. Acesse o painel: `https://aulas.tonicoimbra.com/painel/`
2. Clique na turma desejada
3. Va na aba **Alunos** e clique em **Novo aluno**
4. Preencha:
   - **Nome** - nome completo do aluno
   - **Email** - email da conta Google que o aluno vai usar para login
   - **Matricula** - numero de matricula (opcional)
5. Salve

---

## Opcao 2 - Importar lista via CSV

1. Acesse o painel: `https://aulas.tonicoimbra.com/painel/`
2. Clique na turma desejada
3. Va na aba **Alunos** e clique em **Importar CSV**
4. Prepare um arquivo `.csv` com o seguinte formato:

```csv
nome,email,matricula
Joao Silva,joao.silva@gmail.com,2024001
Maria Souza,maria.souza@gmail.com,2024002
Pedro Costa,pedro.costa@gmail.com,2024003
```

> A coluna `matricula` e opcional. As colunas `nome` e `email` sao obrigatorias.

5. Faca o upload do arquivo e confirme a importacao

---

## Como o login do aluno funciona

1. Voce cadastra o aluno com o email Google dele
2. O aluno acessa o link publico da turma, por exemplo `https://aulas.tonicoimbra.com/turma/<token>/`
3. O aluno clica em **Entrar com Google**
4. O sistema envia o aluno ao Google e, na volta, vincula o acesso ao cadastro pelo mesmo email
5. O aluno so entra se estiver com cadastro ativo e com matricula ativa nessa turma
6. Se o email nao estiver cadastrado, ou se a matricula estiver inativa, o aluno ve uma mensagem pedindo para entrar em contato com o professor

---

## Observacoes

- O email cadastrado precisa ser o mesmo email da conta Google do aluno. Maiusculas e minusculas nao fazem diferenca.
- Um aluno pode estar matriculado em mais de uma turma.
- Para remover o acesso de um aluno, desative a matricula na aba Alunos da turma.
- Se o Google OAuth estiver indisponivel, o portal mostra o login como indisponivel e o aluno continua vendo apenas o conteudo publico.
