from typing import Any, Dict, List
from owlready2 import default_world, base, locstr, label, comment

from class_helpers import restriction
from class_helpers import range as owl_range
from class_helpers import label as pot_label
from class_helpers import comment as pot_comment


# TODO. Hardcoded PREFIX required for entity files
PREFIX = 'pot'


def build_nested_labels(owl_property: Any) -> List[Dict[str, str]]:
    """Return list of dicts with nested labels.

        Args:
            owl_property (Any): 
                Property of entity.
                Can be:  AnnotationPropertyClass, DataPropertyClass, ObjectPropertyClass.

        Returns:
            labels (list of dict of str: str): List of dicts with nested labels
    """
    labels = []
    for l in owl_property.label:
        if l:
            # TODO
            list_of_dict_labels = []
            temp_labels_dict = {'rdfs:label': {}}
            for nested_label in label._get_indirect_values_for_class(l):
                list_of_dict_labels.append({nested_label.lang: nested_label})

            for label_dict in list_of_dict_labels:
                for item in label_dict.items():
                    temp_labels_dict['rdfs:label'][item[0]] = item[1]

            temp_labels_dict['domain'] = [
                f'{PREFIX}:{d.name}' for d in l.domain]

            labels.append(temp_labels_dict)
    return labels


def build_nested_comments(owl_property: Any) -> List[Dict[str, str]]:
    """Return list of dicts with nested comments.

        Args:
            owl_property (Any): 
                Property of entity.
                Can be:  AnnotationPropertyClass, DataPropertyClass, ObjectPropertyClass.

        Returns:
            comments (list of dict of str: str): List of dicts with nested comments
    """
    comments = []
    for c in owl_property.comment:
        if c:
            # TODO
            list_of_dict_comments = []
            temp_comments_dict = {'rdfs:comment': {}}
            for nested_comment in comment._get_indirect_values_for_class(c):
                list_of_dict_comments.append(
                    {nested_comment.lang: nested_comment})

            for comment_dict in list_of_dict_comments:
                for item in comment_dict.items():
                    temp_comments_dict['rdfs:comment'][item[0]] = item[1]

            temp_comments_dict['domain'] = [
                f'{PREFIX}:{d.name}' for d in c.domain]

            comments.append(temp_comments_dict)
    return comments


def build_labels(owl_property: Any) -> Dict[str, str]:
    """Return dict of labels.

        Args:
            owl_property (Any): 
                Property of entity.
                Can be:  AnnotationPropertyClass, DataPropertyClass, ObjectPropertyClass.

        Returns:
            labels (dict of str: str): Dict of labels
    """
    labels = {}
    for l in label._get_indirect_values_for_class(owl_property):
        labels[l.lang] = str(l)
    # ?
    if not labels.items():
        for l in pot_label._get_indirect_values_for_class(owl_property):
            if isinstance(l, locstr):
                labels[l.lang] = str(l)
    return labels


def build_comments(owl_property) -> dict:
    """Return dict of comments.

        Args:
            owl_property (Any): 
                Property of entity.
                Can be:  AnnotationPropertyClass, DataPropertyClass, ObjectPropertyClass.

        Returns:
            comments (list of dict of str: str): List of dicts with nested comments
    """
    comments = {}
    for c in comment._get_indirect_values_for_class(owl_property):
        comments[c.lang] = str(c)
    # ?
    if not comments.items():
        for c in pot_comment._get_indirect_values_for_class(owl_property):
            if isinstance(c, locstr):
                comments[c.lang] = str(c)
    return comments


def build_ranges(owl_property: Any) -> List[str]:
    """Return list of ranges.

        Args:
            owl_property (Any): 
                Property of entity.
                Can be:  AnnotationPropertyClass, DataPropertyClass.

        Returns:
            result_ranges (list of str): List of property ranges
    """
    result_ranges = []
    for range_type in owl_range._get_indirect_values_for_class(owl_property):
        # TODO
        try:
            result_ranges.append(
                str(default_world._unabbreviate(base._universal_datatype_2_abbrev[range_type])).replace(
                    'http://www.w3.org/2001/XMLSchema#', 'xsd:'))
        except KeyError:
            result_ranges.append(str(range_type).replace('XMLSchema.', 'xsd:'))
    return result_ranges


def build_restrictions(owl_property: Any) -> List[str]:
    """Return list of restrictions.

        Args:
            owl_property (Any): 
                Property of entity.
                Can be:  AnnotationPropertyClass, DataPropertyClass, ObjectPropertyClass.

        Returns:
            result_restrictions (list of str): List of property restrictions
    """
    result_restrictions = []
    for restriction_type in restriction._get_indirect_values_for_class(owl_property):
        # TODO
        try:
            result_restrictions.append(
                str(default_world._unabbreviate(base._universal_datatype_2_abbrev[restriction_type])).replace(
                    'http://www.w3.org/2001/XMLSchema#', 'xsd:'))
        except KeyError:
            result_restrictions.append(
                str(restriction_type).replace('XMLSchema.', 'xsd:'))
    return result_restrictions
