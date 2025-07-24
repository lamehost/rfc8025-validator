#!/bin/env python3

"""
A Python script to validate geolocation data formatted as a geofeed according to RFC8025
"""

import csv
import sys
from collections.abc import Generator
from ipaddress import ip_network
from typing import IO, TypedDict


class GeoRecord(TypedDict):
    """
    Geolocation record as specified by RFC8025 with the addition of the error field
    """

    prefix: str
    country: str
    region: str
    city: str
    zip: str


def read_ip2location_data(
    filename: str = "IP2LOCATION-ISO3166-2.CSV",
) -> dict[str, set[str]]:
    """
    Reads the CSV file containing the ISO3166-2 data from the IP2location website

    Arguments:
    ----------
    filename: str
        Filename with the full path. Default: IP2LOCATION-ISO3166-2.CSV

    Returns:
    --------
    dict[str, set[str]]: The records serialized as dict. Country code as keys,
                         sets of regions codes as values
    """
    records = {}

    with open(filename, encoding="utf-8") as csvfile:
        for row in csv.reader(csvfile):
            records.setdefault(row[0], set()).add(row[2])

    return records


def read_geolocation_data(stream: IO) -> Generator[GeoRecord]:
    """
    Reads the CSV file containing the goelocation data formatted as per RFC8025.

    Arguments:
    ----------
    filename: str
        Filename with the full path. Default: geolocation.csv

    Yields:
    --------
    Generator[Record]: Geolocation records
    """
    for row in csv.reader(stream):
        if len(row) != 5:
            row = ",".join(row)
            raise ValueError(f"Malformatted record: {row}")

        record = dict(zip(["prefix", "country", "region", "city", "zip"], row))
        yield GeoRecord(**record)


def validate(record: GeoRecord, iso3166_2: dict[str, set[str]]) -> None:
    """
    Raises ValuError if `record` cannot be validated against `ip2location_data`.

    Arguments:
    ----------
    gelocation_records: GeoRecords
        Geolocation record
    iso3166_2: dict[str, set[str]]
        ISO3166-2 data serialized as dict. Country code as keys, sets of regions codes as values
    """
    try:
        ip_network(record["prefix"])
    except ValueError as error:
        raise ValueError("Invalid prefix") from error

    if record["country"]:
        try:
            iso3166_2[record["country"]]
        except KeyError as error:
            raise ValueError("Wrong country code") from error

    if record["region"]:
        if record["country"]:
            regions = iso3166_2[record["country"]]
        else:
            regions = [region for _regions in iso3166_2.values() for region in _regions]

        if record["region"] not in regions:
            raise ValueError("Wrong region code")


def format_validation_error(record: GeoRecord, error: Exception) -> str:
    """
    Returns nicely formatted validation errors.

    Arguments:
    ---------
    record: GeoRecord
        Geolocation record
    error: Exception
        The exception raised by validate

    Returns:
    -------
    str: The formatted error message
    """
    return (
        f"{error}: "
        f"{record['prefix']},{record['country']},{record['region']},"
        f"{record['city']},{record['zip']}"
    )


def main():
    """
    Main entrypoint for the script.

    Reads the content of the geolocation and ip2location data and performs validation.
    """
    geolocation_data = read_geolocation_data(sys.stdin)
    ip2location_data = read_ip2location_data()

    exit_code = 0
    try:
        for record in geolocation_data:
            try:
                validate(record, ip2location_data)
            except ValueError as error:
                # Error raised by the validator
                print(format_validation_error(record, error))
                exit_code = 1
    except ValueError as error:
        # Error raised by the CSV parser
        print(error)
        exit_code = 1
    finally:
        sys.stdout.flush()

    if exit_code:
        sys.exit(exit_code)


if __name__ == "__main__":
    main()
