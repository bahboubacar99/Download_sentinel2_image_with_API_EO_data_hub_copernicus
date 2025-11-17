# Automated Download of Sentinel-2 Data from Copernicus Data Space
This Python script automates the search and download of Sentinel-2 images (L1C level or L2A) from the Copernicus Data Space Ecosystem. The data is filtered by geographical area, date range and cloud cover rate, then retrieved via S3 URLs and organised locally in a structured manner.

## Features
- OAuth2 authentication and Keycloak token retrieval for Copernicus APIs.
- Search for Sentinel-2 products by criteria (bbox, date, cloud cover, etc.).
- Secure download of .SAFE files via S3 access.
- Automatic organisation and relocation of downloaded files.
- Deletion of source files for efficient disk space management.

## Prerequisites
- Python 3.8 or higher
- Copernicus Data Space access (client_id/client_secret)
- Copernicus S3 access (AWS Access Key/Secret)
- Python packages: oauthlib, requests-oauthlib, requests, boto3, shutil
- Create a user_inputs.py file with your login credentials.
- 
## Install the necessary libraries
pip install oauthlib requests-oauthlib requests boto3

## Path configuration
Modify these variables in the script according to your folder structure:

download_folder: temporary folder for initial download
folder_path: folder for saving text and JSON query files
sentinel_2_folder: where .SAFE files are stored immediately after download
data_sentinel_folder: final structured destination for .SAFE files

## Obtaining credentials
Create an account on [dataspace copernicus](https://dataspace.copernicus.eu) to authenticate your application with the Copernicus Data Space API to obtain an access token.
Generate S3 credentials via this [link](https://eodata-s3keysmanager.dataspace.copernicus.eu/panel/s3-credentials) to access files stored in the Copernicus S3 cloud directly to download Sentinel products (.SAFE). See documentation [here](https://documentation.dataspace.copernicus.eu/APIs/S3.html)

## Limitations
- The script remains linear, without advanced multi-threading or parallelism management (can be added).
- Network errors (timeouts, quota exceeded) are not yet managed in a granular manner.
- For other collections or images, adapt the data request.

## Credits
Sentinel-2 data provided by the Copernicus programme, European Commission.

