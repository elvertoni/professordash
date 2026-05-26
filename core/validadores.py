import re

def detectar_modo(texto: str) -> str:
    """
    Detecta o modo de aula (prático ou conceitual) com base na presença de seções chave.
    """
    secoes_praticas = [
        "passo a passo",
        "erros comuns",
        "o que vamos construir",
        "código completo",
        "pré-requisitos",
        "desafio",
        "checkpoint"
    ]
    texto_lc = texto.lower()
    for secao in secoes_praticas:
        if f"## {secao}" in texto_lc:
            return "prático"
    return "conceitual"

def validar_markdown_aula(texto: str) -> list[str]:
    """
    Valida se o texto de uma aula em Markdown segue as regras do FORMATO_AULAS.md v2.1.
    Retorna uma lista de strings contendo as violações (avisos e erros).
    """
    violacoes = []
    if not texto or not texto.strip():
        return ["O documento está vazio."]

    # 1. Checagem de Título (#)
    h1_headers = [line.strip() for line in texto.splitlines() if line.startswith("# ")]
    if len(h1_headers) != 1:
        violacoes.append(f"Deve haver exatamente um título H1 ('# Título'). Encontrados: {len(h1_headers)}.")

    # 2. Primeiro parágrafo após o H1
    # Vamos encontrar o parágrafo explicativo logo após o H1
    linhas = texto.splitlines()
    h1_idx = -1
    for idx, line in enumerate(linhas):
        if line.startswith("# "):
            h1_idx = idx
            break

    if h1_idx != -1:
        intro_linhas = []
        in_intro = False
        for idx in range(h1_idx + 1, len(linhas)):
            line = linhas[idx].strip()
            if not line:
                if in_intro:
                    break
                continue
            # Se encontrar cabeçalho, bloco ::: ou outro elemento estrutural antes do primeiro parágrafo
            if line.startswith("#") or line.startswith(":::") or line.startswith("---") or line.startswith("`") or line.startswith("<"):
                if not in_intro:
                    violacoes.append("O primeiro elemento útil após o H1 deve ser um parágrafo simples (sem :::, código, HTML ou listas).")
                break
            in_intro = True
            intro_linhas.append(line)
        
        if intro_linhas:
            # Primeiro parágrafo deve ter entre 3 e 6 linhas
            if not (3 <= len(intro_linhas) <= 6):
                violacoes.append(f"O parágrafo introdutório deve ter entre 3 e 6 linhas de texto na fonte. Encontradas: {len(intro_linhas)}.")
        else:
            violacoes.append("Não foi encontrado o parágrafo introdutório obrigatório após o H1.")

    # 3. Seções H2 (##)
    h2_headers = [line.strip() for line in texto.splitlines() if line.startswith("## ")]
    num_h2 = len(h2_headers)
    if num_h2 < 4 or num_h2 > 8:
        violacoes.append(f"A faixa ideal de seções H2 (##) é de 4 a 6 (máximo 8). Encontradas: {num_h2}.")

    # 4. Checar se ## e --- estão fora de wrappers (ou seja, no início da linha)
    for idx, line in enumerate(linhas):
        if "##" in line and not line.startswith("##"):
            violacoes.append(f"Linha {idx + 1}: O cabeçalho '##' deve estar no início da linha (sem espaços ou wrappers HTML).")
        if "---" in line and not line.startswith("---") and not line.strip().startswith("- - -"):
            # Permite --- dentro de blocos de código
            pass

    # 5. Modo de aula
    modo = detectar_modo(texto)

    # 6. Parsear blocos ::: e fences de código e listas por seção
    # Vamos dividir o texto em seções H2 para analisar individualmente
    secoes = []
    current_section_title = "Introdução"
    current_section_lines = []
    
    for line in linhas:
        if line.startswith("## "):
            secoes.append((current_section_title, current_section_lines))
            current_section_title = line[3:].strip()
            current_section_lines = []
        else:
            current_section_lines.append(line)
    secoes.append((current_section_title, current_section_lines))

    # Auxiliares para checagem global
    total_questoes = 0
    questoes_info = []
    roteiro_count = 0
    resumo_count = 0
    tem_resumo_no_fechamento = False

    # Regex para capturar blocos :::
    # Para validar conteúdo interno de blocos :::, vamos usar uma máquina de estados simples
    in_block = False
    block_type = ""
    block_content_lines = []
    block_start_line = 0

    for sec_title, sec_lines in secoes:
        callouts_na_secao = 0
        in_code_block = False
        code_block_lines = 0
        list_items_consecutivos = 0

        for line_offset, line in enumerate(sec_lines):
            stripped = line.strip()

            # Fences de código
            if stripped.startswith("```"):
                if in_code_block:
                    # Fechou bloco de código
                    if code_block_lines > 20 and "código completo" not in sec_title.lower():
                        violacoes.append(f"Na seção '{sec_title}': Bloco de código com mais de 20 linhas ({code_block_lines} linhas) encontrado fora da seção 'Código completo'.")
                    in_code_block = False
                    code_block_lines = 0
                else:
                    in_code_block = True
                continue

            if in_code_block:
                code_block_lines += 1
                continue

            # Listas Markdown
            if not in_block:
                if stripped.startswith("- ") or stripped.startswith("* ") or re.match(r"^\d+\.\s", stripped):
                    list_items_consecutivos += 1
                else:
                    if list_items_consecutivos > 5:
                        violacoes.append(f"Na seção '{sec_title}': Encontrada lista com mais de 5 itens consecutivos ({list_items_consecutivos} itens).")
                    list_items_consecutivos = 0

            # Componentes interativos - detecção de HTML bruto
            if not in_block and not in_code_block:
                raw_html_patterns = [
                    r'class="callout',
                    r'class="questao',
                    r'class="roteiro',
                    r'class="resumo-list"'
                ]
                for pat in raw_html_patterns:
                    if re.search(pat, line):
                        violacoes.append(f"Componentes interativos devem usar a sintaxe ':::tipo', não HTML bruto ('{stripped}').")

            # Blocos :::
            if stripped.startswith(":::"):
                if in_block:
                    # Fechou o bloco :::
                    # Validar o bloco fechado
                    if block_type == "questao":
                        total_questoes += 1
                        valida_questao(block_content_lines, sec_title, total_questoes, violacoes, questoes_info)
                    elif block_type == "roteiro":
                        roteiro_count += 1
                        if len(block_content_lines) == 0:
                            violacoes.append(f"Bloco :::roteiro está vazio.")
                    elif block_type == "resumo":
                        resumo_count += 1
                        if "fechamento" in sec_title.lower() or "conclusão" in sec_title.lower():
                            tem_resumo_no_fechamento = True
                        valida_resumo(block_content_lines, sec_title, violacoes)
                    else:
                        callouts_na_secao += 1
                        valida_callout(block_type, block_content_lines, sec_title, violacoes)

                    in_block = False
                    block_content_lines = []
                else:
                    in_block = True
                    match_type = re.match(r"^:::(\w+)", stripped)
                    if match_type:
                        block_type = match_type.group(1).lower()
                    else:
                        block_type = "dica" # fallback
            elif in_block:
                block_content_lines.append(stripped)

        # Tratar lista ou bloco de código pendente no final da seção
        if list_items_consecutivos > 5:
            violacoes.append(f"Na seção '{sec_title}': Encontrada lista com mais de 5 itens consecutivos ({list_items_consecutivos} itens).")
        if in_code_block and code_block_lines > 20 and "código completo" not in sec_title.lower():
            violacoes.append(f"Na seção '{sec_title}': Bloco de código com mais de 20 linhas ({code_block_lines} linhas) encontrado fora da seção 'Código completo'.")

        if callouts_na_secao > 2:
            violacoes.append(f"Na seção '{sec_title}': Excesso de callouts ({callouts_na_secao} callouts). O máximo permitido por seção ## é 2.")

    # 7. Questões de fixação
    if modo == "conceitual":
        if total_questoes != 2:
            violacoes.append(f"No modo conceitual, deve haver exatamente 2 questões. Encontradas: {total_questoes}.")
    elif modo == "prático":
        if total_questoes > 2:
            violacoes.append(f"No modo prático, é permitido de 0 a 2 questões. Encontradas: {total_questoes}.")

    if len(questoes_info) == 2:
        q1_correta, q2_correta = questoes_info[0], questoes_info[1]
        if q1_correta == q2_correta and q1_correta != "":
            violacoes.append(f"A alternativa correta deve variar entre as questões (ambas possuem a alternativa '{q1_correta}' como correta).")

    # 8. Roteiro do professor
    if roteiro_count > 1:
        violacoes.append(f"Deve haver no máximo 1 bloco :::roteiro por aula. Encontrados: {roteiro_count}.")

    # 9. Resumo no fechamento
    # O resumo deve ter gancho para a próxima aula
    # Vamos verificar se alguma das seções de fechamento possui :::resumo
    if resumo_count > 0 and not tem_resumo_no_fechamento:
        # Se tem resumo no doc mas não na seção de fechamento, dá aviso
        violacoes.append("O bloco :::resumo idealmente deve ficar no fechamento da aula.")
    
    return violacoes

def valida_callout(block_type, content, sec_title, violacoes):
    valid_types = {"objetivo", "importante", "dica", "exemplo", "atencao", "conceito", "exercicio", "curiosidade"}
    if block_type not in valid_types:
        violacoes.append(f"Tipo de callout inválido: ':::{block_type}'. Tipos válidos: {', '.join(valid_types)}.")
    
    # Conteúdo deve ser texto plano (sem markdown de formatação ou fences ou HTML)
    corpo = "\n".join(content)
    if "```" in corpo:
        violacoes.append(f"Na seção '{sec_title}': Blocos de código não podem ficar dentro de callouts ':::{block_type}'. Coloque-os fora.")
    if "**" in corpo or "__" in corpo:
        violacoes.append(f"Na seção '{sec_title}': Negrito (**, __) não deve ser usado dentro de callouts ':::{block_type}'. Use texto plano.")
    if "<" in corpo and ">" in corpo:
        violacoes.append(f"Na seção '{sec_title}': HTML bruto não deve ser usado dentro de callouts ':::{block_type}'.")
    
    if block_type == "atencao":
        # Checa se o texto de atenção reflete erro/cuidado
        alert_keywords = ["erro", "cuidado", "atencao", "bug", "falha", "alerta", "sintoma", "causa", "correção", "evite", "problema"]
        corpo_lc = corpo.lower()
        if not any(k in corpo_lc for k in alert_keywords):
            violacoes.append(f"Na seção '{sec_title}': O bloco :::atencao deve ser reservado para descrever erros comuns ou cuidados específicos.")

def valida_resumo(content, sec_title, violacoes):
    items = []
    tem_gancho = False
    for line in content:
        line_strip = line.strip()
        if not line_strip:
            continue
        items.append(line_strip)
        if "próxima aula" in line_strip.lower() or "proxima aula" in line_strip.lower():
            tem_gancho = True
            
    if len(items) < 3 or len(items) > 4:
        violacoes.append(f"O bloco :::resumo deve conter entre 3 e 4 tópicos. Encontrados: {len(items)}.")
    if not tem_gancho:
        violacoes.append("O bloco :::resumo deve incluir um gancho para a próxima aula (ex.: '- Próxima aula: introdução ao localStorage').")

def valida_questao(content, sec_title, questao_num, violacoes, questoes_info):
    alternativas = []
    gabarito_lines = []
    in_gabarito = False
    correta_count = 0
    correta_letra = ""

    for line in content:
        stripped = line.strip()
        if not stripped:
            continue

        if stripped.startswith(">"):
            in_gabarito = True
            gabarito_lines.append(stripped.lstrip("> ").strip())
            continue

        if in_gabarito:
            gabarito_lines.append(stripped)
            continue

        # Parse alternativa: a) Texto ou a) Texto *
        alt_match = re.match(r"^([a-zA-Z])\)\s*(.+?)(\s*\*\s*)?$", stripped)
        if alt_match:
            letra = alt_match.group(1).upper()
            is_correta = bool(alt_match.group(3))
            alternativas.append(letra)
            if is_correta:
                correta_count += 1
                correta_letra = letra
        else:
            # Se não é alternativa e não é gabarito
            if not in_gabarito:
                violacoes.append(f"Questão {questao_num}: Linha com formato inválido de alternativa: '{stripped}'. Deve ser 'a) texto'.")

    # Guardar letra correta
    questoes_info.append(correta_letra)

    # Validações da estrutura da questão
    if len(alternativas) < 2:
        violacoes.append(f"Questão {questao_num}: Deve conter alternativas (ex.: a), b), c), d)).")
    if correta_count != 1:
        violacoes.append(f"Questão {questao_num}: Deve conter exatamente uma alternativa correta demarcada com '*' no final. Encontradas: {correta_count}.")
    if not gabarito_lines:
        violacoes.append(f"Questão {questao_num}: Falta o gabarito explicativo (iniciado com '>').")
    else:
        # Pelo menos 2 linhas de explicação
        if len(gabarito_lines) < 2:
            violacoes.append(f"Questão {questao_num}: O gabarito explicativo deve conter pelo menos 2 linhas de texto.")
