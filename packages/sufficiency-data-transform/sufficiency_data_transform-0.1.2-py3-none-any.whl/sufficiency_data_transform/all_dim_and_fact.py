import pandas as pd
from decouple import config
from sufficiency_data_transform.dim_maps import (
    category_of_need,
    legal_status,
    ofsted_effectiveness,
    placement_provider,
    placement_type,
    reason_episode_ceased,
    reason_for_new_episode,
    reason_place_change,
)
from sufficiency_data_transform.maps import (
    ons_map,
    dimLookedAfterChild_columns_map,
    gender_map,
    ethnic_description_map,
    uasc_status_map,
    ofsted_provider_map,
    ofsted_to_ons_map,
    postcodes_map,
    episodes_map,
    inspection_map,
)
from sufficiency_data_transform.utils import (
    generate_dim,
    add_nan_row,
    fillna_date_columns,
    fillna_categorical_columns,
    check_encoding,
    open_file,
    open_location,
    write_csv,
)

output_location = config("OUTPUT_LOCATION")
input_location_ext = config("INPUT_LOCATION_EXT")
input_location_903 = config("INPUT_LOCATION_903")


def create_dim_tables():
    """Create lookup tables"""
    fs_out = open_location(output_location)
    generate_dim(category_of_need, "dimCategoryOfNeed.csv", fs_out)
    generate_dim(legal_status, "dimLegalStatus.csv", fs_out)
    generate_dim(ofsted_effectiveness, "dimOfstedEffectiveness.csv", fs_out)
    generate_dim(placement_provider, "dimPlacementProvider.csv", fs_out)
    generate_dim(placement_type, "dimPlacementType.csv", fs_out)
    generate_dim(reason_episode_ceased, "dimReasonEpisodeCeased.csv", fs_out)
    generate_dim(reason_for_new_episode, "dimReasonForNewEpisode.csv", fs_out)
    generate_dim(reason_place_change, "dimReasonPlaceChange.csv", fs_out)


def create_dimONSArea():
    fs_ext = open_location(input_location_ext)
    fs_out = open_location(output_location)

    ons_area = open_file(fs_ext, "ONS Area//ONS Area.csv")

    ons_area.rename(columns=ons_map, inplace=True)

    ons_area.drop(columns=["OBJECTID"], inplace=True)
    # area code should be unknown only if all the possible codes are unknown
    ward_df = ons_area
    ward_df["AreaType"] = "Ward"
    ward_df["AreaCode"] = ward_df["WardCode"]
    ward_df["AreaName"] = ward_df["WardName"]

    la_df = ons_area[
        [
            "LACode",
            "LAName",
            "CountyCode",
            "CountyName",
            "RegionCode",
            "RegionName",
            "CountryCode",
            "CountryName",
        ]
    ]
    la_df["AreaType"] = "LA"
    la_df.loc[~la_df["LACode"].isna(), "AreaCode"] = la_df["LACode"]
    la_df.loc[~la_df["LAName"].isna(), "AreaName"] = la_df["LAName"]

    county_df = ons_area[
        [
            "CountyCode",
            "CountyName",
            "RegionCode",
            "RegionName",
            "CountryCode",
            "CountryName",
        ]
    ]
    county_df["AreaType"] = "County"
    county_df.loc[~county_df["CountyCode"].isna(), "AreaCode"] = county_df["CountyCode"]
    county_df.loc[~county_df["CountyName"].isna(), "AreaName"] = county_df["CountyName"]

    region_df = ons_area[["RegionCode", "RegionName", "CountryCode", "CountryName"]]
    region_df["AreaType"] = "Region"
    region_df.loc[~region_df["RegionCode"].isna(), "AreaCode"] = region_df["RegionCode"]
    region_df.loc[~region_df["RegionName"].isna(), "AreaName"] = region_df["RegionName"]

    country_df = ons_area[["CountryCode", "CountryName"]]
    country_df["AreaType"] = "Country"
    country_df.loc[~country_df["CountryCode"].isna(), "AreaCode"] = country_df[
        "CountryCode"
    ]
    country_df.loc[~country_df["CountryName"].isna(), "AreaName"] = country_df[
        "CountryName"
    ]

    dimONSArea = pd.concat(
        [ward_df, la_df, county_df, region_df, country_df]
    ).drop_duplicates()

    dimONSArea.reset_index(drop=True)
    dimONSArea.reset_index(inplace=True, names="ONSAreaKey")

    # add a row that simulates the scenario where all values are nan
    dimONSArea = add_nan_row(dimONSArea, "ONSAreaKey")

    write_csv(dimONSArea, fs_out, "dimONSArea.csv", False)


def create_dimLookedAfterChild():
    fs_903 = open_location(input_location_903)
    fs_out = open_location(output_location)
    header = open_file(fs_903, "pan_London_SSDA903_Header.csv")
    uasc = open_file(fs_903, "pan_London_SSDA903_UASC.csv")

    ons_area = open_file(fs_out, "dimONSArea.csv")

    ons_area = ons_area[["ONSAreaKey", "AreaName"]]

    dimLookedAfterChild = header.merge(
        uasc, on=["CHILD", "SEX", "DOB", "LA", "YEAR"], how="left"
    )

    dimLookedAfterChild.rename(columns=dimLookedAfterChild_columns_map, inplace=True)
    dimLookedAfterChild["Gender"] = (
        dimLookedAfterChild["Gender"].map(gender_map).fillna("Not Specified")
    )
    dimLookedAfterChild["EthnicDescription"] = dimLookedAfterChild.EthnicCode.map(
        ethnic_description_map
    )

    dimLookedAfterChild["UASCStatusCode"] = dimLookedAfterChild.UASCCeasedDateKey.map(
        lambda x: 0 if pd.isnull(x) else 1
    )
    dimLookedAfterChild["UASCStatusDescription"] = (
        dimLookedAfterChild.UASCStatusCode.map(uasc_status_map)
    )

    dimLookedAfterChild = dimLookedAfterChild.merge(
        ons_area, left_on="LA", right_on="AreaName", how="left"
    )
    dimLookedAfterChild.rename(columns={"ONSAreaKey": "ONSAreaCode"}, inplace=True)
    # remove name columns since they are not present in output
    dimLookedAfterChild.drop(columns=["AreaName", "LA"], inplace=True)

    date_cols = [
        "DateOfBirthKey",
        "UASCCeasedDateKey",
    ]  # these are used to generate other columns above so should only be changed here at the end.
    dimLookedAfterChild = fillna_date_columns(dimLookedAfterChild, date_cols)

    dimLookedAfterChild["Gender"] = dimLookedAfterChild["Gender"].fillna(
        "Not Specified"
    )
    dimLookedAfterChild["EthnicCode"] = dimLookedAfterChild["EthnicCode"].fillna(
        "UNKNOWN"
    )
    dimLookedAfterChild["ChildIdentifier"] = dimLookedAfterChild[
        "ChildIdentifier"
    ].fillna("UNKNOWN CHILD")

    categorical_cols = [
        "SubmissionYearDateKey",
        "EthnicDescription",
        "UASCStatusCode",
        "UASCStatusDescription",
        "ONSAreaCode",
    ]  # replace nans in ons area code
    dimLookedAfterChild = fillna_categorical_columns(
        dimLookedAfterChild, categorical_cols
    )

    dimLookedAfterChild.reset_index(inplace=True, drop=True)
    dimLookedAfterChild.reset_index(inplace=True, names="LookedAfterChildKey")

    write_csv(dimLookedAfterChild, fs_out, "dimLookedAfterChild.csv", False)


def create_dimOfstedProvider():
    fs_ext = open_location(input_location_ext)
    fs_out = open_location(output_location)

    providers_places_31Aug = open_file(
        fs_ext, "Ofsted data//Providers+places_at_31_Aug_2023.csv"
    )
    closed_children_homes = open_file(
        fs_ext, "Ofsted data//Closed_childrens_homes_31Mar23.csv"
    )
    ons_area = open_file(fs_out, "dimONSArea.csv")

    ons_area = ons_area[["ONSAreaKey", "AreaName"]]

    dimOfstedProvider = providers_places_31Aug.merge(
        closed_children_homes, on=["URN", "Registration status"], how="outer"
    )
    dimOfstedProvider = dimOfstedProvider.drop_duplicates(subset="URN", keep="last")

    dimOfstedProvider = dimOfstedProvider.rename(columns=ofsted_provider_map)
    dimOfstedProvider = dimOfstedProvider[
        [
            "URN",
            "ProviderType",
            "Sector",
            "RegistrationDate",
            "ProviderStatus",
            "ClosedDate",
            "MaxUsers",
            "OwnerName",
            "Local authority",
        ]
    ]

    # these come in the data and do not have to be created
    unknown_markers = ["NOTREC", "XXXXXXX", "UNKNOWN"]
    dimOfstedProvider.loc[
        dimOfstedProvider["URN"].isin(unknown_markers), "UnknownSourceFlag"
    ] = "TRUE"
    dimOfstedProvider["UnknownSourceFlag"].fillna("FALSE", inplace=True)
    dimOfstedProvider[dimOfstedProvider["UnknownSourceFlag"] == "TRUE"]

    dimOfstedProvider["Local Authority"] = dimOfstedProvider["Local authority"].replace(
        ofsted_to_ons_map
    )

    dimOfstedProvider = dimOfstedProvider.merge(
        ons_area, left_on="Local Authority", right_on="AreaName", how="left"
    )
    dimOfstedProvider = dimOfstedProvider.drop(columns=["Local Authority", "AreaName"])
    dimOfstedProvider = dimOfstedProvider.rename(columns={"ONSAreaKey": "ONSAreaCode"})

    # Create OfstedProviderKey
    dimOfstedProvider.reset_index(drop=True, inplace=True)
    dimOfstedProvider.reset_index(inplace=True, names="OfstedProviderKey")
    # ["URN"] == "UNKNOWN" etc can only exist in the fact table, not the dimension table.

    # return key -3 if fact table sends a nan
    nan_col = {col: pd.NA for col in dimOfstedProvider.columns}
    nan_col["OfstedProviderKey"] = -3
    dimOfstedProvider.loc[len(dimOfstedProvider)] = nan_col

    # URNs that found no match in this table will return nans be given key -1 in the source table.

    # return key -2 when incoming URN is XXXXXXX in docs.
    nan_col = {col: pd.NA for col in dimOfstedProvider.columns}
    nan_col["URN"] = "XXXXXXX"
    nan_col["OfstedProviderKey"] = -2
    dimOfstedProvider.loc[len(dimOfstedProvider)] = nan_col

    # replace nans
    categorical_columns = [
        "ProviderType",
        "Sector",
        "ProviderStatus",
        "MaxUsers",
        "OwnerName",
        "Local authority",
        "UnknownSourceFlag",
    ]
    date_columns = ["RegistrationDate", "ClosedDate"]
    dimOfstedProvider = fillna_categorical_columns(
        dimOfstedProvider, categorical_columns
    )
    dimOfstedProvider = fillna_date_columns(dimOfstedProvider, date_columns)

    # select relevant columns
    dimOfstedProvider = dimOfstedProvider[
        [
            "OfstedProviderKey",
            "URN",
            "ProviderType",
            "Sector",
            "RegistrationDate",
            "ProviderStatus",
            "ClosedDate",
            "MaxUsers",
            "UnknownSourceFlag",
            "ONSAreaCode",
            "OwnerName",
        ]
    ]

    write_csv(dimOfstedProvider, fs_out, "dimOfstedProvider.csv", False)


def create_dimPostcode():
    fs_ext = open_location(input_location_ext)
    fs_out = open_location(output_location)

    postcodes = open_file(
        fs_ext, "Postcode directory//ONSPD reduced to postcode sector.csv"
    )
    postcodes = postcodes[
        ["pcd2", "lat", "long", "oseast1m", "osnrth1m", "imd", "oslaua", "lsoa11"]
    ]

    dimPostcode = postcodes.rename(postcodes_map, axis=1)

    dimPostcode.reset_index(inplace=True, drop=True)
    dimPostcode.reset_index(inplace=True, names="PostcodeKey")
    dimPostcode = add_nan_row(dimPostcode, "PostcodeKey")

    dimPostcode = fillna_categorical_columns(dimPostcode, list(dimPostcode.columns))

    write_csv(dimPostcode, fs_out, "dimPostcode.csv", False)


def create_factEpisode():
    fs_903 = open_location(input_location_903)
    fs_out = open_location(output_location)

    episodes = open_file(fs_903, "pan_London_SSDA903_Episodes.csv")

    looked_after_child = open_file(fs_out, "dimLookedAfterChild.csv")
    reason_for_new_episode = open_file(fs_out, "dimReasonForNewEpisode.csv")
    legal_status = open_file(fs_out, "dimLegalStatus.csv")
    category_of_need = open_file(fs_out, "dimCategoryOfNeed.csv")
    placement_type = open_file(fs_out, "dimPlacementType.csv")
    placement_provider = open_file(fs_out, "dimPlacementProvider.csv")
    reason_episode_ceased = open_file(fs_out, "dimReasonEpisodeCeased.csv")
    reason_place_change = open_file(fs_out, "dimReasonPlaceChange.csv")
    postcode = open_file(fs_out, "dimPostcode.csv")
    ofsted_provider = open_file(fs_out, "dimOfstedProvider.csv")
    ons_area = open_file(fs_out, "dimONSArea.csv")

    # LookedAfterChildKey

    episodes = episodes.merge(
        looked_after_child, left_on="CHILD", right_on="ChildIdentifier", how="left"
    )

    # ReasonForNewEpisodeKey
    episodes = episodes.merge(
        reason_for_new_episode,
        left_on="RNE",
        right_on="ReasonForNewEpisodeCode",
        how="left",
    )

    # LegalStatusKey
    episodes = episodes.merge(
        legal_status, left_on="LS", right_on="LegalStatusCode", how="left"
    )

    # CategoryOfNeedKey
    episodes = episodes.merge(
        category_of_need, left_on="CIN", right_on="CategoryOfNeedCode", how="left"
    )

    # PlacementTypeKey
    episodes = episodes.merge(
        placement_type, left_on="PLACE", right_on="PlacementTypeCode", how="left"
    )

    # PlacementProviderKey
    episodes = episodes.merge(
        placement_provider,
        left_on="PLACE_PROVIDER",
        right_on="PlacementProviderCode",
        how="left",
    )

    # ReasonEpisodeCeasedKey
    episodes = episodes.merge(
        reason_episode_ceased,
        left_on="REC",
        right_on="ReasonEpisodeCeasedCode",
        how="left",
    )

    # ReasonPlaceChangeKey
    episodes = episodes.merge(
        reason_place_change,
        left_on="REASON_PLACE_CHANGE",
        right_on="ReasonPlaceChangeCode",
        how="left",
    )

    # OfstedProviderKey
    ofsted_provider.URN = ofsted_provider.URN.astype(str)
    episodes.URN = episodes.URN.astype(str)
    episodes = episodes.merge(
        ofsted_provider, left_on="URN", right_on="URN", how="left"
    )

    # ONSAreaKey
    episodes = episodes.merge(ons_area, left_on="LA", right_on="AreaName", how="left")

    postcode = postcode[["PostcodeKey", "Sector"]]

    # HomePostcodeKey
    episodes = episodes.merge(
        postcode, left_on="HOME_POST", right_on="Sector", how="left"
    )
    episodes = episodes.rename(columns={"PostcodeKey": "HomePostcodeKey"})

    # PlacementPostcodeKey
    episodes = episodes.merge(
        postcode, left_on="PL_POST", right_on="Sector", how="left"
    )
    episodes = episodes.rename(columns={"PostcodeKey": "PlacementPostcodeKey"})

    episodes.rename(columns=episodes_map, inplace=True)
    episodes = episodes[
        [
            "LookedAfterChildKey",
            "EpisodeCommencedDateKey",
            "ReasonForNewEpisodeKey",
            "LegalStatusKey",
            "CategoryOfNeedKey",
            "PlacementTypeKey",
            "PlacementProviderKey",
            "EpisodeCeasedDateKey",
            "ReasonEpisodeCeasedKey",
            "ReasonPlaceChangeKey",
            "HomePostcodeKey",
            "PlacementPostcodeKey",
            "OfstedProviderKey",
            "ONSAreaKey",
            "SubmissionYearDateKey",
        ]
    ]

    # any missing keys after merge should be replaced with -1
    episode_key_columns = [
        "LookedAfterChildKey",
        "EpisodeCommencedDateKey",
        "ReasonForNewEpisodeKey",
        "LegalStatusKey",
        "CategoryOfNeedKey",
        "PlacementTypeKey",
        "PlacementProviderKey",
        "EpisodeCeasedDateKey",
        "ReasonEpisodeCeasedKey",
        "ReasonPlaceChangeKey",
        "HomePostcodeKey",
        "PlacementPostcodeKey",
        "OfstedProviderKey",
        "ONSAreaKey",
        "SubmissionYearDateKey",
    ]
    episodes = fillna_categorical_columns(episodes, episode_key_columns)

    write_csv(episodes, fs_out, "Output data//factEpisode.csv", False)


def create_factOfstedInspection():
    fs_out = open_location(output_location)
    fs_ext = open_location(input_location_ext)

    ofsted_effectiveness = open_file(fs_out, "dimOfstedEffectiveness.csv")
    ofsted_provider = open_file(fs_out, "dimOfstedProvider.csv")

    provider_level_at_31Aug = open_file(
        fs_ext, "Ofsted data//Provider_level_at_31_Aug_2023.csv"
    )

    # This sample file returned a UnicodeDecodeError so it was necessary to check that it is read with the right encoding type.
    # leaving in the safeguard until it works in production with the real file.

    encoding = check_encoding(fs_ext, "Ofsted data//Provider_level_in_year_2022-23.csv")
    provider_level_in_year_2022_23 = open_file(
        fs_ext, "Ofsted data//Provider_level_in_year_2022-23.csv", encoding=encoding
    )

    # provider_level_in_year_2022_23 was observed to contain several unnamed empty columns.
    unnamed_columns = [
        col for col in provider_level_in_year_2022_23.columns if "Unnamed" in col
    ]
    provider_level_in_year_2022_23 = provider_level_in_year_2022_23.drop(
        columns=unnamed_columns
    )

    # rename inspection date column in provider_level_at_31Aug so that they match when concatenated.
    provider_level_at_31Aug = provider_level_at_31Aug.rename(
        columns={
            "Latest full inspection date": "Inspection date",
        }
    )

    factOfstedInspection = pd.concat(
        [provider_level_in_year_2022_23, provider_level_at_31Aug]
    )
    factOfstedInspection = factOfstedInspection.drop_duplicates(
        subset=["URN", "Inspection date"], keep="first"
    )

    # create IsLatest column that indicates if inspection is the most recent one recorded for a URN
    factOfstedInspection["IsLatest"] = (
        factOfstedInspection.groupby("URN")["Inspection date"].transform("max")
        == factOfstedInspection["Inspection date"]
    )

    # Update the EndDate where isLatest is True with 2999 if EndDate is missing, otherwise keep it the same as InspectionDateKey
    factOfstedInspection.loc[factOfstedInspection["IsLatest"] == True, "EndDateKey"] = (
        factOfstedInspection.loc[
            factOfstedInspection["IsLatest"] == True, "Inspection date"
        ]
    )
    factOfstedInspection["EndDateKey"].fillna("2999-12-31", inplace=True)

    # Find the next inspection date for each row where isLatest is False
    next_inspection_dates = factOfstedInspection.loc[
        factOfstedInspection["IsLatest"] == False, "Inspection date"
    ].shift(-1)

    # Update the EndDate where isLatest is False with the next inspection date
    factOfstedInspection.loc[
        factOfstedInspection["IsLatest"] == False, "EndDateKey"
    ] = next_inspection_dates

    factOfstedInspection = factOfstedInspection.rename(columns=inspection_map)
    factOfstedInspection = factOfstedInspection[
        ["InspectionDateKey", "EndDateKey", "OwnerName", "Effectiveness", "IsLatest"]
    ]

    factOfstedInspection.IsLatest = factOfstedInspection.IsLatest.map(
        {True: "TRUE", False: "FALSE"}
    )

    # fill nans
    categorical_columns = ["OwnerName"]
    factOfstedInspection = fillna_categorical_columns(
        factOfstedInspection, categorical_columns
    )
    date_columns = ["InspectionDateKey", "EndDateKey"]
    factOfstedInspection = fillna_date_columns(factOfstedInspection, date_columns)

    # create OfstedEffectivenessKey
    factOfstedInspection["Effectiveness"] = factOfstedInspection[
        "Effectiveness"
    ].fillna("Unknown")
    factOfstedInspection = factOfstedInspection.merge(
        ofsted_effectiveness,
        how="left",
        left_on="Effectiveness",
        right_on="OverallEffectiveness",
    )
    factOfstedInspection = factOfstedInspection.drop(
        columns=["Effectiveness", "OverallEffectiveness", "Grade"]
    )

    # create OfstedProviderKey
    ofsted_provider = ofsted_provider[["OfstedProviderKey", "OwnerName"]]
    factOfstedInspection = factOfstedInspection.merge(
        ofsted_provider, how="left", on="OwnerName"
    )
    factOfstedInspection = factOfstedInspection.drop(columns=["OwnerName"])

    # replace keys that couldn't be matched with -1
    key_columns = ["OfstedProviderKey", "OfstedEffectivenessKey"]
    factOfstedInspection = fillna_categorical_columns(factOfstedInspection, key_columns)

    factOfstedInspection.reset_index(inplace=True, drop=True)
    factOfstedInspection.reset_index(inplace=True, names="factOfstedInspectionKey")

    write_csv(factOfstedInspection, fs_out, "factOfstedInspection.csv")


def create_sufficiency_data():
    create_dim_tables()
    create_dimONSArea()
    create_dimLookedAfterChild()
    create_dimOfstedProvider()
    create_dimPostcode()
    create_factEpisode()
    create_factOfstedInspection()
