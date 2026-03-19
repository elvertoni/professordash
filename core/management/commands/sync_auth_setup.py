import os

from django.conf import settings
from django.contrib.sites.models import Site
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Sincroniza Site e valida a configuração do Google OAuth."

    def handle(self, *args, **options):
        domain = self._get_site_domain()
        site_name = os.environ.get("APP_SITE_NAME", "ProfessorDash").strip() or "ProfessorDash"

        site, _ = Site.objects.update_or_create(
            id=1,
            defaults={"domain": domain, "name": site_name},
        )
        self.stdout.write(self.style.SUCCESS(f"Site atualizado: {site.domain}"))

        client_id = os.environ.get("GOOGLE_CLIENT_ID", "").strip()
        client_secret = os.environ.get("GOOGLE_CLIENT_SECRET", "").strip()

        if bool(client_id) != bool(client_secret):
            self.stdout.write(
                self.style.WARNING(
                    "Google OAuth incompleto: defina GOOGLE_CLIENT_ID e "
                    "GOOGLE_CLIENT_SECRET juntos. Configuração atual mantida."
                )
            )
            return

        if not client_id:
            self.stdout.write(
                "Google OAuth não configurado via .env."
            )
            return

        from allauth.socialaccount.models import SocialApp

        removidos, _ = SocialApp.objects.filter(provider="google").delete()
        if removidos:
            self.stdout.write(
                self.style.SUCCESS(
                    "SocialApp(s) do Google removido(s) para evitar duplicidade com .env."
                )
            )

        self.stdout.write(self.style.SUCCESS("Google OAuth validado via .env."))

    def _get_site_domain(self) -> str:
        domain = os.environ.get("APP_DOMAIN", "").strip()
        if domain:
            return domain

        for host in settings.ALLOWED_HOSTS:
            cleaned = host.strip()
            if cleaned and cleaned not in {"localhost", "127.0.0.1"}:
                return cleaned

        return "localhost"
