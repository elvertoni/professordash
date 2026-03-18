"""
Detector e montador do padrão RCO (Registro de Classe Online — SEED-PR).

Padrão de nomes dos arquivos:
  AULA_XX_<DISCIPLINA>.pptx                ← slides principais
  AULA_XX_ATIVIDADE_<DISCIPLINA>.docx      ← questões da atividade oficial
  AULA_XX_PRATICA_<DISCIPLINA>.docx        ← atividade prática
"""

import re
import logging
from dataclasses import dataclass
from typing import Optional

from .base import ResultadoExtracao, TipoArquivo
from .pptx import extrair_pptx
from .docx import extrair_docx

logger = logging.getLogger(__name__)


# ── Tipos de papel no conjunto RCO ────────────────────────────────────────────

class PapelRCO:
    SLIDES    = 'slides'
    ATIVIDADE = 'atividade'
    PRATICA   = 'pratica'
    OUTRO     = 'outro'


@dataclass
class ConjuntoRCO:
    """Agrupa os 3 arquivos de uma aula RCO."""
    slides:    Optional[object] = None   # arquivo PPTX
    atividade: Optional[object] = None   # arquivo DOCX atividade
    pratica:   Optional[object] = None   # arquivo DOCX prática

    @property
    def completo(self) -> bool:
        return self.slides is not None and self.atividade is not None

    @property
    def resumo(self) -> str:
        partes = []
        if self.slides:    partes.append('✅ Slides')
        if self.atividade: partes.append('✅ Atividade')
        if self.pratica:   partes.append('✅ Prática')
        else:              partes.append('⚠️  Prática (opcional, não enviada)')
        return ' | '.join(partes)


# ── Detector de papel pelo nome do arquivo ────────────────────────────────────

def detectar_papel_rco(nome_arquivo: str) -> str:
    """
    Identifica o papel de um arquivo no padrão RCO pelo seu nome.

    Exemplos:
      AULA_03_ATIVIDADE_FRONT_END.docx → 'atividade'
      AULA_03_PRATICA_FRONT_END.docx   → 'pratica'
      AULA_03_FRONT_END.pptx           → 'slides'
    """
    nome = nome_arquivo.upper()

    # Atividade tem prioridade (verificar antes de 'slides')
    if 'ATIVIDADE' in nome:
        return PapelRCO.ATIVIDADE

    # Prática
    if 'PRATICA' in nome or 'PRÁTICA' in nome or 'PRACTICE' in nome:
        return PapelRCO.PRATICA

    # Slides — PPTX sem marcador de atividade/prática
    if nome.endswith(('.PPTX', '.PPT')):
        return PapelRCO.SLIDES

    return PapelRCO.OUTRO


def detectar_numero_aula(nome_arquivo: str) -> Optional[int]:
    """Extrai o número da aula do nome do arquivo. Ex: AULA_03_... → 3"""
    match = re.search(r'AULA[_\s]?(\d+)', nome_arquivo.upper())
    return int(match.group(1)) if match else None


# ── Extração do conjunto RCO ──────────────────────────────────────────────────

def extrair_rco(conjunto: ConjuntoRCO) -> dict:
    """
    Extrai conteúdo dos 3 arquivos do conjunto RCO.
    Retorna dict com conteúdo de cada papel.
    """
    resultado = {
        PapelRCO.SLIDES:    ResultadoExtracao('', TipoArquivo.PPTX),
        PapelRCO.ATIVIDADE: ResultadoExtracao('', TipoArquivo.DOCX),
        PapelRCO.PRATICA:   ResultadoExtracao('', TipoArquivo.DOCX),
    }

    if conjunto.slides:
        logger.info('Extraindo slides RCO...')
        resultado[PapelRCO.SLIDES] = extrair_pptx(conjunto.slides)

    if conjunto.atividade:
        logger.info('Extraindo atividade RCO...')
        resultado[PapelRCO.ATIVIDADE] = extrair_docx(conjunto.atividade)

    if conjunto.pratica:
        logger.info('Extraindo prática RCO...')
        resultado[PapelRCO.PRATICA] = extrair_docx(conjunto.pratica)

    # Log de qualidade
    for papel, res in resultado.items():
        if res.conteudo:
            logger.info(f'  {papel}: {res.resumo}')
        elif papel != PapelRCO.PRATICA:  # prática é opcional
            logger.warning(f'  {papel}: sem conteúdo extraído')

    return resultado


def montar_conteudo_rco(extracao: dict) -> dict:
    """
    Monta o conteúdo estruturado para o prompt da IA a partir da extração RCO.

    Retorna:
        {
            'slides':    str,   # conteúdo dos slides (principal)
            'atividade': str,   # questões e alternativas
            'pratica':   str,   # atividade prática
        }
    """
    return {
        'slides':    extracao[PapelRCO.SLIDES].conteudo,
        'atividade': extracao[PapelRCO.ATIVIDADE].conteudo,
        'pratica':   extracao[PapelRCO.PRATICA].conteudo,
    }


def montar_conjunto_de_uploads(arquivos_dict: dict) -> ConjuntoRCO:
    """
    Recebe o dict de arquivos do request.FILES e monta o ConjuntoRCO.

    Uso na view Django:
        conjunto = montar_conjunto_de_uploads(request.FILES)
    """
    conjunto = ConjuntoRCO()

    for campo, arquivo in arquivos_dict.items():
        nome = getattr(arquivo, 'name', campo)
        papel = detectar_papel_rco(nome)

        if papel == PapelRCO.SLIDES:
            conjunto.slides = arquivo
        elif papel == PapelRCO.ATIVIDADE:
            conjunto.atividade = arquivo
        elif papel == PapelRCO.PRATICA:
            conjunto.pratica = arquivo
        else:
            logger.warning(f'Arquivo não reconhecido como RCO: {nome}')

    return conjunto
