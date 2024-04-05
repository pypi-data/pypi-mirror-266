ethnic_description_map = {
    "WBRI": "White British",
    "WIRI": "White Irish",
    "WOTH": "Any other White background",
    "WIRT": "Traveller of Irish Heritage",
    "GROM": "Gypsy/Roma",
    "MWBC": "White and Black Caribbean",
    "MWBA": "White and Black African",
    "MWAS": "White and Asian",
    "MOTH": "Any other Mixed background",
    "AIND": "Indian",
    "APKN": "Pakistani",
    "ABAN": "Bangladeshi",
    "CHNE": "Chinese",
    "AOTH": "Any other Asian background",
    "BCRB": "Caribbean",
    "BAFR": "African",
    "BOTH": "Any other Black background",
    "OOTH": "Any other ethnic group",
    "REFU": "Refused",
    "NOBT": "Information not yet obtained",
    "UNKNOWN": "Unknown",
}

uasc_status_map = {
    0: "Child was not an unaccompanied asylum-seeking child (UASC) at any time during the year",
    1: "Child was an unaccompanied asylum-seeking child (UASC) during the year",
    "UNKNOWN": "Unknown",
}

category_of_need_map = {
    "N1": "Abuse of neglect",
    "N2": "Child's disability",
    "N3": "Parental illness or disability",
    "N4": "Family in acute stress",
    "N5": "Family dysfunction",
    "N6": "Socially unacceptable behaviour",
    "N7": "Low income",
    "N8": "Absent parenting",
}
postcodes_map = {
    "pcd2": "Sector",
    "oslaua": "ONSAreaCode",
    "lsoa11": "LSOA2011",
    "lat": "Latitude",
    "long": "Longitude",
    "oseast1m": "OSEastings",
    "osnrth1m": "OSNorthings",
    "imd": "IMD",
}

gender_map = {
    1.0: "Male",
    1: "Male",
    2.0: "Female",
    2: "Female",
}

ons_map = {
    "_WD21CD": "WardCode",
    "WD21NM": "WardName",
    "LAD21CD": "LACode",
    "LAD21NM": "LAName",
    "CTY21CD": "CountyCode",
    "CTY21NM": "CountyName",
    "RGN21CD": "RegionCode",
    "RGN21NM": "RegionName",
    "CTRY21CD": "CountryCode",
    "CTRY21NM": "CountryName",
}

dimLookedAfterChild_columns_map = {
    "CHILD": "ChildIdentifier",
    "SEX": "Gender",
    "DOB": "DateOfBirthKey",
    "ETHNIC": "EthnicCode",
    "DUC": "UASCCeasedDateKey",
    "YEAR": "SubmissionYearDateKey",
}

uasc_status_map = {
    0: "Child was not an unaccompanied asylum-seeking child (UASC) at any time during the year",
    1: "Child was an unaccompanied asylum-seeking child (UASC) during the year",
    "UNKNOWN": "Unknown",
}

ofsted_provider_map = {
    "Provision type": "ProviderType",
    "Registration date": "RegistrationDate",
    "Registration status": "ProviderStatus",
    "Date closed": "ClosedDate",
    "Places": "MaxUsers",
    "Organisation name": "OwnerName",
}

ofsted_to_ons_map = {
    "Westmorland and Furness": "Westmoreland",
    "Bristol": "Bristol, City of",
    "Bournemouth, Christchurch & Poole": "Bournemouth, Christchurch and Poole",
    "Durham": "County Durham",
    "Cumberland": "Carlisle",
    "Herefordshire": "Herefordshire, County of",
    "Kingston upon Hull": "Kingston upon Hull, City of",
    "Southend on Sea": "Southend-on-Sea",
}

episodes_map = {
    "DECOM": "EpisodeCommencedDateKey",
    "DEC": "EpisodeCeasedDateKey",
    "YEAR": "SubmissionYearDateKey",
}

inspection_map = {
    "Inspection date": "InspectionDateKey",
    "Inspection publication date": "EndDateKey",  # change
    "Organisation which owns the provider": "OwnerName",  # to get OfstedProviderKey
    "Overall experiences and progress of children and young people": "Effectiveness",  # to get OfstedEffectivenessKey
}
