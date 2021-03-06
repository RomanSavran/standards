from typing import Any, Dict

from generators.commons.extended_properties import nest
from generators.commons.builders import prop_get_full_id, class_get_full_id, build_attributes


def create_context_from_data_product(rdf_class, entity_file: Dict[str, Any], onto, export_onto_url: str, PREFIX='pot', VERSION=1.1) -> Dict[str, Any]:
    """Return dict of generated properties to create Context from rdf classes.

        Args:
            rdf_class (models.RDFClass): RDFClass model object
            entity_file (dict of str: Any):
                Dictionary with directory, filename and id of entity
            onto (namespace.Ontology): An ontology loaded with owlready2.
            export_onto_url (str): Link to base ontologies.
            PREFIX (str, optional): Id prefix.
            VERSION (number, optional): Version number
        Returns:
            context_template (dict of str: Any): Dictionary of required parameters
    """
    corresponds = {
        "DataProductContext": "DataProductContext",
        "DataProductOutput": "DataProductOutput",
        "DataProductParameters": "DataProductParameters",
        "DataProductParameters": "DataProductParameters",
        "WeatherForecastDataProductContext": "Weather",
        "WeatherForecastDataProductOutput": "Weather",
        "WeatherForecastDataProductParameters": "Weather",
        "ForecastDataProductContext": "Forecast",
        "ForecastDataProductOutput": "Forecast",
        "ForecastDataProductParameters": "Forecast",
        "LtifDataProductContext": "Ltif",
        "LtifDataProductOutput": "Ltif",
        "LtifDataProductParameters": "Ltif",
        "SensorDataProductContext": "Sensor",
        "SensorDataProductOutput": "Sensor",
        "SensorDataProductParameters": "Sensor",
        "AccuWeatherForecastDataProductContext": "AccuWeather",
        "AccuWeatherForecastDataProductOutput": "AccuWeather",
        "AccuWeatherForecastDataProductParameters": "AccuWeather",
        "DocumentDataProductContext": "Document",
        "DocumentDataProductOutput": "Document",
        "DocumentDataProductParameters": "Document",
        "DocumentSigningDataProductContext": "Signing",
        "DocumentSigningDataProductOutput": "Signing",
        "DocumentSigningDataProductParameters": "Signing",
        "SignSpaceDataProductContext": "SignSpace",
        "SignSpaceDataProductOutput": "SignSpace",
        "SignSpaceDataProductParameters": "SignSpace",
        "PriceForecastDataProductContext": "Price",
        "PriceForecastDataProductOutput": "Price",
        "PriceForecastDataProductParameters": "Price",
        "ElectricityPriceForecastDataProductContext": "Electricity",
        "ElectricityPriceForecastDataProductOutput": "Electricity",
        "ElectricityPriceForecastDataProductParameters": "Electricity"
    }

    if entity_file.get('id') not in ('DataProductContext', 'DataProductOutput', 'DataProductParameters'):
        entity_name = entity_file.get('id').split('/')
        new_path = []
        for e in entity_name:
            new_path.append(corresponds[e])
        entity_file['dir'], entity_file['filename'], entity_file['id'] = '/'.join(new_path[:-1]), f'{new_path[-1]}.jsonld', '/'.join(new_path) 
        
    context_template = {
        '@version': VERSION,
        rdf_class.entity.name: {"@id": f'pot:{rdf_class.entity.name}'},
        '@schema': f"{export_onto_url}Schema/{entity_file.get('id')}",
        f'{PREFIX}': {
            '@id': f'{export_onto_url}Vocabulary/',
            '@prefix': True
        }
    }

    # Hard Code for now
    context_template["productCode"] = {"@id": "pot:productCode"}
    context_template["timestamp"] = {"@id": "pot:timestamp"}
    context_template["parameters"] = {"@id": "pot:parameters"}

    # Define and fill propeties for each supported attribute
    total_attributes = build_attributes(rdf_class, onto)
    for rdf_attribute in total_attributes:
        attribute_properties = dict()
        attribute_properties['@id'] = f'{PREFIX}:{str(rdf_attribute).split(".")[1]}'
        attribute_properties['@nest'] = "parameters"

        context_template[rdf_attribute.name] = attribute_properties

    for dependent in rdf_class.entity.subclasses():
        context_template[dependent.name] = {
            'rdfs:subClassOf': {
                '@id': f'{PREFIX}:{class_get_full_id(dependent).replace(f"/{dependent.name}", "")}'
            }
        }

    context_wrapper = {'@context': context_template}
    return context_wrapper
