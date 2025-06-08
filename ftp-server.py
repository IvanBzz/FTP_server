import os
import shutil
import socket
import logging
from datetime import datetime

# Настройки сервера
HOST = 'localhost'
PORT = 9090
SERVER_ROOT = os.path.join(os.getcwd(), 'server_files')  # Корневая директория сервера

# Настройка логирования
logging.basicConfig(
    filename='ftp_server.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)


def ensure_server_root():
    """Создает корневую директорию сервера, если ее нет"""
    if not os.path.exists(SERVER_ROOT):
        os.makedirs(SERVER_ROOT)
        logging.info(f"Created server root directory: {SERVER_ROOT}")


def process_request(request, current_dir=SERVER_ROOT):
    """Обрабатывает запросы клиента"""
    try:
        parts = request.split(maxsplit=2)
        if not parts:
            return "ERROR: Empty request"

        cmd = parts[0].lower()

        # Безопасное получение абсолютного пути
        def get_safe_path(path):
            path = os.path.join(current_dir, path)
            abs_path = os.path.abspath(path)
            if not abs_path.startswith(os.path.abspath(SERVER_ROOT)):
                raise PermissionError("Access denied: trying to access outside server root")
            return abs_path

        # Команды
        if cmd == 'pwd':
            return current_dir

        elif cmd == 'ls':
            files = os.listdir(current_dir)
            return '\n'.join(files)

        elif cmd == 'mkdir' and len(parts) > 1:
            dir_path = get_safe_path(parts[1])
            os.mkdir(dir_path)
            logging.info(f"Created directory: {dir_path}")
            return f"Directory '{parts[1]}' created"

        elif cmd == 'rmdir' and len(parts) > 1:
            dir_path = get_safe_path(parts[1])
            os.rmdir(dir_path)
            logging.info(f"Removed directory: {dir_path}")
            return f"Directory '{parts[1]}' removed"

        elif cmd == 'rm' and len(parts) > 1:
            file_path = get_safe_path(parts[1])
            os.remove(file_path)
            logging.info(f"Removed file: {file_path}")
            return f"File '{parts[1]}' removed"

        elif cmd == 'rename' and len(parts) > 2:
            old_path = get_safe_path(parts[1])
            new_path = get_safe_path(parts[2])
            os.rename(old_path, new_path)
            logging.info(f"Renamed: {old_path} -> {new_path}")
            return f"Renamed '{parts[1]}' to '{parts[2]}'"

        elif cmd == 'upload' and len(parts) > 2:
            file_path = get_safe_path(parts[1])
            with open(file_path, 'w') as f:
                f.write(parts[2])
            logging.info(f"Uploaded file: {file_path}")
            return f"File '{parts[1]}' uploaded"

        elif cmd == 'download' and len(parts) > 1:
            file_path = get_safe_path(parts[1])
            with open(file_path, 'r') as f:
                content = f.read()
            logging.info(f"Downloaded file: {file_path}")
            return content

        elif cmd == 'cd' and len(parts) > 1:
            new_dir = get_safe_path(parts[1])
            if os.path.isdir(new_dir):
                current_dir = new_dir
                return f"Changed directory to: {current_dir}"
            else:
                return f"Directory '{parts[1]}' not found"

        elif cmd == 'exit':
            return "Goodbye!"

        else:
            return "ERROR: Unknown command or invalid arguments"

    except PermissionError as e:
        logging.warning(f"Permission denied: {request} - {str(e)}")
        return f"ERROR: {str(e)}"
    except FileNotFoundError:
        logging.warning(f"File not found: {request}")
        return "ERROR: File or directory not found"
    except Exception as e:
        logging.error(f"Error processing request '{request}': {str(e)}")
        return f"ERROR: {str(e)}"


def start_server():
    """Запускает FTP сервер"""
    ensure_server_root()

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind((HOST, PORT))
        sock.listen()
        logging.info(f"FTP Server started on {HOST}:{PORT}")
        print(f"FTP Server started on {HOST}:{PORT}. Root directory: {SERVER_ROOT}")

        while True:
            conn, addr = sock.accept()
            logging.info(f"New connection from {addr}")
            print(f"New connection from {addr}")

            with conn:
                current_dir = SERVER_ROOT

                while True:
                    try:
                        request = conn.recv(1024).decode().strip()
                        if not request:
                            break

                        logging.info(f"Request from {addr}: {request}")
                        print(f"Request from {addr}: {request}")

                        if request.lower() == 'exit':
                            response = process_request(request, current_dir)
                            conn.send(response.encode())
                            break

                        response = process_request(request, current_dir)

                        # Обновляем текущую директорию после команды cd
                        if request.lower().startswith('cd ') and not response.startswith("ERROR"):
                            current_dir = response.split(': ')[1]
                            response = f"Current directory: {current_dir}"

                        conn.send(response.encode())

                    except ConnectionResetError:
                        logging.info(f"Client {addr} disconnected unexpectedly")
                        print(f"Client {addr} disconnected unexpectedly")
                        break

            logging.info(f"Connection with {addr} closed")
            print(f"Connection with {addr} closed")


if __name__ == '__main__':
    start_server()
