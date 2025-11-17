from oauthlib.oauth2 import BackendApplicationClient
from requests_oauthlib import OAuth2Session
import os
import json
import requests
import logging
import urllib
import boto3
import shutil
import user_inputs as inp


download_folder = "folder path"

# Vos identifiants de client
# If you don't have any user/pass, register at https://dataspace.copernicus.eu
# Username and Password below should be inside quotation marks ("").
client_id = "YOUR_CLIENT_ID",
client_secret = "YOUR_SECRET"

def get_keycloak(client_id: str, client_secret: str) -> str:
    data = {
        "grant_type": "client_credentials",
        "client_id": inp.client_id,
        "client_secret": inp.client_secret,
     
        }
    try:
        r = requests.post("https://identity.dataspace.copernicus.eu/auth/realms/CDSE/protocol/openid-connect/token",
        data=data,
        )
        r.raise_for_status()
    except Exception as e:
        raise Exception(
            f"Keycloak token creation failed. Reponse from the server was: {r.json()}"
            )
    return r.json()["access_token"]




# Créer une session
client = BackendApplicationClient(client_id=client_id)
oauth = OAuth2Session(client=client)

# Obtenir le jeton pour la session
token = oauth.fetch_token(token_url='https://identity.dataspace.copernicus.eu/auth/realms/CDSE/protocol/openid-connect/token',
                          client_secret=client_secret, include_client_id=True)

# Votre requête pour télécharger les données
## corse bbox [9.448360, 42.597807, 10.116206, 42.837569]
### Jamestown bbox [-0.228033, 5.526456 , -0.210153, 5.532696]
## Topouzelis_zone  "bbox": [26.562476, 39.105150 , 26.568298 , 39.109634 ]
data = {
    "bbox": [-0.228033, 5.526456 , -0.210153, 5.532696 ],
    "datetime": "2020-06-01T00:00:00Z/2020-06-20T00:00:00Z",
    "collections": ["sentinel-2-l1c"], ## or sentinel-2-l2A
    "limit": 100,
    #"next": 2,
    "filter": "eo:cloud_cover < 70",
}

url = "https://sh.dataspace.copernicus.eu/api/v1/catalog/1.0.0/search"
response = oauth.post(url, json=data)
print("resultat de reponse:  ",  response.status_code)

# Vérifier le statut de la réponse
if response.status_code == 200:
    print("La requête de téléchargement des données a été réussie.")
    # Spécifier le dossier où enregistrer les données téléchargées
    folder_path = "folder path for file .txt"
    file_path = os.path.join(folder_path, "donnees_telechargees.txt")
    # Enregistrer les données dans un fichier local
    with open(file_path, 'w') as f:
        f.write(response.text)
    print("Les données ont été enregistrées avec succès dans :", file_path)
else:

    print("Il y a eu un problème avec la requête de téléchargement des données. Statut de la réponse :", response.status_code)


keycloak_token = get_keycloak("client_id", "client_secret")

# Créer une session OAuth2
session = OAuth2Session(client=client, token=token)

# Mettre à jour les en-têtes de la session avec le jeton d'authentification
session.headers.update({'Authorization': f'Bearer {keycloak_token}'})

# Récupérer les données de recherche au format JSON
json_data = response.json()

folder_path = "folder path for file .txt"
file_path = os.path.join(folder_path, "json_data.json")

with open(file_path, 'w') as outfile:
    json.dump(json_data, outfile)


# Récupérer l'URL de téléchargement à partir du résultat JSON
#download_url = json_data['features'][0]['assets']['data']['href']
# Charger le JSON
data = json_data

# Extraire les liens commençant par "s3"
download_url = [feature['assets']['data']['href'] for feature in data['features'] if feature['assets']['data']['href'].startswith('s3')]

print(download_url)

################################################################################################################
################################################################################################################
#                         TELECHARGEMENT DES IMAGES SENTINEL-2
################################################################################################################           
## identifian s3
# If you don't have any creditential generate here https://eodata-s3keysmanager.dataspace.copernicus.eu/panel/s3-credentials
# Username and Password below should be inside quotation marks ("").
#s3_acces_key = "YOUR_AWS_KEY",
#s3_secret_key = "YOUR_AWS_SECRET",

session = boto3.session.Session()
s3 = boto3.resource(
    's3',
    endpoint_url='https://eodata.dataspace.copernicus.eu',
    aws_access_key_id= "YOUR_AWS_KEY",
    aws_secret_access_key= "YOUR_AWS_SECRET",
    region_name= 'default'
)  

def download(s3_resource, product_url: str, target: str = "") -> None:
    
    """ Télécharge chaque fichier dans le bucket avec l'URL de produit fournie comme préfixe

    #Lève FileNotFoundError si le produit n'est pas trouvé

    #Args:
     #   s3_resource: Objet s3.ServiceResource de boto3
      #  product_url: URL du produit à télécharger
      #  target: Répertoire local pour les fichiers téléchargés. Doit se terminer par un '/'. Par défaut, le répertoire courant.
    """
   
    # Extraire le nom du seau et le chemin du produit de l'URL
    bucket_name, product_key = product_url.split("/", 3)[-2:]
    
    # Obtenir l'objet s3.Bucket correspondant au nom du seau
    bucket = s3_resource.Bucket(bucket_name)

    # Filtrer les objets du seau avec le préfixe du produit
    files = bucket.objects.filter(Prefix=product_key)
    if not list(files):
        raise FileNotFoundError(f"Aucun fichier trouvé pour {product_url}")
   
       
   # Télécharger chaque fichier
    for file in files:
        os.makedirs(os.path.dirname(file.key), exist_ok=True)
        if not os.path.isdir(file.key):
            bucket.download_file(file.key, f"{target}{file.key}")

# Récupérer l'URL de téléchargement à partir du résultat JSON
product_urls = download_url 

# Télécharger chaque fichier du produit
for url in product_urls:
    download(s3, url)

print("Tous les fichiers ont été téléchargés avec succès dans le dossier :", download_folder)

##parcourir selectionner tous les dossier .SAFE et les mettre dans nouvel repertoire
######################################################################################
#######################################################################################
######################################################################################

# Chemin du dossier "sentinel-2"
sentinel_2_folder = "folder path where download stock automatically same path of .py file"

# Chemin du dossier "data_sentinel" 
data_sentinel_folder = "folder path where download will move after"

# Parcours de tous les dossiers dans le dossier "sentinel-2"
for root, dirs, files in os.walk(sentinel_2_folder):
    for dir in dirs:
        # Vérifier si le dossier se termine par ".SAFE"
        if dir.endswith(".SAFE"):
            # Construire le chemin complet du dossier
            source_folder = os.path.join(root, dir)
            
            # Extraire les 44 premières lettres du nom du dossier
            new_subfolder_name = dir[:44]
            
            # Construire le chemin complet du nouveau sous-dossier dans "data_sentinel"
            target_subfolder = os.path.join(data_sentinel_folder, new_subfolder_name)
            
            # Créer le nouveau sous-dossier s'il n'existe pas déjà
            os.makedirs(target_subfolder, exist_ok=True)
            
            # Déplacer le dossier ".SAFE" vers le nouveau sous-dossier
            shutil.move(source_folder, target_subfolder)

print("Déplacement des dossiers terminé.")

# Supprimer le dossier "sentinel-2"
shutil.rmtree(sentinel_2_folder)
print("Le dossier sentinel-2 a été supprimé avec succès.")
