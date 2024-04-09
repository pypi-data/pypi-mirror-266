# TODO: Publish tools to PyPi..
from __future__ import annotations

from multiprocessing import Process
from socket import AF_INET, SOCK_DGRAM, socket

from pyftpdlib.authorizers import DummyAuthorizer
from pyftpdlib.handlers import FTPHandler
from pyftpdlib.servers import FTPServer


def get_ip() -> str:
	s = socket(AF_INET, SOCK_DGRAM)
	try:
		# doesn't even have to be reachable
		s.connect(('10.255.255.255', 1))
		ip = s.getsockname()[0]
	except Exception:
		ip = '0.0.0.0'
	finally:
		s.close()
	return ip


# Sync stuff (use like InstantRun in AStudio) using watchdog-ftp-sync
# or access by any ftp client

# TODO: Write ftp logs to different place..


def run_ftp_server(authorizer: DummyAuthorizer, ip: str, port: int) -> None:
	from logging import getLogger

	ftpl = getLogger('pyftpdlib')

	handler = FTPHandler
	handler.authorizer = authorizer

	server = FTPServer((ip, port), handler)
	server.serve_forever()

	# TODO: Toast on any updates..?

	ftpl.warning(f'FTP server started on ip {get_ip()} port {port}')


def ftp_server_proc(
	*,
	user: str = 'android', passwd: str = 'android',
	ip: str = '0.0.0.0', port: int = 2121,
) -> Process:
	authorizer = DummyAuthorizer()
	authorizer.add_user(user, passwd, '.', perm='elradfmw')

	# TODO: On app quit/stop correctly destroy process..
	# Access using your device ip (you can get it from device options "About phone")
	ftp_process = Process(target=run_ftp_server, args=(authorizer, ip, port))
	ftp_process.start()

	return ftp_process


if __name__ == '__main__':
	ftp_server_proc().join()
