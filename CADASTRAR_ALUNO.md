# Como cadastrar alunos no ProfessorDash

Para que um aluno consiga fazer login com o Google no portal da turma, ele precisa
estar previamente cadastrado no sistema com o **mesmo email da conta Google** que
vai usar para entrar.

---

## Opção 1 — Cadastrar um aluno individualmente

1. Acesse o painel: `https://aulas.tonicoimbra.com/painel/`
2. Clique na turma desejada
3. Vá na aba **Alunos** → clique em **Novo aluno**
4. Preencha:
   - **Nome** — nome completo do aluno
   - **Email** — email da conta Google que o aluno vai usar para login
   - **Matrícula** — número de matrícula (opcional)
5. Salve

---

## Opção 2 — Importar lista via CSV (recomendado para turmas grandes)

1. Acesse o painel: `https://aulas.tonicoimbra.com/painel/`
2. Clique na turma desejada
3. Vá na aba **Alunos** → clique em **Importar CSV**
4. Prepare um arquivo `.csv` com o seguinte formato:

```
nome,email,matricula
João Silva,joao.silva@gmail.com,2024001
Maria Souza,maria.souza@gmail.com,2024002
Pedro Costa,pedro.costa@gmail.com,2024003
```

> A coluna `matricula` é opcional. As colunas `nome` e `email` são obrigatórias.

5. Faça o upload do arquivo e confirme a importação

---

## Como o login do aluno funciona

1. Você cadastra o aluno com o email Google dele
2. O aluno acessa o link público da turma (ex: `https://aulas.tonicoimbra.com/turma/<token>/`)
3. O aluno clica em **Entrar com Google**
4. O sistema reconhece o email e libera o acesso automaticamente
5. Se o email não estiver cadastrado, o aluno vê uma mensagem pedindo para entrar em contato com o professor

---

## Observações

- O email cadastrado precisa ser **exatamente o email da conta Google** do aluno
- Um aluno pode estar matriculado em mais de uma turma
- Para remover o acesso de um aluno, desative a matrícula na aba Alunos da turma
