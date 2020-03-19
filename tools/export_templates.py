VERSION = 1.1
EXPORT_URL = 'https://standards.oftrust.net/v1/'
PREFIX = 'pot'


def BASE_IDENTITY_TEMPLATE(export_onto_url: str) -> dict:
    return {
        '@version': VERSION,
        '@vocab': f'{export_onto_url}vocabularies/.jsonld#',
        '@classDefinition': '',
        f'{PREFIX}': {
            '@id': f'{export_onto_url}Vocabulary/',
            '@prefix': True
        },
        'data': f'{PREFIX}:data',
        'metadata': f'{PREFIX}:metadata',
    }


def DEFENITION_TEMPLATE(export_onto_url: str) -> dict:
    return {
        '@context': {
            '@version': VERSION,
            'xsd': {
                '@id': 'http://www.w3.org/2001/XMLSchema#',
                '@prefix': True
            },
            f'{PREFIX}': {
                '@id': f'{export_onto_url}Vocabulary/',
                '@prefix': True
            },
            'description': {},
            'label': {
                '@id': 'rdfs:label',
                '@container': ['@language', '@set']
            },
            'comment': {
                '@id': 'rdfs:comment',
                '@container': ['@language', '@set']
            }
        },
    }


def VOCABULARY_TEMPLATE(export_onto_url: str) -> dict:
    return {
        '@context': {
            '@version': VERSION,
            f'{PREFIX}': {
                '@id': f'{export_onto_url}Vocabulary/',
                '@prefix': True
            },
            'rdf': {
                '@id': 'http://www.w3.org/1999/02/22-rdf-syntax-ns#',
                '@prefix': True
            },
            'rdfs': {
                '@id': 'http://www.w3.org/2000/01/rdf-schema#',
                '@prefix': True
            },
            'owl': {
                '@id': 'http://www.w3.org/2002/07/owl#',
                '@prefix': True
            },
            'vs': {
                '@id': 'http://www.w3.org/2003/06/sw-vocab-status/ns#',
            },
            'xsd': {
                '@id': 'http://www.w3.org/2001/XMLSchema#',
                '@prefix': True
            },
            'label': '',
            'comment': ''
        }
    }
