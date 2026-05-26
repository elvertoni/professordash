#!/usr/bin/env python
import sys
import os

# Adiciona o diretório raiz ao path do python para poder importar core.validadores
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

try:
    from core.validadores import validar_markdown_aula
except ImportError:
    print("Erro: Não foi possível importar o módulo core.validadores. Execute o script na raiz do repositório.")
    sys.exit(1)


def main():
    arquivos = sys.argv[1:]
    if not arquivos:
        return 0

    erros_totais = 0

    for caminho in arquivos:
        if not caminho.endswith(".md"):
            continue

        if not os.path.exists(caminho):
            continue

        # Ignorar arquivos de documentação do sistema se necessário, mas vamos validar apenas arquivos de aula
        # Por simplicidade, se o arquivo contiver um H1 e seções H2, nós validamos
        try:
            with open(caminho, "r", encoding="utf-8", errors="replace") as f:
                conteudo = f.read()
        except Exception as e:
            print(f"Erro ao ler {caminho}: {e}")
            erros_totais += 1
            continue

        # Heurística para saber se é um markdown de aula
        if not conteudo.strip().startswith("#"):
            # Não é uma aula de formato canônico, ignora
            continue

        erros = validar_markdown_aula(conteudo)
        erros_graves = [e for e in erros if any(k in e.lower() for k in ["vazio", "h1", "questão", "html bruto", "inválido", "roteiro", "início da linha"])]

        if erros_graves:
            print(f"\n[FALHA] O arquivo '{caminho}' possui violações graves do FORMATO_AULAS.md:")
            for erro in erros_graves:
                print(f"  - {erro}")
            erros_totais += 1
            
            # Mostrar avisos secundários também
            avisos = [e for e in erros if e not in erros_graves]
            if avisos:
                print("  Avisos adicionais:")
                for aviso in avisos:
                    print(f"    - {aviso}")
        else:
            # Apenas avisos, deixa passar mas notifica
            if erros:
                print(f"\n[AVISO] '{caminho}' passou na validação com os seguintes alertas de estilo:")
                for aviso in erros:
                    print(f"  - {aviso}")

    if erros_totais > 0:
        print(f"\nValidação falhou. {erros_totais} arquivo(s) com formato inválido. Ajuste-os antes de commitar.")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
