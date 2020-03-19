from owlready2 import Thing, label, comment, locstr, default_world, base, DataPropertyClass, ObjectPropertyClass, ThingClass, AnnotationPropertyClass

from class_helpers import readonly, required, subPropertyOf, range, restriction, subClassOf, domain, nest
from class_helpers import label as pot_label
from class_helpers import comment as pot_comment


def prop_get_full_id(prop: DataPropertyClass) -> str:
    property_id = ''
    subproperties = list(subPropertyOf._get_indirect_values_for_class(prop))
    if subproperties and subproperties[0].name != 'topDataProperty':
        property_id = f'{prop_get_full_id(subproperties[0])}/'
    return f'{property_id}{prop.name}'


def class_get_full_id(prop: ThingClass) -> str:
    class_id = ''
    subclass = list(subClassOf._get_indirect_values_for_class(prop))
    if subclass and subclass[0] != Thing:
        class_id = f'{class_get_full_id(subclass[0])}/'
    return f'{class_id}{prop.name}'


def owl_property_context(rdf_attribute: DataPropertyClass) -> dict:
    result = {
        '@id': f'pot:{prop_get_full_id(rdf_attribute)}'
    }
    nest_list = nest._get_indirect_values_for_class(rdf_attribute)
    if nest_list:
        result['@nest'] = nest_list[0].name
    return result


def build_nested_labels(rdf_attribute: DataPropertyClass) -> list:
    labels = []
    for c in rdf_attribute.label:
        if c:
            # TODO
            list_of_dict_labels = []
            temp_labels_dict = {'rdfs:label': {}}
            for l in label._get_indirect_values_for_class(c):
                list_of_dict_labels.append({l.lang: l})

            for label_dict in list_of_dict_labels:
                for item in label_dict.items():
                    temp_labels_dict['rdfs:label'][item[0]] = item[1]

            temp_labels_dict['domain'] = [f'pot:{d.name}' for d in c.domain]

            labels.append(temp_labels_dict)
    return labels


def build_nested_comments(rdf_attribute: DataPropertyClass) -> list:
    comments = []
    for c in rdf_attribute.comment:
        if c:
            # TODO
            list_of_dict_comments = []
            temp_comments_dict = {'rdfs:comment': {}}
            for l in comment._get_indirect_values_for_class(c):
                list_of_dict_comments.append({l.lang: l})

            for comment_dict in list_of_dict_comments:
                for item in comment_dict.items():
                    temp_comments_dict['rdfs:comment'][item[0]] = item[1]

            temp_comments_dict['domain'] = [f'pot:{d.name}' for d in c.domain]

            comments.append(temp_comments_dict)
    return comments


def build_labels(rdf_attribute: ObjectPropertyClass) -> dict:
    labels = {}
    for l in label._get_indirect_values_for_class(rdf_attribute):
        labels[l.lang] = str(l)
    # ?
    if not labels.items():
        for l in pot_label._get_indirect_values_for_class(rdf_attribute):
            if isinstance(l, locstr):
                labels[l.lang] = str(l)
    return labels


def build_comments(rdf_attribute: DataPropertyClass) -> dict:
    comments = {}
    for c in comment._get_indirect_values_for_class(rdf_attribute):
        comments[c.lang] = str(c)
    # ?
    if not comments.items():
        for c in pot_comment._get_indirect_values_for_class(rdf_attribute):
            if isinstance(c, locstr):
                comments[c.lang] = str(c)
    return comments


def build_ranges(prop: DataPropertyClass, range_types: AnnotationPropertyClass) -> list:
    result_ranges = []
    for range_type in range_types._get_indirect_values_for_class(prop):
        # TODO
        try:
            result_ranges.append(
                str(default_world._unabbreviate(base._universal_datatype_2_abbrev[range_type])).replace(
                    'http://www.w3.org/2001/XMLSchema#', 'xsd:'))
        except KeyError:
            result_ranges.append(str(range_type).replace('XMLSchema.', 'xsd:'))
    return result_ranges


def owl_property_to_python_base(rdf_attribute: DataPropertyClass) -> dict:
    _type = default_world._unabbreviate(rdf_attribute._owl_type).replace(
        'http://www.w3.org/2002/07/owl#', 'owl:')

    result = {
        '@id': f'pot:{prop_get_full_id(rdf_attribute)}',
        '@type': _type,
    }

    subproperties = list(
        subPropertyOf._get_indirect_values_for_class(rdf_attribute))
    if subproperties:
        result['subPropertyOf'] = f'pot:{prop_get_full_id(subproperties[0])}'

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


def owl_property_to_python_for_definition(rdf_attribute: DataPropertyClass) -> dict:
    result = owl_property_to_python_base(rdf_attribute)

    is_required = required._get_indirect_values_for_class(rdf_attribute)
    if is_required:
        result['pot:required'] = is_required[0]

    is_readonly = readonly._get_indirect_values_for_class(rdf_attribute)
    if is_readonly:
        result['pot:readonly'] = is_readonly[0]

    if list(range._get_indirect_values_for_class(rdf_attribute)):
        result['pot:valueType'] = build_ranges(rdf_attribute, range)

    if list(restriction._get_indirect_values_for_class(rdf_attribute)):
        result['xsd:restriction'] = build_ranges(rdf_attribute, restriction)

    return result


def owl_property_to_python_for_vocabulary(rdf_attribute: DataPropertyClass) -> dict:
    result = owl_property_to_python_base(rdf_attribute)

    if list(range._get_indirect_values_for_class(rdf_attribute)):
        result['pot:valueType'] = build_ranges(rdf_attribute, range)

    if list(restriction._get_indirect_values_for_class(rdf_attribute)):
        result['xsd:restriction'] = build_ranges(rdf_attribute, restriction)

    domains = []
    for d in domain._get_indirect_values_for_class(rdf_attribute):
        domains.append(f'pot:{d.name}')
    if domains:
        result['domain'] = domains

    return result
