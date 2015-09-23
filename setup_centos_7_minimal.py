#!/usr/bin/env python

from argparse import ArgumentParser
from sys import exit
from subprocess import call, STDOUT
from os import devnull, makedirs
from os.path import basename, expanduser, isdir
from time import time
from logging import getLogger, StreamHandler, Formatter, INFO, DEBUG

F_DEV_NULL = open(devnull, 'w')
SCRIPT_NAME = basename(__file__)
LOG_FOLDER = expanduser('~/.centos_7_setup')

logger = getLogger()
handler = StreamHandler()
formatter = Formatter(
	'%(asctime)s %(name)-12s %(levelname)-8s %(message)s'
)
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(INFO)

def set_log_file():
	if not isdir(LOG_FOLDER):
		logger.info('Creating directory {0}'.format(LOG_FOLDER))
		makedirs(LOG_FOLDER)
	try:
		F_DEV_NULL = open('{0}/{1}.log'.format(
			LOG_FOLDER,
			str(int(time()))
		), 'w+')
	except Exception as error:
		logger.info('Error opening log file.')
		logger.info(str(error))
		F_DEV_NULL = open(devnull, 'w')

def exec_command(command):
	'''
	Exec shell commands
	'''
	return call(
		command, 
		shell=True,
		stdout=F_DEV_NULL,
		stderr=STDOUT
	)

def check_so_version():
	'''
	Check if we are on CentOS 7 OS
	If yes return True and continue with configuration procedure.
	If we are on different system exit(1) will be performed.
	'''
	from platform import dist
	if dist()[0] == 'centos':
		return True
	if int(dist()[1].split('.')[0]) == 7:
		return True
	logger.error('OS not supported by this script.')
	logger.error('Please use this script only on CentOS 7 minimal')
	exit(1)

def setup_packages():
	'''
	Do the default customization and update packages.
	'''
	logger.info('Updating packages')
	exec_command('yum update -y')
	logger.info('Installing tools')
	exec_command('yum -y install wget postfix vim-enhanced bind-utils tcpdump lsof sysstat nmap iptraf ntp man screen')
	logger.info('Fixing logrotate')
	exec_command("sed -i 's/^weekly$/monthly/' /etc/logrotate.conf")
	exec_command(
		"""
		sed -i 's/^rotate 4$/rotate 24\\ncompresscmd \/usr\/bin\/bzip2\\nuncompresscmd \/usr\/bin\/bunzip2\\ncompressoptions -9\\ncompressext .bz2/' /etc/logrotate.conf
		"""
	)
	logger.info('Disabling SELINUX end graphic boot')
	exec_command("sed -i 's/SELINUX=enforcing/SELINUX=disabled/' /etc/selinux/config")
	exec_command("sed -i 's/rhgb//' /boot/grub2/grub.cfg")
	exec_command("sed -i 's/quiet//' /boot/grub2/grub.cfg")
	logger.info('Disabling firewall')
	exec_command('systemctl disable firewalld.service')

def main():
	'''
	Main function.
	Check user arguments and perform every action needed to complete the first setup.
	'''
	check_so_version()
	set_log_file()

	parser = ArgumentParser()
	parser.add_argument('--vmware', dest='vmware', action='store_true', help='Is virtual machine')
	parser.add_argument('--ipv6', dest='ipv6', action='store_true', help='Maintain IPv6 enabled')
	parser.add_argument('--eth', dest='eth', help='Ethetnet name')
	parser.add_argument('--clean-kernel', dest='kernel', action='store_true', help='Remove old kernels')
	parser.add_argument('-d', '--debug', dest='debug', action='store_true', help='Enable debug messages')

	args = parser.parse_args()
	if args.kernel:
		logger.info('Cleaning up old kernels.')
		exec_command('yum -y remove `rpm -q kernel | grep -v \`uname -r\``')
		logger.info('Kernels removed.')
		exit(0)
	if args.debug:
		logger.setLevel(DEBUG)

	setup_packages()
	if args.vmware:
		exec_command('yum install net-tools open-vm-tools -y')
	if not args.ipv6:
		if args.eth is None:
			logger.error('Ethernet name not defined.')
			exit(2)
		else:
			exec_command('echo "NOZEROCONF=yes" >> /etc/sysconfig/network')
			exec_command('echo "NETWORKING_IPV6=no" >> /etc/sysconfig/network')
			exec_command('echo "# Disables IPv6" >> /etc/sysctl.conf')
			exec_command('echo "net.ipv6.conf.all.disable_ipv6 = 1" >> /etc/sysctl.conf')
			exec_command('echo "net.ipv6.conf.default.disable_ipv6 = 1" >> /etc/sysctl.conf')
			exec_command('echo "net.ipv6.conf.{0}.disable_ipv6 = 1" >> /etc/sysctl.conf'.format(args.eth))

	logger.info('First configuration terminate.')
	logger.info('Reboot the system and then remove the old kernels with the following command:')
	logger.info('\t{0} --clean-kernel'.format(SCRIPT_NAME))

if __name__ == '__main__':
	main()