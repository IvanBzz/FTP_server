import socket

HOST = 'localhost'
PORT = 9090


def main():
    print("FTP Client. Type 'help' for commands list.")

    while True:
        try:
            request = input("ftp> ").strip()
            if not request:
                continue

            if request.lower() == 'help':
                print("Available commands:")
                print("ls - List files in current directory")
                print("pwd - Show current directory")
                print("mkdir <dirname> - Create directory")
                print("rmdir <dirname> - Remove directory")
                print("rm <filename> - Remove file")
                print("rename <oldname> <newname> - Rename file")
                print("upload <filename> <content> - Upload file")
                print("download <filename> - Download file")
                print("cd <dirname> - Change directory")
                print("exit - Disconnect from server")
                continue

            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.connect((HOST, PORT))
                sock.send(request.encode())
                response = sock.recv(1024).decode()
                print(response)

            if request.lower() == 'exit':
                break

        except KeyboardInterrupt:
            print("\nDisconnecting...")
            break
        except Exception as e:
            print(f"Error: {e}")


if __name__ == '__main__':
    main()
