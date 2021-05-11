"""
This script downloads Sentinel-1 data. A Geojson or a shapefile over the area
we are interested in to collect data should be provided. Additional arguments
can be provided when searching for data (e.g search by product type or satellite orbit)

usage: download_sentinel1.py [-h] [-o OUTDIR] [-aoi FOOTPRINT] [-s START_DATE]
                             [-e END_DATE] [-t PRODUCT_TYPE]
                             [-p PASS_DIRECTION] [-d] [--online]

optional arguments:
  -h, --help            show this help message and exit
  -o OUTDIR, --outdir OUTDIR
                        Specify an output directory
  -aoi FOOTPRINT, --footprint FOOTPRINT
                        Specify a directory path to a Geojson or shapefile to
                        be used as a footprint for searching S1 data
  -s START_DATE, --start_date START_DATE
                        Specify start date for searching data from
                        syntax:YYYYMMDD
  -e END_DATE, --end_date END_DATE
                        Specify end date for searching data to syntax:YYYYMMDD
  -t PRODUCT_TYPE, --product_type PRODUCT_TYPE
                        Specify product type (valid product types: GRD, SLC or
                        OCN)
  -p PASS_DIRECTION, --pass_direction PASS_DIRECTION
                        Specify orbit (valid orbits: ascending or descending)
  -d, --download        Download the prodcuts found
  --online              check if requested product is online or offline


Examples
----------

Find the number of scenes acquired over our AOI in ascending orbit
------------------------------------------------------------------
python3 download_sentinel1.py -s 20190201 -e 20190816 -aoi aoi/AOI.geojson -p ascending


Check if the scenes we are interested in are online
------------------------------------------------------------------
python3 download_sentinel1.py -s 20190201 -e 20190816 -aoi aoi/AOI.geojson -p ascending --online

Download all SAR scenes found
------------------------------------------------------------------
python3 download_sentinel1.py -s 20190201 -e 20190816 -aoi aoi/AOI.geojson -p ascending -d

"""

import argparse
from pathlib import Path
import os
from datetime import datetime
import datetime
import shapely
import json
from sentinelsat import SentinelAPI, read_geojson, geojson_to_wkt
import numpy as np
import pandas as pd


def sentinel_api(user, password):
    """Connect the the API

    parameters
    ----------
    user: provide the username
    password: provide the password
    """
    api_url = "https://scihub.copernicus.eu/dhus/"
    # api query
    api = SentinelAPI(
        user=user,
        password=password,
        api_url=api_url)
    return api


def query(footprint_path,
          start_date,
          end_date,
          prod_type=None,
          pass_direction=None):
    """Searches for products over the footprint

    parameters
    ----------
    footprint_path: provide the path to the footprint vector file
    start_date: provide the start date to search from
    end_date: provide the end date to search to
    prod_type: provide product type (GRD,SLC,OCN)
    pass_direction: provide orbit (ascending or descending)
    """
    user = os.environ['user']
    password = os.environ['password']
    api = sentinel_api(user, password)
    # search by polygon using a Geojson
    footprint = geojson_to_wkt(read_geojson(footprint_path))

    # create a dataframe with the dates specified
    # so we can be able to perform operations
    date = [start_date, end_date]
    values = {'dates': date}
    df = pd.DataFrame(values, columns=['dates'])
    df['dates'] = pd.to_datetime(df['dates'], format='%Y%m%d')

    assert (df['dates'][0] < df['dates'][1]
            ), f"The start date {df['dates'][0]} must be smaller than the end date {df['dates'][1]}"

    if prod_type is None and pass_direction is None:
        products = api.query(footprint,
                             date=(date[0], date[1]),
                             platformname='Sentinel-1',
                             )
        print(f'{len(products)} scenes have been found in total', '\n')

    elif pass_direction and not prod_type:
        products = api.query(footprint,
                             date=(date[0], date[1]),
                             platformname='Sentinel-1',
                             orbitdirection=pass_direction
                             )
        print(f'{len(products)} scenes have been found in total', '\n')

    elif prod_type and not pass_direction:
        products = api.query(footprint,
                             date=(date[0], date[1]),
                             platformname='Sentinel-1',
                             producttype=prod_type
                             )
        print(f'{len(products)} scenes have been found in total', '\n')

    else:
        products = api.query(footprint,
                             date=(date[0], date[1]),
                             platformname='Sentinel-1',
                             producttype=prod_type,
                             orbitdirection=pass_direction
                             )
        print(f'{len(products)} scenes have been found in total', '\n')
    return api.to_dataframe(products)


def is_online(products):
    """Check whether the requested products are online

    parameters
    ----------
    products: pandas dataframe containing the products \
              derived from the query funtion
    """
    user = os.environ['user']
    password = os.environ['password']
    api = sentinel_api(user, password)

    products_online = []
    products_offline = []
    for i, row in products.iterrows():
        product = row[['title', 'uuid', 'beginposition']]
        date = product['beginposition']
        date_str = date.strftime('%Y-%m-%d')
        uuid = product['uuid']
        meta = api.get_product_odata(uuid)
        if meta['Online']:
            products_online.append(meta['title'])
        else:
            products_offline.append(meta['title'])

    if len(products_offline) == 0 and len(products_online) > 0:
        print(
            f" All products requested({len(products_online)}) are online",
            '\n')
        online = [print(prod) for prod in products_online]
    elif len(products_offline) > 0 and len(products_online) == 0:
        print(
            f"All products requested ({len(products_offline)}) are offline",
            '\n')
        offline = [print(prod) for prod in products_offline]
    else:
        print(
            f"{len(products_online)} online and {len(products_offline)} offline products have been found",
            '\n')
        print('Online products', '\n')
        online = [print(prod) for prod in products_online]
        print('offline products', '\n')
        offline = [print(prod) for prod in products_offline]


def download(products,
             output):
    """Check whether the requested products are online

    parameters
    ----------
    products: pandas dataframe containing the products \
              derived from the query funtion
    output: Specify output path
    """
    user = os.environ['user']
    password = os.environ['password']
    api = sentinel_api(user, password)

    for i, row in products.iterrows():
        product = row[['title', 'uuid', 'beginposition']]
        date = product['beginposition']
        date_str = date.strftime('%Y-%m-%d')
        uuid = product['uuid']
        meta = api.get_product_odata(uuid)
        if meta['Online']:
            print('Product {} is online.'.format(meta['title']))
            api.download(product['uuid'], output)
        else:
            print('Product {} is not online.'.format(meta['title']))


if __name__ == "__main__":

    parser = argparse.ArgumentParser()

    parser.add_argument(
        '-o',
        '--outdir',
        required=False,
        help='Specify an output directory'
    )

    parser.add_argument(
        '-aoi',
        '--footprint',
        required=False,
        help='Specify a directory path to a Geojson or shapefile \
            to be used as a footprint for searching S1 data'
    )

    parser.add_argument(
        '-s',
        '--start_date',
        required=False,
        help='Specify start date for searching data from \
             syntax:YYYYMMDD'
    )

    parser.add_argument(
        '-e',
        '--end_date',
        required=False,
        help='Specify end date for searching data to \
             syntax:YYYYMMDD'
    )

    parser.add_argument(
        '-t',
        '--product_type',
        required=False,
        help='Specify product type (valid product types: GRD, SLC or OCN)'
    )

    parser.add_argument(
        '-p',
        '--pass_direction',
        required=False,
        help='Specify orbit (valid orbits: ascending or descending)'
    )

    parser.add_argument(
        '-d',
        '--download',
        action='store_true',
        help='Download the prodcuts found'
    )

    parser.add_argument(
        '--online',
        action='store_true',
        help='check if requested product is online or offline'
    )

    args = parser.parse_args()

    if not args.footprint:
        parser.error(
            'Please provide a path to the footprint file(use option -aoi) to be used '
            'as AOI for searching S1 data. The file format can be either Geojson or shapefile')

    if not args.start_date or not args.end_date:
        parser.error(
            'Please provide a start and an end date to search for data')

    elif args.product_type and not args.pass_direction:
        if args.product_type not in ['GRD', 'SLC', 'OCN']:
            print(f"The product specified {args.product_type} does not exist."
                  " Valid products: GRD, SLC or OCN")
        else:
            products = query(
                args.footprint,
                args.start_date,
                args.end_date,
                prod_type=args.product_type)

    elif args.pass_direction and not args.product_type:
        if args.pass_direction not in ['ascending', 'descending']:
            print(f"The orbit specified {args.pass_direction} does not exist."
                  " Valid orbits: ascending or descending")
        else:
            products = query(
                args.footprint,
                args.start_date,
                args.end_date,
                pass_direction=args.pass_direction)

    elif args.pass_direction and args.product_type:
        if args.pass_direction not in [
                'ascending',
                'descending'] or args.product_type not in [
                'GRD',
                'SLC',
                'OCN']:
            print(
                f"Please make sure valid product types and valid orbits have been specified \n"
                " Valid orbits: ascending or descending \n valid products: GRD, SLC and OCN")
        else:
            products = query(
                args.footprint,
                args.start_date,
                args.end_date,
                prod_type=args.product_type,
                pass_direction=args.pass_direction)

    else:
        products = query(args.footprint, args.start_date, args.end_date)

    if args.online:
        is_online(products)

    if args.download and not args.outdir:
        path = Path.cwd()
        download(products, path)

    elif args.download and args.outdir:
        download(products, args.outdir)
