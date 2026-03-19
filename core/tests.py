"""
Testes para o app core — validação de uploads (validar_arquivo).

Cobertura:
- PDF válido passa na validação
- ZIP válido passa na validação
- Arquivo maior que 50 MB lança ValidationError
- Tipo MIME não permitido lança ValidationError com mensagem adequada
- PNG é aceito em TIPOS_PERMITIDOS_ENTREGA mas bloqueado em TIPOS_PERMITIDOS_MATERIAL
- Mensagem de erro descreve o tipo bloqueado
"""
import io

import pytest
from allauth.socialaccount.models import SocialApp
from django.contrib.sites.models import Site
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.core.management import call_command
from django.urls import reverse

from core.validators import (
    MAX_UPLOAD_SIZE,
    TIPOS_PERMITIDOS_ENTREGA,
    TIPOS_PERMITIDOS_MATERIAL,
    validar_arquivo,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_uploaded_file(content: bytes, name: str = "test.bin", content_type: str = "application/octet-stream") -> InMemoryUploadedFile:
    """Cria um InMemoryUploadedFile com o conteúdo binário fornecido."""
    buf = io.BytesIO(content)
    return InMemoryUploadedFile(
        file=buf,
        field_name="arquivo",
        name=name,
        content_type=content_type,
        size=len(content),
        charset=None,
    )


# Bytes mágicos detectados corretamente pelo libmagic
PDF_MAGIC = b"%PDF-1.4 fake content for testing"
ZIP_MAGIC = b"PK\x03\x04" + b"\x00" * 60  # PK header = ZIP

# PNG mínimo válido de 1x1 pixel — libmagic exige a estrutura IHDR completa
PNG_MAGIC = bytes([
    0x89, 0x50, 0x4E, 0x47, 0x0D, 0x0A, 0x1A, 0x0A,  # PNG signature
    0x00, 0x00, 0x00, 0x0D, 0x49, 0x48, 0x44, 0x52,  # IHDR length + type
    0x00, 0x00, 0x00, 0x01, 0x00, 0x00, 0x00, 0x01,  # 1x1 dimensions
    0x08, 0x02, 0x00, 0x00, 0x00, 0x90, 0x77, 0x53,  # bit depth, color type, etc.
    0xDE, 0x00, 0x00, 0x00, 0x0C, 0x49, 0x44, 0x41,  # IDAT chunk
    0x54, 0x08, 0xD7, 0x63, 0xF8, 0xCF, 0xC0, 0x00,
    0x00, 0x00, 0x02, 0x00, 0x01, 0xE2, 0x21, 0xBC,
    0x33, 0x00, 0x00, 0x00, 0x00, 0x49, 0x45, 0x4E,  # IEND chunk
    0x44, 0xAE, 0x42, 0x60, 0x82,
])


# ---------------------------------------------------------------------------
# 4.14 — Testes de validar_arquivo()
# ---------------------------------------------------------------------------


class TestValidarArquivoTiposPermitidos:
    """Testes para tipos de arquivo aceitos nas diferentes listas de permissão."""

    def test_pdf_valido_passa_validacao_material(self):
        """application/pdf deve ser aceito como material didático."""
        # Arrange
        arquivo = _make_uploaded_file(PDF_MAGIC, name="aula.pdf", content_type="application/pdf")

        # Act / Assert — não deve lançar exceção
        validar_arquivo(arquivo, tipos_permitidos=TIPOS_PERMITIDOS_MATERIAL)

    def test_zip_valido_passa_validacao_material(self):
        """application/zip deve ser aceito como material didático."""
        # Arrange
        arquivo = _make_uploaded_file(ZIP_MAGIC, name="projeto.zip", content_type="application/zip")

        # Act / Assert — não deve lançar exceção
        validar_arquivo(arquivo, tipos_permitidos=TIPOS_PERMITIDOS_MATERIAL)

    def test_png_e_aceito_em_entregas(self):
        """image/png deve ser aceito na lista de entregas de alunos."""
        # Arrange
        arquivo = _make_uploaded_file(PNG_MAGIC, name="screenshot.png", content_type="image/png")

        # Act / Assert — não deve lançar exceção
        validar_arquivo(arquivo, tipos_permitidos=TIPOS_PERMITIDOS_ENTREGA)

    def test_png_nao_e_aceito_em_materiais(self):
        """image/png NÃO deve ser aceito na lista de materiais didáticos."""
        # Arrange
        arquivo = _make_uploaded_file(PNG_MAGIC, name="imagem.png", content_type="image/png")

        # Act / Assert
        with pytest.raises(ValidationError) as exc_info:
            validar_arquivo(arquivo, tipos_permitidos=TIPOS_PERMITIDOS_MATERIAL)

        # Verifica que a mensagem indica que o tipo não é permitido
        assert "Tipo de arquivo não permitido" in str(exc_info.value)

    def test_tipos_material_sao_subconjunto_de_entrega(self):
        """Todo tipo permitido em materiais deve também ser permitido em entregas."""
        for tipo in TIPOS_PERMITIDOS_MATERIAL:
            assert tipo in TIPOS_PERMITIDOS_ENTREGA, (
                f"{tipo} está em MATERIAL mas não em ENTREGA"
            )


class TestValidarArquivoTamanho:
    """Testes para o limite de tamanho de arquivo."""

    def test_arquivo_dentro_do_limite_passa(self):
        """Arquivo com tamanho menor que MAX_UPLOAD_SIZE deve passar na validação."""
        # Arrange — 1 KB de conteúdo PDF
        conteudo = PDF_MAGIC + b"X" * (1024 - len(PDF_MAGIC))
        arquivo = _make_uploaded_file(conteudo, name="pequeno.pdf")
        arquivo.size = len(conteudo)

        # Act / Assert
        validar_arquivo(arquivo, tipos_permitidos=TIPOS_PERMITIDOS_MATERIAL)

    def test_arquivo_maior_que_50mb_lanca_validation_error(self):
        """Arquivo com size > MAX_UPLOAD_SIZE deve lançar ValidationError de tamanho."""
        # Arrange — simula arquivo de 51 MB sem alocar memória real
        arquivo = _make_uploaded_file(PDF_MAGIC, name="gigante.pdf")
        arquivo.size = MAX_UPLOAD_SIZE + 1  # 50 MB + 1 byte

        # Act / Assert
        with pytest.raises(ValidationError) as exc_info:
            validar_arquivo(arquivo, tipos_permitidos=TIPOS_PERMITIDOS_MATERIAL)

        mensagem = str(exc_info.value)
        assert "50" in mensagem  # mensagem menciona o limite em MB

    def test_arquivo_exatamente_no_limite_passa(self):
        """Arquivo com size == MAX_UPLOAD_SIZE deve passar (limite é inclusivo)."""
        # Arrange
        arquivo = _make_uploaded_file(PDF_MAGIC, name="exato.pdf")
        arquivo.size = MAX_UPLOAD_SIZE  # exatamente 50 MB

        # Act / Assert — não deve lançar exceção
        validar_arquivo(arquivo, tipos_permitidos=TIPOS_PERMITIDOS_MATERIAL)


class TestValidarArquivoTiposBloqueados:
    """Testes para tipos MIME explicitamente bloqueados."""

    def test_executavel_nao_e_permitido(self):
        """Executável Windows (assinatura MZ) deve ser bloqueado em qualquer lista.

        libmagic detecta o MIME como application/x-dosexec para arquivos MZ.
        """
        # Arrange — assinatura MZ (executável Windows)
        exe_magic = b"MZ" + b"\x00" * 62
        arquivo = _make_uploaded_file(exe_magic, name="virus.exe", content_type="application/x-dosexec")

        # Act / Assert
        with pytest.raises(ValidationError) as exc_info:
            validar_arquivo(arquivo, tipos_permitidos=TIPOS_PERMITIDOS_MATERIAL)

        mensagem = str(exc_info.value)
        assert "Tipo de arquivo não permitido" in mensagem

    def test_mensagem_de_erro_cita_o_tipo_bloqueado(self):
        """A mensagem de ValidationError deve citar o MIME type detectado pelo libmagic.

        libmagic detecta executáveis Windows como application/x-dosexec.
        """
        # Arrange
        exe_magic = b"MZ" + b"\x00" * 62
        arquivo = _make_uploaded_file(exe_magic, name="prog.exe")

        # Act / Assert
        with pytest.raises(ValidationError) as exc_info:
            validar_arquivo(arquivo, tipos_permitidos=TIPOS_PERMITIDOS_MATERIAL)

        mensagem = str(exc_info.value)
        # A mensagem menciona o tipo detectado (application/x-dosexec)
        assert "application/x-dosexec" in mensagem

    def test_tipo_padrao_usa_lista_material_quando_nao_especificado(self):
        """Quando tipos_permitidos não é passado, deve usar TIPOS_PERMITIDOS_MATERIAL."""
        # Arrange — PNG não está na lista de materiais
        arquivo = _make_uploaded_file(PNG_MAGIC, name="foto.png")

        # Act / Assert
        with pytest.raises(ValidationError):
            validar_arquivo(arquivo)  # sem passar tipos_permitidos

    def test_arquivo_html_e_aceito_em_materiais(self):
        """text/html deve ser aceito como material didático (código-fonte)."""
        # Arrange — conteúdo HTML simples
        html = b"<!DOCTYPE html><html><body>Oi</body></html>"
        arquivo = _make_uploaded_file(html, name="pagina.html", content_type="text/html")

        # Act / Assert — não deve lançar exceção
        validar_arquivo(arquivo, tipos_permitidos=TIPOS_PERMITIDOS_MATERIAL)

    def test_arquivo_python_e_aceito_em_materiais(self):
        """text/x-python deve ser aceito como material didático."""
        # Arrange
        py = b"print('hello world')\n"
        arquivo = _make_uploaded_file(py, name="script.py", content_type="text/x-python")

        # Act / Assert — não deve lançar exceção
        validar_arquivo(arquivo, tipos_permitidos=TIPOS_PERMITIDOS_MATERIAL)


@pytest.mark.django_db
class TestAuthBootstrap:
    def test_sync_auth_setup_sincroniza_site_e_remove_socialapp_google_duplicado(
        self, monkeypatch
    ):
        monkeypatch.setenv("APP_DOMAIN", "aulas.tonicoimbra.com")
        monkeypatch.setenv("APP_SITE_NAME", "ProfessorDash")
        monkeypatch.setenv("GOOGLE_CLIENT_ID", "google-client-id")
        monkeypatch.setenv("GOOGLE_CLIENT_SECRET", "google-client-secret")

        app = SocialApp.objects.create(
            provider="google",
            name="Google OAuth",
            client_id="db-client-id",
            secret="db-client-secret",
        )
        app.sites.add(Site.objects.get_current())

        call_command("sync_auth_setup")

        site = Site.objects.get(id=1)

        assert site.domain == "aulas.tonicoimbra.com"
        assert site.name == "ProfessorDash"
        assert not SocialApp.objects.filter(provider="google").exists()

    def test_sync_auth_setup_nao_quebra_com_google_parcial(self, monkeypatch):
        monkeypatch.setenv("GOOGLE_CLIENT_ID", "google-client-id")
        monkeypatch.delenv("GOOGLE_CLIENT_SECRET", raising=False)

        call_command("sync_auth_setup")

        assert not SocialApp.objects.filter(provider="google").exists()

    def test_login_page_expoe_link_de_google(self, client, monkeypatch):
        monkeypatch.setenv("GOOGLE_CLIENT_ID", "google-client-id")
        monkeypatch.setenv("GOOGLE_CLIENT_SECRET", "google-client-secret")
        call_command("sync_auth_setup")

        response = client.get(reverse("login"))
        html = response.content.decode()

        assert response.status_code == 200
        assert reverse("google_login") in html
        assert "Entrar com Google" in html

    def test_login_page_nao_quebra_sem_google_configurado(self, client):
        response = client.get(reverse("login"))
        html = response.content.decode()

        assert response.status_code == 200
        assert "Entrar com Google" not in html
