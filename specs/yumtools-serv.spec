Name:           q-yumtools-server
Version:        1.1.0
Release:        1%{?dist}
BuildArch:      noarch
Summary:        去哪儿网专属工具——yumtools yumtools-server 服务器端
Packager:       yan.lu <yan.lu@qunar.com>, zhen.pei <zhen.pei@qunar.com>, dongliang.ma <dongliang.ma@qunar.com>
Group:		Qunar/YumServer
License:        Qunar Company License
URL:		http://wiki.corp.qunar.com/display/opswiki/YumServer
AutoReqProv:    no
Requires:       q-python27
Requires:       q-python27-clint
Requires:       q-python27-pyyaml
Requires:       createrepo

%description
去哪儿网专属工具——yumtools 服务器端

%install
cd /home/dongliang.ma/code/yumtools
mkdir -p %{buildroot}/usr/bin
mkdir -p %{buildroot}/etc
mkdir -p %{buildroot}/usr/share/yumtools
install -m 755 usr/bin/yumtools-server %{buildroot}/usr/bin/yumtools-server
install -m 644 etc/* %{buildroot}/etc/
cp share/yumtools/* %{buildroot}/usr/share/yumtools -R

%post
mkdir -p /var/{run,log}/yumtools-serv
%postun
%files
# binaray files
%defattr(0755,root,root,0755)
/usr/bin/yumtools-server

# config
%defattr(0644,root,root,0755)
%config(noreplace) /etc/*

# other files
%defattr(0644,root,root,0755)
/usr/share/yumtools/*

%changelog
* Thu Apr 18 2013 马冬亮 <dongliang.ma@qunar.com>
- 添加ldap验证，命令执行成功，自动发送邮件通知 
* Tue Dec  11 2012 陆研 <yan.lu@qunar.com> 1.0.2-1.el6
- fix checksum parameter under 5u
* Tue Dec  6 2012 陆研 <yan.lu@qunar.com> 1.0.1-1.el6
- remove umask flag
* Tue Oct  29 2012 陆研 <yan.lu@qunar.com> 1.0.0-1.el6
- first build from https://github.com/jaypei/yumtools

