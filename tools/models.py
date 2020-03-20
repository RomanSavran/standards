import os
from copy import deepcopy
from typing import Any, Dict, List, NoReturn

from owlready2 import label, comment, Thing

from class_helpers import subClassOf
from utils import owl_property_to_python_for_vocabulary

# TODO. Hardcoded PREFIX required for entity files
PREFIX = 'pot'


class AbstractRDFEntity:
    SKIP_BASES = 1

    def __init__(self, entity: Any) -> NoReturn:
        """Abstract RDF entity initialization method.

        Args:
            entity (Any): 
                Entity, property or annotation class.
                Can be: ThingClass, DataPropertyClass, 
                        ObjectPropertyClass, AnnotationPropertyClass
        Attributes:
            entity (Thing): Class defined in the ontology.
            directories (None): Directories.

        """
        self.entity = entity
        self.directories = None

    @staticmethod
    def build_directories(entity: Any) -> List[str]:
        """Return list of RDF entity name and its parents names.

        Args:
            entity (Any): 
                Entity, property or annotation class.
                Can be: PropertyClass, ThingClass, 
                        DataPropertyClass, ObjectPropertyClass, 
                        AnnotationPropertyClass
        Returns:
            directories (list of str): List of directories.
        """
        parents = entity.is_a
        new_directories = []
        if len(parents):
            for parent in parents:
                directories = AbstractRDFEntity.build_directories(parent)
                for directory in directories:
                    new_directories.append(
                        os.path.join(directory, entity.name))
            return new_directories
        else:
            directories = [entity.name, ]
        return directories

    def get_files(self) -> List[Dict[str, str]]:
        """Return list of dictionaries with directory, filename and id of entity

        Returns:
            directories (list of dict of str: str): 
                List of dictionaries with directory, filename and id of entity
        """
        result_directories = []
        for result_directory in self.build_directories(self.entity):
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

    def get_files(self) -> List[Dict[str, str]]:
        """Return list of dictionaries with directory, filename and id of entity

        Returns:
            (list of dict): 
                List of dictionaries with directory, filename and id of entity
        """
        directories = max(self.build_directories(self.entity), key=len)
        property_directories = directories.split(os.path.sep)[self.SKIP_BASES:]
        if property_directories[0] == 'topDataProperty':
            property_directories.pop(0)
        return [{
            'dir': os.path.sep.join(property_directories[:-1]),
            'filename': f'{property_directories[-1]}.jsonld',
            'id': '/'.join(property_directories[self.SKIP_BASES:])
        }]

    def to_python(self, vocabulary_template: Dict[str, str]) -> Dict[str, str]:
        """Return modified vocabulary template.

        Args:
            vocabulary_template (dict of str: str): `Vocabulary` entity template

        Returns:
            vocabulary_dict (dict of str: str): Dict with `Vocabulary` parameters
        """
        vocabulary_dict = deepcopy(vocabulary_template)
        vocabulary_dict['@context']['label'] = {
            '@id': 'rdfs:label',
            "@container": ['@language', '@set']
        }
        vocabulary_dict['@context']['comment'] = {
            '@id': 'rdfs:comment',
            "@container": ['@language', '@set']
        }
        vocabulary_dict[self.entity.name] = owl_property_to_python_for_vocabulary(
            self.entity)
        return vocabulary_dict


class RDFClass(AbstractRDFEntity):

    def to_python(self, context: Dict[str, str]) -> Dict[str, Any]:
        """Return dict with parameters proccessed using context.

        Args:
            context (dict of str: str): 
                Dictionary with directory, filename and id of entity

        Returns:
            result (dict of str: str): Dict with entity parameters
        """
        result = {
            '@id': f'{PREFIX}:{context.get("id")}',
            '@type': 'owl:Class'
        }
        subclasses = list(
            subClassOf._get_indirect_values_for_class(self.entity))
        if subclasses and subclasses[0] != Thing:
            result['subClassOf'] = f'{PREFIX}:{subclasses[0].name}'

        labels = {}
        for l in label._get_indirect_values_for_class(self.entity):
            labels[l.lang] = str(l)
        if len(labels):
            result['rdfs:label'] = labels

        comments = {}
        for c in comment._get_indirect_values_for_class(self.entity):
            comments[c.lang] = str(c)
        if len(comments):
            result['rdfs:comment'] = comments

        return result
