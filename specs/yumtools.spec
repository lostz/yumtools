Name:           q-yumtools
Version:        1.1.1
Release:        1%{?dist}
BuildArch:      noarch
Summary:        去哪儿网专属工具——将RPM包上传至YumServer的管理工具集，包括上传、分支转移、删除命令
Packager:       yan.lu <yan.lu@qunar.com>, zhen.pei <zhen.pei@qunar.com>, dongliang.ma <dongliang.ma@qunar.com>
Group:		Qunar/YumServer
License:        Qunar Company License
URL:		http://wiki.corp.qunar.com/display/opswiki/YumServer
AutoReqProv:    no
Requires:       q-python27
Requires:       q-python27-clint
Requires:       q-python27-pyyaml
Requires:       q-python27-pyrpm
Requires:       createrepo

%description
去哪儿网专属工具——将RPM包上传至YumServer的管理工具集，包括上传、分支转移、删除命令
详细说明请看：http://wiki.corp.qunar.com/display/opswiki/YumServer

%install
cd /home/dongliang.ma/code/yumtools
mkdir -p %{buildroot}/usr/bin
mkdir -p %{buildroot}/etc
mkdir -p %{buildroot}/usr/share/yumtools
install -m 755 usr/bin/yumtools %{buildroot}/usr/bin/yumtools
#install -m 755 usr/bin/yumtools-serv %{buildroot}/usr/bin/yumtools-serv
install -m 644 etc/* %{buildroot}/etc/
cp share/yumtools/* %{buildroot}/usr/share/yumtools -R

%post

%postun

%files
# binaray files
%defattr(0755,root,root,0755)
/usr/bin/yumtools
#/usr/bin/yumtools-serv
#/usr/bin/yumtools-passwd

# config
%defattr(0644,root,root,0755)
%config(noreplace) /etc/*

# other files
%defattr(0644,root,root,0755)
/usr/share/yumtools/*
#%exclude /usr/share/yumtools/*.py
#%exclude /usr/share/yumtools/validate/*.py
#%exclude /usr/share/yumtools/yumtoolslib/*.py
#%exclude /usr/share/yumtools/yumtoolslib/client/*.py
#%exclude /usr/share/yumtools/yumtoolslib/commands/*.py
#%exclude /usr/share/yumtools/yumtoolslib/server/*.py

%changelog
* Thu Apr 18 2013 马冬亮 <dongliang.ma@qunar.com> 1.1.0-e16
- 更新帮助信息
* Thu Apr 18 2013 马冬亮 <dongliang.ma@qunar.com> 1.1.0-e16
- 简化命令参数，添加ldap验证，重构客户端代码
* Tue Oct  29 2012 陆研 <yan.lu@qunar.com> 1.0.0-1.el6
- first build from https://github.com/jaypei/yumtools

