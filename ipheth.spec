#
# Conditional build:
%bcond_without	dist_kernel	# allow non-distribution kernel
%bcond_with	kernel		# don't build kernel modules
%bcond_without	userspace	# don't build userspace programs
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

%define		rel	1
%define		pname	ipheth
Summary:	iPhone USB Ethernet Driver
Name:       %{pname}%{_alt_kernel}
Version:	0.1
Release:	%{rel}
License:	BSD/GPL v2
Group:		X11/Applications
Source0:	%{name}.tar.bz2
# Source0-md5:	89171c4f95f298340bf1dbf5a487b787
URL:		http://giagio.com/wiki/moin.cgi/iPhoneEthernetDriver
BuildRequires:	libimobiledevice-devel
Requires:	udev-core
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
This is a Linux Kernel driver that adds support for iPhone tethering
through USB cables. Unlike other solutions out there, you don't need
to jailbreak your phone or install third-party proxy applications.

%package -n kernel%{_alt_kernel}-net-ipheth
Summary:	Linux driver for iPhone USB Ethernet Driver
Release:	%{rel}@%{_kernel_ver_str}
Group:		Base/Kernel
Requires(post,postun):	/sbin/depmod
%if %{with dist_kernel}
%requires_releq_kernel
Requires(postun):	%releq_kernel
%endif

%description -n kernel%{_alt_kernel}-net-ipheth
Linux driver for iPhone USB Ethernet Driver.

%prep
%setup -q -n %{name}

%build
%if %{with kernel}
%build_kernel_modules -C ipheth-driver -m ipheth CONFIG_DEBUG_SECTION_MISMATCH=y
%endif
%if %{with userspace}
%{__make} -C ipheth-pair \
	CC="%{__cc}" \
	CFLAGS="%{rpmcflags}"
%endif

%install
rm -rf $RPM_BUILD_ROOT
%if %{with kernel}
%install_kernel_modules -m ipheth-driver/ipheth -d misc
%endif

%if %{with userspace}
install -d $RPM_BUILD_ROOT{/lib/udev,/etc/udev/rules.d}
install -p ipheth-pair/ipheth-pair $RPM_BUILD_ROOT/lib/udev
cp -a ipheth-pair/90-iphone-tether.rules $RPM_BUILD_ROOT/etc/udev/rules.d
%endif

%clean
rm -rf $RPM_BUILD_ROOT

%post	-n kernel%{_alt_kernel}-net-ipheth
%depmod %{_kernel_ver}

%postun	-n kernel%{_alt_kernel}-net-ipheth
%depmod %{_kernel_ver}

%files
%defattr(644,root,root,755)
%config(noreplace) %verify(not md5 mtime size) /etc/udev/rules.d/90-iphone-tether.rules
%attr(755,root,root) /lib/udev/ipheth-pair

%if %{with kernel}
%files -n kernel%{_alt_kernel}-net-ipheth
%defattr(644,root,root,755)
/lib/modules/%{_kernel_ver}/misc/*.ko*
%endif
