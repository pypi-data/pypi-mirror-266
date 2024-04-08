from typing import TypedDict, cast


class SpecimenDetails(TypedDict, total=False):
    """A partial representation of the specimen details in the Caris JSON file"""

    specimenReceivedDate: str
    specimenCollectionDate: str
    specimenSite: str


class ParsedSpecimenDetails(TypedDict):
    bodySite: str
    receivedDate: str
    collDate: str


def parse_specimen_details(specimen_details: SpecimenDetails) -> ParsedSpecimenDetails:
    return {
        "bodySite": specimen_details.get("specimenSite", ""),
        "receivedDate": specimen_details.get("specimenReceivedDate", ""),
        "collDate": specimen_details.get("specimenCollectionDate", ""),
    }


def ensure_single_specimen_details(
    specimen_details: SpecimenDetails | list[SpecimenDetails],
) -> SpecimenDetails:
    if isinstance(specimen_details, dict):
        return specimen_details

    # Sometimes, we have multiple specimen details
    # In this case, we expect but also assert that they are all the same
    sites = {specimen["specimenSite"] for specimen in specimen_details}

    if len(sites) > 1:
        raise ValueError(f"Multiple specimen sites found")

    return specimen_details[0]


def extract_and_parse_specimen_details(data: dict) -> ParsedSpecimenDetails:
    specimen_information = data["specimenInformation"]
    specimen_details: SpecimenDetails | list[SpecimenDetails] | None = None

    # The key for the specimen details varies based on the test type
    potential_keys = [
        # Tissue case
        "tumorSpecimenInformation",
        # Liquid case
        "liquidBiopsySpecimenInformation",
    ]
    for key in potential_keys:
        if key in specimen_information:
            specimen_details = cast(
                SpecimenDetails | list[SpecimenDetails], specimen_information[key]
            )
            break

    if not specimen_details:
        raise ValueError("No specimen details found in data")

    specimen_details = ensure_single_specimen_details(specimen_details)

    return parse_specimen_details(specimen_details)
