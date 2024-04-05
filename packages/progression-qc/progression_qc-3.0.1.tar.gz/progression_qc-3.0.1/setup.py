from setuptools import setup


with open("progression_qc/VERSION") as f:
    version = f.read()[8:]

setup(
    name="progression_qc",
    version=version,
    description="progression_qc est un compilateur/validateur pour la production de d'exercices pour Progression. progression_qc reçoit sur l'entrée standard ou en paramètre un fichier YAML contenant la description d'une question et reproduit sur la sortie standard le résultat traité et validé.",
    url="https://git.dti.crosemont.quebec/progression/validateur",
    author="Patrick Lafrance",
    author_email="plafrance@crosemont.qc.ca",
    license='GPLv3+',
    packages=["progression_qc", "progression_qc/schemas"],
    package_data={"progression_qc": ["VERSION"]},
    install_requires=["cerberus", "pyyaml-include==1.4.1", "werkzeug"],
    classifiers=['Programming Language :: Python :: 3'],
)
