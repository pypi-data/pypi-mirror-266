from progression_qc import progression_qc

def test_valider_question_sys_complète_valide_avec_tests():
    from question_sys_complète_valide_avec_tests import question

    résultat = progression_qc.valider_schema_yaml_infos_question(question)

    assert résultat == {"avertissements":{}, "erreurs":{}}

def test_valider_question_sys_complète_valide_avec_réponse():
    from question_sys_complète_valide_avec_réponse import question

    résultat = progression_qc.valider_schema_yaml_infos_question(question)

    assert résultat == {"avertissements":{}, "erreurs":{}}

def test_valider_question_sys_minimale_valide_avec_tests():
    from question_sys_minimale_valide_avec_tests import question

    résultat = progression_qc.valider_schema_yaml_infos_question(question)

    assert résultat == {"avertissements":{}, "erreurs":{}}

def test_valider_question_sys_minimale_valide_avec_réponse():
    from question_sys_minimale_valide_avec_réponse import question

    résultat = progression_qc.valider_schema_yaml_infos_question(question)

    assert résultat == {"avertissements":{}, "erreurs":{}}

def test_valider_question_sys_sans_image_ni_tests():
    from question_sys_sans_image_ni_tests import question

    résultat = progression_qc.valider_schema_yaml_infos_question(question)

    assert résultat == {"avertissements":{},
                        'erreurs': {'tests': ['required field'],
                                    'image': ['required field'],
                                    'réponse': ['required field']}}


def test_valider_question_sys_avec_image_et_tests_vides():
    from question_sys_avec_image_et_tests_vides import question

    résultat = progression_qc.valider_schema_yaml_infos_question(question)

    assert résultat == {"avertissements":{},
                        'erreurs': {'tests': ['empty values not allowed'],
                                    'image': ['empty values not allowed']}}

def test_valider_question_sys_avec_image_et_réponse_vides():
    from question_sys_avec_image_et_réponse_vides import question

    résultat = progression_qc.valider_schema_yaml_infos_question(question)

    assert résultat == {"avertissements":{},
                        'erreurs': {'réponse': ['empty values not allowed'],
                                    'image': ['empty values not allowed']}}

def test_valider_question_sys_test_sortie_nulle():
    from question_sys_test_sortie_nulle import question

    résultat = progression_qc.valider_schema_yaml_infos_question(question)

    assert résultat == {"avertissements":{}, "erreurs": {"tests": [{0: [{"sortie": ["null value not allowed"]}]}]}}

def test_valider_question_sys_utilisateur_nul():
    from question_sys_utilisateur_nul import question

    résultat = progression_qc.valider_schema_yaml_infos_question(question)

    assert résultat == {"avertissements":{}, "erreurs": {"utilisateur": ["null value not allowed"]}}

def test_valider_question_sys_utilisateur_invalide():
    from question_sys_utilisateur_invalide import question

    résultat = progression_qc.valider_schema_yaml_infos_question(question)

    assert résultat == {"avertissements":{}, "erreurs": {"utilisateur": ["value does not match regex '^[a-z][-a-z0-9_]*$'"]}}

def test_valider_question_sys_init_nul():
    from question_sys_init_nul import question

    résultat = progression_qc.valider_schema_yaml_infos_question(question)

    assert résultat == {"avertissements":{}, "erreurs": {"init": ["null value not allowed"]}}

def test_valider_question_sys_init_vide():
    from question_sys_init_vide import question

    résultat = progression_qc.valider_schema_yaml_infos_question(question)

    assert résultat == {"avertissements":{}, "erreurs": {"init": ["empty values not allowed"]}}

def test_valider_question_prog_complète():
    from question_prog_complète_valide import question

    résultat = progression_qc.valider_schema_yaml_infos_question(question)

    assert résultat == {"avertissements": {}, "erreurs": {}}

def test_valider_question_avec_dict_pour_énoncés():
    from question_avec_dict_pour_énoncés import question

    résultat = progression_qc.valider_schema_yaml_infos_question(question)

    assert résultat == {"avertissements": {}, "erreurs": {}}

def test_valider_question_prog_minimale():
    from question_prog_minimale_valide import question

    résultat = progression_qc.valider_schema_yaml_infos_question(question)

    assert résultat == {"avertissements": {}, "erreurs": {}}

def test_valider_question_avec_avertissement():
    from question_avec_avertissement import question

    résultat = progression_qc.valider_schema_yaml_infos_question(question)

    assert résultat == {"avertissements": {'tata': ['unknown field']}, "erreurs": {}}

def test_valider_question_avec_erreur():
    from question_avec_erreur import question

    résultat = progression_qc.valider_schema_yaml_infos_question(question)

    assert résultat == {"avertissements": {}, "erreurs": {'type': ['required field']}}

def test_valider_question_prog_test_avec_sortie_nulle():
    from question_prog_test_sortie_nulle import question

    résultat = progression_qc.valider_schema_yaml_infos_question(question)

    assert résultat == {"avertissements": {}, "erreurs": {"tests": [{0: [{"sortie": ["null value not allowed"]}]}]}}

def test_valider_question_prog_test_avec_params_nul():
    from question_prog_test_params_nul import question

    résultat = progression_qc.valider_schema_yaml_infos_question(question)

    assert résultat == {"avertissements": {}, "erreurs": {"tests": [{0: [{"params": ["null value not allowed"]}]}]}}

def test_valider_question_prog_sans_ébauches_ni_tests():
    from question_prog_sans_ébauches_ni_tests import question

    résultat = progression_qc.valider_schema_yaml_infos_question(question)

    assert résultat == {"avertissements": {},
                        'erreurs': {'tests': ['required field'],
                                    'ébauches': ['required field']}}

def test_valider_question_prog_avec_ébauches_et_tests_vides():
    from question_prog_avec_ébauches_et_tests_vides import question

    résultat = progression_qc.valider_schema_yaml_infos_question(question)

    assert résultat == {"avertissements": {},
                        'erreurs': {'tests': ['empty values not allowed'],
                                    'ébauches': ['empty values not allowed']}}
