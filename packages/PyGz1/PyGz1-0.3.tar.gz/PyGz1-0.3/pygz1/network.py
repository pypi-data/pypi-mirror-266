import requests
import socket
import subprocess
import os
import platform

def fetch_url(url):
    response = requests.get(url)
    return response.text

def post_data(url, data):
    response = requests.post(url, data=data)
    return response.text

def download_file(url, filename):
    response = requests.get(url)
    with open(filename, 'wb') as f:
        f.write(response.content)

def get_json(url):
    response = requests.get(url)
    return response.json()

def get_headers(url):
    response = requests.head(url)
    return response.headers

def get_ip_address(domain):
    return socket.gethostbyname(domain)

def check_host(hostname):
    result = subprocess.run(['ping', '-c', '1', hostname], stdout=subprocess.PIPE)
    return result.returncode == 0

def execute_command(command):
    result = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    return result.stdout.strip()

def get_system_info():
    info = {
        "System": platform.system(),
        "Node Name": platform.node(),
        "Release": platform.release(),
        "Version": platform.version(),
        "Machine": platform.machine(),
        "Processor": platform.processor()
    }
    return info

def list_files(directory):
    return os.listdir(directory)

def create_directory(directory):
    os.makedirs(directory, exist_ok=True)

def delete_file(filename):
    if os.path.exists(filename):
        os.remove(filename)
        return True
    else:
        return False

def rename_file(old_name, new_name):
    if os.path.exists(old_name):
        os.rename(old_name, new_name)
        return True
    else:
        return False

def get_file_size(filename):
    if os.path.exists(filename):
        return os.path.getsize(filename)
    else:
        return None
    
def check_github_file(owner, repo, file_path, expected_content, token=None):
    # Формируем URL для получения содержимого файла
    url = f"https://raw.githubusercontent.com/{owner}/{repo}/main/{file_path}"

    try:
        # Отправляем запрос к API GitHub
        response = requests.get(url)

        # Если запрос завершился успешно
        if response.status_code == 200:
            # Получаем содержимое файла
            file_content = response.text.strip()

            # Проверяем, совпадает ли содержимое файла с ожидаемым содержимым
            if file_content != expected_content:
                messagebox.showinfo("Изменения в файле", f"Содержимое файла изменилось:\n\n{file_content}")
            else:
                print("Содержимое файла не изменилось.")
        else:
            print(f"Не удалось получить содержимое файла {file_path} из репозитория.")
    except requests.RequestException as e:
        print("Не удалось проверить файл на GitHub:", e)