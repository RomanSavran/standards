import json
import os
import sys
import argparse
from copy import deepcopy
from collections import OrderedDict
from owlready2 import get_ontology, Ontology
from models import RDFClass, RDFProperty
from export_templates import BASE_IDENTITY_TEMPLATE, DEFENITION_TEMPLATE, VOCABULARY_TEMPLATE, EXPORT_URL
from utils import owl_property_to_python_for_definition, owl_property_context, class_get_full_id, \
    owl_property_to_python_for_vocabulary
from class_helpers import Link, Identity


def create_definition_from_rdf_class(rdf_class, entity_file, onto, export_pot_url, template):
    vocabulary = f"{export_pot_url}Vocabulary/{entity_file.get('id')}"

    vocabulary_dict = deepcopy(template)
    vocabulary_dict['@context']['@vocab'] = vocabulary
    vocabulary_dict['@context']['description'] = {
        '@id': 'rdfs:comment',
        '@container': ['@language', '@set']
    }

    supported_class = rdf_class.to_python(entity_file)
    supported_attrs = {
        'data': {
            '@id': 'pot:data',
            '@type': 'pot:SupportedAttribute',
            'rdfs:label': 'data',
            'rdfs:comment': {
                'en-us': 'data'
            },
            'pot:required': False,
        }
    }

    total_attributes = set()
    for a in onto.data_properties():
        if rdf_class.rdf_entity.ancestors().intersection(a.domain):
            total_attributes.add(a)

    for a in onto.object_properties():
        if rdf_class.rdf_entity.ancestors().intersection(a.domain):
            total_attributes.add(a)

    for rdf_attribute in total_attributes:
        supported_attrs[str(rdf_attribute.name)] = owl_property_to_python_for_definition(
            rdf_attribute)

    supported_attrs = OrderedDict(
        sorted(supported_attrs.items(), key=lambda t: t[0]))

    supported_class['pot:supportedAttribute'] = supported_attrs
    vocabulary_dict['pot:supportedClass'] = supported_class
    return vocabulary_dict


def create_identity_from_rdf_class(rdf_class, entity_file, onto, export_pot_url, template):
    vocabulary = f"{export_pot_url}ClassDefinitions/{entity_file.get('id')}"
    identity_dict = deepcopy(template)
    identity_dict['@vocab'] = f"{export_pot_url}Vocabulary/{entity_file.get('id')}"
    identity_dict['@classDefinition'] = vocabulary

    total_attributes = set()
    for a in onto.data_properties():
        if rdf_class.rdf_entity.ancestors().intersection(a.domain):
            total_attributes.add(a)

    for a in onto.object_properties():
        if rdf_class.rdf_entity.ancestors().intersection(a.domain):
            total_attributes.add(a)

    for rdf_attribute in total_attributes:
        identity_dict[rdf_attribute.name] = owl_property_context(rdf_attribute)

    return {
        '@context': identity_dict
    }


def create_vocabulary_from_rdf_class(rdf_class: RDFClass, entity_file: dict, onto: Ontology, template: dict) -> dict:
    vocabulary_dict = deepcopy(template)
    total_attributes = set()
    for a in onto.data_properties():
        if rdf_class.rdf_entity.ancestors().intersection(a.domain):
            total_attributes.add(a)

    for a in onto.object_properties():
        if rdf_class.rdf_entity.ancestors().intersection(a.domain):
            total_attributes.add(a)

    for rdf_attribute in total_attributes:
        vocabulary_dict[rdf_attribute.name] = owl_property_to_python_for_vocabulary(
            rdf_attribute)

    vocabulary_dict[rdf_class.rdf_entity.name] = rdf_class.to_python(
        entity_file)
    vocabulary_dict['@context']['label'] = {
        '@id': 'rdfs:label',
        "@container": ['@language', '@set']
    }
    vocabulary_dict['@context']['comment'] = {
        '@id': 'rdfs:comment',
        "@container": ['@language', '@set']
    }

    for dependent in rdf_class.rdf_entity.subclasses():
        vocabulary_dict[dependent.name] = {
            'rdfs:subClassOf': {
                '@id': 'pot:{}'.format(class_get_full_id(dependent).replace(f'/{dependent.name}', ''))
            }
        }

    return vocabulary_dict


def is_link_identity_relations(rdf_class: RDFClass) -> bool:
    return (Link in rdf_class.rdf_entity.ancestors() or Identity in rdf_class.rdf_entity.ancestors()) and (rdf_class.rdf_entity != Link and rdf_class.rdf_entity != Identity)


def write_dump_to_file(dir_context, entity_file, data_to_dump):
    entity_dir_path = os.path.join(
        dir_context, entity_file.get('dir'))
    entity_file_path = os.path.join(
        entity_dir_path, entity_file.get('filename'))
    os.makedirs(entity_dir_path, exist_ok=True)

    with open(entity_file_path, 'w', encoding='utf-8') as rf:
        rf.write(json.dumps(data_to_dump, indent=4,
                            separators=(',', ': '), ensure_ascii=False))


def parse(fname, export_pot_url):
    onto = get_ontology(fname).load()

    base_identity_template = BASE_IDENTITY_TEMPLATE(export_pot_url)
    definition_template = DEFENITION_TEMPLATE(export_pot_url)
    vocabulary_template = VOCABULARY_TEMPLATE(export_pot_url)

    for rdf_class in [RDFClass(i) for i in onto.classes()]:
        files = rdf_class.get_files()
        for entity_file in files:
            if is_link_identity_relations(rdf_class):

                data_to_dump = create_definition_from_rdf_class(
                    rdf_class, entity_file, onto, export_pot_url, definition_template)
                write_dump_to_file(CLASS_DEFINITIONS_DIR,
                                   entity_file, data_to_dump)

                data_to_dump = create_identity_from_rdf_class(
                    rdf_class, entity_file, onto, export_pot_url, base_identity_template)

                write_dump_to_file(CONTEXT_DIR, entity_file, data_to_dump)

            data_to_dump = create_vocabulary_from_rdf_class(
                rdf_class, entity_file, onto, vocabulary_template)
            write_dump_to_file(VOCABULARY_DIR, entity_file, data_to_dump)

    for rdf_property in [RDFProperty(i) for i in onto.properties()]:
        files = rdf_property.get_files()
        for property_file in files:
            data_to_dump = rdf_property.to_python(vocabulary_template)
            write_dump_to_file(VOCABULARY_DIR, property_file, data_to_dump)


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
    _export_pot_url = args.export_url

    VOCABULARY_DIR = os.path.join(BASE_DIR, 'Vocabulary')
    CONTEXT_DIR = os.path.join(BASE_DIR, 'Context')
    CLASS_DEFINITIONS_DIR = os.path.join(BASE_DIR, 'ClassDefinitions')

    parse(filename, _export_pot_url)
