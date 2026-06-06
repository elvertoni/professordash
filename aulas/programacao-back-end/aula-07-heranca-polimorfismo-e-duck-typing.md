# Aula 07 — Herança, polimorfismo e duck typing

A orientação a objetos não para nas classes e objetos. Dois conceitos poderosos vêm a seguir: herança, que permite criar classes especializadas a partir de classes gerais, e polimorfismo, que permite que objetos de tipos diferentes respondam ao mesmo método de formas diferentes. O duck typing do Python leva isso ainda mais longe: "se anda como pato, nada como pato e grasna como pato, então é pato". Vamos construir um sistema de pagamentos que ilustra esses conceitos na prática.

## O que vamos construir

Um sistema de processamento de pagamentos onde diferentes formas de pagamento (cartão de crédito, boleto, PIX) compartilham uma interface comum, mas cada uma implementa sua própria lógica. O sistema processa uma lista de pagamentos sem precisar saber qual tipo específico cada um é.

:::objetivo Resultado final
Um script Python com classes que usam herança e polimorfismo
para processar pagamentos de formas diferentes (cartão, boleto,
PIX) através de um único método processar().
:::

## Pré-requisitos

:::dica Para esta aula você precisa de
Python 3, editor de código. Conhecimento de classes, métodos,
__init__ e @property da aula 06.
:::

## Passo a passo

1. **Criar a classe base** — A classe-mãe define a interface comum.

```python
class Pagamento:
    def __init__(self, valor, descricao):
        self.valor = valor
        self.descricao = descricao
        self.status = "Pendente"
    
    def processar(self):
        """Método genérico — será sobrescrito pelas filhas."""
        raise NotImplementedError("Cada forma de pagamento deve implementar processar().")
    
    def exibir_resumo(self):
        return f"{self.descricao}: R${self.valor:.2f} - {self.status}"
```

A classe base não deve ser instanciada diretamente para processar pagamentos — ela serve como contrato para as classes filhas. O `raise NotImplementedError` garante que qualquer classe filha que esqueça de implementar `processar()` receba um erro claro.

2. **Criar a classe CartaoCredito** — Herda de Pagamento e sobrescreve processar().

```python
class CartaoCredito(Pagamento):
    def __init__(self, valor, descricao, numero_cartao, parcelas=1):
        super().__init__(valor, descricao)
        self.ultimos_digitos = numero_cartao[-4:]
        self.parcelas = parcelas
    
    def processar(self):
        import time
        print(f"⏳ Autorizando cartão final {self.ultimos_digitos}...")
        time.sleep(1)  # Simula processamento
        self.status = "Aprovado"
        return f"Cartão final {self.ultimos_digitos} aprovado em {self.parcelas}x."
```

A chamada `super().__init__` invoca o construtor da classe-mãe para não precisar repetir a inicialização dos atributos herdados.

3. **Criar a classe Boleto** — Cada tipo implementa processar() de forma diferente.

```python
import random
import string

class Boleto(Pagamento):
    def processar(self):
        codigo = ''.join(random.choices(string.digits, k=47))
        self.status = "Aguardando Pagamento"
        return f"Boleto gerado: {codigo}\nVencimento: 3 dias úteis."
```

4. **Criar a classe PIX** — Mais uma implementação específica.

```python
class PIX(Pagamento):
    def __init__(self, valor, descricao, chave_pix):
        super().__init__(valor, descricao)
        self.chave_pix = chave_pix
    
    def processar(self):
        import time
        print(f"⏳ Processando PIX...")
        time.sleep(0.5)
        self.status = "Confirmado"
        return f"PIX de R${self.valor:.2f} para {self.chave_pix} confirmado!"
```

5. **Demonstrar polimorfismo** — Uma única função processa qualquer tipo de pagamento.

```python
def processar_pagamentos(lista_pagamentos):
    for pagamento in lista_pagamentos:
        resultado = pagamento.processar()
        print(resultado)
        print(pagamento.exibir_resumo())
        print("-" * 30)
```

Mesmo sem saber se cada item é CartaoCredito, Boleto ou PIX, a função chama `processar()` em cada um — e cada classe responde de forma diferente. Isso é polimorfismo.

6. **Criar a classe Teste** — Duck typing na prática.

```python
class PagamentoTeste:
    """Não herda de Pagamento, mas implementa a mesma interface."""
    def processar(self):
        return "✅ Pagamento de teste processado (modo sandbox)."

# Duck typing: a função aceita qualquer objeto que tenha processar()
processar_pagamentos([PagamentoTeste()])
# Funciona! O Python não verifica o tipo — só se o método existe.
```

:::exemplo Duck typing explicado
```python
class Pato:
    def som(self): return "Quack!"

class Cachorro:
    def som(self): return "Au au!"

class Carro:
    def som(self): return "Buzina!"

# Função que aceita qualquer objeto com método som()
def fazer_barulho(coisa):
    print(coisa.som())

fazer_barulho(Pato())     # Quack!
fazer_barulho(Cachorro()) # Au au!
fazer_barulho(Carro())    # Buzina!
```
:::

## Checkpoint

:::objetivo Você está no caminho certo se
O script processa diferentes pagamentos sem erro, cada um com
sua lógica específica. A função processar_pagamentos funciona
com qualquer objeto que tenha o método processar(), mesmo sem
herdar de Pagamento.
:::

## Erros comuns

:::atencao Sintoma: TypeError: super().__init__() missing arguments
Causa: esqueceu de chamar super().__init__() ou passou os
argumentos errados. Correção: a classe filha deve chamar
super().__init__() com os parâmetros que a classe mãe espera.
:::

:::atencao Sintoma: NotImplementedError ao processar pagamento
Causa: a classe filha não implementou o método processar().
Correção: cada classe concreta deve sobrescrever todos os
métodos abstratos definidos na classe base.
:::

## Desafio

Crie uma classe `PagamentoDebito` que herda de Pagamento e implementa processar() pedindo confirmação por senha de 4 dígitos. Adicione-a à lista de pagamentos para testar.

:::importante Desafio extra
Para quem terminar primeiro: implemente um método de classe
`Pagamento.relatorio(lista_pagamentos)` que conta quantos
pagamentos foram aprovados, quantos estão pendentes e o valor
total processado. Use @classmethod.
:::

## Código completo

```python
import time
import random
import string

# --- Classe base ---
class Pagamento:
    def __init__(self, valor, descricao):
        self.valor = valor
        self.descricao = descricao
        self.status = "Pendente"
    
    def processar(self):
        raise NotImplementedError("Cada forma de pagamento deve implementar processar().")
    
    def exibir_resumo(self):
        return f"{self.descricao}: R${self.valor:.2f} - {self.status}"

# --- Classes filhas ---
class CartaoCredito(Pagamento):
    def __init__(self, valor, descricao, numero_cartao, parcelas=1):
        super().__init__(valor, descricao)
        self.ultimos_digitos = numero_cartao[-4:]
        self.parcelas = parcelas
    
    def processar(self):
        print(f"⏳ Autorizando cartão final {self.ultimos_digitos}...")
        time.sleep(0.5)
        self.status = "Aprovado"
        return f"Cartão final {self.ultimos_digitos} aprovado em {self.parcelas}x."

class Boleto(Pagamento):
    def processar(self):
        codigo = ''.join(random.choices(string.digits, k=47))
        self.status = "Aguardando Pagamento"
        return f"Boleto gerado: {codigo[:5]}...{codigo[-5:]}"

class PIX(Pagamento):
    def __init__(self, valor, descricao, chave_pix):
        super().__init__(valor, descricao)
        self.chave_pix = chave_pix
    
    def processar(self):
        print(f"⏳ Processando PIX para {self.chave_pix}...")
        time.sleep(0.3)
        self.status = "Confirmado"
        return f"PIX de R${self.valor:.2f} confirmado!"

# --- Polimorfismo ---
def processar_pagamentos(lista_pagamentos):
    for pagamento in lista_pagamentos:
        resultado = pagamento.processar()
        print(resultado)
        print(pagamento.exibir_resumo())
        print("-" * 30)

# --- Duck typing ---
class PagamentoTeste:
    def processar(self):
        return "✅ Pagamento de teste processado (sandbox)."

# --- Execução ---
if __name__ == "__main__":
    pagamentos = [
        CartaoCredito(150.00, "Curso Front-End", "1234567890123456", 3),
        Boleto(89.90, "Camiseta Oficial",),
        PIX(25.00, "Contribuição", "ana@email.com"),
        PagamentoTeste(),
    ]
    
    processar_pagamentos(pagamentos)
    
    # Demonstrando @classmethod (desafio)
    @classmethod
    def relatorio(cls, pagamentos):
        total = sum(p.valor for p in pagamentos if hasattr(p, 'valor'))
        aprovados = sum(1 for p in pagamentos if getattr(p, 'status', '') in ("Aprovado", "Confirmado"))
        print(f"\n📊 Relatório: {aprovados}/{len(pagamentos)} processados, R${total:.2f}")
    
    Pagamento.relatorio = relatorio
    Pagamento.relatorio(pagamentos)
```

## Fechamento

:::resumo
- Herança: classes filhas herdam atributos e métodos da classe-mãe (super)
- super().__init__() chama o construtor da classe-mãe
- Polimorfismo: objetos de diferentes classes respondem ao mesmo método
- Duck typing: se um objeto tem o método, funciona — o tipo não importa
- raise NotImplementedError garante que filhas implementem métodos obrigatórios
- Próxima aula: introdução ao Django — models e admin
:::
