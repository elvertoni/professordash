from allauth.socialaccount.adapter import DefaultSocialAccountAdapter


class SocialAccountAdapter(DefaultSocialAccountAdapter):
    """
    Após login Google, vincula o User ao Aluno cadastrado com o mesmo email.
    Isso permite que AlunoAutenticadoMixin encontre a matrícula via aluno__user.
    """

    def save_user(self, request, sociallogin, form=None):
        user = super().save_user(request, sociallogin, form)
        self._vincular_aluno(user)
        return user

    def pre_social_login(self, request, sociallogin):
        """Vincula também em logins subsequentes (não apenas no cadastro)."""
        super().pre_social_login(request, sociallogin)
        if sociallogin.is_existing:
            self._vincular_aluno(sociallogin.user)

    @staticmethod
    def _vincular_aluno(user):
        if not user or not user.pk or not user.email:
            return
        try:
            from alunos.models import Aluno

            aluno = Aluno.objects.get(email__iexact=user.email, user__isnull=True)
            aluno.user = user
            aluno.save(update_fields=["user"])
        except (Aluno.DoesNotExist, Aluno.MultipleObjectsReturned):
            pass
