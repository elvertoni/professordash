"""
Integração com Google Drive — ProfessorDash Gerador de Aulas

Permite importar diretamente arquivos das pastas RCO do SEED-PR
sem precisar baixar e fazer upload manualmente.

Autenticação: OAuth2 via django-allauth (conta Google já conectada)
Escopos necessários: drive.readonly
"""

import io
import logging
import os
from dataclasses import dataclass
from typing import Optional

logger = logging.getLogger(__name__)

# ── Configuração ───────────────────────────────────────────────────────────────

DRIVE_SCOPES = ['https://www.googleapis.com/auth/drive.readonly']

MIME_TIPOS_SUPORTADOS = {
    'application/vnd.openxmlformats-officedocument.presentationml.presentation': '.pptx',
    'application/vnd.ms-powerpoint': '.ppt',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document': '.docx',
    'application/msword': '.doc',
    'application/pdf': '.pdf',
    'text/plain': '.txt',
    # Google Workspace (exporta para Office)
    'application/vnd.google-apps.presentation': '.pptx',
    'application/vnd.google-apps.document': '.docx',
}

MIME_EXPORTACAO = {
    'application/vnd.google-apps.presentation':
        'application/vnd.openxmlformats-officedocument.presentationml.presentation',
    'application/vnd.google-apps.document':
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
}


# ── Dataclasses ────────────────────────────────────────────────────────────────

@dataclass
class ArquivoDrive:
    id:        str
    nome:      str
    mime_type: str
    tamanho:   int = 0
    pasta_id:  str = ''

    @property
    def extensao(self) -> str:
        return MIME_TIPOS_SUPORTADOS.get(self.mime_type, '')

    @property
    def suportado(self) -> bool:
        return self.mime_type in MIME_TIPOS_SUPORTADOS

    @property
    def eh_google_workspace(self) -> bool:
        return self.mime_type.startswith('application/vnd.google-apps.')

    @property
    def nome_completo(self) -> str:
        if self.extensao and not self.nome.endswith(self.extensao):
            return f'{self.nome}{self.extensao}'
        return self.nome

    def __repr__(self):
        return f'<ArquivoDrive {self.nome} ({self.mime_type})>'


@dataclass
class PastaRCO:
    """Representa uma pasta de aula no padrão RCO do Drive."""
    id:     str
    nome:   str
    arquivos: list  # list[ArquivoDrive]

    @property
    def numero_aula(self) -> Optional[int]:
        import re
        match = re.search(r'AULA[_\s]?(\d+)', self.nome.upper())
        return int(match.group(1)) if match else None


# ── Cliente do Drive ───────────────────────────────────────────────────────────

class DriveClient:
    """
    Wrapper do Google Drive API v3.
    Usa as credenciais OAuth do usuário via django-allauth.
    """

    def __init__(self, credentials=None, token: str = ''):
        """
        Inicializa com credenciais OAuth.

        Uso com django-allauth:
            from allauth.socialaccount.models import SocialToken
            token = SocialToken.objects.get(account__user=request.user,
                                            account__provider='google')
            client = DriveClient(token=token.token)

        Uso com service account (bot):
            client = DriveClient.from_service_account('credentials.json')
        """
        self._credentials = credentials
        self._token = token
        self._service = None

    @classmethod
    def from_service_account(cls, json_path: str) -> 'DriveClient':
        """Inicializa com service account (para uso no servidor)."""
        from google.oauth2 import service_account
        creds = service_account.Credentials.from_service_account_file(
            json_path, scopes=DRIVE_SCOPES
        )
        return cls(credentials=creds)

    @classmethod
    def from_user_token(cls, access_token: str) -> 'DriveClient':
        """Inicializa com token OAuth do usuário (via allauth)."""
        from google.oauth2.credentials import Credentials
        creds = Credentials(token=access_token)
        return cls(credentials=creds)

    def _get_service(self):
        if self._service:
            return self._service

        from googleapiclient.discovery import build
        from google.oauth2.credentials import Credentials

        if not self._credentials and self._token:
            self._credentials = Credentials(token=self._token)

        self._service = build('drive', 'v3', credentials=self._credentials,
                              cache_discovery=False)
        return self._service

    # ── Listagem ────────────────────────────────────────────────────────────

    def listar_pasta(self, pasta_id: str) -> list:
        """Lista arquivos de uma pasta do Drive."""
        service = self._get_service()

        resultado = service.files().list(
            q=f"'{pasta_id}' in parents and trashed=false",
            fields='files(id, name, mimeType, size)',
            includeItemsFromAllDrives=True,
            supportsAllDrives=True,
            orderBy='name',
        ).execute()

        arquivos = []
        for item in resultado.get('files', []):
            arq = ArquivoDrive(
                id=item['id'],
                nome=item['name'],
                mime_type=item['mimeType'],
                tamanho=int(item.get('size', 0)),
                pasta_id=pasta_id,
            )
            if arq.suportado:
                arquivos.append(arq)

        return arquivos

    def listar_subpastas(self, pasta_id: str) -> list:
        """Lista subpastas de uma pasta (útil para encontrar AULA_01, AULA_02...)."""
        service = self._get_service()

        resultado = service.files().list(
            q=(
                f"'{pasta_id}' in parents "
                f"and mimeType='application/vnd.google-apps.folder' "
                f"and trashed=false"
            ),
            fields='files(id, name)',
            includeItemsFromAllDrives=True,
            supportsAllDrives=True,
            orderBy='name',
        ).execute()

        return [
            {'id': item['id'], 'nome': item['name']}
            for item in resultado.get('files', [])
        ]

    def buscar_pasta_por_nome(self, nome: str, pasta_pai_id: str = '') -> Optional[dict]:
        """Busca uma pasta pelo nome (ex: 'AULA_03')."""
        service = self._get_service()

        q = f"name='{nome}' and mimeType='application/vnd.google-apps.folder' and trashed=false"
        if pasta_pai_id:
            q += f" and '{pasta_pai_id}' in parents"

        resultado = service.files().list(
            q=q,
            fields='files(id, name)',
            includeItemsFromAllDrives=True,
            supportsAllDrives=True,
        ).execute()

        arquivos = resultado.get('files', [])
        return arquivos[0] if arquivos else None

    # ── Download ────────────────────────────────────────────────────────────

    def baixar_arquivo(self, arquivo: ArquivoDrive) -> io.BytesIO:
        """
        Baixa um arquivo do Drive e retorna como BytesIO.
        Exporta automaticamente arquivos Google Workspace para Office.
        """
        service = self._get_service()

        if arquivo.eh_google_workspace:
            # Exporta Google Slides/Docs para PPTX/DOCX
            mime_exportar = MIME_EXPORTACAO.get(arquivo.mime_type)
            if not mime_exportar:
                raise ValueError(f'Não sei exportar: {arquivo.mime_type}')

            logger.info(f'Exportando {arquivo.nome} como {mime_exportar}...')
            request = service.files().export_media(
                fileId=arquivo.id,
                mimeType=mime_exportar,
            )
        else:
            logger.info(f'Baixando {arquivo.nome}...')
            request = service.files().get_media(fileId=arquivo.id)

        buffer = io.BytesIO()

        from googleapiclient.http import MediaIoBaseDownload
        downloader = MediaIoBaseDownload(buffer, request)

        done = False
        while not done:
            _, done = downloader.next_chunk()

        buffer.seek(0)
        buffer.name = arquivo.nome_completo  # importante para o extrator detectar extensão
        return buffer

    # ── RCO ─────────────────────────────────────────────────────────────────

    def carregar_pasta_rco(self, pasta_id: str) -> 'PastaRCO':
        """
        Carrega uma pasta no padrão RCO e identifica os arquivos por papel.
        """
        from .rco import detectar_papel_rco, PapelRCO

        arquivos = self.listar_pasta(pasta_id)

        # Busca o nome da pasta
        service = self._get_service()
        meta = service.files().get(
            fileId=pasta_id, fields='name'
        ).execute()

        pasta = PastaRCO(
            id=pasta_id,
            nome=meta.get('name', pasta_id),
            arquivos=arquivos,
        )

        logger.info(
            f'Pasta RCO: {pasta.nome} | '
            f'{len(arquivos)} arquivo(s) suportado(s)'
        )

        return pasta

    def extrair_rco_do_drive(self, pasta_id: str) -> dict:
        """
        Pipeline completo: baixa e extrai os 3 arquivos RCO de uma pasta.
        Retorna o mesmo formato de montar_conteudo_rco().
        """
        from .rco import (detectar_papel_rco, PapelRCO, ConjuntoRCO,
                          extrair_rco, montar_conteudo_rco)

        pasta = self.carregar_pasta_rco(pasta_id)
        conjunto = ConjuntoRCO()

        for arq_meta in pasta.arquivos:
            papel = detectar_papel_rco(arq_meta.nome)
            if papel == PapelRCO.OUTRO:
                continue

            try:
                buffer = self.baixar_arquivo(arq_meta)
                if papel == PapelRCO.SLIDES:
                    conjunto.slides = buffer
                elif papel == PapelRCO.ATIVIDADE:
                    conjunto.atividade = buffer
                elif papel == PapelRCO.PRATICA:
                    conjunto.pratica = buffer
            except Exception as e:
                logger.error(f'Erro ao baixar {arq_meta.nome}: {e}')

        logger.info(f'Conjunto RCO: {conjunto.resumo}')

        extracao = extrair_rco(conjunto)
        return montar_conteudo_rco(extracao)


# ── Helpers para Views Django ──────────────────────────────────────────────────

def get_drive_client_do_usuario(user) -> Optional[DriveClient]:
    """
    Retorna DriveClient autenticado com o token Google do usuário.
    Retorna None se o usuário não tiver conta Google conectada.

    Uso na view:
        client = get_drive_client_do_usuario(request.user)
        if not client:
            return JsonResponse({'erro': 'Conta Google não conectada.'}, status=400)
    """
    try:
        from allauth.socialaccount.models import SocialToken, SocialApp

        app   = SocialApp.objects.get(provider='google')
        token = SocialToken.objects.get(
            account__user=user,
            account__provider='google',
        )
        return DriveClient.from_user_token(token.token)

    except Exception as e:
        logger.warning(f'Sem token Google para {user}: {e}')
        return None


def listar_pastas_rco_do_drive(user, pasta_disciplina_id: str) -> list:
    """
    Lista as subpastas de uma disciplina no Drive (AULA_01, AULA_02...).
    Usado para popular o dropdown de importação do Drive na interface.
    """
    client = get_drive_client_do_usuario(user)
    if not client:
        return []

    try:
        subpastas = client.listar_subpastas(pasta_disciplina_id)
        return sorted(subpastas, key=lambda x: x['nome'])
    except Exception as e:
        logger.error(f'Erro ao listar subpastas: {e}')
        return []
