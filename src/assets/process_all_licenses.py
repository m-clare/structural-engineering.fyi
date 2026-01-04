#!/usr/bin/env python3
import pandas as pd
import numpy as np
import re
from math import isnan
from datetime import datetime
import hashlib

state_mapping = {
    "Wyoming": "WY",
    "Wisconsin": "WI",
    "Washington": "WA",
    "Virginia": "VA",
    "Texas": "TX",
    "Tennessee": "TN",
    "South Dakota": "SD",
    "Pennsylvania": "PA",
    "Oregon": "OR",
    "Oklahoma": "OK",
    "OUT OF COUNTRY": None,
    "North Carolina": "NC",
    "New York": "NY",
    "Nebraska": "NE",
    "Minnesota": "MN",
    "Michigan": "MI",
    "Massachusetts": "MA",
    "Louisiana": "LA",
    "Kentucky": "KY",
    "Kansas": "KS",
    "Iowa": "IA",
    "Illinois": "IL",
    "Georgia": "GA",
    "Colorado": "CO",
    "California": "CA",
    "Arkansas": "AR",
    "00": None,
    "-1": None,
    "AA": None,
    "AB": None,
    "AP": None,
    "BC": None,
    "FO": None,
    "QC": None,
    "PQ": None,
    "ON": None,
    "NA": None,
    "  ": None,
}


def generate_name_hash(first_name, last_name, suffix="", origin_state=""):
    """
    Generate a consistent hash for a name combination
    """
    name_string = f"{first_name.strip().upper()}|{last_name.strip().upper()}|{suffix.strip().upper()}|{origin_state.strip().upper()}"
    return hashlib.sha256(name_string.encode()).hexdigest()[:16]


def standardize_date(date_str, state):
    """
    Convert each state date formats to datetime object or None
    """

    if pd.isna(date_str):
        return None

    try:
        if state in ["IL", "AK", "HI"]:
            month, day, year = date_str.split("/")
            formattedDate = f"{year}-{month:0>2}-{day:0>2}"
            return datetime.strptime(formattedDate, "%Y-%m-%d")
        elif state in ["CA"]:
            month, day, year = date_str.split("/")
            yearNum = int(year)
            if yearNum <= 100:
                if yearNum <= 24:
                    yearNum += 2000
                else:
                    yearNum += 1900
            formattedDate = f"{str(yearNum)}-{month:0>2}-{day:0>2}"
            return datetime.strptime(formattedDate, "%Y-%m-%d")
        elif state in ["GA", "UT", "WA"]:
            return datetime.strptime(date_str, "%Y-%m-%d")
        elif state in ["OK"]:
            return datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S")
        elif state in ["OR"]:
            return datetime.strptime(date_str, "%m/%d/%Y")

    except Exception as e:
        print(e)
        return None

    return None


def standardize_state(location_str, state):
    """
    Convert each location to a state abbreviation (if it exists)
    """

    if pd.isna(location_str):
        return None

    try:
        if state in ["AK", "CA", "NV", "OK", "OR", "UT", "WA", "IL"]:
            if location_str in state_mapping:
                return state_mapping[location_str]
            return location_str
        elif state in ["GA"]:
            pattern = r",\s*([A-Z]{2})\s"
            match = re.search(pattern, location_str)
            if match:
                state = match.group(1)
                return state

    except Exception as e:
        print(e)
        return None


def clean_name(name):
    """
    Clean and standardize name string:
    - Remove titles (Mr, Mrs, etc)
    - Remove extra spaces
    - Convert to uppercase
    Returns: name
    """
    if pd.isna(name):
        return ""

    # Extract gender from title first
    # gender_from_title = extract_gender_from_title(name)

    # Remove titles
    titles = r"^(MR|MRS|MS|DR|MISS|M/S|M/M)\.?\s+"
    name = re.sub(titles, "", str(name).upper(), flags=re.IGNORECASE)

    # Remove extra spaces and standardize special characters
    name = re.sub(r"[^\w\s\.]", " ", name)  # Keep periods for suffixes like "JR."
    name = " ".join(name.split())

    return name


def extract_name_parts(name):
    """
    Extract first, middle, last names, and suffix from a full name string.
    Returns tuple of (first_name, middle_name, last_name, suffix)
    """
    if pd.isna(name):
        return ("", "", "", "")

    # List of common suffixes
    suffixes = r"\b(JR|SR|I{2,3}|IV|V|ESQ)\.?$"

    # Split the name into parts
    parts = name.split()
    if not parts:
        return ("", "", "", "")

    # Check if last part is a suffix
    suffix = ""
    if len(parts) > 1:
        last_part = parts[-1].strip(".")
        if re.match(suffixes, last_part):
            suffix = last_part
            parts = parts[:-1]

    if len(parts) == 1:
        return (parts[0], "", "", suffix)
    elif len(parts) == 2:
        return (parts[0], "", parts[1], suffix)
    else:
        return (parts[0], " ".join(parts[1:-1]), parts[-1], suffix)


def standardize_dataset(df, state):
    """
    Standardize names from different state datasets into common format
    """
    df = df.copy()

    if state == "IL":
        df["first_name"] = df["First Name"].apply(clean_name)
        df["middle_name"] = df["Middle"].apply(clean_name)
        df["last_name"] = df["Last Name"].apply(clean_name)
        df["suffix"] = df["Suffix"].apply(clean_name)
        df["license_date"] = df["Original Issue Date"].apply(
            standardize_date, args=(state,)
        )
        df["origin_state"] = df["State"].apply(standardize_state, args=(state,))
        df["expiration_date"] = df["Expiration Date"].apply(
            standardize_date, args=(state,)
        )
        df["license_active"] = df["License Status"] == "ACTIVE"

    elif state == "CA":
        # CA has separate name fields, check first name for title
        df["first_name"] = df["First Name"].apply(clean_name)
        df["middle_name"] = df["Middle Name"].apply(clean_name)
        df["last_name"] = df["Org/Last Name"].apply(clean_name)
        df["suffix"] = ""
        df["license_date"] = df["Original Issue Date"].apply(
            standardize_date, args=(state,)
        )
        df["origin_state"] = df["State"].apply(standardize_state, args=(state,))
        df["expiration_date"] = df["Expiration Date"].apply(
            standardize_date, args=(state,)
        )
        df["license_active"] = df["License Status"] == "Active"

    elif state == "GA":
        df["full_name_cleaned"] = df["fullName"].apply(clean_name)
        df[["first_name", "middle_name", "last_name", "suffix"]] = (
            df["full_name_cleaned"].apply(extract_name_parts).apply(pd.Series)
        )
        df["license_date"] = df["issueDate"].apply(standardize_date, args=(state,))
        df["origin_state"] = df["location"].apply(standardize_state, args=(state,))
        df["expiration_date"] = df["expirationDate"].apply(
            standardize_date, args=(state,)
        )
        df["license_active"] = df["licenseStatus"].isin(
            ["Active", "Active-Renewal Pending"]
        )

    elif state == "NV":
        df["full_name_cleaned"] = df["full_name"].apply(clean_name)
        df[["first_name", "middle_name", "last_name", "suffix"]] = (
            df["full_name_cleaned"].apply(extract_name_parts).apply(pd.Series)
        )
        df["license_date"] = None
        df["origin_state"] = df["state"].apply(standardize_state, args=(state,))
        df["license_active"] = df["status"] == "ACTIVE"
        df["expiration_date"] = df["expiration_date"].apply(
            standardize_date, args=(state,)
        )

    elif state == "HI":
        df["full_name_cleaned"] = df["full_name"].apply(clean_name)
        df[["first_name", "middle_name", "last_name", "suffix"]] = (
            df["full_name_cleaned"].apply(extract_name_parts).apply(pd.Series)
        )
        df["license_date"] = df["original_license_date"].apply(
            standardize_date, args=(state,)
        )
        df["origin_state"] = None
        df["license_active"] = df["status"] == "Current, Valid & In Good Standing"
        df["expiration_date"] = df["expiration_date"].apply(
            standardize_date, args=(state,)
        )

    elif state == "UT":
        df["full_name_cleaned"] = df["FULL NAME"].apply(clean_name)
        df[["first_name", "middle_name", "last_name", "suffix"]] = (
            df["full_name_cleaned"].apply(extract_name_parts).apply(pd.Series)
        )
        df["license_date"] = df["ISSUE DATE"].apply(standardize_date, args=(state,))
        df["origin_state"] = df["STATE"].apply(standardize_state, args=(state,))
        df["expiration_date"] = df["EXPIRATION DATE"].apply(
            standardize_date, args=(state,)
        )
        df["license_active"] = df["LICENSE STATUS"] == "Active"

    elif state == "WA":
        df["full_name_cleaned"] = df["license_printable_name"].apply(clean_name)
        df[["first_name", "middle_name", "last_name", "suffix"]] = (
            df["full_name_cleaned"].apply(extract_name_parts).apply(pd.Series)
        )
        df["license_date"] = df["original_issue_date"].apply(
            standardize_date, args=(state,)
        )
        df["origin_state"] = df["state"].apply(standardize_state, args=(state,))
        df["expiration_date"] = df["expiration_date"].apply(
            standardize_date, args=(state,)
        )
        df["license_active"] = df["status"] == "Active"

    elif state == "OK":
        df["first_name"] = df["FirstName"].apply(clean_name)
        df["middle_name"] = df["MiddleName"].apply(clean_name)
        df["last_name"] = df["LastName"].apply(clean_name)
        df["suffix"] = ""
        df["license_date"] = df["OriginalLicenseDate"].apply(
            standardize_date, args=(state,)
        )
        df["origin_state"] = df["State"].apply(standardize_state, args=(state,))
        df["expiration_date"] = df["LicenseExpirationDate"].apply(
            standardize_date, args=(state,)
        )
        df["license_active"] = df["LicenseStatusTypeName"] == "Active"

    elif state == "OR":
        df["first_name"] = df["First Name"].apply(clean_name)
        df["middle_name"] = ""
        df["last_name"] = df["Last Name"].apply(clean_name)
        df["suffix"] = ""
        df["license_date"] = df["License Date"].apply(standardize_date, args=(state,))
        df["origin_state"] = df["State"].apply(standardize_state, args=(state,))
        df["expiration_date"] = df["Expiration Date"].apply(
            standardize_date, args=(state,)
        )
        df["license_active"] = df["Status"] == "Active"

    elif state == "AK":
        df["full_name_cleaned"] = df["Owners"].apply(clean_name)
        df[["first_name", "middle_name", "last_name", "suffix"]] = (
            df["full_name_cleaned"].apply(extract_name_parts).apply(pd.Series)
        )
        df["license_date"] = df["DateIssued"].apply(standardize_date, args=(state,))
        df["origin_state"] = df["STATE"].apply(standardize_state, args=(state,))
        df["expiration_date"] = df["DateExpired"].apply(standardize_date, args=(state,))
        df["license_active"] = df["Status"] == "Active"

    # Add state identifier
    df["source_state"] = state

    # Select only needed columns
    return df[
        [
            "first_name",
            "middle_name",
            "last_name",
            "suffix",
            "source_state",
            "license_date",
            "origin_state",
            "license_active",
            "expiration_date",
        ]
    ]


def determine_origin_state(group_df):
    """
    Determine the consensus origin state for a group of records.
    Returns the origin state if there's consensus, None if conflicting.
    """
    # Get all non-null origin states
    origin_states = group_df[
        group_df["origin_state"].notna() & (group_df["origin_state"] != "")
    ]["origin_state"].unique()

    if len(origin_states) == 0:
        # No origin state information available
        return None
    elif len(origin_states) == 1:
        # Consensus - all records agree on origin state
        return origin_states[0]
    else:
        # Conflict - different origin states found
        return "CONFLICT"


def process_middle_names_and_states(group_df):
    """
    Process a group of names to find compatible middle names and determine match confidence.
    Also checks for origin state conflicts.
    Returns information about the match including confidence level.
    """
    # Check origin state first - if there's a conflict, split into separate groups
    consensus_origin = determine_origin_state(group_df)

    if consensus_origin == "CONFLICT":
        # Split by origin state and process separately
        results = []
        for origin_state, origin_group in group_df.groupby("origin_state"):
            if pd.isna(origin_state) or origin_state == "":
                continue
            result = process_middle_names_and_states_internal(
                origin_group, origin_state
            )
            if result:
                results.append(result)
        return results if results else None
    else:
        # No conflict, process as one group
        result = process_middle_names_and_states_internal(group_df, consensus_origin)
        return [result] if result else None


def process_middle_names_and_states_internal(group_df, consensus_origin):
    """
    Process a group of names to find compatible middle names and determine match confidence.
    Returns information about the match including confidence level.
    """
    # Separate records with and without middle names
    has_middle = group_df[
        group_df["middle_name"].notna() & (group_df["middle_name"] != "")
    ].copy()
    no_middle = group_df[
        group_df["middle_name"].isna() | (group_df["middle_name"] == "")
    ].copy()

    # Extract all middle names and their states
    name_state_pairs = []
    for _, row in has_middle.iterrows():
        if pd.notna(row["middle_name"]) and row["middle_name"]:
            for name in row["middle_name"].split(","):
                name = name.strip()
                if name:
                    name_state_pairs.append((name, row["source_state"]))

    # Separate full names and initials
    full_names = [
        (name, state)
        for name, state in name_state_pairs
        if len(name.replace(" ", "")) > 1
    ]
    initials = [
        (name, state)
        for name, state in name_state_pairs
        if len(name.replace(" ", "")) == 1
    ]

    # Find compatible matches
    compatible_pairs = []
    compatible_pairs.extend(full_names)

    # Only add initials that match full names
    for initial, state in initials:
        if any(name.startswith(initial) for name, _ in full_names):
            compatible_pairs.append((initial, state))

    # Determine match confidence
    if compatible_pairs:
        compatible_pairs.sort(key=lambda x: (len(x[0]) == 1, x[0]))
        compatible_names = sorted(set(name for name, _ in compatible_pairs))
        compatible_states = sorted(set(state for _, state in compatible_pairs))

        if not no_middle.empty:
            compatible_states = sorted(
                set(compatible_states) | set(no_middle["source_state"])
            )

        if len(compatible_names) == 1:
            confidence = "HIGH"
        else:
            confidence = "MEDIUM"

        middle_name_result = ", ".join(compatible_names)
    elif len(group_df["source_state"].unique()) > 1:
        confidence = "LOW"
        middle_name_result = ""
        compatible_states = sorted(group_df["source_state"].unique())
    else:
        # Single state, single record - singleton
        return None

    return {
        "middle_name": middle_name_result,
        "states": compatible_states,
        "confidence": confidence,
        "origin_state": consensus_origin,
        "group_df": group_df,
    }


def create_master_license_list(dfs_dict):
    """
    Create a master list where each record represents one license in one state.
    All matched names get the same hash.
    """
    # Combine all dataframes
    all_names = pd.concat(dfs_dict.values(), ignore_index=True)
    all_names = all_names.fillna("")

    # Create composite last name with suffix
    all_names["last_name_with_suffix"] = all_names.apply(
        lambda x: f"{x['last_name']} {x['suffix']}" if x["suffix"] else x["last_name"],
        axis=1,
    ).str.strip()

    # Store all license records
    master_records = []

    # Process each name group
    for name_key, group in all_names.groupby(["first_name", "last_name_with_suffix"]):
        first_name = name_key[0]
        last_name = name_key[1]

        # Process the group to find matches
        match_results = process_middle_names_and_states(group)

        if match_results:
            for match_info in match_results:
                # Multiple states - matched person
                middle_name = match_info["middle_name"]
                confidence = match_info["confidence"]
                consensus_origin = match_info["origin_state"]
                group_df = match_info["group_df"]

                name_hash = generate_name_hash(
                    first_name, last_name, "", consensus_origin or ""
                )

                first_license_date = group_df["license_date"].min()

                earliest_active_license = group_df[group_df["license_active"] == True][
                    "license_date"
                ].min()
                has_active_license = (
                    True
                    if len(group_df[group_df["license_active"] == True]) > 0
                    else False
                )

                origin = group_df.sort_values(by="origin_state")

                # Create one record per state for this matched person
                for _, row in group_df.iterrows():
                    master_records.append(
                        {
                            "name_hash": name_hash,
                            "license_state": row["source_state"],
                            "first_name": first_name,
                            "middle_name": middle_name,
                            "last_name": last_name,
                            "match_confidence": confidence,
                            "license_date": row["license_date"],
                            "license_year": row["license_date"].year,
                            "origin_state": origin.iloc[
                                -1, origin.columns.get_loc("origin_state")
                            ],
                            "license_active": row["license_active"],
                            "license_expiration_date": row["expiration_date"],
                            "first_license": row["license_date"] == first_license_date,
                            "oldest_active_license": (
                                row["license_date"] == earliest_active_license
                                if has_active_license == True
                                else "N/A"
                            ),
                        }
                    )
        else:
            # Singleton - single state, single record
            row = group.iloc[0]
            name_hash = generate_name_hash(
                first_name, last_name, "", row["origin_state"] or ""
            )
            master_records.append(
                {
                    "name_hash": name_hash,
                    "license_state": row["source_state"],
                    "first_name": first_name,
                    "middle_name": row["middle_name"],
                    "last_name": last_name,
                    "match_confidence": "SINGLETON",
                    "license_date": row["license_date"],
                    "license_year": row["license_date"].year,
                    "origin_state": row["origin_state"],
                    "license_active": row["license_active"],
                    "license_expiration_date": row["expiration_date"],
                    "first_license": True,
                    "oldest_active_license": (
                        row["license_active"]
                        if row["license_active"] == True
                        else "N/A"
                    ),
                }
            )

    # Convert to DataFrame
    master_df = pd.DataFrame(master_records)

    # Sort by name_hash and then by license_state
    if not master_df.empty:
        master_df = master_df.sort_values(["name_hash", "license_state"])

    return master_df


def filter_active_licenses(df, state):
    """
    Filter dataframe to only include active licenses based on state-specific criteria
    """
    df = df.copy()

    if state == "CA":
        return df[df["License Status"] == "Active"]

    elif state == "UT":
        return df[df["LICENSE STATUS"] == "Active"]

    elif state == "IL":
        return df[df["License Status"] == "ACTIVE"]

    elif state == "GA":
        return df[df["licenseStatus"].isin(["Active", "Active-Renewal Pending"])]

    elif state == "HI":
        return df[df["status"] == "Current, Valid & In Good Standing"]

    elif state == "NV":
        return df[df["status"] == "ACTIVE"]

    elif state == "WA":
        return df[df["status"] == "Active"]

    elif state == "OR":
        return df[df["Status"] == "Active"]

    elif state == "AK":
        return df[df["Status"] == "Active"]

    elif state == "OK":
        return df[df["LicenseStatusTypeName"] == "Active"]
    return df


if __name__ == "__main__":
    dfs = {
        "IL": pd.read_csv("./clean/20251129_il_se.csv"),
        "CA": pd.read_csv("./clean/20251129_ca_se.csv"),
        "GA": pd.read_json("./clean/20251129_ga_se.json"),
        "NV": pd.read_json("./clean/20251202_nv_se.json"),
        "HI": pd.read_json("./clean/20251201_hi_se.json"),
        "UT": pd.read_csv("./clean/20251128_ut_se.csv"),
        "WA": pd.read_json("./clean/20260101_wa_se.json"),
        "OK": pd.read_json("./clean/2025_ok_se.json"),
        "OR": pd.read_csv("./clean/20251129_or_se.csv"),
        "AK": pd.read_csv("./clean/20251129_ak_se.csv"),
    }

    # Print initial record counts
    total_records = 0
    print("\nInitial Dataset Sizes:")
    for state, df in dfs.items():
        record_count = len(df)
        total_records += record_count
        print(f"{state}: {record_count:,} records")
    print(f"Total initial records: {total_records:,}")

    # Process all licenses
    print("\n=== Processing ALL Licenses ===")
    standardized_dfs_all = {}
    for state, df in dfs.items():
        standardized_dfs_all[state] = standardize_dataset(df, state)

    master_all = create_master_license_list(standardized_dfs_all)
    master_all.to_csv("master_all_licenses.csv", index=False)

    # Print summary for all licenses
    unique_people_all = master_all["name_hash"].nunique()
    total_licenses_all = len(master_all)
    print(f"\nAll Licenses Summary:")
    print(f"Unique individuals: {unique_people_all:,}")
    print(f"Total license records: {total_licenses_all:,}")
    print(f"Average licenses per person: {total_licenses_all/unique_people_all:.2f}")

    # Count by confidence level
    print("\nMatch Confidence Breakdown (All):")
    for conf in ["SINGLETON", "LOW", "MEDIUM", "HIGH"]:
        count = len(master_all[master_all["match_confidence"] == conf])
        pct = (count / total_licenses_all * 100) if total_licenses_all > 0 else 0
        print(f"{conf}: {count:,} ({pct:.1f}%)")

    # Process active licenses
    print("\n=== Processing ACTIVE Licenses ===")
    filtered_dfs = {}
    total_active = 0
    print("\nActive License Counts:")
    for state, df in dfs.items():
        filtered_df = filter_active_licenses(df, state)
        filtered_dfs[state] = filtered_df
        active_count = len(filtered_df)
        total_active += active_count
        inactive_count = len(df) - active_count
        print(f"{state}: {active_count:,} active, {inactive_count:,} inactive")
    print(f"Total active licenses: {total_active:,}")
    print(f"Total inactive licenses: {total_records - total_active:,}")

    # Standardize active licenses
    standardized_dfs_active = {}
    for state, df in filtered_dfs.items():
        standardized_dfs_active[state] = standardize_dataset(df, state)

    master_active = create_master_license_list(standardized_dfs_active)
    master_active.to_csv("master_active_licenses.csv", index=False)

    # Print summary for active licenses
    unique_people_active = master_active["name_hash"].nunique()
    total_licenses_active = len(master_active)
    print(f"\nActive Licenses Summary:")
    print(f"Unique individuals: {unique_people_active:,}")
    print(f"Total license records: {total_licenses_active:,}")
    print(
        f"Average licenses per person: {total_licenses_active/unique_people_active:.2f}"
    )

    # Count by confidence level
    print("\nMatch Confidence Breakdown (Active):")
    for conf in ["SINGLETON", "LOW", "MEDIUM", "HIGH"]:
        count = len(master_active[master_active["match_confidence"] == conf])
        pct = (count / total_licenses_active * 100) if total_licenses_active > 0 else 0
        print(f"{conf}: {count:,} ({pct:.1f}%)")

    # Multi-state license holders
    multi_state_hashes = (
        master_active.groupby("name_hash")
        .filter(lambda x: len(x) > 1)["name_hash"]
        .unique()
    )
    print(f"\nMulti-state license holders: {len(multi_state_hashes):,}")
