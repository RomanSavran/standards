import json
import os
import sys
import argparse

from owlready2 import get_ontology, Ontology

from models import RDFClass, RDFProperty
from class_helpers import Link, Identity
from export_templates import BASE_IDENTITY_TEMPLATE, DEFENITION_TEMPLATE, VOCABULARY_TEMPLATE
from utils import create_definition_from_rdf_class, create_identity_from_rdf_class, create_vocabulary_from_rdf_class


def is_link_identity_relations(rdf_class) -> bool:
    return (Link in rdf_class.rdf_entity.ancestors() or Identity in rdf_class.rdf_entity.ancestors()) and (rdf_class.rdf_entity != Link and rdf_class.rdf_entity != Identity)


def write_dump_to_file(dir_context: str, entity_file: dict, data_to_dump: dict) -> None:
    """
    Function to write all entities into various stuctured files.

        Parameters:
            dir_context (str): Entity directory.
            entity_file (dict): Entity stucture dict.
            data_to_dump (dict): Entity.

        Returns:
            None
    """
    entity_dir_path = os.path.join(
        dir_context, entity_file.get('dir'))
    entity_file_path = os.path.join(
        entity_dir_path, entity_file.get('filename'))
    os.makedirs(entity_dir_path, exist_ok=True)

    with open(entity_file_path, 'w', encoding='utf-8') as rf:
        rf.write(json.dumps(data_to_dump, indent=4,
                            separators=(',', ': '), ensure_ascii=False))


def build_rdf_clasess(onto, export_onto_url: str, definition_template: dict, base_identity_template: dict, vocabulary_template: dict) -> None:
    """
    Function to build rdf classes from ontology.

        Parameters:
            onto: An ontology loaded with owlready2.
            export_onto_url (str): Link to base ontologies.
            definition_template (dict): Template for definitions.
            base_identity_template (dict): Template for identities.
            vocabulary_template (dict): Template for vocabularies.

        Returns:
            None
    """
    for rdf_class in [RDFClass(i) for i in onto.classes()]:
        files = rdf_class.get_files()
        for entity_file in files:
            if is_link_identity_relations(rdf_class):

                data_to_dump = create_definition_from_rdf_class(
                    rdf_class, entity_file, onto, export_onto_url, definition_template)
                write_dump_to_file(CLASS_DEFINITIONS_DIR,
                                   entity_file, data_to_dump)

                data_to_dump = create_identity_from_rdf_class(
                    rdf_class, entity_file, onto, export_onto_url, base_identity_template)

                write_dump_to_file(CONTEXT_DIR, entity_file, data_to_dump)

            data_to_dump = create_vocabulary_from_rdf_class(
                rdf_class, entity_file, onto, vocabulary_template)
            write_dump_to_file(VOCABULARY_DIR, entity_file, data_to_dump)


def build_rdf_properties(onto, vocabulary_template: dict) -> None:
    """
    Function to build rdf properties from ontology.

        Parameters:
            onto: An ontology loaded with owlready2.
            vocabulary_template (dict): Template for vocabularies.

        Returns:
            None
    """
    for rdf_property in [RDFProperty(i) for i in onto.properties()]:
        files = rdf_property.get_files()
        for property_file in files:
            data_to_dump = rdf_property.to_python(vocabulary_template)
            write_dump_to_file(VOCABULARY_DIR, property_file, data_to_dump)


def parse(fname: str, export_onto_url: str) -> None:
    """
    Main ontology parser.

        Parameters:
            fname (str): File that contains ontology. <file.owl>
            export_onto_url (str): Link to base ontologies.

        Returns:
            None
    """
    onto = get_ontology(fname).load()

    base_identity_template = BASE_IDENTITY_TEMPLATE(export_onto_url)
    definition_template = DEFENITION_TEMPLATE(export_onto_url)
    vocabulary_template = VOCABULARY_TEMPLATE(export_onto_url)

    build_rdf_clasess(onto, export_onto_url, definition_template,
                      base_identity_template, vocabulary_template)
    build_rdf_properties(onto, vocabulary_template)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "filename", help="You have to select file to parse: <filename.owl>")
    parser.add_argument("output_dir", help="You have to pass output folder")
    parser.add_argument(
        "export_url", help="You have to select export pot url: https://<my-onto.test>")
    args = parser.parse_args()

    filename = args.filename
    BASE_DIR = args.output_dir
    export_onto_url = args.export_url

    VOCABULARY_DIR = os.path.join(BASE_DIR, 'Vocabulary')
    CONTEXT_DIR = os.path.join(BASE_DIR, 'Context')
    CLASS_DEFINITIONS_DIR = os.path.join(BASE_DIR, 'ClassDefinitions')
    PREFIX = 'pot'

    parse(filename, export_onto_url)
