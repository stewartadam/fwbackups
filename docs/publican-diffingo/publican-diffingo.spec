%define brand diffingo

Name:		publican-diffingo
Summary:	Common documentation files for %{brand}
Version:	0.1
Release:	1%{?dist}
License:	CC-BY-SA
Group:		Applications/Text
Buildroot:	%{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
Buildarch:	noarch
Source:		http://downloads.diffingo.com/fwbackups/%{name}-%{version}.tgz
Requires:	publican >= 1.0
BuildRequires:	publican >= 1.0
URL:		https://www.diffingo.com/oss/fwbackups

%description
This package provides common files and templates needed to build documentation
for %{brand} with publican.

%prep
%setup -q 

%build
publican build --formats=xml --langs=all --publish

%install
rm -rf $RPM_BUILD_ROOT
mkdir -p -m755 $RPM_BUILD_ROOT%{_datadir}/publican/Common_Content
publican install_brand --path=$RPM_BUILD_ROOT%{_datadir}/publican/Common_Content

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(-,root,root,-)
%doc README
%doc COPYING
%{_datadir}/publican/Common_Content/%{brand}

%changelog
* Thu Oct 28 2010 Stewart Adam <s.adam at diffingo.com> 0.1-1
- Change installbrand to install_brand in %%install and fill in sample details

* Wed Jun 30 2010 Stewart Adam <s.adam at diffingo.com> 0.1-0
- Created Brand

