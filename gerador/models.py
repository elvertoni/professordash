from django.db import models

from core.models import BaseModel


class SessaoGeracao(BaseModel):
    MODO_CHOICES = [("rco", "Material RCO"), ("livre", "Material Livre")]
    NIVEL_CHOICES = [("tecnico", "Técnico"), ("superior", "Superior"), ("eja", "EJA")]
    FOCO_CHOICES = [
        ("equilibrado", "Equilibrado"),
        ("teorico", "Mais teórico"),
        ("pratico", "Mais prático"),
    ]
    PROVIDER_CHOICES = [
        ("claude", "Claude Sonnet"),
        ("gemini", "Gemini 2.5 Pro"),
        ("gpt4o", "GPT-4o"),
    ]
    STATUS_CHOICES = [
        ("rascunho", "Rascunho"),
        ("planejando", "Planejando"),
        ("gerando", "Gerando"),
        ("concluido", "Concluído"),
        ("erro", "Erro"),
    ]

    disciplina = models.ForeignKey(
        "turmas.Turma",
        on_delete=models.CASCADE,
        related_name="sessoes_geracao",
        verbose_name="Turma/Disciplina",
    )
    modo = models.CharField(max_length=10, choices=MODO_CHOICES, default="rco")
    num_aulas = models.IntegerField(default=1)
    nivel = models.CharField(max_length=20, choices=NIVEL_CHOICES, default="tecnico")
    foco = models.CharField(max_length=20, choices=FOCO_CHOICES, default="equilibrado")
    provider = models.CharField(max_length=30, choices=PROVIDER_CHOICES, default="claude")
    instrucoes = models.TextField(blank=True)
    planejamento = models.JSONField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="rascunho")
    tokens_usados = models.IntegerField(default=0)
    custo_estimado = models.DecimalField(max_digits=8, decimal_places=4, default=0)

    class Meta:
        verbose_name = "Sessão de Geração"
        verbose_name_plural = "Sessões de Geração"
        ordering = ["-criado_em"]

    def __str__(self):
        return f"Sessão #{self.pk} — {self.disciplina} ({self.get_modo_display()})"


class MaterialEntrada(BaseModel):
    TIPO_CHOICES = [
        ("pdf", "PDF"),
        ("pptx", "PPTX"),
        ("docx", "DOCX"),
        ("url", "URL"),
        ("texto", "Texto livre"),
    ]
    PAPEL_RCO_CHOICES = [
        ("slides", "Slides"),
        ("atividade", "Atividade"),
        ("pratica", "Prática"),
        ("outro", "Outro"),
    ]

    sessao = models.ForeignKey(
        SessaoGeracao,
        on_delete=models.CASCADE,
        related_name="materiais",
    )
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES)
    papel_rco = models.CharField(
        max_length=20, choices=PAPEL_RCO_CHOICES, blank=True, default=""
    )
    arquivo = models.FileField(upload_to="gerador/inputs/", blank=True)
    url = models.URLField(blank=True)
    texto_livre = models.TextField(blank=True)
    conteudo_extraido = models.TextField(blank=True)
    ordem = models.IntegerField(default=0)

    class Meta:
        verbose_name = "Material de Entrada"
        verbose_name_plural = "Materiais de Entrada"
        ordering = ["ordem"]

    def __str__(self):
        return f"{self.get_tipo_display()} — Sessão #{self.sessao_id}"
