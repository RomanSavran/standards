import os
from copy import deepcopy

from owlready2 import label, comment, Thing
from class_helpers import subClassOf
from utils import owl_property_to_python_for_vocabulary


class AbstractRDFEntity:
    SKIP_BASES = 1

    def __init__(self, rdf_entity: Thing) -> None:
        self.rdf_entity = rdf_entity
        self.directories = None

    @staticmethod
    def build_directories(rdf_entity: Thing) -> list:
        """
        Build directories for rdf_entities and their parents
            Parameters:
                rdf_entity (owl.Thing): Thing entity
            Returns:
                directories (list): List or directories
        """
        parents = rdf_entity.is_a
        new_directories = []
        if len(parents):
            for parent in parents:
                directories = AbstractRDFEntity.build_directories(parent)
                for directory in directories:
                    new_directories.append(
                        os.path.join(directory, rdf_entity.name))
            return new_directories
        else:
            directories = [rdf_entity.name, ]
        return directories

    def get_files(self) -> list:
        result_directories = []
        for result_directory in self.build_directories(self.rdf_entity):
            entities = result_directory.split(os.path.sep)
            result_directories.append({
                'dir': os.path.sep.join(entities[self.SKIP_BASES:-1]),
                'filename': f'{entities[-1]}.jsonld',
                'id': '/'.join(entities[self.SKIP_BASES:])
            })
        self.directories = result_directories
        return self.directories


class RDFProperty(AbstractRDFEntity):
    SKIP_BASES = 2

    def get_files(self) -> list:
        directories = max(self.build_directories(self.rdf_entity), key=len)
        property_directories = directories.split(os.path.sep)[self.SKIP_BASES:]
        if property_directories[0] == 'topDataProperty':
            property_directories.pop(0)
        return [{
            'dir': os.path.sep.join(property_directories[:-1]),
            'filename': f'{property_directories[-1]}.jsonld',
            'id': '/'.join(property_directories[self.SKIP_BASES:])
        }]

    def to_python(self, vocabulary_template: dict) -> dict:
        vocabulary_dict = deepcopy(vocabulary_template)
        vocabulary_dict['@context']['label'] = {
            '@id': 'rdfs:label',
            "@container": ['@language', '@set']
        }
        vocabulary_dict['@context']['comment'] = {
            '@id': 'rdfs:comment',
            "@container": ['@language', '@set']
        }
        vocabulary_dict[self.rdf_entity.name] = owl_property_to_python_for_vocabulary(
            self.rdf_entity)
        return vocabulary_dict


class RDFClass(AbstractRDFEntity):

    def to_python(self, context: dict) -> dict:
        result = {
            '@id': f'pot:{context.get("id")}',
            '@type': 'owl:Class'
        }
        subclasses = list(
            subClassOf._get_indirect_values_for_class(self.rdf_entity))
        if subclasses and subclasses[0] != Thing:
            result['subClassOf'] = f'pot:{subclasses[0].name}'

        labels = dict()
        for l in label._get_indirect_values_for_class(self.rdf_entity):
            labels[l.lang] = str(l)
        if len(labels):
            result['rdfs:label'] = labels

        comments = dict()
        for c in comment._get_indirect_values_for_class(self.rdf_entity):
            comments[c.lang] = str(c)
        if len(comments):
            result['rdfs:comment'] = comments

        return result
