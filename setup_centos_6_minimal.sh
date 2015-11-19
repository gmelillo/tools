#!/bin/bash

echo "NOZEROCONF=yes" >> /etc/sysconfig/network
echo "NETWORKING_IPV6=no" >> /etc/sysconfig/network

echo "# Disables IPv6" >> /etc/sysctl.conf
echo "net.ipv6.conf.all.disable_ipv6 = 1" >> /etc/sysctl.conf
echo "net.ipv6.conf.default.disable_ipv6 = 1" >> /etc/sysctl.conf

sed -i 's/SELINUX=enforcing/SELINUX=permissive/' /etc/selinux/config

sed -i 's/rhgb//' /boot/grub/grub.conf
sed -i 's/quiet//' /boot/grub/grub.conf

yum -y update && yum -y install wget postfix vim-enhanced bind-utils tcpdump lsof sysstat nmap iptraf ntp man screen

echo -e "\
[vmware-tools] \n\
name=VMware Tools \n\
baseurl=http://packages.vmware.com/tools/esx/5.1/rhel6/\$basearch \n\
enabled=1 \n\
gpgcheck=1 \n\
gpgkey=http://packages.vmware.com/tools/keys/VMWARE-PACKAGING-GPG-DSA-KEY.pub \n\
       http://packages.vmware.com/tools/keys/VMWARE-PACKAGING-GPG-RSA-KEY.pub \n\
priority=1 \n\
" > /etc/yum.repos.d/vmware-tools.repo

yum install vmware-tools-esx-nox -y

sed -i 's/^weekly$/monthly/' /etc/logrotate.conf 
sed -i 's/^rotate 4$/rotate 24\ncompresscmd \/usr\/bin\/bzip2\nuncompresscmd \/usr\/bin\/bunzip2\ncompressoptions -9\ncompressext .bz2/' /etc/logrotate.conf

sed -i 's/restrict -6 default kod nomodify notrap nopeer noquery/#restrict -6 default kod nomodify notrap nopeer noquery/' /etc/ntp.conf
sed -i 's/restrict -6 ::1/#restrict -6 ::1/' /etc/ntp.conf

chkconfig ntpd on
chkconfig auditd off
chkconfig ip6tables off
chkconfig netfs off
chkconfig iscsi off
chkconfig iscsid off

reboot

yum -y remove `rpm -q kernel | grep -v \`uname -r\``