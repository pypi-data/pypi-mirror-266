from progression_qc.progression_qc import *
import progression_qc
import traceback
import urllib

if __name__ == "__main__":
    args = traiter_paramètres()

    if args.version:
        print(f"progression_qc version {progression_qc.__version__}")
        code_retour = 0
    else:
        try:
            infos_question = charger_question(args.fichier, get_readers())
            if not infos_question:
                resultats = {"erreurs": {args.fichier: "Format YAML invalide"}}
            else:
                resultats = valider_schema_yaml_infos_question(infos_question)
                resultats["infos_question"] = infos_question
            code_retour = déterminer_code_retour(resultats)
        except (urllib.error.HTTPError, urllib.error.URLError) as e:
            code_retour = 255
            if args.verbose:
                print(traceback.format_exc(), file=sys.stderr)
            resultats = {"erreurs": {args.fichier: e}}

        if not args.quiet:
            if args.json:
                afficher_résultats_json(resultats)
            else:
                afficher_résultats(resultats)

    exit(code_retour)
