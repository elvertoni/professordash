"""
Tipos base compartilhados entre todos os extratores.
"""

import re
from dataclasses import dataclass, field
from enum import Enum


class TipoArquivo(str, Enum):
    PDF        = 'pdf'
    PPTX       = 'pptx'
    DOCX       = 'docx'
    TXT        = 'txt'
    URL        = 'url'
    TEXTO      = 'texto'
    DRIVE      = 'drive'
    DESCONHECIDO = 'desconhecido'


@dataclass
class ResultadoExtracao:
    conteudo:  str
    tipo:      TipoArquivo
    paginas:   int        = 0
    slides:    int        = 0
    palavras:  int        = 0
    erro:      str        = ''
    metadados: dict       = field(default_factory=dict)

    def __post_init__(self):
        if self.conteudo and not self.palavras:
            self.palavras = len(self.conteudo.split())

    @property
    def ok(self) -> bool:
        return bool(self.conteudo) and not self.erro

    @property
    def resumo(self) -> str:
        return (
            f"{self.tipo.value.upper()} | "
            f"{self.palavras:,} palavras | "
            f"{self.paginas or self.slides} {'slides' if self.slides else 'páginas'}"
        )


class ExtratorBase:
    """Interface comum para todos os extratores."""

    def extrair(self, fonte) -> ResultadoExtracao:
        raise NotImplementedError

    def validar(self, fonte) -> bool:
        return fonte is not None


def limpar_texto(texto: str) -> str:
    """Remove ruído comum em textos extraídos de arquivos."""
    if not texto:
        return ''

    # Remove múltiplas linhas em branco
    texto = re.sub(r'\n{3,}', '\n\n', texto)

    # Remove espaços múltiplos
    texto = re.sub(r'[ \t]{2,}', ' ', texto)

    # Remove linhas com apenas pontilhados ou traços (cabeçalhos de tabela, etc.)
    texto = re.sub(r'^[.\-_=]{3,}\s*$', '', texto, flags=re.MULTILINE)

    # Remove caracteres de controle (exceto \n e \t)
    texto = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', '', texto)

    return texto.strip()
