# NOTE
# - setup guide:
#   http://wiki.birth-online.de/know-how/hardware/apple-iphone/airvideo-server-linux
# - clarify source files license and remove nosource

%include	/usr/lib/rpm/macros.java
Summary:	Air-Video Video Streaming Server
Name:		airvideo
Version:	2.4.5
Release:	0.11
License:	GPL v2+ with LGPL v2+ parts
Group:		Applications/Multimedia
Source0:	http://inmethod.com/air-video/download/ffmpeg-for-%{version}-beta6.tar.bz2
# NoSource0-md5:	241844e9d41bbd9f8852955291490910
NoSource:	0
Source1:	%{name}.init
Source2:	http://inmethod.com/air-video/download/linux/alpha6/AirVideoServerLinux.jar#/avs-alpha6.jar
# NoSource2-md5:	b619c088eea230afa92181393a36e1c0
NoSource:	2
Source3:	test.properties
Source4:	avs.avahi
URL:		http://www.inmethod.com/air-video/
BuildRequires:	lame-libs-devel
BuildRequires:	libx264-devel >= 0.1.3
BuildRequires:	pkgconfig
BuildRequires:	rpm-javaprov
BuildRequires:	rpmbuild(macros) >= 1.470
Requires(post,preun):	/sbin/chkconfig
Requires:	faac
Requires:	jpackage-utils
Requires:	mpeg4ip-server
Requires:	rc-scripts
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%define		_noautoreqdep	libGL.so.1 libGLU.so.1

%define		specflags	-fno-strict-aliasing

# -fomit-frame-pointer is always needed on x86 due to lack of registers (-fPIC takes one)
%define		specflags_ia32	-fomit-frame-pointer
# -mmmx is needed to enable <mmintrin.h> code.
%define		specflags_i586	-mmmx
%define		specflags_i686	-mmmx
%define		specflags_ppc	-fPIC

%description
Air Video can stream videos in almost any format to your iPhone, iPad
and iPod touch. You don't need to copy your videos to the device just
to watch them.

%package avahi
Summary:	airvideo service configuration for avahi
Summary(pl.UTF-8):	Konfiguracja serwisu airvideo dla avahi
Group:		Applications
Requires:	%{name} = %{version}-%{release}
Requires:	avahi

%description avahi
airvideo service configuration for avahi.

%prep
%setup -qc
mv ffmpeg/{*,.??*} .; rmdir ffmpeg

%build
# notes:
# - it's not autoconf configure
# - --disable-debug, --disable-optimizations, tune=generic causes not to override our optflags

./configure \
	--arch=%{_target_base_arch} \
	--prefix=%{_prefix} \
	--libdir=%{_libdir} \
	--shlibdir=%{_libdir} \
	--mandir=%{_mandir} \
	--cc="%{__cc}" \
	--extra-cflags="-D_GNU_SOURCE=1 %{rpmcppflags} %{rpmcflags}" \
	--extra-ldflags="%{rpmcflags} %{rpmldflags}" \
	--disable-debug \
	--disable-optimizations \
	--disable-stripping \
	--enable-pthreads \
	--disable-shared \
	--enable-static \
	--enable-gpl \
	--enable-libx264 \
	--enable-libmp3lame \
	--disable-decoder=aac \
	--disable-indevs \
	--disable-outdevs \
	--disable-vaapi \
%ifnarch %{ix86} %{x8664}
	--disable-mmx \
%endif
%ifarch i386 i486
	--disable-mmx \
%endif
	--enable-runtime-cpudetect

%{__make}

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT{%{_sysconfdir},%{_sbindir},%{_javadir},/etc/{rc.d/init.d,avahi/services},/var/lib/airvideo}
install -p ffmpeg $RPM_BUILD_ROOT%{_sbindir}/%{name}
install -p %{SOURCE1} $RPM_BUILD_ROOT/etc/rc.d/init.d/%{name}

cp -p %{SOURCE2} $RPM_BUILD_ROOT%{_javadir}/AirVideoServerLinux.jar
cp -p %{SOURCE3} $RPM_BUILD_ROOT%{_sysconfdir}/%{name}.properties
cp -p %{SOURCE4} $RPM_BUILD_ROOT%{_sysconfdir}/avahi/services/%{name}.service

%clean
rm -rf $RPM_BUILD_ROOT

%post
/sbin/chkconfig --add %{name}
%service %{name} restart

%preun
if [ "$1" = "0" ]; then
	%service -q %{name} stop
	/sbin/chkconfig --del %{name}
fi

%files
%defattr(644,root,root,755)
%attr(755,root,root) %{_sbindir}/airvideo
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/%{name}.properties
%attr(754,root,root) /etc/rc.d/init.d/%{name}
%{_javadir}/AirVideoServerLinux.jar
# XXX, if it really writes something, get dedicated user
%dir /var/lib/airvideo

%files avahi
%defattr(644,root,root,755)
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/avahi/services/%{name}.service
