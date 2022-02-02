#!/usr/bin/env python3
import argparse
import json
import requests

from collections import defaultdict

ACCESS_TOKEN = "<ACCESS_TOKEN>"

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
    # Store the paginated data in here
    data = []

    # This might work for our request
    response = requests.get("https://graph.facebook.com/v5.0/ads_archive", params={
        "access_token": ACCESS_TOKEN,
        "ad_type": "POLITICAL_AND_ISSUE_ADS",
        "ad_active_status": "ALL",
        "search_page_ids": "100801038449520",
        "ad_reached_countries": ["US"],
        "ad_delivery_date_min": "2020-09-01",
        "ad_delivery_date_max": "2020-12-31",
        "fields": "id, ad_delivery_start_time, ad_delivery_stop_time, ad_snapshot_url, bylines, delivery_by_region, demographic_distribution, impressions, publisher_platforms, spend"
    })

    # Get the json document and pull out the next link and the data
    json = response.json()
    next_link = json['paging']['next']
    data = data + json['data']

    # Loop through the next links and collect the data
    while next_link:
        response = requests.get(next_link)
        json = response.json()
        if 'paging' not in json:
            break
        next_link = json['paging']['next']
        data = data + json['data']

    # DEBUG (BNR): Uncomment if you need to test with a file instead of requests
    # with open("data.json", "r") as f:
    #    data = json.loads(f.read())

    total_impressions = 0
    total_impressions_by_region = defaultdict(int)
    for d in data["data"]:
        try:
            # Calculate different impression data
            impressions = calculate_impressions_midpoint(d)
            impressions_by_region = calculate_impressions_by_region(d, impressions)

            # Aggregate impressions
            total_impressions = impressions + total_impressions
            for k, v in impressions_by_region.items():
                total_impressions_by_region[k] += v

        except Exception:
            pass

    # Log out the impressions by region
    print(f"Total impressions: {total_impressions}")
    print("Total impressions by region:")
    for k, v in total_impressions_by_region.items():
        print(f"\t{k}: {v}")


# This is a python convention for creating scripts
if __name__ == "__main__":
    main()
