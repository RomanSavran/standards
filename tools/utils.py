from copy import deepcopy
from collections import OrderedDict

from owlready2 import Thing, DataPropertyClass, ObjectPropertyClass, ThingClass, AnnotationPropertyClass, default_world, Ontology

from class_helpers import readonly, required, subPropertyOf, range, restriction, subClassOf, domain, nest
from builders import build_comments, build_labels, build_nested_comments, build_nested_labels, build_ranges

PREFIX = 'pot'


def prop_get_full_id(prop: DataPropertyClass) -> str:
    """
    Function to get DataPropertyClass id.

        Parameters:
            prop (DataPropertyClass): 

        Returns:
            '' (str): Combined property id and property name
    """
    property_id = ''
    subproperties = list(subPropertyOf._get_indirect_values_for_class(prop))
    if subproperties and subproperties[0].name != 'topDataProperty':
        property_id = f'{prop_get_full_id(subproperties[0])}/'
    return f'{property_id}{prop.name}'


def class_get_full_id(prop: ThingClass) -> str:
    """
    Function to get ThingClass id.

        Parameters:
            prop (ThingClass): 

        Returns:
            '' (str): Combined class id and property name
    """
    class_id = ''
    subclass = list(subClassOf._get_indirect_values_for_class(prop))
    if subclass and subclass[0] != Thing:
        class_id = f'{class_get_full_id(subclass[0])}/'
    return f'{class_id}{prop.name}'


def owl_property_to_python_base(rdf_attribute: DataPropertyClass) -> dict:
    """
    Function to transform property to python base. 
    Generate: labels, nested labels, comments, nested comments

        Parameters:
            rdf_attribute (DataPropertyClass): 

        Returns:
            result (dict): Dict of property parameters
    """
    _type = default_world._unabbreviate(rdf_attribute._owl_type).replace(
        'http://www.w3.org/2002/07/owl#', 'owl:')

    result = {
        '@id': f'{PREFIX}:{prop_get_full_id(rdf_attribute)}',
        '@type': _type,
    }

    subproperties = list(
        subPropertyOf._get_indirect_values_for_class(rdf_attribute))
    if subproperties:
        result['subPropertyOf'] = f'{PREFIX}:{prop_get_full_id(subproperties[0])}'

    # TODO
    labels = build_labels(rdf_attribute)
    if labels.items():
        result["rdfs:label"] = labels

    # TODO
    comments = build_comments(rdf_attribute)
    if comments.items():
        result["rdfs:comment"] = comments

    # TODO
    nested_comments = build_nested_comments(rdf_attribute)
    if len(nested_comments):
        result["comment"] = nested_comments

    # TODO
    nested_labes = build_nested_labels(rdf_attribute)
    if len(nested_labes):
        result["label"] = nested_labes

    return result


# Create Definition


def owl_property_to_python_for_definition(rdf_attribute: DataPropertyClass) -> dict:
    """
    Function to create definitions from rdf classes.

        Parameters:
            rdf_attribute (DataPropertyClass): 

        Returns:
            result (dict): Dict of property parameters
    """
    result = owl_property_to_python_base(rdf_attribute)

    is_required = required._get_indirect_values_for_class(rdf_attribute)
    if is_required:
        result[f'{PREFIX}:required'] = is_required[0]

    is_readonly = readonly._get_indirect_values_for_class(rdf_attribute)
    if is_readonly:
        result[f'{PREFIX}:readonly'] = is_readonly[0]

    if list(range._get_indirect_values_for_class(rdf_attribute)):
        result[f'{PREFIX}:valueType'] = build_ranges(rdf_attribute, range)

    if list(restriction._get_indirect_values_for_class(rdf_attribute)):
        result['xsd:restriction'] = build_ranges(rdf_attribute, restriction)

    return result


def create_definition_from_rdf_class(rdf_class, entity_file, onto, export_onto_url: str, template: dict) -> dict:
    """
    Function to create definitions from rdf classes.

        Parameters:
            rdf_class :
            entity_file :
            onto: An ontology loaded with owlready2.
            export_onto_url (str): Link to base ontologies.
            template (dict): Template for definitions.

        Returns:
            vocabulary_dict (dict): 
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

    supported_class[f'{PREFIX}:supportedAttribute'] = supported_attrs
    vocabulary_dict[f'{PREFIX}:supportedClass'] = supported_class
    return vocabulary_dict

# Create Identity


def owl_property_context(rdf_attribute: DataPropertyClass) -> dict:
    result = {
        '@id': f'{PREFIX}:{prop_get_full_id(rdf_attribute)}'
    }
    nest_list = nest._get_indirect_values_for_class(rdf_attribute)
    if nest_list:
        result['@nest'] = nest_list[0].name
    return result


def create_identity_from_rdf_class(rdf_class, entity_file, onto, export_onto_url: str, template: dict) -> dict:
    """
    Function to create identities from rdf classes.

        Parameters:
            rdf_class :
            entity_file :
            onto: An ontology loaded with owlready2.
            export_onto_url (str): Link to base ontologies.
            template (dict): Template for definitions.

        Returns:
            {} (dict): 
    """
    vocabulary = f"{export_onto_url}ClassDefinitions/{entity_file.get('id')}"
    identity_dict = deepcopy(template)
    identity_dict['@vocab'] = f"{export_onto_url}Vocabulary/{entity_file.get('id')}"
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

# Create Vocabulary


def owl_property_to_python_for_vocabulary(rdf_attribute: DataPropertyClass) -> dict:
    result = owl_property_to_python_base(rdf_attribute)

    if list(range._get_indirect_values_for_class(rdf_attribute)):
        result[f'{PREFIX}:valueType'] = build_ranges(rdf_attribute, range)

    if list(restriction._get_indirect_values_for_class(rdf_attribute)):
        result['xsd:restriction'] = build_ranges(rdf_attribute, restriction)

    domains = []
    for d in domain._get_indirect_values_for_class(rdf_attribute):
        domains.append(f'{PREFIX}:{d.name}')
    if domains:
        result['domain'] = domains

    return result


def create_vocabulary_from_rdf_class(rdf_class, entity_file: dict, onto: Ontology, template: dict) -> dict:
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
                '@id': f'{PREFIX}:{class_get_full_id(dependent).replace(f"/{dependent.name}", "")}'
            }
        }

    return vocabulary_dict
