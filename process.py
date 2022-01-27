#!/usr/bin/env python3
import argparse
import json

from collections import defaultdict

def calculate_impressions_midpoint(data):
    """Calculate impressions midpoint"""
    # Convert from a string of characters into an integer
    upper_bound = int(data["impressions"]["upper_bound"])
    lower_bound = int(data["impressions"]["lower_bound"])

    return round((upper_bound + lower_bound) / 2)

def calculate_impressions_by_region(data, impressions):
    """Calculate impressions by regions"""
    # Create a new dict to contain the results
    result = {}

    # Loop through each region and calculate the impressions
    for chunk in data["delivery_by_region"]:
        result[chunk["region"]] = round(impressions * float(chunk["percentage"]))

    return result

def calculate_impressions_by_gender(data, impressions):
    """Calculates impressions by gender"""
    # Create a new dict to contain the results. The categories are pre-populated with 0s.
    results = {"male": 0, "female": 0, "unknown": 0}

    # Loop through demographic data
    for d in data["demographic_distribution"]:
        # Let's break this expression down:
        # 1. result[d["gender"]] looks for the key in the result dict that matches d["gender"]
        # 2. += is a short hand operator for addition and assignment. e.g. foo +=1 is the same
        #    as foo = foo + 1
        # 3. float(d["percentage"]) converts the JSON data into a decimal number (programmers
        #    call those floats because the decimal can move around).
        # 4. round(impressions * float(d["percentage"])) multiplies the percentage by the
        #    impressions and rounds up to the nearest integer
        results[d["gender"]] += round(impressions * float(d["percentage"]))

    return results

def calculate_impressions_by_age(data, impressions):
    """Calculate impressions by age"""
    # Create a new default dict to contain the results. The default dict makes any new element
    # default to a value specified by the user. In our case we're defaulting to an integer 0.
    # int is actually a function that retuns 0 when called with no arguments
    results = defaultdict(int)

    # Loop through the demographic data and add up the impressions
    for d in data["demographic_distribution"]:
        # Let's break this expression down:
        # 1. result[d["age"]] looks for the key in the result dict that matches d["age"]. If
        #    there is no key that matches d["age"] the default dict will make one with the value
        #    of int(), which is always 0.
        # 2. += is a short hand operator for addition and assignment. e.g. foo +=1 is the same
        #    as foo = foo + 1
        # 3. float(d["percentage"]) converts the JSON data into a decimal number (programmers
        #    call those floats because the decimal can move around).
        # 4. round(impressions * float(d["percentage"])) multiplies the percentage by the
        #    impressions and rounds up to the nearest integer
        results[d["age"]] += round(impressions * float(d["percentage"]))

    return results

def main():
    """Entrypoint of the program"""
    # Tell python to read in an argument named "file" from the command line
    parser = argparse.ArgumentParser(description="Basic analysis of FB ad data")
    parser.add_argument("file", type=str)

    # This might work for our request
    # response = requests.get("https://graph.facebook.com/v5.0/ads_archive", params={
    #     "access_token": "<YOUR ACCESS TOKEN HERE>",
    #     "ad_type": "POLITICAL_AND_ISSUE_ADS",
    #     "ad_active_status": "ALL",
    #     "search_page_ids": "100801038449520",
    #     "ad_reached_countries": "[US]",
    #     "ad_delivery_date_min": "2020-09-01",
    #     "ad_delivery_date_max": "2021-12-31",
    #     "fields": "id, ad_delivery_start_time, ad_delivery_stop_time, ad_snapshot_url, bylines, delivery_by_region, demographic_distribution, impressions, publisher_platforms, spend"
    # })
    # data = response.json()

    # Open the file passed in as an argument and convert it into a python dict
    args = parser.parse_args()
    with open(args.file, "r") as f:
        data = json.loads(f.read())

    # Grab the first object from the data array
    d = data["data"][0]

    # Calculate different impression data
    impressions = calculate_impressions_midpoint(d)
    impressions_by_region = calculate_impressions_by_region(d, impressions) 
    impressions_by_gender = calculate_impressions_by_gender(d, impressions)
    impressions_by_age = calculate_impressions_by_age(d, impressions)

    # Log the data
    print("Impressions by region:")

    # This for loop takes each key value pair and prints them.
    # The .items() call returns the key, value pairs as tuples and the (k, v)
    # saves the key to k, and the value to v
    for (k, v) in impressions_by_region.items():
        # This is a format string, the {} tell python to replace what's inside
        # with the contents of a variable
        print(f"{k}: {v}")

    print("\nImpressions by gender:")
    for (k, v) in impressions_by_gender.items():
        print(f"{k}: {v}")

    print("\nImpressions by age:")
    for (k, v) in impressions_by_age.items():
        print(f"{k}: {v}")

# This is a python convention for creating scripts
if __name__ == "__main__":
    main()
