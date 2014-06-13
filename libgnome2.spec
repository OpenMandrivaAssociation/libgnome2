%define url_ver %(echo %{version}|cut -d. -f1,2)

%define bootstrap 0
%{?_without_bootstrap: %global bootstrap 0}
%{?_with_bootstrap: %global bootstrap 1}

%define api	2
%define major	0
%define pkgname libgnome
%define libname	%mklibname gnome %{api} %{major}
%define devname	%mklibname -d gnome %{api}

Summary:	GNOME libraries
Name:		%{pkgname}%{api}
Version:	2.32.1
Release:	15
Group:		System/Libraries
License:	LGPLv2+
Url:		http://www.gnome.org/
Source0:	ftp://ftp.gnome.org/pub/GNOME/sources/libgnome/%{url_ver}/%{pkgname}-%{version}.tar.bz2
# (fc) 1.116.0-2mdk use Mdk default background
Patch1:		libgnome-background.patch
# (fc) 2.2.0.1-2mdk Ia Ora as default theme
Patch4:		libgnome-defaulttheme.patch
# (fc) 2.19.1-2mdv mark gnome_program_init with sentinel (SUSE)
Patch6:		libgnome-sentinel.patch
# (fc) 2.19.1-2mdv fix va_list usage (SUSE)
Patch7:		libgnome-2.19.1-va_list.patch
# (fc) 2.19.1-2mdv enable sound server and events by default, remove almost default sound events
Patch8:		libgnome-2.19.1-sounds-default.patch
# (fc) 2.24.1-2mdv use www-browser as default browser
Patch9:		libgnome-2.24.1-www-browser.patch
# (fc) 2.28.0-2mdv put back icons in menu and buttons
Patch10:	libgnome-2.28.0-icons.patch
# md glib2.0 >= 2.31.0 g_thread_init
Patch11:	libgnome-2.32.1_g_thread_init.patch

BuildRequires:	intltool >= 0.40.0
BuildRequires:	pkgconfig(gconf-2.0) >= 1.1.11 GConf2
BuildRequires:	pkgconfig(glib-2.0) >= 2.8.0
BuildRequires:	pkgconfig(gmodule-2.0) >= 2.8.0
BuildRequires:	pkgconfig(gnome-vfs-2.0) >= 2.5.3
BuildRequires:	pkgconfig(gobject-2.0) >= 2.0.0
BuildRequires:	pkgconfig(libbonobo-2.0) >= 2.13.0
%if !%bootstrap
BuildRequires:	gtk-doc
BuildRequires:	pkgconfig(libcanberra) >= 0
%endif
BuildRequires:	pkgconfig(popt)
Requires:	%{name}-schemas >= %{version}-%{release}
Requires:	%{libname} >= %{version}-%{release}

%description
Data files for the GNOME library such as translations.

%package schemas
Summary:	Default configuration for some GNOME software
Group:		%{group}
# needs gconftool-2
Requires:	GConf2
Conflicts:	%{name} < 2.30.0-2

%description schemas
Default configuration for GNOME software

%package -n %{libname}
Summary:	Dynamic libraries for GNOME applications
Group:		%{group}

%description -n %{libname}
GNOME library contains extra API to let your GNOME applications shine.

%package -n %{devname}
Summary:	Development libraries, include files for GNOME
Group:		Development/GNOME and GTK+
Provides:	%{name}-devel = %{version}-%{release}
Requires:	%{libname} = %{version}
Obsoletes:	%{mklibname -d gnome 2 0} < 2.32.1-6

%description -n %{devname}
Development library and headers file
needed in order to develop applications using the GNOME library

%prep
%setup -qn %{pkgname}-%{version}
%apply_patches

# this is a hack for glib2.0 >= 2.31.0
sed -i -e 's/-DG_DISABLE_DEPRECATED//g' \
	./libgnome/Makefile.*

%build
%configure2_5x \
	--disable-static \
	--disable-schemas-install \
%if %{bootstrap}
	--enable-canberra=no
%else
	--enable-gtk-doc
%endif

%make

%install
%makeinstall_std

%find_lang %{pkgname}-2.0

%define schemas desktop_gnome_accessibility_keyboard desktop_gnome_accessibility_startup desktop_gnome_applications_at_mobility desktop_gnome_applications_at_visual desktop_gnome_applications_browser desktop_gnome_applications_terminal desktop_gnome_applications_office desktop_gnome_applications_window_manager desktop_gnome_background desktop_gnome_file_views desktop_gnome_interface desktop_gnome_lockdown desktop_gnome_peripherals_keyboard desktop_gnome_peripherals_mouse desktop_gnome_sound desktop_gnome_thumbnail_cache desktop_gnome_thumbnailers desktop_gnome_typing_break

# update default theme on distribution upgrade
%triggerpostun -- libgnome2 < 2.28.0-3
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
%preun_uninstall_gconf_schemas %{schemas}

%files -f %{pkgname}-2.0.lang
%doc NEWS
%config(noreplace) %{_sysconfdir}/sound/events/*
%{_bindir}/gnome-open
%{_libdir}/bonobo/monikers/*.so
%{_libdir}/bonobo/servers/*
%{_mandir}/man7/*
%{_datadir}/gnome-background-properties/gnome-default.xml
%{_datadir}/pixmaps/backgrounds/gnome/background-default.jpg

%files -n %{libname}
%{_libdir}/libgnome-%{api}.so.%{major}*

%files -n %{devname}
%doc ChangeLog
%doc %{_datadir}/gtk-doc/html/*
%{_includedir}/*
%{_libdir}/pkgconfig/*
%{_libdir}/*.so

%files schemas
%{_sysconfdir}/gconf/schemas/desktop_gnome_*.schemas

