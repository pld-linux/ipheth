#
# Conditional build:
%bcond_without	dist_kernel	# allow non-distribution kernel
%bcond_with		kernel		# don't build kernel modules
%bcond_without	userspace	# don't build userspace programs
%bcond_with	verbose		# verbose build (V=1)

Summary:	iPhone USB Ethernet Driver
Name:		ipheth
Version:	0.1
Release:	0.1
License:	GPL v2
Group:		X11/Applications
Source0:	%{name}.tar.bz2
# Source0-md5:	0cc73e6033025c8ba8c5ef0090a631b1
URL:		http://giagio.com/wiki/moin.cgi/iPhoneEthernetDriver
BuildRequires:	libimobiledevice-devel
Requires:	udev-core
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
This is a Linux Kernel driver that adds support for iPhone tethering
through USB cables. Unlike other solutions out there, you don't need
to jailbreak your phone or install third-party proxy applications.

%prep
%setup -q -n %{name}

%build
%if %{with userspace}
%{__make} -C ipheth-pair \
	CC="%{__cc}" \
	CFLAGS="%{rpmcflags}"
%endif

%install
rm -rf $RPM_BUILD_ROOT
%if %{with userspace}
install -d $RPM_BUILD_ROOT{/lib/udev,/etc/udev/rules.d}
install -p ipheth-pair/ipheth-pair $RPM_BUILD_ROOT/lib/udev
cp -a ipheth-pair/90-iphone-tether.rules $RPM_BUILD_ROOT/etc/udev/rules.d
%endif

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(644,root,root,755)
%config(noreplace) %verify(not md5 mtime size) /etc/udev/rules.d/90-iphone-tether.rules
%attr(755,root,root) /lib/udev/ipheth-pair
