Name:           yumtools
Version:        0.2
Release:        2%{?dist}
BuildArch:      noarch
Summary:        A tools set whitch upload, remove, setbranch rpm packages and rebuild index on a yum repository.

Packager:       jaypei
License:        GPL

AutoReqProv:    no
Requires:       python27
Requires:       python27-clint
Requires:       python27-pyyaml
Requires:       createrepo

%description
A tools set whitch upload, remove, setbranch rpm packages and rebuild index on a yum repository.

%post

%postun

%files
# binaray files
%defattr(0755,root,root,0755)
/usr/bin/yumtools
/usr/bin/yumtools-serv
/usr/bin/yumtools-passwd

# config
%defattr(0644,root,root,0755)
%config(noreplace) /etc/*

# other files
%defattr(0644,root,root,0755)
/usr/share/yumtools/*


