import os, sys, json, cloudpickle, warnings
import pandas as pd
from IPython.core.display import display, HTML
from IPython.display import IFrame

current_path = os.path.dirname(__file__)
base_project = os.path.dirname(current_path)
sys.path.insert(0, current_path)
sys.path.insert(0, base_project)

from spartaqube_utils import get_ws_settings, request_service
import spartaqube_install as spartaqube_install
warnings.filterwarnings("ignore", category=UserWarning)

class Spartaqube:

    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, api_key=None):
        spartaqube_install.entrypoint()
        self._set_api_key(api_key)

    def _set_api_key(self, api_key=None):
        api_key_env = os.getenv('SPARTAQUBE_API_KEY', None)
        if api_key_env is not None:
            self.api_key = api_key_env
            self._prepare_ws_settings()
            return
        
        if api_key is not None:
            self.api_key = api_key
            
        self._prepare_ws_settings()
        
    def _prepare_ws_settings(self):
        '''
        Prepare web services settings
        '''
        if hasattr(self, 'api_key'):
            self.domain_or_ip, self.api_token_id = get_ws_settings(self.api_key)
        else:
            local_port = spartaqube_install.get_local_port()
            if local_port is not None:
                self.domain_or_ip = f'http://localhost:{local_port}'
                self.api_token_id = 'public'
            else:
                raise Exception('SpartaQube is not running...')
            
    def get_common_api_params(self) -> dict:
        return {
            'api_token_id': self.api_token_id,
        }

    def get_status(self):
        data_dict = self.get_common_api_params()
        return self.query_service('get_status', data_dict)

    # def get_library(self) -> list:
    #     data_dict = self.get_common_api_params()
    #     return self.query_service('get_library', data_dict) 

    def get_library(self) -> list:
        return self.get_widgets()

    def get_widgets(self) -> list:
        data_dict = self.get_common_api_params()
        return self.query_service('get_widgets', data_dict)
    
    def get_widget(self, widget_id, width='60%', height=500):
        return HTML(f'<iframe src="{self.domain_or_ip}/plot-widget?id={widget_id}" width="{width}" height="{height}" frameborder="0" allow="clipboard-write"></iframe>')
        # return IFrame(src=f"{self.domain_or_ip}/plot-widget?id={widget_id}&api_token_id={self.api_token_id}", width=width, height=height)
        
    def get_widget_data(self, widget_id) -> list:
        '''
        Get widget data
        '''
        data_dict = self.get_common_api_params()
        data_dict['widget_id'] = widget_id
        res_dict = self.query_service('get_widget_data', data_dict)
        if res_dict['res'] == 1:
            res_list = []
            for json_data in res_dict['data']:
                data_dict = json.loads(json_data)
                res_list.append(pd.DataFrame(data=data_dict['data'], index=data_dict['index'], columns=data_dict['columns']))
            return res_list

        return res_dict

    def new_plot(self, *argv, width='100%', height=600):
        '''
        Create a new plot widget component using notebook variables
        '''
        if len(argv) == 0:
            raise Exception('You must pass at least one input variable to plot')
        else:
            data_dict = self.get_common_api_params()
            data_dict['data'] = cloudpickle.dumps(argv).decode('latin1')
            res_session_dict = self.query_service('new_plot_api_variables', data_dict)
            # print("res_session_dict")
            # print(res_session_dict)
            if res_session_dict['res'] == 1:
                session_id = res_session_dict['session_id']
                # return IFrame(src=f"{self.domain_or_ip}/plot-new-api?session={session_id}&api_token_id={self.api_token_id}", width=width, height=height)
                return HTML(f'<iframe src="{self.domain_or_ip}/plot-new-api?session={session_id}&api_token_id={self.api_token_id}" width="{width}" height="{height}" frameborder="0" allow="clipboard-write"></iframe>')
            else:
                print("An error occurred, could not start a new SpartaQube plot session...")

    def plot_data(self, widget_id, xAxis:list=None, yAxisArr:list=None, labelsArr:list=None, radiusBubbleArr:list=None,
            rangesAxisArr:list=None, measuresAxisArr:list=None, markersAxisArr:list=None, width='60%', height=600):
        '''
        Plot data using existing widget template
        '''
        data_dict = self.get_common_api_params()
        data_dict['widget_id'] = widget_id
        data_dict['data'] = cloudpickle.dumps(
            {
                'xAxis': xAxis, 'yAxisArr': yAxisArr, 
                'labelsArr': labelsArr, 'radiusBubbleArr': radiusBubbleArr, 
                'rangesAxisArr': rangesAxisArr, 'measuresAxisArr': measuresAxisArr, 'markersAxisArr': markersAxisArr
            }
        ).decode('latin1')
        res_session_dict = self.query_service('new_plot_api_variables', data_dict)
        if res_session_dict['res'] == 1:
            session_id = res_session_dict['session_id']
            return HTML(f'<iframe src="{self.domain_or_ip}/plot-widget?id={widget_id}&session={session_id}&api_token_id={self.api_token_id}" width="{width}" height="{height}" frameborder="0" allow="clipboard-write"></iframe>')
            # return IFrame(src=f"{self.domain_or_ip}/plot-widget?id={widget_id}&session={session_id}&api_token_id={self.api_token_id}", width=width, height=height)

        else:
            print("An error occurred, could not start a new Spartaqube plot session...")

    def get_connectors(self):
        data_dict = self.get_common_api_params()
        return self.query_service('get_connectors', data_dict)

    def get_data_from_connector():
        pass

    def query_service(self, service_name:str, data_dict:dict) -> dict:
        '''
        POST requests
        '''
        return request_service(self, service_name=service_name, data_dict=data_dict)

    def stop_server(self):
        spartaqube_install.stop_server()