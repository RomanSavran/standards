VERSION = 1.1
EXPORT_URL = 'https://standards.oftrust.net/v1/'


def BASE_IDENTITY_TEMPLATE(pot_export_url: str) -> dict:
    return {
        '@version': VERSION,
        '@vocab': f"{pot_export_url}vocabularies/.jsonld#",
        '@classDefinition': '',
        "pot": {
            "@id": f"{pot_export_url}Vocabulary/",
            "@prefix": True
        },
        "data": "pot:data",
        "metadata": "pot:metadata",
    }


def DEFENITION_TEMPLATE(pot_export_url: str) -> dict:
    return {
        "@context": {
            "@version": VERSION,
            "xsd": {
                "@id": "http://www.w3.org/2001/XMLSchema#",
                "@prefix": True
            },
            "pot": {
                "@id": f"{pot_export_url}Vocabulary/",
                "@prefix": True
            },
            "description": {},
            "label": {
                '@id': 'rdfs:label',
                "@container": ['@language', '@set']
            },
            "comment": {
                '@id': 'rdfs:comment',
                "@container": ['@language', '@set']
            }
        },
    }


def VOCABULARY_TEMPLATE(pot_export_url:str) -> dict:
    return {
        "@context": {
            '@version': VERSION,
            "pot": {
                "@id": f"{pot_export_url}Vocabulary/",
                "@prefix": True
            },
            "rdf": {
                "@id": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
                "@prefix": True
            },
            "rdfs": {
                "@id": "http://www.w3.org/2000/01/rdf-schema#",
                "@prefix": True
            },
            "owl": {
                "@id": "http://www.w3.org/2002/07/owl#",
                "@prefix": True
            },
            "vs": {
                "@id": "http://www.w3.org/2003/06/sw-vocab-status/ns#",
            },
            "xsd": {
                "@id": "http://www.w3.org/2001/XMLSchema#",
                "@prefix": True
            },
            "label": "",
            "comment": ""
        }
    }
