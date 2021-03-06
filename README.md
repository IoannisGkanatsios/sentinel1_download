# Download Sentinel-1 scenes

**Credentials**

Create a `.env` file and add the credentials required to log into [sentinel-hub](https://scihub.copernicus.eu/dhus/#/home). Add the following:

```
user="your username"

password="your password"
```

The `download_sentinel1.py` script looks into `.env` file for the `username` and `password`

**Run the script**

```
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
```

**Visualization**

Using the script within jupyter folder, we can visualize the SAR scenes over our AOI using a basemap
