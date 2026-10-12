from festival.text import slugify


def test_slugify_removes_accents():
    assert slugify("Théâtre des Planches") == "theatre-des-planches"


def test_slugify_cleans_spaces_and_symbols():
    assert slugify("Élodie  Marchal !") == "elodie-marchal"