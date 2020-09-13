#
# Conditional build:
%bcond_without	dist_kernel	# allow non-distribution kernel
%bcond_with	kernel		# kernel modules [already in Linux >= 2.6.34]
%bcond_without	userspace	# userspace programs
%bcond_with	verbose		# verbose build (V=1)

%if %{without kernel}
%undefine	with_dist_kernel
%endif
%if "%{_alt_kernel}" != "%{nil}"
%undefine	with_userspace
%endif
%if %{without userspace}
# nothing to be placed to debuginfo package
%define		_enable_debug_packages	0
%endif

%define		rel	8
%define		pname	ipheth
Summary:	iPhone USB Ethernet Driver
Summary(pl.UTF-8):	Sterownik ethernetowy dla iPhone'a po USB
Name:		%{pname}%{_alt_kernel}
Version:	1.0
Release:	%{rel}
License:	BSD/GPL v2
Group:		X11/Applications
#Source0Download: https://github.com/dgiagio/ipheth/releases/
Source0:	https://github.com/downloads/dgiagio/ipheth/ipheth-%{version}.tar.gz
# Source0-md5:	80548f0d419ff0c2784d148b40b2aeb6
URL:		https://github.com/dgiagio/ipheth
BuildRequires:	libimobiledevice-devel >= 1
BuildRequires:	pkgconfig
Requires:	udev-core
Requires:	usbmuxd
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
This is a Linux Kernel driver that adds support for iPhone tethering
through USB cables. Unlike other solutions out there, you don't need
to jailbreak your phone or install third-party proxy applications.

This package contains the device pairing program.

%description -l pl.UTF-8
ipheth to sterownik jądra Linuksa dodające obsługę transmisji
ethernetowej z iPhonem przez kabel USB. W przeciwieństwie do innych
rozwiązań, nie wymaga to łamania zabezpieczeń telefonu ani
instalowania zewnętrznych proxy.

Ten pakiet zawiera program do parowania urządzeń.

%package -n kernel%{_alt_kernel}-net-ipheth
Summary:	Linux driver for iPhone USB Ethernet Driver
Summary(pl.UTF-8):	Sterownik jądra Linuksa do ethernetu dla iPhone'a po USB
Release:	%{rel}@%{_kernel_ver_str}
Group:		Base/Kernel
Requires(post,postun):	/sbin/depmod
%if %{with dist_kernel}
%requires_releq_kernel
Requires(postun):	%releq_kernel
%endif

%description -n kernel%{_alt_kernel}-net-ipheth
Linux driver for iPhone USB Ethernet Driver.

%description -n kernel%{_alt_kernel}-net-ipheth -l pl.UTF-8
Sterownik jądra Linuksa do ethernetu dla iPhone'a po USB.

%prep
%setup -q

%build
%if %{with kernel}
%build_kernel_modules -C ipheth-driver -m ipheth CONFIG_DEBUG_SECTION_MISMATCH=y
%endif

%if %{with userspace}
%{__make} -C ipheth-pair \
	CC="%{__cc}" \
	CFLAGS="%{rpmcflags} -Wall" \
	LDLIBS="%{rpmldflags} $(pkg-config --libs libimobiledevice-1.0)"
%endif

%install
rm -rf $RPM_BUILD_ROOT

%if %{with kernel}
%install_kernel_modules -m ipheth-driver/ipheth -d misc -s update -n %{pname}
cat <<'EOF' >> $RPM_BUILD_ROOT/etc/modprobe.d/%{_kernel_ver}/%{pname}.conf
blacklist %{pname}
EOF
%endif

%if %{with userspace}
install -d $RPM_BUILD_ROOT/lib/udev/rules.d
install -p ipheth-pair/ipheth-pair $RPM_BUILD_ROOT/lib/udev
cp -p ipheth-pair/90-iphone-tether.rules $RPM_BUILD_ROOT/lib/udev/rules.d
%endif

%clean
rm -rf $RPM_BUILD_ROOT

%post	-n kernel%{_alt_kernel}-net-ipheth
%depmod %{_kernel_ver}

%postun	-n kernel%{_alt_kernel}-net-ipheth
%depmod %{_kernel_ver}

%files
%defattr(644,root,root,755)
/lib/udev/rules.d/90-iphone-tether.rules
%attr(755,root,root) /lib/udev/ipheth-pair

%if %{with kernel}
%files -n kernel%{_alt_kernel}-net-ipheth
%defattr(644,root,root,755)
/etc/modprobe.d/%{_kernel_ver}/ipheth.conf
/lib/modules/%{_kernel_ver}/misc/ipheth.ko*
%endif
