from dataskillhub.extract import (
    Version,
    ExportConfig,
    DossierCompetence,
    Section,
    flat_export,
)


# part test


def test_flat_export():
    config = ExportConfig(
        post="data scientise",
        versions=[
            Version(name="Pipo", file_id="s", anonymised=False),
            Version(name="PPI", file_id="t1", anonymised=True),
            Version(name="PLP", file_id="t2", anonymised=True),
        ],
    )
    config_section = {
        "valeur_ajoutee": {
            "title": "Valeur ajoutée sur votre mission",
            "headingLevels": [],
        },
        "competences_cles": {"title": "Compétences clés", "headingLevels": []},
    }
    body_dict = {
        "valeur_ajoutee": Section(
            title="Valeur ajoutée sur votre mission", content="ok/valeur_ajoutee.md" # noqa
        ),
        "competences_cles": Section(
            title="Compétences clés", content="ok/competences_cles.md"
        ),
    }
    dc_list = [
        DossierCompetence(
            identity="Pipo",
            anonyme=False,
            post="data scientise",
            body=body_dict,
            file_id="s",  # noqa
        ),
        DossierCompetence(
            identity="PPI",
            anonyme=True,
            post="data scientise",
            body=body_dict,
            file_id="t1",
        ),
        DossierCompetence(
            identity="PLP",
            anonyme=True,
            post="data scientise",
            body=body_dict,
            file_id="t2",
        ),
    ]
    assert flat_export(config_section, config, "ok") == dc_list
