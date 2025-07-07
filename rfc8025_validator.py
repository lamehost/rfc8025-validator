#!/bin/env python3

"""
A Python script to validate geolocation data formatted as a geofeed according to RFC8025
"""

import csv
import sys
from collections.abc import Generator, Iterable
from ipaddress import ip_network
from typing import IO, NotRequired, TypedDict


class GeoRecord(TypedDict):
    """
    Geolocation record as specified by RFC8025 with the addition of the error field
    """

    prefix: str
    country: str
    region: str
    city: str
    zip: str
    _error: NotRequired[str | None]


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
        record = dict(zip(["prefix", "country", "region", "city", "zip"], row))
        yield GeoRecord(record)


def validate(
    geolocation_records: Iterable[GeoRecord], iso3166_2: dict[str, set[str]]
) -> Generator[GeoRecord]:
    """
    Validate `gelocation_data` against `ip2location_data`.

    Arguments:
    ----------
    gelocation_records: Iterable[GeoRecords]
        Geolocation records
    iso3166_2: dict[str, set[str]]
        ISO3166-2 data serialized as dict. Country code as keys, sets of regions codes as values

    Yields:
    -------
    Generator[GeoRecord]: Malformed GeoRecords
    """
    for record in geolocation_records:
        try:
            ip_network(record["prefix"])
        except ValueError:
            record["_error"] = "Invalid prefix"
            yield record
            continue

        if record["country"]:
            try:
                iso3166_2[record["country"]]
            except KeyError:
                record["_error"] = "Wrong country code"
                yield record
                continue

        if record["region"]:
            if record["country"]:
                regions = iso3166_2[record["country"]]
            else:
                regions = [
                    region for _regions in iso3166_2.values() for region in _regions
                ]

            if record["region"] not in regions:
                record["_error"] = "Wrong region code"
                yield record


def main():
    """
    Main entrypoint for the script.

    Reads the content of the geolocation and ip2location data and performs validation.
    """
    geolocation_data = read_geolocation_data(sys.stdin)
    ip2location_data = read_ip2location_data()

    malformed_records = validate(geolocation_data, ip2location_data)

    for record in malformed_records:
        print(
            f"{record['_error']}: "
            f"{record['prefix']},{record['country']},{record['region']},"
            f"{record['city']},{record['zip']}"
        )


if __name__ == "__main__":
    main()
