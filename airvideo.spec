# NOTE
# - setup guide:
#   http://wiki.birth-online.de/know-how/hardware/apple-iphone/airvideo-server-linux
# - clarify source files license and remove nosource

%include	/usr/lib/rpm/macros.java
Summary:	Air-Video Video Streaming Server
Name:		airvideo
Version:	2.2.5
Release:	0.8
License:	GPL v2+ with LGPL v2+ parts
Group:		Applications/Multimedia
Source0:	http://www.inmethod.com/air-video/download/ffmpeg-for-%{version}.tar.bz2
# NoSource0-md5:	1623d51b433555e08d0c2fcf1dee1b55
NoSource:	0
Source1:	%{name}.init
Source2:	http://inmethod.com/air-video/download/linux/alpha1/AirVideoServerLinux.jar
# NoSource2-md5:	312d6dd45f6c9928e1570da67a6d8ee6
NoSource:	2
Source3:	test.properties
URL:		http://www.inmethod.com/air-video/
BuildRequires:	faad2-devel
BuildRequires:	lame-libs-devel
BuildRequires:	libx264-devel >= 0.1.3
BuildRequires:	pkgconfig
BuildRequires:	rpm-javaprov
BuildRequires:	rpmbuild(macros) >= 1.470
Requires:	faac
Requires:	jpackage-utils
Requires(post,preun):	/sbin/chkconfig
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

%prep
%setup -qc
mv ffmpeg/* .; rmdir ffmpeg

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
	--enable-libfaad \
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
install -d $RPM_BUILD_ROOT{%{_sysconfdir},%{_sbindir},%{_javadir},/etc/rc.d/init.d,/var/lib/airvideo}
install -p ffmpeg $RPM_BUILD_ROOT%{_sbindir}/%{name}
install -p %{SOURCE1} $RPM_BUILD_ROOT/etc/rc.d/init.d/%{name}

cp -p %{SOURCE2} $RPM_BUILD_ROOT%{_javadir}
cp -p %{SOURCE3} $RPM_BUILD_ROOT%{_sysconfdir}/%{name}.properties

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
%dir %attr(755,nobody,nobody) /var/lib/airvideo
