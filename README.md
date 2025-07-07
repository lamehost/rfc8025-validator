# RFC8025 / Geofeed validator
A Python script to validate geolocation data formatted as a geofeed according to [RFC8025](https://tools.ietf.org/html/rfc8025 "null"). The script checks for valid IP prefixes, and correct country and region codes against the ISO 3166-2 dataset.  
After validation, the malformed records are printed to standard output with a description of the error.

## ISO 3166-2 dataset
The official 3166-2 paper as published by ISO is a PDF, and costs ~100USD. For simplicity this script use the [same dataset formated as CSV that can be downloaded for free from ip2location.com](https://www.ip2location.com/free/iso3166-2).

## Setup
1. Clone the repository or download the script.
2. Download the IP2Location ISO3166-2 data file: 
3. Place the CSV file named IP2LOCATION-ISO3166-2.CSV in the same directory as the script

## Usage
The script reads the geofeed from `stdin`. You can pipe a CSV file into it or enter data manually.

## Example
Assuming you have a file named `geolocation.csv` with the following content:
```
192.0.2.0/24,US,CA,Los Angeles,90001
2001:db8::/32,DE,BE,Berlin,10115
198.51.100.0/24,US,XYZ,"Fake City",12345
10.0.0.0/8,XX,,,""
999.999.999.999/99,US,CA,,""
```

You can validate it by running:
```
cat geolocation.csv | python3 rfc8025_validator.py
```

The script will output the records that failed validation, prefixed with an error message:
```
Wrong region code: 198.51.100.0/24,US,XYZ,Fake City,12345
Wrong country code: 10.0.0.0/8,XX,,,
Invalid prefix: 999.999.999.999/99,US,CA,,
```
 
