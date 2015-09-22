#!/usr/bin/env python

from argparse import ArgumentParser
from sys import exit
from subprocess import call

def exec_command(command):
	'''
	Exec shell commands
	'''
	return call(command, shell=True)

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
	print('OS not supported by this script.')
	print('Please use this script only on CentOS 7 minimal')
	exit(1)

def setup_packages():
	'''
	Do the default customization and update packages.
	'''
	print('Updating packages')
	exec_command('yum update -y')
	print('Installing tools')
	exec_command('yum -y install wget postfix vim-enhanced bind-utils tcpdump lsof sysstat nmap iptraf ntp man screen')
	print('Fixing logrotate')
	exec_command("sed -i 's/^weekly$/monthly/' /etc/logrotate.conf")
	exec_command(
		"""
		sed -i 's/^rotate 4$/rotate 24\\ncompresscmd \/usr\/bin\/bzip2\\nuncompresscmd \/usr\/bin\/bunzip2\\ncompressoptions -9\\ncompressext .bz2/' /etc/logrotate.conf
		"""
	)
	print('Disabling SELINUX end graphic boot')
	exec_command("sed -i 's/SELINUX=enforcing/SELINUX=disabled/' /etc/selinux/config")
	exec_command("sed -i 's/rhgb//' /boot/grub2/grub.cfg")
	exec_command("sed -i 's/quiet//' /boot/grub2/grub.cfg")
	print('Disabling firewall')
	exec_command('systemctl disable firewalld.service')

def main():
	'''
	Main function.
	Check user arguments and perform every action needed to complete the first setup.
	'''
	check_so_version()

	parser = ArgumentParser()
	parser.add_argument('--vmware', dest='vmware', action='store_true', help='Is virtual machine')
	parser.add_argument('--ipv6', dest='ipv6', action='store_true', help='Maintain IPv6 enabled')
	parser.add_argument('--eth', dest='eth', help='Ethetnet name')
	parser.add_argument('--clean-kernel', dest='kernel', action='store_true', help='Remove old kernels')

	args = parser.parse_args()
	if args.kernel:
		exec_command('yum -y remove `rpm -q kernel | grep -v \`uname -r\``')
		exit(0)

	setup_packages()
	if args.vmware:
		exec_command('yum install net-tools open-vm-tools -y')
	if not args.ipv6:
		if args.eth is None:
			print('Ethernet name not defined.')
			exit(2)
		else:
			exec_command('echo "NOZEROCONF=yes" >> /etc/sysconfig/network')
			exec_command('echo "NETWORKING_IPV6=no" >> /etc/sysconfig/network')
			exec_command('echo "# Disables IPv6" >> /etc/sysctl.conf')
			exec_command('echo "net.ipv6.conf.all.disable_ipv6 = 1" >> /etc/sysctl.conf')
			exec_command('echo "net.ipv6.conf.default.disable_ipv6 = 1" >> /etc/sysctl.conf')
			exec_command('echo "net.ipv6.conf.{0}.disable_ipv6 = 1" >> /etc/sysctl.conf'.format(args.eth))

	print('First configuration terminate.')
	print('Reboot the system and then remove the old kernels with the following command:')
	print('\tyum -y remove `rpm -q kernel | grep -v \`uname -r\``')

if __name__ == '__main__':
	main()