%define req_esound_version	0.2.28
%define req_gnomevfs2_version	2.5.3
%define req_libbonobo_version	2.13.0
%define req_libxslt_version	1.0.18
%define api_version	2
%define lib_major	0
%define pkgname     libgnome
%define lib_name	%mklibname gnome %{api_version} %{lib_major}
%define develname %mklibname -d gnome %{api_version}

Summary: GNOME libraries
Name: %{pkgname}%{api_version}
Version: 2.32.0
Release: %mkrel 2
Source0: ftp://ftp.gnome.org/pub/GNOME/sources/%{pkgname}/%{pkgname}-%{version}.tar.bz2
# (fc) 1.116.0-2mdk use Mdk default background
Patch1: libgnome-background.patch
# (fc) 2.2.0.1-2mdk Ia Ora as default theme
Patch4: libgnome-defaulttheme.patch
# (fc) 2.19.1-2mdv mark gnome_program_init with sentinel (SUSE)
Patch6: libgnome-sentinel.patch
# (fc) 2.19.1-2mdv fix va_list usage (SUSE)
Patch7: libgnome-2.19.1-va_list.patch
# (fc) 2.19.1-2mdv enable sound server and events by default, remove almost default sound events
Patch8: libgnome-2.19.1-sounds-default.patch
# (fc) 2.24.1-2mdv use www-browser as default browser
Patch9: libgnome-2.24.1-www-browser.patch
# (fc) 2.28.0-2mdv put back icons in menu and buttons
Patch10: libgnome-2.28.0-icons.patch
License: LGPLv2+
Group: System/Libraries
Url: http://www.gnome.org/
BuildRoot: %{_tmppath}/%{name}-%{version}-buildroot
BuildRequires: popt-devel
BuildRequires: libbzip2-devel
BuildRequires: gnome-vfs2-devel >= %{req_gnomevfs2_version}
BuildRequires: esound-devel >= %{req_esound_version}
BuildRequires: libxslt-devel >= %{req_libxslt_version}
BuildRequires: gtk-doc
BuildRequires: libbonobo2_x-devel >= %{req_libbonobo_version}
BuildRequires: libcanberra-devel
BuildRequires: intltool >= 0.40.0
Requires: %{name}-schemas >= %{version}-%{release}

%description
Data files for the GNOME library such as translations.


%package schemas
Summary:	Default configuration for some GNOME software
Group:		%{group}
Conflicts:	%{name} < 2.30.0-2mdv

%description schemas
Default configuration for GNOME software

%package -n %{lib_name}
Summary:	Dynamic libraries for GNOME applications
Group:		%{group}
Requires:	%{name} >= %{version}

%description -n %{lib_name}
GNOME library contains extra API to let your GNOME applications shine.

%package -n %develname
Summary:	Static libraries, include files for GNOME
Group:		Development/GNOME and GTK+
Provides:	%{name}-devel = %{version}-%{release}
Requires:	%{lib_name} = %{version}
Requires:	%{name} = %{version}
Requires:   libgnome-vfs2-devel
Requires:   esound-devel >= %{req_esound_version}
Requires:   libbonobo2_x-devel >= %{req_libbonobo_version}
Obsoletes: %mklibname -d gnome 2 0

%description -n %develname
Static library and headers file
needed in order to develop applications using the GNOME library

%prep
%setup -q -n %{pkgname}-%{version}
%patch1 -p1 -b .background
%patch4 -p1 -b .defaulttheme
%patch6 -p1 -b .sentinel
%patch7 -p1 -b .va_list
%patch8 -p1 -b .sound-defaults
%patch9 -p1 -b .www-browser
%patch10 -p1 -b .icons

%build
%configure2_5x --enable-gtk-doc

%make

%install
rm -rf $RPM_BUILD_ROOT

GCONF_DISABLE_MAKEFILE_SCHEMA_INSTALL=1 %makeinstall_std

# remove unpackaged files
rm -f $RPM_BUILD_ROOT%{_libdir}/gnome-vfs-2.0/modules/*.{la,a} \
  $RPM_BUILD_ROOT%{_libdir}/bonobo/monikers/*.{la,a}

%find_lang %{pkgname}-2.0

%clean
rm -rf $RPM_BUILD_ROOT

%define schemas desktop_gnome_accessibility_keyboard desktop_gnome_accessibility_startup desktop_gnome_applications_at_mobility desktop_gnome_applications_at_visual desktop_gnome_applications_browser desktop_gnome_applications_terminal desktop_gnome_applications_office desktop_gnome_applications_window_manager desktop_gnome_background desktop_gnome_file_views desktop_gnome_interface desktop_gnome_lockdown desktop_gnome_peripherals_keyboard desktop_gnome_peripherals_mouse desktop_gnome_sound desktop_gnome_thumbnail_cache desktop_gnome_thumbnailers desktop_gnome_typing_break

# update default theme on distribution upgrade
%triggerpostun -- libgnome2 < 2.28.0-3mdv
if [ "x$META_CLASS" != "x" ]; then
 case "$META_CLASS" in
  *server) GTK2_THEME="Ia Ora Gray" ;;
  *desktop) GTK2_THEME="Ia Ora Steel" ;;
  *download) GTK2_THEME="Ia Ora Night";;
 esac

  if [ "x$GTK2_THEME" != "x" ]; then 
  %{_bindir}/gconftool-2 --config-source=xml::/etc/gconf/gconf.xml.local-defaults/ --direct --type=string --set /desktop/gnome/interface/gtk_theme "$GTK2_THEME" > /dev/null
  fi
fi


%post schemas
%if %mdkversion < 200900
%post_install_gconf_schemas %schemas
%endif
if [ ! -d %{_sysconfdir}/gconf/gconf.xml.local-defaults/desktop/gnome/interface -a "x$META_CLASS" != "x" ]; then
 case "$META_CLASS" in
  *server) GTK2_THEME="Ia Ora Gray" ;;
  *desktop) GTK2_THEME="Ia Ora Steel" ;;
  *download) GTK2_THEME="Ia Ora Night";;
 esac

  if [ "x$GTK2_THEME" != "x" ]; then 
  %{_bindir}/gconftool-2 --config-source=xml::/etc/gconf/gconf.xml.local-defaults/ --direct --type=string --set /desktop/gnome/interface/gtk_theme "$GTK2_THEME" > /dev/null
  fi
fi

if [ ! -f /root/.gconf/desktop/gnome/background/%gconf.xml ]; then
  gconftool-2 --set /desktop/gnome/background/picture_options --type=string none
  gconftool-2 --set /desktop/gnome/background/primary_color --type=string "#B20003"
fi

%preun schemas
%preun_uninstall_gconf_schemas %schemas

%if %mdkversion < 200900
%post -n %{lib_name} -p /sbin/ldconfig
%endif
  
%if %mdkversion < 200900
%postun -n %{lib_name} -p /sbin/ldconfig
%endif

%files -f %{pkgname}-2.0.lang
%defattr(-,root,root)
%doc NEWS 
%config(noreplace) %{_sysconfdir}/sound/events/*
%{_bindir}/gnome-open
%{_libdir}/bonobo/monikers/*.so
%{_libdir}/bonobo/servers/*
%{_mandir}/man7/*
%_datadir/gnome-background-properties/gnome-default.xml
%_datadir/pixmaps/backgrounds/gnome/background-default.jpg

%files -n %{lib_name}
%defattr(-,root,root)
%{_libdir}/libgnome-%{api_version}.so.%{lib_major}*

%files -n %develname
%defattr(-,root,root)
%doc ChangeLog
%doc %{_datadir}/gtk-doc/html/*
%{_includedir}/*
%{_libdir}/pkgconfig/*
%{_libdir}/*.so
%attr(644,root,root) %{_libdir}/*.la
%{_libdir}/*.a

%files schemas
%defattr(-,root,root)
%{_sysconfdir}/gconf/schemas/desktop_gnome_accessibility_keyboard.schemas
%{_sysconfdir}/gconf/schemas/desktop_gnome_accessibility_startup.schemas
%{_sysconfdir}/gconf/schemas/desktop_gnome_applications_at_mobility.schemas
%{_sysconfdir}/gconf/schemas/desktop_gnome_applications_at_visual.schemas
%{_sysconfdir}/gconf/schemas/desktop_gnome_applications_browser.schemas
%{_sysconfdir}/gconf/schemas/desktop_gnome_applications_office.schemas
%{_sysconfdir}/gconf/schemas/desktop_gnome_applications_terminal.schemas
%{_sysconfdir}/gconf/schemas/desktop_gnome_applications_window_manager.schemas
%{_sysconfdir}/gconf/schemas/desktop_gnome_background.schemas
%{_sysconfdir}/gconf/schemas/desktop_gnome_file_views.schemas
%{_sysconfdir}/gconf/schemas/desktop_gnome_interface.schemas
%{_sysconfdir}/gconf/schemas/desktop_gnome_lockdown.schemas
%{_sysconfdir}/gconf/schemas/desktop_gnome_peripherals_keyboard.schemas
%{_sysconfdir}/gconf/schemas/desktop_gnome_peripherals_mouse.schemas
%{_sysconfdir}/gconf/schemas/desktop_gnome_sound.schemas
%{_sysconfdir}/gconf/schemas/desktop_gnome_thumbnail_cache.schemas
%{_sysconfdir}/gconf/schemas/desktop_gnome_thumbnailers.schemas 
%{_sysconfdir}/gconf/schemas/desktop_gnome_typing_break.schemas
