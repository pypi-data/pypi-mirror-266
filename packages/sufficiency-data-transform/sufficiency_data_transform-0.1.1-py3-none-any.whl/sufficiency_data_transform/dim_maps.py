category_of_need = [
    {
        "CategoryOfNeedKey": -1,
        "CategoryOfNeedCode": -1,
        "CategoryOfNeedDescription": "(Unknown)",
    },
    {
        "CategoryOfNeedKey": 1,
        "CategoryOfNeedCode": "N1",
        "CategoryOfNeedDescription": "Abuse of neglect ",
    },
    {
        "CategoryOfNeedKey": 2,
        "CategoryOfNeedCode": "N2",
        "CategoryOfNeedDescription": "Child's disability",
    },
    {
        "CategoryOfNeedKey": 3,
        "CategoryOfNeedCode": "N3",
        "CategoryOfNeedDescription": "Parental illness or disability ",
    },
    {
        "CategoryOfNeedKey": 4,
        "CategoryOfNeedCode": "N4",
        "CategoryOfNeedDescription": "Family in acute stress ",
    },
    {
        "CategoryOfNeedKey": 5,
        "CategoryOfNeedCode": "N5",
        "CategoryOfNeedDescription": "Family dysfunction ",
    },
    {
        "CategoryOfNeedKey": 6,
        "CategoryOfNeedCode": "N6",
        "CategoryOfNeedDescription": "Socially unacceptable behaviour ",
    },
    {
        "CategoryOfNeedKey": 7,
        "CategoryOfNeedCode": "N7",
        "CategoryOfNeedDescription": "Low income ",
    },
    {
        "CategoryOfNeedKey": 8,
        "CategoryOfNeedCode": "N8",
        "CategoryOfNeedDescription": "Absent parenting ",
    },
]

legal_status = [
    {
        "LegalStatusKey": -1,
        "LegalStatusCode": -1,
        "LegalStatusDescription": "(Unknown)",
    },
    {
        "LegalStatusKey": 1,
        "LegalStatusCode": "C1",
        "LegalStatusDescription": "Interim care order ",
    },
    {
        "LegalStatusKey": 2,
        "LegalStatusCode": "C2",
        "LegalStatusDescription": "Full care order ",
    },
    {
        "LegalStatusKey": 3,
        "LegalStatusCode": "D1",
        "LegalStatusDescription": "Freeing order granted ",
    },
    {
        "LegalStatusKey": 4,
        "LegalStatusCode": "E1",
        "LegalStatusDescription": "Placement order granted ",
    },
    {
        "LegalStatusKey": 5,
        "LegalStatusCode": "J1",
        "LegalStatusDescription": "Remanded to local authority accommodation or to youth detention accommodation ",
    },
    {
        "LegalStatusKey": 6,
        "LegalStatusCode": "J2",
        "LegalStatusDescription": "Placed in local authority accommodation under the Police and Criminal Evidence Act 1984, including secure accommodation.  However, this would not necessarily be accommodation where the child would be detained. ",
    },
    {
        "LegalStatusKey": 7,
        "LegalStatusCode": "J3",
        "LegalStatusDescription": "Sentenced to Youth Rehabilitation Order (Criminal Justice and Immigration Act 2008 as amended by Legal Aid, Sentencing and Punishment of Offenders Act (LASPOA) 2012 with residence or intensive fostering requirement) ",
    },
    {
        "LegalStatusKey": 8,
        "LegalStatusCode": "L1",
        "LegalStatusDescription": "Under police protection and in local authority accommodation ",
    },
    {
        "LegalStatusKey": 9,
        "LegalStatusCode": "L2",
        "LegalStatusDescription": "Emergency protection order (EPO) ",
    },
    {
        "LegalStatusKey": 10,
        "LegalStatusCode": "L3",
        "LegalStatusDescription": "Under child assessment order and in local authority accommodation ",
    },
    {
        "LegalStatusKey": 11,
        "LegalStatusCode": "V2",
        "LegalStatusDescription": "Single period of accommodation under section 20 (Children Act 1989) ",
    },
    {
        "LegalStatusKey": 12,
        "LegalStatusCode": "V3",
        "LegalStatusDescription": "Accommodated under an agreed series of short-term breaks, when individual episodes of care are recorded ",
    },
    {
        "LegalStatusKey": 13,
        "LegalStatusCode": "V4",
        "LegalStatusDescription": "Accommodated under an agreed series of short-term breaks, when agreements are recorded (NOT individual episodes of care) ",
    },
]

ofsted_effectiveness = [
    {"OfstedEffectivenessKey": -1, "Grade": -1, "OverallEffectiveness": "Unknown"},
    {"OfstedEffectivenessKey": 1, "Grade": "4", "OverallEffectiveness": "Adequate"},
    {
        "OfstedEffectivenessKey": 2,
        "Grade": "-",
        "OverallEffectiveness": "Not provided as service is inspected as part of the ILACS inspection",
    },
    {
        "OfstedEffectivenessKey": 3,
        "Grade": "-",
        "OverallEffectiveness": "Not yet inspected",
    },
    {"OfstedEffectivenessKey": 4, "Grade": "1", "OverallEffectiveness": "Outstanding"},
    {"OfstedEffectivenessKey": 5, "Grade": "2", "OverallEffectiveness": "Good"},
    {
        "OfstedEffectivenessKey": 6,
        "Grade": "3",
        "OverallEffectiveness": "Requires improvement to be good",
    },
    {"OfstedEffectivenessKey": 7, "Grade": "5", "OverallEffectiveness": "Inadequate"},
]

placement_provider = [
    {
        "PlacementProviderKey": -1,
        "PlacementProviderCode": -1,
        "PlacementProviderDescription": "(Unknown)",
    },
    {
        "PlacementProviderKey": 1,
        "PlacementProviderCode": "PR0",
        "PlacementProviderDescription": "Parent(s) or other person(s) with parental responsibility ",
    },
    {
        "PlacementProviderKey": 2,
        "PlacementProviderCode": "PR1",
        "PlacementProviderDescription": "Own provision (by the local authority) including a regional adoption agency where the child's responsible local authority is the host authority ",
    },
    {
        "PlacementProviderKey": 3,
        "PlacementProviderCode": "PR2",
        "PlacementProviderDescription": "Other local authority provision, including a regional adoption agency where another local authority is the host authority ",
    },
    {
        "PlacementProviderKey": 4,
        "PlacementProviderCode": "PR3",
        "PlacementProviderDescription": "Other public provision (for example, a primary care trust) ",
    },
    {
        "PlacementProviderKey": 5,
        "PlacementProviderCode": "PR4",
        "PlacementProviderDescription": "Private provision ",
    },
    {
        "PlacementProviderKey": 6,
        "PlacementProviderCode": "PR5",
        "PlacementProviderDescription": "Voluntary/third sector provision ",
    },
]

placement_type = [
    {
        "PlacementTypeKey": -1,
        "PlacementTypeCode": -1,
        "PlacementTypeDescription": "(Unknown)",
    },
    {
        "PlacementTypeKey": 1,
        "PlacementTypeCode": "A3",
        "PlacementTypeDescription": "Placed for adoption with parental/guardian consent with current foster carer(s) (under Section 19 of the Adoption and Children Act 2002) or with a freeing order where parental/guardian consent has been given (under Section 18(1)(a) of the Adoption Act 1976) ",
    },
    {
        "PlacementTypeKey": 2,
        "PlacementTypeCode": "A4",
        "PlacementTypeDescription": "Placed for adoption with parental/guardian consent not with current foster carer(s) (under Section 19 of the Adoption and Children Act 2002) or with a freeing order where parental/guardian consent has been given under Section 18(1)(a) of the Adoption Act 1976 ",
    },
    {
        "PlacementTypeKey": 3,
        "PlacementTypeCode": "A5",
        "PlacementTypeDescription": "Placed for adoption with placement order with current foster carer(s) (under Section 21 of the Adoption and Children Act 2002) or with a freeing order where parental/guardian consent was dispensed with (under Section 18(1)(b) the Adoption Act 1976)",
    },
    {
        "PlacementTypeKey": 4,
        "PlacementTypeCode": "A6",
        "PlacementTypeDescription": "Placed for adoption with placement order not with current foster carer(s) (under Section 21 of the Adoption and Children Act 2002) or with a freeing order where parental/guardian consent was dispensed with (under Section 18(1)(b) of the Adoption Act 1976) ",
    },
    {
        "PlacementTypeKey": 5,
        "PlacementTypeCode": "H5",
        "PlacementTypeDescription": "Semi-independent living accommodation not subject to children's homes regulations ",
    },
    {
        "PlacementTypeKey": 6,
        "PlacementTypeCode": "K1",
        "PlacementTypeDescription": "Secure children's homes ",
    },
    {
        "PlacementTypeKey": 7,
        "PlacementTypeCode": "K2",
        "PlacementTypeDescription": "Children's Homes subject to Children's Homes Regulations ",
    },
    {
        "PlacementTypeKey": 8,
        "PlacementTypeCode": "P1",
        "PlacementTypeDescription": "Placed with own parent(s) or other person(s) with parental responsibility ",
    },
    {
        "PlacementTypeKey": 9,
        "PlacementTypeCode": "P2",
        "PlacementTypeDescription": "Independent living for example in a flat, lodgings, bedsit, bed and breakfast (B&B) or with friends, with or without formal support ",
    },
    {
        "PlacementTypeKey": 10,
        "PlacementTypeCode": "P3",
        "PlacementTypeDescription": "Residential employment ",
    },
    {
        "PlacementTypeKey": 11,
        "PlacementTypeCode": "R1",
        "PlacementTypeDescription": "Residential care home ",
    },
    {
        "PlacementTypeKey": 12,
        "PlacementTypeCode": "R2",
        "PlacementTypeDescription": "National Health Service (NHS)/health trust or other establishment providing medical or nursing care ",
    },
    {
        "PlacementTypeKey": 13,
        "PlacementTypeCode": "R3",
        "PlacementTypeDescription": "Family centre or mother and baby unit ",
    },
    {
        "PlacementTypeKey": 14,
        "PlacementTypeCode": "R5",
        "PlacementTypeDescription": "Young offender institution (YOI) ",
    },
    {
        "PlacementTypeKey": 15,
        "PlacementTypeCode": "S1",
        "PlacementTypeDescription": "All residential schools, except where dual-registered as a school and children's home ",
    },
    {
        "PlacementTypeKey": 16,
        "PlacementTypeCode": "T0",
        "PlacementTypeDescription": "All types of temporary move (see paragraphs above for further details) ",
    },
    {
        "PlacementTypeKey": 17,
        "PlacementTypeCode": "T1",
        "PlacementTypeDescription": "Temporary periods in hospital ",
    },
    {
        "PlacementTypeKey": 18,
        "PlacementTypeCode": "T2",
        "PlacementTypeDescription": "Temporary absences of the child on holiday ",
    },
    {
        "PlacementTypeKey": 19,
        "PlacementTypeCode": "T3",
        "PlacementTypeDescription": "Temporary accommodation whilst normal foster carer(s) is/are on holiday ",
    },
    {
        "PlacementTypeKey": 20,
        "PlacementTypeCode": "T4",
        "PlacementTypeDescription": "Temporary accommodation of seven days or less, for any reason, not covered by codes T1 to T3 ",
    },
    {
        "PlacementTypeKey": 21,
        "PlacementTypeCode": "U1",
        "PlacementTypeDescription": "Foster placement with relative(s) or friend(s) - long term fostering ",
    },
    {
        "PlacementTypeKey": 22,
        "PlacementTypeCode": "U2",
        "PlacementTypeDescription": "Fostering placement with relative(s) or friend(s) who is/are also an approved adopter(s) - fostering for adoption /concurrent planning ",
    },
    {
        "PlacementTypeKey": 23,
        "PlacementTypeCode": "U3",
        "PlacementTypeDescription": "Fostering placement with relative(s) or friend(s) who is/are not longterm or fostering for adoption /concurrent planning ",
    },
    {
        "PlacementTypeKey": 24,
        "PlacementTypeCode": "U4",
        "PlacementTypeDescription": "Foster placement with other foster carer(s) - long term fostering ",
    },
    {
        "PlacementTypeKey": 25,
        "PlacementTypeCode": "U5",
        "PlacementTypeDescription": "Foster placement with other foster carer(s) who is/are also an approved adopter(s) - fostering for adoption /concurrent planning ",
    },
    {
        "PlacementTypeKey": 26,
        "PlacementTypeCode": "U6",
        "PlacementTypeDescription": "Foster placement with other foster carer(s) - not long term or fostering for adoption /concurrent planning ",
    },
    {
        "PlacementTypeKey": 27,
        "PlacementTypeCode": "Z1",
        "PlacementTypeDescription": "Other placements (must be listed on a schedule sent to DfE with annual submission) ",
    },
]

reason_episode_ceased = [
    {
        "ReasonEpisodeCeasedKey": -1,
        "ReasonEpisodeCeasedCode": -1,
        "ReasonEpisodeCeasedDescription": "(Unknown)",
    },
    {
        "ReasonEpisodeCeasedKey": 1,
        "ReasonEpisodeCeasedCode": "E11",
        "ReasonEpisodeCeasedDescription": "Adopted - application for an adoption order unopposed   ",
    },
    {
        "ReasonEpisodeCeasedKey": 2,
        "ReasonEpisodeCeasedCode": "E12",
        "ReasonEpisodeCeasedDescription": "Adopted - consent dispensed with by the court ",
    },
    {
        "ReasonEpisodeCeasedKey": 3,
        "ReasonEpisodeCeasedCode": "E13",
        "ReasonEpisodeCeasedDescription": "Left care to live with parent(s), relative(s), or other person(s) with no parental responsibility. ",
    },
    {
        "ReasonEpisodeCeasedKey": 4,
        "ReasonEpisodeCeasedCode": "E14",
        "ReasonEpisodeCeasedDescription": "Accommodation on remand ended ",
    },
    {
        "ReasonEpisodeCeasedKey": 5,
        "ReasonEpisodeCeasedCode": "E15",
        "ReasonEpisodeCeasedDescription": "Age assessment determined child is aged 18 or over and E5, E6 and E7 do not apply, such as an unaccompanied asylum-seeking child (UASC) whose age has been disputed ",
    },
    {
        "ReasonEpisodeCeasedKey": 6,
        "ReasonEpisodeCeasedCode": "E16",
        "ReasonEpisodeCeasedDescription": "Child moved abroad ",
    },
    {
        "ReasonEpisodeCeasedKey": 7,
        "ReasonEpisodeCeasedCode": "E17",
        "ReasonEpisodeCeasedDescription": "Aged 18 (or over) and remained with current carers (inc under staying put arrangements) ",
    },
    {
        "ReasonEpisodeCeasedKey": 8,
        "ReasonEpisodeCeasedCode": "E2",
        "ReasonEpisodeCeasedDescription": "Died ",
    },
    {
        "ReasonEpisodeCeasedKey": 9,
        "ReasonEpisodeCeasedCode": "E3",
        "ReasonEpisodeCeasedDescription": "Care taken over by another local authority in the UK ",
    },
    {
        "ReasonEpisodeCeasedKey": 10,
        "ReasonEpisodeCeasedCode": "E41",
        "ReasonEpisodeCeasedDescription": "Residence order (or, from 22 April 2014, a child arrangement order which sets out with whom the child is to live) granted ",
    },
    {
        "ReasonEpisodeCeasedKey": 11,
        "ReasonEpisodeCeasedCode": "E45",
        "ReasonEpisodeCeasedDescription": "Special guardianship order made to former foster carer(s), who was/are a relative(s) or friend(s) ",
    },
    {
        "ReasonEpisodeCeasedKey": 12,
        "ReasonEpisodeCeasedCode": "E46",
        "ReasonEpisodeCeasedDescription": "Special guardianship order made to former foster carer(s), other than relative(s) or friend(s) ",
    },
    {
        "ReasonEpisodeCeasedKey": 13,
        "ReasonEpisodeCeasedCode": "E47",
        "ReasonEpisodeCeasedDescription": "Special guardianship order made to carer(s), other than former foster carer(s), who was/are a relative(s) or friend(s) ",
    },
    {
        "ReasonEpisodeCeasedKey": 14,
        "ReasonEpisodeCeasedCode": "E48",
        "ReasonEpisodeCeasedDescription": "Special guardianship order made to carer(s), other than former foster carer(s), other than relative(s) or friend(s) ",
    },
    {
        "ReasonEpisodeCeasedKey": 15,
        "ReasonEpisodeCeasedCode": "E4A",
        "ReasonEpisodeCeasedDescription": "Returned home to live with parent(s), relative(s), or other person(s) with parental responsibility as part of the care planning process (not under a special guardianship order or residence order or (from 22 April 2014) a child arrangement order). ",
    },
    {
        "ReasonEpisodeCeasedKey": 16,
        "ReasonEpisodeCeasedCode": "E4B",
        "ReasonEpisodeCeasedDescription": "Returned home to live with parent(s), relative(s), or other person(s) with parental responsibility which was not part of the current care planning process (not under a special guardianship order or residence order or (from 22 April 2014) a child arrangement order). ",
    },
    {
        "ReasonEpisodeCeasedKey": 17,
        "ReasonEpisodeCeasedCode": "E5",
        "ReasonEpisodeCeasedDescription": "Moved into independent living arrangement and no longer looked-after: supportive accommodation providing formalised advice/support arrangements (such as most hostels, young men's Christian association, foyers, staying close and care leavers projects). Includes both children leaving care before and at age 18 ",
    },
    {
        "ReasonEpisodeCeasedKey": 18,
        "ReasonEpisodeCeasedCode": "E6",
        "ReasonEpisodeCeasedDescription": "Moved into independent living arrangement and no longer looked-after : accommodation providing no formalised advice/support arrangements (such as bedsit, own flat, living with friend(s)). Includes both children leaving care before and at age 18 ",
    },
    {
        "ReasonEpisodeCeasedKey": 19,
        "ReasonEpisodeCeasedCode": "E7",
        "ReasonEpisodeCeasedDescription": "Transferred to residential care funded by adult social care services ",
    },
    {
        "ReasonEpisodeCeasedKey": 20,
        "ReasonEpisodeCeasedCode": "E8",
        "ReasonEpisodeCeasedDescription": "Period of being looked-after ceased for any other reason (where none of the other reasons apply) ",
    },
    {
        "ReasonEpisodeCeasedKey": 21,
        "ReasonEpisodeCeasedCode": "E9",
        "ReasonEpisodeCeasedDescription": "Sentenced to custody ",
    },
    {
        "ReasonEpisodeCeasedKey": 22,
        "ReasonEpisodeCeasedCode": "X1",
        "ReasonEpisodeCeasedDescription": "Episode ceases, and new episode begins on same day, for any reason ",
    },
]

reason_for_new_episode = [
    {
        "ReasonForNewEpisodeKey": -1,
        "ReasonForNewEpisodeCode": -1,
        "ReasonForNewEpisodeDescription": "(Unknown)",
    },
    {
        "ReasonForNewEpisodeKey": 1,
        "ReasonForNewEpisodeCode": "B",
        "ReasonForNewEpisodeDescription": "Change of legal status and placement and carer(s) at the same time",
    },
    {
        "ReasonForNewEpisodeKey": 2,
        "ReasonForNewEpisodeCode": "L",
        "ReasonForNewEpisodeDescription": "Change of legal status only",
    },
    {
        "ReasonForNewEpisodeKey": 3,
        "ReasonForNewEpisodeCode": "P",
        "ReasonForNewEpisodeDescription": "Change of placement and carer(s) only",
    },
    {
        "ReasonForNewEpisodeKey": 4,
        "ReasonForNewEpisodeCode": "S",
        "ReasonForNewEpisodeDescription": "Started to be looked-after",
    },
    {
        "ReasonForNewEpisodeKey": 5,
        "ReasonForNewEpisodeCode": "T",
        "ReasonForNewEpisodeDescription": "Change of placement (but same carer(s)) only",
    },
    {
        "ReasonForNewEpisodeKey": 6,
        "ReasonForNewEpisodeCode": "U",
        "ReasonForNewEpisodeDescription": "Change of legal status and change of placement (but same carer(s)) at the same time",
    },
]

reason_place_change = [
    {
        "ReasonPlaceChangeKey": -1,
        "ReasonPlaceChangeCode": -1,
        "ReasonPlaceChangeDescription": "(Unknown)",
    },
    {
        "ReasonPlaceChangeKey": 1,
        "ReasonPlaceChangeCode": "ALLEG",
        "ReasonPlaceChangeDescription": "Allegation (s47) ",
    },
    {
        "ReasonPlaceChangeKey": 2,
        "ReasonPlaceChangeCode": "APPRR",
        "ReasonPlaceChangeDescription": "Approval removed ",
    },
    {
        "ReasonPlaceChangeKey": 3,
        "ReasonPlaceChangeCode": "CARPL",
        "ReasonPlaceChangeDescription": "Change to/Implementation of Care Plan ",
    },
    {
        "ReasonPlaceChangeKey": 4,
        "ReasonPlaceChangeCode": "CHILD",
        "ReasonPlaceChangeDescription": "Child requests placement end ",
    },
    {
        "ReasonPlaceChangeKey": 5,
        "ReasonPlaceChangeCode": "CLOSE",
        "ReasonPlaceChangeDescription": "Resignation/ closure of provision ",
    },
    {
        "ReasonPlaceChangeKey": 6,
        "ReasonPlaceChangeCode": "CREQB",
        "ReasonPlaceChangeDescription": "Carer(s) requests placement end due to child's behaviour ",
    },
    {
        "ReasonPlaceChangeKey": 7,
        "ReasonPlaceChangeCode": "CREQO",
        "ReasonPlaceChangeDescription": "Carer(s) requests placement end other than due to child's behaviour ",
    },
    {
        "ReasonPlaceChangeKey": 8,
        "ReasonPlaceChangeCode": "CUSTOD",
        "ReasonPlaceChangeDescription": "Custody arrangement ",
    },
    {
        "ReasonPlaceChangeKey": 9,
        "ReasonPlaceChangeCode": "LAREQ",
        "ReasonPlaceChangeDescription": "Responsible/area authority requests placement end ",
    },
    {
        "ReasonPlaceChangeKey": 10,
        "ReasonPlaceChangeCode": "OTHER",
        "ReasonPlaceChangeDescription": "Other ",
    },
    {
        "ReasonPlaceChangeKey": 11,
        "ReasonPlaceChangeCode": "PLACE",
        "ReasonPlaceChangeDescription": "Change in the status of placement only ",
    },
    {
        "ReasonPlaceChangeKey": 12,
        "ReasonPlaceChangeCode": "STAND",
        "ReasonPlaceChangeDescription": "Standards of care concern ",
    },
]
