import requests
from PIL import Image
from io import BytesIO
import os
import pandas as pd
import io

species = 9606


def net(protein_name):

    STRING_network = "https://string-db.org/api/image/network"

    parameters = {
        "identifiers": protein_name,
        "species": species,
        "networ k_flavor": "physical interactions"
    }

    http_response_1 = requests.get(STRING_network, params=parameters)

    if http_response_1.status_code == 200:

        network = Image.open(BytesIO(http_response_1.content))
        new_network = Image.new("RGB", network.size, "white")
        new_network.paste(network, (0, 0), network)
        
        directory = 'img_cache'
        if not os.path.exists(directory):
            os.makedirs(directory)

        img_path = os.path.join(directory, f"{protein_name}_network_image.png")
        new_network.save(img_path)
    else:
        print(f"Error > Status code: {http_response_1.status_code}")


def get_partners(protein_name):
    STRING_partner = "https://string-db.org/api/tsv/interaction_partners"

    parameters_partners = {
        "identifiers": protein_name,
        "species": species
    }

    http_response_2 = requests.get(STRING_partner, params=parameters_partners)

    if http_response_2.status_code == 200:
        df = pd.read_csv(io.StringIO(http_response_2.text), sep='\t')
        print(df)  

        directory_csv = 'interaction_partner_data'
        if not os.path.exists(directory_csv):
            os.makedirs(directory_csv)
        
        csv_file_path = os.path.join(directory_csv, f"{protein_name}_interaction_partners.csv")
        df.to_csv(csv_file_path, index=False)

    else:
        print(f"Error > Status code: {http_response_2.status_code}")




