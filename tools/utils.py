from copy import deepcopy
from collections import OrderedDict
from typing import Any, Dict

from owlready2 import Thing, default_world

from class_helpers import range as owl_range
from class_helpers import readonly, required, subPropertyOf, restriction, subClassOf, domain, nest
from builders import build_comments, build_labels, build_nested_comments, build_nested_labels, build_ranges, build_restrictions


PREFIX = 'pot'
A = set()


def prop_get_full_id(owl_property: Any) -> str:
    """Return property id.

        Args:
            owl_property (Any): 
                Property of entity.
                Can be: ObjectPropertyClass, AnnotationPropertyClass, DataPropertyClass.
        Returns:
            (str): Combined property id and property name.
    """
    property_id = ''
    subproperties = list(
        subPropertyOf._get_indirect_values_for_class(owl_property))
    if subproperties and subproperties[0].name != 'topDataProperty':
        property_id = f'{prop_get_full_id(subproperties[0])}/'
    return f'{property_id}{owl_property.name}'


def class_get_full_id(entity: Any) -> str:
    """Return ThingClass id.

        Args:
            entity (Any): ThingClass entity.

        Returns:
            (str): Combined class id and entity name.
    """
    class_id = ''
    subclass = list(subClassOf._get_indirect_values_for_class(entity))
    if subclass and subclass[0] != Thing:
        class_id = f'{class_get_full_id(subclass[0])}/'
    return f'{class_id}{entity.name}'


def owl_property_to_python_base(owl_property: Any) -> Dict[str, Any]:
    """Return dict of generated parameters using property.

        Args:
            owl_property (Any): 
                Property of entity.
                Can be: ObjectPropertyClass, AnnotationPropertyClass, DataPropertyClass.

        Returns:
            result (dict of str: Any): Dict of generated parameters.
    """
    _type = default_world._unabbreviate(owl_property._owl_type).replace(
        'http://www.w3.org/2002/07/owl#', 'owl:')

    result = {
        '@id': f'{PREFIX}:{prop_get_full_id(owl_property)}',
        '@type': _type,
    }

    subproperties = list(
        subPropertyOf._get_indirect_values_for_class(owl_property))
    if subproperties:
        result['subPropertyOf'] = f'{PREFIX}:{prop_get_full_id(subproperties[0])}'

    # TODO
    labels = build_labels(owl_property)
    if labels.items():
        result["rdfs:label"] = labels

    # TODO
    comments = build_comments(owl_property)
    if comments.items():
        result["rdfs:comment"] = comments

    # TODO
    nested_comments = build_nested_comments(owl_property)
    if nested_comments:
        result["comment"] = nested_comments

    # TODO
    nested_labes = build_nested_labels(owl_property)
    if nested_labes:
        result["label"] = nested_labes

    return result


# Create Definition


def owl_property_to_python_for_definition(owl_property: Any) -> Dict[str, Any]:
    """Return dict of generated properties required for definition.

        Args:
            owl_property (Any): 
                Property of entity.
                Can be: DataPropertyClass, ObjectPropertyClass

        Returns:
            result (dict): Dict of property parameters
    """
    result = owl_property_to_python_base(owl_property)

    is_required = required._get_indirect_values_for_class(owl_property)
    if is_required:
        result[f'{PREFIX}:required'] = is_required[0]

    is_readonly = readonly._get_indirect_values_for_class(owl_property)
    if is_readonly:
        result[f'{PREFIX}:readonly'] = is_readonly[0]

    if list(owl_range._get_indirect_values_for_class(owl_property)):
        result[f'{PREFIX}:valueType'] = build_ranges(owl_property)

    if list(restriction._get_indirect_values_for_class(owl_property)):
        result['xsd:restriction'] = build_restrictions(owl_property)

    return result


def create_definition_from_rdf_class(rdf_class, entity_file: Dict[str, str], onto, export_onto_url: str, template: Dict[str, str]) -> Dict[str, Any]:
    """Return dict of generated properties to create definitions from rdf classes.

        Args:
            rdf_class (models.RDFClass): RDFClass model object
            entity_file (dict of str: Any): 
                Dictionary with directory, filename and id of entity
            onto (namespace.Ontology): An ontology loaded with owlready2.
            export_onto_url (str): Link to base ontologies.
            template (dict of str: str): Template for definitions.

        Returns:
            vocabulary_dict (dict of str: Any): Dictionary of required parameters
    """
    
    vocabulary = f"{export_onto_url}Vocabulary/{entity_file.get('id')}"

    vocabulary_dict = deepcopy(template)
    vocabulary_dict['@context']['@vocab'] = vocabulary
    vocabulary_dict['@context']['description'] = {
        '@id': 'rdfs:comment',
        '@container': ['@language', '@set']
    }

    supported_class = rdf_class.to_python(entity_file)
    supported_attrs = {
        'data': {
            '@id': f'{PREFIX}:data',
            '@type': f'{PREFIX}:SupportedAttribute',
            'rdfs:label': 'data',
            'rdfs:comment': {
                'en-us': 'data'
            },
            f'{PREFIX}:required': False,
        }
    }

    total_attributes = set()
    for a in onto.data_properties():
        if rdf_class.entity.ancestors().intersection(a.domain):
            total_attributes.add(a)

    for a in onto.object_properties():
        if rdf_class.entity.ancestors().intersection(a.domain):
            total_attributes.add(a)

    for rdf_attribute in total_attributes:
        supported_attrs[str(rdf_attribute.name)] = owl_property_to_python_for_definition(
            rdf_attribute)

    supported_attrs = OrderedDict(
        sorted(supported_attrs.items(), key=lambda t: t[0]))

    supported_class[f'{PREFIX}:supportedAttribute'] = supported_attrs
    vocabulary_dict[f'{PREFIX}:supportedClass'] = supported_class
    
    return vocabulary_dict

# Create Identity


def owl_property_context(owl_property: Any) -> Dict[str, str]:
    """Return dict of generated nest parameter.

        Args:
            owl_property (Any): 
                Property of entity.
                Can be: DataPropertyClass, ObjectPropertyClass

        Returns:
            result (dict of str: str): Dictionary of nest parameters
    """
    result = {
        '@id': f'{PREFIX}:{prop_get_full_id(owl_property)}'
    }
    nest_list = nest._get_indirect_values_for_class(owl_property)
    if nest_list:
        result['@nest'] = nest_list[0].name
    return result


def create_identity_from_rdf_class(rdf_class, entity_file: Dict[str, Any], onto, export_onto_url: str, template: Dict[str, str]) -> Dict[str, Any]:
    """Return dict of generated properties to create identity from rdf classes.

        Args:
            rdf_class (models.RDFClass): RDFClass model object.
            entity_file (dict of str: Any): 
                Dictionary with directory, filename and id of entity.
            onto (namespace.Ontology): An ontology loaded with owlready2.
            export_onto_url (str): Link to base ontologies.
            template (dict of str: str): Template for definitions.

        Returns:
            (dict of str: Any): Dictionary of required parameters.
    """
    vocabulary = f"{export_onto_url}ClassDefinitions/{entity_file.get('id')}"
    identity_dict = deepcopy(template)
    identity_dict['@vocab'] = f"{export_onto_url}Vocabulary/{entity_file.get('id')}"
    identity_dict['@classDefinition'] = vocabulary

    total_attributes = set()
    for a in onto.data_properties():
        if rdf_class.entity.ancestors().intersection(a.domain):
            total_attributes.add(a)

    for a in onto.object_properties():
        if rdf_class.entity.ancestors().intersection(a.domain):
            total_attributes.add(a)

    for rdf_attribute in total_attributes:
        identity_dict[rdf_attribute.name] = owl_property_context(rdf_attribute)

    return {
        '@context': identity_dict
    }

# Create Vocabulary


def owl_property_to_python_for_vocabulary(owl_property) -> dict:
    """Return dict of generated properties required for vocabulary.

        Args:
            owl_property (Any): 
                Property of entity.
                Can be: DataPropertyClass, ObjectPropertyClass, AnnotationPropertyClass.

        Returns:
            result (dict): Dict of property parameters.
    """
    result = owl_property_to_python_base(owl_property)

    if list(owl_range._get_indirect_values_for_class(owl_property)):
        result[f'{PREFIX}:valueType'] = build_ranges(owl_property)

    if list(restriction._get_indirect_values_for_class(owl_property)):
        result['xsd:restriction'] = build_restrictions(owl_property)

    domains = []
    for d in domain._get_indirect_values_for_class(owl_property):
        domains.append(f'{PREFIX}:{d.name}')
    if domains:
        result['domain'] = domains

    return result


def create_vocabulary_from_rdf_class(rdf_class, entity_file: Dict[str, Any], onto, template: Dict[str, str]) -> Dict[str, Any]:
    """Return dict of generated properties to create vocabulary from rdf classes.

        Args:
            rdf_class (models.RDFClass): RDFClass model object.
            entity_file (dict of str: Any): 
                Dictionary with directory, filename and id of entity.
            onto (namespace.Ontology): An ontology loaded with owlready2.
            template (dict of str: str): Template for definitions.

        Returns:
            vocabulary_dict (dict of str: Any): Dictionary of required parameters.
    """
    vocabulary_dict = deepcopy(template)
    total_attributes = set()
    for a in onto.data_properties():
        if rdf_class.entity.ancestors().intersection(a.domain):
            total_attributes.add(a)

    for a in onto.object_properties():
        if rdf_class.entity.ancestors().intersection(a.domain):
            total_attributes.add(a)

    for rdf_attribute in total_attributes:
        vocabulary_dict[rdf_attribute.name] = owl_property_to_python_for_vocabulary(
            rdf_attribute)

    vocabulary_dict[rdf_class.entity.name] = rdf_class.to_python(
        entity_file)
    vocabulary_dict['@context']['label'] = {
        '@id': 'rdfs:label',
        "@container": ['@language', '@set']
    }
    vocabulary_dict['@context']['comment'] = {
        '@id': 'rdfs:comment',
        "@container": ['@language', '@set']
    }

    for dependent in rdf_class.entity.subclasses():
        vocabulary_dict[dependent.name] = {
            'rdfs:subClassOf': {
                '@id': f'{PREFIX}:{class_get_full_id(dependent).replace(f"/{dependent.name}", "")}'
            }
        }

    return vocabulary_dict
