import socket


def get_domain(ip):
    try:
        return socket.gethostbyaddr(ip)[0]
    except socket.herror as e:
        if 'host not found' in str(e):
            return None
        else:
            raise Exception(e)
