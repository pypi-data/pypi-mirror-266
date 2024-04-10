import os
import base64
import json
import hashlib
import requests
from cryptography.fernet import Fernet

def get_ws_settings(api_key:str) -> list:
    return (Fernet(get_keygen_fernet().encode('utf-8'))).decrypt(base64.b64decode(api_key)).decode('utf-8').split('@')[1:]

def get_keygen_fernet() -> str:
    return base64.b64encode(hashlib.md5('spartaqube-api-key'.encode('utf-8')).hexdigest().encode('utf-8')).decode('utf-8')

def request_service(spartaqube_api_intance, service_name:str, data_dict:dict) -> dict:
    '''
    Web service request
    '''
    data_dict['api_service'] = service_name
    json_data_params = {
        'jsonData': json.dumps(data_dict)
    }
    headers = {
        "Content-Type": "application/json"
    }
    url = f"{spartaqube_api_intance.domain_or_ip}/api_web_service"
    res_req = requests.post(url, json=json_data_params, headers=headers)
    status_code = res_req.status_code
    if status_code != 200:
        print(f"An error occurred, status_code: {status_code}")
        return {
            'res': -1,
            'status_code': status_code,
        }

    return json.loads(res_req.text)

def upload_resources(spartaqube_api_intance, data_dict:dict, file_path:str) -> dict:
    '''
    Upload resources (file or folder)
    '''

    def upload_func(files):
        json_data_params = {
            'jsonData': json.dumps(data_dict)
        }
        headers = {
            "Content-Type": "application/json"
        }
        url = f"{spartaqube_api_intance.domain_or_ip}:{spartaqube_api_intance.http_port}/api_web_service"
        # print("url  > "+str(url))
        res_req = requests.post(url, json=json_data_params, headers=headers, files=files)
        status_code = res_req.status_code
        if status_code != 200:
            print(f"An error occurred, status_code: {status_code}")
            return {
                'res': -1,
                'status_code': status_code,
            }

        return json.loads(res_req.text)
    
    data_dict['api_service'] = 'upload'
    is_file = False
    if os.path.isfile(file_path):
        is_file = True

    if is_file:
        file_name, file_extension = os.path.splitext(os.path.basename(file_path))
        files = {'file': (f"{file_name}.{file_extension}", open(file_path, 'rb'))}
        return upload_func(files)
    else: # We are dealing with a folder, we are going to recursively upload each file
        pass
    