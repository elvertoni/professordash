import pytest
from django.urls import reverse


@pytest.mark.django_db
def test_aluno_inativo_nao_acessa_minha_area(client_aluno, aluno, turma):
    aluno.ativo = False
    aluno.save(update_fields=["ativo"])

    response = client_aluno.get(
        reverse("turmas:portal_minha_area", kwargs={"token": turma.token_publico}),
        follow=True,
    )

    assert response.status_code == 200
    assert response.redirect_chain[-1][0].endswith(
        reverse("turmas:portal", kwargs={"token": turma.token_publico})
    )
    assert "seu acesso a esta turma nao esta liberado" in response.content.decode().lower()
