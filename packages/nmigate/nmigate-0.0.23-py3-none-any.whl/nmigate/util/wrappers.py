import functools
from urllib.parse import parse_qs, urlparse
from datetime import datetime
import xmltodict
from typing import Union, Dict, Any

def log(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        op_result = func(*args, **kwargs)
        return op_result

    return wrapper


def postProcessXml(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs) -> Dict[str, Any]:
        # Before
        op_result = func(*args, **kwargs)

        xml_string = op_result.text.replace(
            '<?xml version="1.0" encoding="UTF-8"?>', ""
        )
        # xml_string = op_result.text.replace('<?xml version="1.0" encoding="UTF-8"?>', '')
        # Define custom entities for é, ï, and ü characters
        entity_definitions = "<!DOCTYPE root [\n"
        entity_definitions += '<!ENTITY eacute "&#233;">\n'
        entity_definitions += '<!ENTITY iuml "&#239;">\n'
        entity_definitions += '<!ENTITY uuml "&#252;">\n'
        entity_definitions += '<!ENTITY rsquo "&#x2019;">\n'
        entity_definitions += "]>\n"
        # Parse XML string into an Element object
        response_dict = xmltodict.parse(entity_definitions + xml_string)
        return response_dict

    return wrapper


def postProcessingOutput(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs)  -> Dict[str, Union[str, Dict[str, str]]]:
        # Before
        nmi_operation = func(*args, **kwargs)

        # clean unwished logging data
        if "req" in nmi_operation and "security_key" in nmi_operation["req"]:
            nmi_operation["req"].pop("security_key")

        # pre process nmi_detail
        nmi_response = nmi_operation.pop("response")
        nmi_response_parsed_url = urlparse(nmi_response.text)
        nmi_response_cleared = parse_qs(nmi_response_parsed_url.path)

        # create new dictionary with all the data
        nmi_operation["nm_response"] = nmi_response_cleared
        nmi_operation["date"] = datetime.now()

        # Validate if nmi response is successful
        if nmi_response_cleared["response_code"][0] == "100":
            nmi_operation["successful"] = True
        else:
            nmi_operation["successful"] = False

        new_res = {}
        try:
            for key in nmi_operation["nm_response"]:
                new_res[key] = nmi_operation["nm_response"][key][0]
        except:
            pass
        nmi_operation["nm_response"] = new_res
        return nmi_operation

    return wrapper
