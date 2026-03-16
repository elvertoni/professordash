import magic
from django.core.exceptions import ValidationError

# 50 MB
MAX_UPLOAD_SIZE = 50 * 1024 * 1024

# Tipos aceitos em materiais didáticos
TIPOS_PERMITIDOS_MATERIAL = [
    "application/pdf",
    "application/zip",
    "application/x-zip-compressed",
    "application/vnd.ms-powerpoint",
    "application/vnd.openxmlformats-officedocument.presentationml.presentation",
    "text/plain",
    "text/html",
    "text/markdown",
    "text/x-python",
    "text/javascript",
    "text/css",
    "application/json",
]

# Tipos aceitos em entregas de alunos (superset dos materiais)
TIPOS_PERMITIDOS_ENTREGA = TIPOS_PERMITIDOS_MATERIAL + [
    "application/msword",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "image/png",
    "image/jpeg",
]


def validar_arquivo(arquivo, tipos_permitidos=None):
    """
    Valida o MIME type real (via python-magic) e o tamanho do arquivo.
    Lança ValidationError se o arquivo for inválido.

    Args:
        arquivo: InMemoryUploadedFile ou similar (com .read(), .seek(), .size)
        tipos_permitidos: lista de MIME types aceitos. Default: TIPOS_PERMITIDOS_MATERIAL
    """
    if tipos_permitidos is None:
        tipos_permitidos = TIPOS_PERMITIDOS_MATERIAL

    if arquivo.size > MAX_UPLOAD_SIZE:
        raise ValidationError(
            f"Arquivo muito grande. Tamanho máximo permitido: "
            f"{MAX_UPLOAD_SIZE // (1024 * 1024)} MB."
        )

    mime = magic.from_buffer(arquivo.read(2048), mime=True)
    arquivo.seek(0)

    if mime not in tipos_permitidos:
        raise ValidationError(
            f"Tipo de arquivo não permitido: {mime}. "
            f"Tipos aceitos: {', '.join(tipos_permitidos)}."
        )
