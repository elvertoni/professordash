"""
Management command para criar dados de seed para desenvolvimento/testes.

Uso:
    python manage.py criar_seed_data
    python manage.py criar_seed_data --admin-password admin123
    python manage.py criar_seed_data --turmas 2 --alunos-por-turma 5

Cria:
    - 1 superuser (admin/professor)
    - 2-3 turmas de teste com nomes realistas
    - 5-10 alunos fictícios por turma (nomes brasileiros, email @escola.pr.gov.br)
    - Matrículas vinculando alunos às turmas
    - 1 user Django por aluno (senha: aluno123 — apenas para dev)
    - SocialApp do Google OAuth configurado (se .env tiver credenciais)
    - Site configurado (django.contrib.sites)

Compatível com SQLite (dev) e PostgreSQL (prod) — usa exclusivamente a ORM.
"""

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.sites.models import Site
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from alunos.models import Aluno
from turmas.models import Matricula, Turma

User = get_user_model()

# ---------------------------------------------------------------------------
# Dados de seed
# ---------------------------------------------------------------------------

SUPERUSER_DEFAULTS = {
    "username": "professor",
    "email": "professor@escola.pr.gov.br",
    "first_name": "Toni",
    "last_name": "Coimbra",
    "is_staff": True,
    "is_superuser": True,
}

TURMAS_PADRAO = [
    {
        "nome": "Programação Front-End",
        "codigo": "PFE-2A-M-2026",
        "descricao": "Desenvolvimento web com HTML, CSS, JavaScript e frameworks modernos.",
        "periodo": "2º Ano A Manhã",
        "ano_letivo": 2026,
    },
    {
        "nome": "Programação Back-End",
        "codigo": "PBE-2A-M-2026",
        "descricao": "Desenvolvimento server-side com Python, APIs REST e banco de dados.",
        "periodo": "2º Ano A Manhã",
        "ano_letivo": 2026,
    },
    {
        "nome": "Banco de Dados",
        "codigo": "BD-2A-M-2026",
        "descricao": "Modelagem, SQL, normalização e administração de bancos de dados relacionais.",
        "periodo": "2º Ano A Manhã",
        "ano_letivo": 2026,
    },
]

# 10 alunos fictícios brasileiros — cada seed usa um subconjunto
ALUNOS_FICTICIOS = [
    {"nome": "Ana Beatriz Silva",   "email": "ana.beatriz.silva@escola.pr.gov.br"},
    {"nome": "Bruno Henrique Lima", "email": "bruno.henrique.lima@escola.pr.gov.br"},
    {"nome": "Camila Souza Santos", "email": "camila.souza.santos@escola.pr.gov.br"},
    {"nome": "Daniel Oliveira Costa","email": "daniel.oliveira.costa@escola.pr.gov.br"},
    {"nome": "Eduarda Pereira Gomes","email": "eduarda.pereira.gomes@escola.pr.gov.br"},
    {"nome": "Felipe Augusto Rocha","email": "felipe.augusto.rocha@escola.pr.gov.br"},
    {"nome": "Gabriela Martins Dias","email": "gabriela.martins.dias@escola.pr.gov.br"},
    {"nome": "Henrique Almeida Neto","email": "henrique.almeida.neto@escola.pr.gov.br"},
    {"nome": "Isabela Cristina Rios","email": "isabela.cristina.rios@escola.pr.gov.br"},
    {"nome": "João Pedro Barbosa",  "email": "joao.pedro.barbosa@escola.pr.gov.br"},
]

ALUNO_SENHA = "aluno123"  # Apenas para desenvolvimento! Não usar em produção.


class Command(BaseCommand):
    help = "Cria dados de seed para desenvolvimento: admin, turmas, alunos e matrículas."

    def add_arguments(self, parser):
        parser.add_argument(
            "--admin-password",
            default="admin123",
            help="Senha do superuser admin (padrão: admin123).",
        )
        parser.add_argument(
            "--turmas",
            type=int,
            default=0,
            help="Quantidade de turmas a criar (0 = todas as 3 padrão).",
        )
        parser.add_argument(
            "--alunos-por-turma",
            type=int,
            default=0,
            help="Quantidade de alunos por turma (0 = 5, ou tantos quanto possível).",
        )
        parser.add_argument(
            "--no-social-app",
            action="store_true",
            help="Não configurar SocialApp do Google (útil se .env já tiver credenciais).",
        )

    def handle(self, *args, **options):
        admin_password = options["admin_password"]
        qtd_turmas = options["turmas"]
        qtd_alunos = options["alunos_por_turma"]
        no_social_app = options["no_social_app"]

        # --- Validações ---
        if qtd_turmas and qtd_turmas > len(TURMAS_PADRAO):
            self.stdout.write(
                self.style.WARNING(
                    f"Só há {len(TURMAS_PADRAO)} turmas definidas. "
                    f"Criando todas."
                )
            )
            qtd_turmas = len(TURMAS_PADRAO)

        # Resolve defaults
        turmas_para_criar = TURMAS_PADRAO[:qtd_turmas] if qtd_turmas else TURMAS_PADRAO

        if not settings.USE_TZ:
            # Garantir que timezone-aware não seja exigido
            pass

        # -------------------------------------------------------------------
        # 1. Superuser (admin/professor)
        # -------------------------------------------------------------------
        with transaction.atomic():
            self._criar_superuser(admin_password)

            # -------------------------------------------------------------------
            # 2. Site
            # -------------------------------------------------------------------
            self._configurar_site()

            # -------------------------------------------------------------------
            # 3. Turmas
            # -------------------------------------------------------------------
            turmas_criadas = self._criar_turmas(turmas_para_criar)

            # -------------------------------------------------------------------
            # 4. Alunos + Users + Matrículas
            # -------------------------------------------------------------------
            self._criar_alunos_e_matriculas(turmas_criadas, qtd_alunos)

            # -------------------------------------------------------------------
            # 5. SocialApp do Google (opcional)
            # -------------------------------------------------------------------
            if not no_social_app:
                self._configurar_social_app()

        # -------------------------------------------------------------------
        # Resumo final
        # -------------------------------------------------------------------
        self._exibir_resumo(admin_password)

    # =======================================================================
    # Métodos auxiliares
    # =======================================================================

    def _criar_superuser(self, password: str) -> User:
        """Cria ou atualiza o superuser padrão do professor."""
        if User.objects.filter(username=SUPERUSER_DEFAULTS["username"]).exists():
            user = User.objects.get(username=SUPERUSER_DEFAULTS["username"])
            user.email = SUPERUSER_DEFAULTS["email"]
            user.first_name = SUPERUSER_DEFAULTS["first_name"]
            user.last_name = SUPERUSER_DEFAULTS["last_name"]
            user.is_staff = True
            user.is_superuser = True
            user.set_password(password)
            user.save(update_fields=[
                "email", "first_name", "last_name", "is_staff",
                "is_superuser", "password",
            ])
            self.stdout.write(
                self.style.SUCCESS(
                    f"Superuser ATUALIZADO: {user.username} ({user.email})"
                )
            )
        else:
            user = User.objects.create_superuser(
                username=SUPERUSER_DEFAULTS["username"],
                email=SUPERUSER_DEFAULTS["email"],
                password=password,
                first_name=SUPERUSER_DEFAULTS["first_name"],
                last_name=SUPERUSER_DEFAULTS["last_name"],
            )
            self.stdout.write(
                self.style.SUCCESS(
                    f"Superuser CRIADO: {user.username} ({user.email})"
                )
            )
        return user

    def _configurar_site(self):
        """Configura o Site com id=1 (django.contrib.sites)."""
        domain = getattr(settings, "ALLOWED_HOSTS", ["localhost"])[0]
        site, created = Site.objects.update_or_create(
            id=1,
            defaults={"domain": domain, "name": "ProfessorDash"},
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f"Site CRIADO: {site.domain}"))
        else:
            self.stdout.write(self.style.SUCCESS(f"Site ATUALIZADO: {site.domain}"))

    def _criar_turmas(self, turmas_data: list) -> list[Turma]:
        """Cria ou recupera turmas. Retorna lista das turmas (criadas ou já existentes)."""
        turmas_criadas = []
        for data in turmas_data:
            turma, created = Turma.objects.get_or_create(
                codigo=data["codigo"],
                defaults={
                    "nome": data["nome"],
                    "descricao": data["descricao"],
                    "periodo": data["periodo"],
                    "ano_letivo": data["ano_letivo"],
                    "ativa": True,
                },
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f"Turma CRIADA: {turma}"))
            else:
                self.stdout.write(f"Turma já existe: {turma}")
            turmas_criadas.append(turma)
        return turmas_criadas

    def _criar_alunos_e_matriculas(
        self,
        turmas: list[Turma],
        qtd_por_turma: int,
    ):
        """
        Cria alunos (com user Django) e matrículas para cada turma.
        Distribui os alunos fictícios de forma que cada turma tenha alunos
        diferentes (ou compartilhados se não houver alunos suficientes).
        """
        qtd = qtd_por_turma if qtd_por_turma else min(5, len(ALUNOS_FICTICIOS))
        alunos_disponiveis = list(ALUNOS_FICTICIOS)

        # Se a quantidade solicitada excede os disponíveis, usa com repetição
        if qtd > len(alunos_disponiveis):
            self.stdout.write(
                self.style.WARNING(
                    f"Só há {len(alunos_disponiveis)} alunos fictícios definidos. "
                    f"Usando {len(alunos_disponiveis)} por turma (repetindo se necessário)."
                )
            )

        for idx, turma in enumerate(turmas):
            # Cada turma pega um subconjunto diferente dos alunos fictícios,
            # com sliding window para variar os alunos entre turmas.
            start = (idx * qtd) % len(alunos_disponiveis)
            alunos_turma = []
            for i in range(qtd):
                aluno_data = alunos_disponiveis[(start + i) % len(alunos_disponiveis)]
                alunos_turma.append(aluno_data)

            self.stdout.write(f"\n  Turma: {turma.nome}")
            for aluno_data in alunos_turma:
                # --- Criar ou recuperar Aluno ---
                aluno, aluno_created = Aluno.objects.get_or_create(
                    email=aluno_data["email"],
                    defaults={"nome": aluno_data["nome"], "ativo": True},
                )
                if aluno_created:
                    self.stdout.write(f"    Aluno CRIADO: {aluno.nome}")
                else:
                    # Atualiza nome se mudou
                    if aluno.nome != aluno_data["nome"]:
                        aluno.nome = aluno_data["nome"]
                        aluno.save(update_fields=["nome"])

                # --- Criar user Django para o aluno (login de teste) ---
                self._criar_user_para_aluno(aluno)

                # --- Criar matrícula ---
                _, mat_created = Matricula.objects.get_or_create(
                    aluno=aluno,
                    turma=turma,
                    defaults={"ativa": True},
                )
                if mat_created:
                    self.stdout.write(f"      Matrícula CRIADA: {aluno.nome} → {turma.nome}")

    def _criar_user_para_aluno(self, aluno: Aluno):
        """
        Cria ou atualiza um User Django para o aluno,
        permitindo login de teste com email + senha fixa.
        """
        email = aluno.email
        if aluno.user_id:
            # Já vinculado — apenas garante que a senha está correta
            user = aluno.user
            if not user.check_password(ALUNO_SENHA):
                user.set_password(ALUNO_SENHA)
                user.save(update_fields=["password"])
                self.stdout.write(
                    f"      Senha ATUALIZADA para user: {user.email}"
                )
            return

        # Tenta encontrar user existente pelo email
        user = User.objects.filter(email=email).first()
        if user:
            user.set_password(ALUNO_SENHA)
            user.save(update_fields=["password"])
            aluno.user = user
            aluno.save(update_fields=["user"])
            self.stdout.write(
                f"      User VINCULADO ao aluno: {user.email}"
            )
            return

        # Cria novo user
        username_base = email.split("@")[0].replace(".", "_")
        username = username_base
        contador = 1
        while User.objects.filter(username=username).exists():
            username = f"{username_base}_{contador}"
            contador += 1

        user = User.objects.create_user(
            username=username,
            email=email,
            password=ALUNO_SENHA,
            first_name=aluno.nome.split()[0] if aluno.nome.split() else "",
        )
        aluno.user = user
        aluno.save(update_fields=["user"])
        self.stdout.write(
            f"      User CRIADO para aluno: {user.email} (user: {user.username})"
        )

    def _configurar_social_app(self):
        """
        Cria um SocialApp do Google OAuth com as credenciais do .env
        (se disponíveis e válidas), ou cria um placeholder.
        """
        from allauth.socialaccount.models import SocialApp

        client_id = getattr(settings, "GOOGLE_CLIENT_ID", "").strip()
        client_secret = getattr(settings, "GOOGLE_CLIENT_SECRET", "").strip()

        app = None
        if client_id and client_secret:
            # Usa credenciais reais do .env
            app, created = SocialApp.objects.update_or_create(
                provider="google",
                name="Google OAuth (produção)",
                defaults={
                    "client_id": client_id,
                    "secret": client_secret,
                    "key": "",
                },
            )
            if created:
                self.stdout.write(
                    self.style.SUCCESS("SocialApp Google CRIADO com credenciais do .env")
                )
            else:
                self.stdout.write(
                    self.style.SUCCESS("SocialApp Google ATUALIZADO com credenciais do .env")
                )
        else:
            # Cria placeholder para testes (útil quando .env não tem credenciais)
            # O sync_auth_setup.py existente substituirá quando credenciais reais chegarem
            try:
                app, created = SocialApp.objects.update_or_create(
                    provider="google",
                    name="Google OAuth (placeholder dev)",
                    defaults={
                        "client_id": "placeholder-dev-client-id",
                        "secret": "placeholder-dev-client-secret",
                        "key": "",
                    },
                )
                if created:
                    self.stdout.write(
                        self.style.WARNING(
                            "SocialApp Google CRIADO com placeholder. "
                            "Configure GOOGLE_CLIENT_ID e GOOGLE_CLIENT_SECRET no .env "
                            "para credenciais reais."
                        )
                    )
                else:
                    self.stdout.write(
                        "SocialApp Google já existe (placeholder ou real)."
                    )
            except Exception as e:
                self.stdout.write(
                    self.style.WARNING(
                        f"Não foi possível criar SocialApp placeholder: {e}"
                    )
                )

        # Vincular ao Site id=1 (essencial para o allauth funcionar)
        if app is not None:
            app.sites.add(1)

    def _exibir_resumo(self, admin_password: str):
        """Exibe um resumo do que foi criado."""
        qtd_users = User.objects.count()
        qtd_alunos = Aluno.objects.count()
        qtd_turmas = Turma.objects.count()
        qtd_matriculas = Matricula.objects.count()

        self.stdout.write("\n" + "=" * 60)
        self.stdout.write(self.style.SUCCESS("SEED DATA CRIADO COM SUCESSO!"))
        self.stdout.write("=" * 60)
        self.stdout.write(f"  Superuser:         {SUPERUSER_DEFAULTS['username']}")
        self.stdout.write(f"    Email:           {SUPERUSER_DEFAULTS['email']}")
        self.stdout.write(f"    Senha:           {admin_password}")
        self.stdout.write(f"  Total de turmas:   {qtd_turmas}")
        self.stdout.write(f"  Total de alunos:   {qtd_alunos}")
        self.stdout.write(f"  Total de matrículas: {qtd_matriculas}")
        self.stdout.write(f"  Total de users:    {qtd_users}")
        self.stdout.write(f"  Senha dos alunos de teste: {ALUNO_SENHA}")
        self.stdout.write("=" * 60)
        self.stdout.write(
            self.style.WARNING(
                "ATENÇÃO: Use estas credenciais apenas em ambiente de "
                "desenvolvimento!"
            )
        )
