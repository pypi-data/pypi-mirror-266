from pathlib import Path
from src.core_pro import Gcloud


path = Path.home() / 'PycharmProjects/retrieval/token_json/shopee-vn-product-team.json'
blob_path = 'vm_matching_result'
file_path = Path.home() / 'PycharmProjects/retrieval/data/20240129/db.parq'
Gcloud(str(path)).upload_file(blob_path, file_path)
url = Gcloud(str(path)).generate_download_signed_url_v4('vm_matching_result/db.parq', minutes=60)
