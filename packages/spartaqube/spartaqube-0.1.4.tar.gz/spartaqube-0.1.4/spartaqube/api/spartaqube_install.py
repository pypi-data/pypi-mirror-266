import sys, os, subprocess, threading, socket, psutil, json

# **********************************************************************************************************************
def set_environment_variable(name, value):
    try:
        os.environ[name] = value
    except Exception as e:
        print(f"Error setting environment variable '{name}': {e}")

def set_environment_variable_persist(name, value):
    try:
        subprocess.run(['setx', name, value])
        # print(f"Environment variable '{name}' set to '{value}'")
    except Exception as e:
        # print(f"Error setting environment variable '{name}': {e}")
        pass

def find_process_by_port(port):
    for proc in psutil.process_iter(['pid', 'name', 'connections']):
        try:
            for conn in proc.connections():
                if conn.laddr.port == port:
                    return proc
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    return None

def is_port_available(port:int) -> bool:
    try:
        # Create a socket object
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            # Try to connect to the specified port
            s.bind(("localhost", port))
            return True
    except socket.error:
        return False
    
def generate_port() -> int:
    port = 8664
    while not is_port_available(port):
        port += 1

    return port
# **********************************************************************************************************************

def set_spartaqube_shortcut():
    '''
    Set spartaqube exec to env
    '''
    current_path = os.path.dirname(__file__)
    base_path = os.path.dirname(current_path)
    spartaqube_exec = os.path.join(base_path, 'cli/spartaqube')
    set_environment_variable_persist('spartaqube', spartaqube_exec)

def db_make_migrations():
    '''
    make migrations
    '''
    current_path = os.path.dirname(__file__)
    base_path = os.path.dirname(current_path)
    process = subprocess.Popen("python manage.py makemigrations", stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, cwd=base_path)
    stdout, stderr = process.communicate()
    if len(stderr) > 0:
        print(stderr.decode())

def db_migrate():
    '''
    migrate
    '''
    current_path = os.path.dirname(__file__)
    base_path = os.path.dirname(current_path)
    process = subprocess.Popen("python manage.py migrate", stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, cwd=base_path)
    stdout, stderr = process.communicate()
    if len(stderr) > 0:
        print(stderr.decode())

def create_public_user():
    '''
    Public user
    '''
    current_path = os.path.dirname(__file__)
    base_path = os.path.dirname(current_path)
    process = subprocess.Popen("python manage.py createpublicuser", stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, cwd=base_path)
    stdout, stderr = process.communicate()
    if len(stderr) > 0:
        print(stderr.decode())

def create_admin_user():
    '''
    Admin user
    '''
    current_path = os.path.dirname(__file__)
    base_path = os.path.dirname(current_path)
    process = subprocess.Popen("python manage.py createadminuser", stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, cwd=base_path)
    stdout, stderr = process.communicate()
    if len(stderr) > 0:
        print(stderr.decode())

def get_local_port():
    try:
        current_path = os.path.dirname(__file__)
        with open(os.path.join(current_path, 'app_data.json'), "r") as json_file:
            loaded_data_dict = json.load(json_file)
        
        return loaded_data_dict['port']
    except:
        return None

def is_application_running() -> bool:
    '''
    
    '''
    port = get_local_port()
    if port is None:
        return False
    else:
        if is_port_available(port):
            return False
        else:
            return True

def start_server(port=None):
    '''
    runserver at port
    '''

    if port is None:
        port = generate_port()
    else:
        if not is_port_available(port):
            port = generate_port()

    def thread_job():
        current_path = os.path.dirname(__file__)
        base_path = os.path.dirname(current_path)
        process = subprocess.Popen(f"python manage.py runserver {port} &", stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, cwd=base_path)
        stdout, stderr = process.communicate()
        if len(stderr) > 0:
            print(stderr.decode())
        
    t = threading.Thread(target=thread_job, args=())
    t.start()

    print(f"SpartaQube served on port {port}")
    print(f"GUI available at http://localhost:{port}")
    app_data_dict = {'port': port}
    current_path = os.path.dirname(__file__)
    with open(os.path.join(current_path, "app_data.json"), "w") as json_file:
        json.dump(app_data_dict, json_file)

def stop_server(port=None):
    if port is None:
        port = get_local_port()

    if port is not None:
        process = find_process_by_port(port)
        if process:
            print(f"Found process running on port {port}: {process.pid}")
            process.terminate()
            print(f"SpartaQube server stopped")
        else:
            print(f"No process found running on port {port}.")
    else:
        raise Exception("Port not specify")

def entrypoint(port=None, force_startup=False):
    '''
    
    '''
    print("Preparing SpartaQube, please wait...")
    if is_application_running() and not force_startup:
        print(f"Spartaqube is running on port {get_local_port()}")
    else:
        set_spartaqube_shortcut()
        db_make_migrations()
        db_migrate()
        create_public_user()
        create_admin_user()
        start_server(port=port)

if __name__ == '__main__':
    entrypoint()