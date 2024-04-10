import os,json,base64,json
def sparta_1651948b09():A=os.path.dirname(__file__);B=os.path.dirname(A);return json.loads(open(B+'/platform.json').read())['PLATFORM']
def sparta_4168c15b51(b):return base64.b64decode(b).decode('utf-8')
def sparta_6c710a790c(s):return base64.b64encode(s.encode('utf-8'))