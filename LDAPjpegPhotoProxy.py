import ldap3
import http.server
import ssl
import configparser

class MyServerHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path.endswith('.jpg'):
            config = configparser.ConfigParser()
            config.read('config.ini')
            ldap_uri = config.get('ldap', 'uri')
            ldap_username = config.get('ldap', 'username')
            ldap_password = config.get('ldap', 'password')
            ldap_searchbase = config.get('ldap', 'search_base')
            ldap_usernameattribute = config.get('ldap', 'username_attribute')
            ldap_photoattribute = config.get('ldap', 'photo_attribute')

            username = self.path.replace('/','').replace('.jpg','')

            try:
                server = ldap3.Server(ldap_uri)
                conn = ldap3.Connection(server, user=ldap_username, password=ldap_password, auto_bind=True)

                conn.search(ldap_searchbase, f'({ldap_usernameattribute}={username})', attributes=[ldap_photoattribute])
                if not conn.entries:
                    print(f"\nUser, {username}, not found in LDAP")
                    self.send_response(404)
                    self.end_headers()
                else:
                    self.send_response(200)
                    self.send_header("Content-type", "image/jpeg")
                    self.end_headers()

                    entry = conn.entries[0]
                    if 'jpegPhoto' in entry:
                        binary_data = entry.jpegPhoto.value 
                        self.wfile.write(binary_data)
            except ldap3.core.exceptions.LDAPBindError as bind_error:
                print(str(bind_error))
            except ldap3.core.exceptions.LDAPPasswordIsMandatoryError as pwd_mandatory_error:
                print(str(pwd_mandatory_error))
        else:
            self.send_response(404)
            self.end_headers()

if __name__ == "__main__":
    config = configparser.ConfigParser()
    config.read('config.ini')
    listen_address = config.get('http', 'listen')
    listen_port = config.getint('http', 'port')
    cert_file = config.get('http', 'cert')
    key_file = config.get('http', 'key')

    server_address = (listen_address, listen_port)

    http_server = http.server.HTTPServer(server_address, MyServerHandler)

    if config['http']['https']:
        context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        context.load_cert_chain(certfile=cert_file, keyfile=key_file)
        context.check_hostname = False
        http_server.socket = context.wrap_socket(http_server.socket, server_side=True)
        print(f"Server started at https://{server_address[0]}:{server_address[1]}")
    else:
        print(f"Server started at http://{server_address[0]}:{server_address[1]}")
    try:
        http_server.serve_forever()
    except KeyboardInterrupt:
        http_server.server_close()
        print("\nServer stopped.")
