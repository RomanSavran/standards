from owlready2 import default_world, base, locstr, label, comment
from owlready2 import DataPropertyClass, ObjectPropertyClass, AnnotationPropertyClass

from class_helpers import label as pot_label
from class_helpers import comment as pot_comment

PREFIX = 'pot'


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

            temp_labels_dict['domain'] = [
                f'{PREFIX}:{d.name}' for d in c.domain]

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

            temp_comments_dict['domain'] = [f'{PREFIX}:{d.name}' for d in c.domain]

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
