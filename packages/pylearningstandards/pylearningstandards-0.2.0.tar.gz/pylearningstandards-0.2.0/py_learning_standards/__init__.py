#
# This software is Copyright ©️ 2020 The University of Southern California. All Rights Reserved.
# Permission to use, copy, modify, and distribute this software and its documentation for educational, research and non-profit purposes, without fee, and without a written agreement is hereby granted, provided that the above copyright notice and subject to the full license file found in the root of this software deliverable. Permission to make commercial use of this software may be obtained by contacting:  USC Stevens Center for Innovation University of Southern California 1150 S. Olive Street, Suite 2300, Los Angeles, CA 90115, USA Email: accounting@stevens.usc.edu
#
# The full terms of this copyright and license should always be found in the root directory of this software deliverable as "license.txt" and if these terms are not found with this software, please contact the USC Stevens Center for the full license.
#
from dataclasses import dataclass
from dataclass_wizard import JSONWizard, json_field
from typing import Dict, Any, Optional, List, cast

NAMESPACE_ASN = "asn"
NAMESPACE_CETERMS = "ceterms"
NAMESPACE_CEASN = "ceasn"
NAMESPACE_DCT = "dct"
NAMESPACE_IFLA = "ifla"
NAMESPACE_LMT = "lmt"
NAMESPACE_LRMI = "lrmi"
NAMESPACE_RDFS = "rdfs"
NAMESPACE_SCD = "scd"
NAMESPACE_SDO = "sdo"
NAMESPACE_SKOS = "skos"


def to_list_no_nones(list: List[Any]) -> List[Any]:
    result = []
    for item in list:
        if isinstance(item, Dict):
            result.append(to_dict_no_nones(item))
        elif isinstance(item, List):
            result.append(cast(Any, to_list_no_nones(item)))
        else:
            result.append(item)
    return result


def to_dict_no_nones(dictionary: Dict) -> Dict[str, Any]:
    result = {}

    for key in dictionary.keys():
        if dictionary[key] is not None:
            if isinstance(dictionary[key], Dict):
                result[key] = to_dict_no_nones(dictionary[key])
            if isinstance(dictionary[key], List):
                result[key] = cast(Any, to_list_no_nones(dictionary[key]))
            else:
                result[key] = dictionary[key]
    return result


@dataclass
class BaseJSONLDObject(JSONWizard):

    id: Optional[str] = json_field("id", all=True, default=None)
    type: Optional[str] = json_field("@type", all=True, default=None)

    def to_dict_no_nones(self) -> Dict[str, Any]:
        return to_dict_no_nones(self.to_dict())


def create_en_us_lang_string(raw_string: str) -> Dict[str, str]:
    return {"en_us": raw_string}


@dataclass
class Competency(BaseJSONLDObject):

    ctid: Optional[str] = json_field(f"{NAMESPACE_CEASN}:ctid", all=True, default=None)
    competency_text: Optional[Dict[str, str]] = json_field(
        f"{NAMESPACE_CEASN}:competencyText", all=True, default=None
    )
    relevance: Optional[float] = json_field("relevance", all=True, default=None)


@dataclass
class LearningResource(BaseJSONLDObject):

    assesses: Optional[List[Competency]] = json_field(
        f"{NAMESPACE_LRMI}:assesses", all=True, default=None
    )
    teaches: Optional[List[Competency]] = json_field(
        f"{NAMESPACE_LRMI}:teaches", all=True, default=None
    )
    title: Optional[str] = json_field(f"{NAMESPACE_DCT}:title", all=True, default=None)
    description: Optional[str] = json_field(
        f"{NAMESPACE_DCT}:description", all=True, default=None
    )
    duration: Optional[str] = json_field(
        f"{NAMESPACE_SDO}:duration", all=True, default=None
    )
    complexity: Optional[float] = json_field("complexity", all=True, default=None)
