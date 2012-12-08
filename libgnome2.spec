%define bootstrap 0
%{?_without_bootstrap: %global bootstrap 0}
%{?_with_bootstrap: %global bootstrap 1}

%define api_version	2
%define lib_major	0
%define pkgname 	libgnome
%define lib_name	%mklibname gnome %{api_version} %{lib_major}
%define develname	%mklibname -d gnome %{api_version}

Summary:	GNOME libraries
Name:		%{pkgname}%{api_version}
Version:	2.32.1
Release:	6
Group:		System/Libraries
License:	LGPLv2+
URL:		http://www.gnome.org/
Source0:	ftp://ftp.gnome.org/pub/GNOME/sources/%{pkgname}/%{pkgname}-%{version}.tar.bz2
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
Requires:	%{lib_name} >= %{version}-%{release}

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

%package -n %{lib_name}
Summary:	Dynamic libraries for GNOME applications
Group:		%{group}

%description -n %{lib_name}
GNOME library contains extra API to let your GNOME applications shine.

%package -n %{develname}
Summary:	Development libraries, include files for GNOME
Group:		Development/GNOME and GTK+
Provides:	%{name}-devel = %{version}-%{release}
Requires:	%{lib_name} = %{version}
Obsoletes:	%{mklibname -d gnome 2 0} < 2.32.1-6

%description -n %{develname}
Static library and headers file
needed in order to develop applications using the GNOME library

%prep
%setup -q -n %{pkgname}-%{version}
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

%files -n %{lib_name}
%{_libdir}/libgnome-%{api_version}.so.%{lib_major}*

%files -n %{develname}
%doc ChangeLog
%doc %{_datadir}/gtk-doc/html/*
%{_includedir}/*
%{_libdir}/pkgconfig/*
%{_libdir}/*.so

%files schemas
%{_sysconfdir}/gconf/schemas/desktop_gnome_*.schemas

%changelog
* Wed Nov 16 2011 Matthew Dawkins <mattydaw@mandriva.org> 2.32.1-4
+ Revision: 730801
- rebuild
  cleaned up spec
  used apply_patches macros for patches
  removed reqs for devel pkgs in the devel pkg
  disabled static build
  removed .la files
  removed req for main pkg by lib pkg, removes dep loop
  added BR for Gconf2
  removed old conflicts
  converted BRs to pkgconfig provides
  added bootstrap build condition
  added p11 & workaround for building with glib2.0 >= 2.31.0
  removed old ldconfig scriptlet
  removed defattr
  removed use of mkrel

* Sun May 22 2011 Funda Wang <fwang@mandriva.org> 2.32.1-3
+ Revision: 677083
- rebuild to add gconf2 as req

* Wed May 04 2011 Oden Eriksson <oeriksson@mandriva.com> 2.32.1-2
+ Revision: 666076
- mass rebuild

* Mon Jan 31 2011 Götz Waschk <waschk@mandriva.org> 2.32.1-1
+ Revision: 634556
- update to new version 2.32.1

* Tue Dec 14 2010 Funda Wang <fwang@mandriva.org> 2.32.0-2mdv2011.0
+ Revision: 621672
- rebuild for new popt

* Mon Sep 27 2010 Götz Waschk <waschk@mandriva.org> 2.32.0-1mdv2011.0
+ Revision: 581432
- update to new version 2.32.0

* Fri Jul 30 2010 Götz Waschk <waschk@mandriva.org> 2.31.0-1mdv2011.0
+ Revision: 563549
- update build deps
- new version

* Fri May 07 2010 Frederic Crozat <fcrozat@mandriva.com> 2.30.0-2mdv2010.1
+ Revision: 543366
- Move schemas to libgnome2-schemas, to prevent dependency on obsolete libgnome2 stuff

* Tue Mar 30 2010 Götz Waschk <waschk@mandriva.org> 2.30.0-1mdv2010.1
+ Revision: 529711
- update to new version 2.30.0

* Tue Feb 16 2010 Funda Wang <fwang@mandriva.org> 2.28.0-4mdv2010.1
+ Revision: 506778
- add BR on popt

* Fri Oct 23 2009 Frederic Crozat <fcrozat@mandriva.com> 2.28.0-3mdv2010.0
+ Revision: 459081
- Update default themes

* Wed Oct 21 2009 Frederic Crozat <fcrozat@mandriva.com> 2.28.0-2mdv2010.0
+ Revision: 458581
- Patch10: add back icons on menu and buttons by default

* Wed Sep 23 2009 Götz Waschk <waschk@mandriva.org> 2.28.0-1mdv2010.0
+ Revision: 447635
- update to new version 2.28.0

* Thu Jul 30 2009 Götz Waschk <waschk@mandriva.org> 2.27.5-1mdv2010.0
+ Revision: 404691
- update to new version 2.27.5

* Wed Apr 15 2009 Frederic Crozat <fcrozat@mandriva.com> 2.26.0-3mdv2009.1
+ Revision: 367436
- Fix default theme for One and Powerpack

* Wed Apr 01 2009 Frederic Crozat <fcrozat@mandriva.com> 2.26.0-2mdv2009.1
+ Revision: 363313
- Update default theme colors for Mdv 2009.1

* Tue Mar 17 2009 Götz Waschk <waschk@mandriva.org> 2.26.0-1mdv2009.1
+ Revision: 356775
- update to new version 2.26.0

* Sat Mar 07 2009 Antoine Ginies <aginies@mandriva.com> 2.25.1-2mdv2009.1
+ Revision: 351414
- rebuild

* Fri Mar 06 2009 Götz Waschk <waschk@mandriva.org> 2.25.1-1mdv2009.1
+ Revision: 349855
- new version
- rediff patch 1

* Mon Sep 29 2008 Frederic Crozat <fcrozat@mandriva.com> 2.24.1-2mdv2009.0
+ Revision: 289258
- Patch9: use www-browser as default browser

* Mon Sep 22 2008 Götz Waschk <waschk@mandriva.org> 2.24.1-1mdv2009.0
+ Revision: 286940
- new version

* Mon Sep 22 2008 Götz Waschk <waschk@mandriva.org> 2.24.0-1mdv2009.0
+ Revision: 286615
- new version

* Tue Sep 16 2008 Götz Waschk <waschk@mandriva.org> 2.23.92-1mdv2009.0
+ Revision: 285201
- new version
- drop patch 9

* Tue Aug 26 2008 Frederic Crozat <fcrozat@mandriva.com> 2.23.5-2mdv2009.0
+ Revision: 276215
- Change default theme to Ia Ora Smooth for all distrib flavors

* Tue Aug 19 2008 Götz Waschk <waschk@mandriva.org> 2.23.5-1mdv2009.0
+ Revision: 273713
- new version
- drop patch 10

* Tue Aug 12 2008 Frederic Crozat <fcrozat@mandriva.com> 2.23.4-4mdv2009.0
+ Revision: 271116
- Patch10 (SVN): add schemas for sound theme
- Patch9: use gvfs/gio to open urls with gnome-open (Mdv bug #40894)
- Update patch8 to set ia_ora as sound theme

* Thu Jul 03 2008 Götz Waschk <waschk@mandriva.org> 2.23.4-3mdv2009.0
+ Revision: 230967
- fix buildrequires
- new version
- update schemas list
- update license

* Fri Jun 20 2008 Pixel <pixel@mandriva.com> 2.22.0-3mdv2009.0
+ Revision: 227421
- rebuild for fixed %%update_icon_cache/%%clean_icon_cache/%%post_install_gconf_schemas
- rpm filetriggers deprecates update_menus/update_scrollkeeper/update_mime_database/update_icon_cache/update_desktop_database/post_install_gconf_schemas

* Tue Jun 17 2008 Thierry Vignaud <tv@mandriva.org> 2.22.0-2mdv2009.0
+ Revision: 222600
- rebuild

  + Pixel <pixel@mandriva.com>
    - do not call ldconfig in %%post/%%postun, it is now handled by filetriggers

* Mon Mar 10 2008 Götz Waschk <waschk@mandriva.org> 2.22.0-1mdv2008.1
+ Revision: 183565
- new version

* Wed Mar 05 2008 Götz Waschk <waschk@mandriva.org> 2.21.91-1mdv2008.1
+ Revision: 180165
- new version
- update file list
- update gconf schemas list

* Thu Feb 28 2008 Frederic Crozat <fcrozat@mandriva.com> 2.21.90-3mdv2008.1
+ Revision: 176514
- Add missing schema registrations

* Thu Feb 28 2008 Frederic Crozat <fcrozat@mandriva.com> 2.21.90-2mdv2008.1
+ Revision: 176490
- Update patch1 to use transition backgrounds
- Change default theme : Ia Ora Smooth for Free and Ia Ora Blue for One

* Mon Jan 28 2008 Götz Waschk <waschk@mandriva.org> 2.21.90-1mdv2008.1
+ Revision: 159190
- new version
- drop patch 5

  + Olivier Blin <blino@mandriva.org>
    - restore BuildRoot

  + Thierry Vignaud <tv@mandriva.org>
    - kill re-definition of %%buildroot on Pixel's request

* Mon Dec 17 2007 Götz Waschk <waschk@mandriva.org> 2.20.1.1-2mdv2008.1
+ Revision: 121633
- rebuild for new libpopt

* Wed Oct 17 2007 Götz Waschk <waschk@mandriva.org> 2.20.1.1-1mdv2008.1
+ Revision: 99728
- new version
- dro patch 2

* Tue Oct 16 2007 Götz Waschk <waschk@mandriva.org> 2.20.1-2mdv2008.1
+ Revision: 99101
- fix for upstream bug #478299 (schema file installation)

* Mon Oct 15 2007 Götz Waschk <waschk@mandriva.org> 2.20.1-1mdv2008.1
+ Revision: 98392
- new version

* Tue Oct 09 2007 Frederic Crozat <fcrozat@mandriva.com> 2.20.0-5mdv2008.0
+ Revision: 95774
- Fix default theme for desktop (ie One) META_CLASS, ensure trigger is run also for previous broken version of package

* Wed Sep 19 2007 Frederic Crozat <fcrozat@mandriva.com> 2.20.0-4mdv2008.0
+ Revision: 90579
- Fix patch1 to apply on correct file

* Tue Sep 18 2007 Guillaume Rousse <guillomovitch@mandriva.org> 2.20.0-3mdv2008.0
+ Revision: 89838
- rebuild

* Mon Sep 17 2007 Frederic Crozat <fcrozat@mandriva.com> 2.20.0-2mdv2008.0
+ Revision: 89255
- Migrate One system to new Ia Ora One theme

* Mon Sep 17 2007 Götz Waschk <waschk@mandriva.org> 2.20.0-1mdv2008.0
+ Revision: 89122
- new version
- rediff patch 1
- new devel name
- update file list

* Fri Sep 14 2007 Frederic Crozat <fcrozat@mandriva.com> 2.19.1-3mdv2008.0
+ Revision: 85666
- Update patch8 with Ia Ora sound theme

* Thu Sep 13 2007 Frederic Crozat <fcrozat@mandriva.com> 2.19.1-2mdv2008.0
+ Revision: 85285
- Patch6 (SUSE): mark gnoem_program_init with sentinel
- Patch7 (SUSE): fix va_list usage
- Patch8: enable sound server and sound events by default, disable all sound events but login and set it to Mandriva one

* Mon Jul 30 2007 Götz Waschk <waschk@mandriva.org> 2.19.1-1mdv2008.0
+ Revision: 56557
- new version

* Tue Jun 19 2007 Götz Waschk <waschk@mandriva.org> 2.19.0-1mdv2008.0
+ Revision: 41286
- new version
- drop merged patch


* Tue Apr 03 2007 Frederic Crozat <fcrozat@mandriva.com> 2.18.0-2mdv2007.1
+ Revision: 150317
- Patch6 (SVN): better set application name, useful for bug-buddy (GNOME bug #424949)

* Mon Mar 12 2007 Götz Waschk <waschk@mandriva.org> 2.18.0-1mdv2007.1
+ Revision: 141784
- new version
- readd ChangeLog
- new version

  + Thierry Vignaud <tvignaud@mandriva.com>
    - no need to package big ChangeLog when NEWS is already there

* Mon Feb 12 2007 Götz Waschk <waschk@mandriva.org> 2.17.91-1mdv2007.1
+ Revision: 119011
- new version

* Mon Jan 22 2007 Götz Waschk <waschk@mandriva.org> 2.17.90-1mdv2007.1
+ Revision: 111950
- new version

* Wed Jan 10 2007 Götz Waschk <waschk@mandriva.org> 2.17.3-1mdv2007.1
+ Revision: 107100
- new version

* Tue Jan 09 2007 Götz Waschk <waschk@mandriva.org> 2.17.2-1mdv2007.1
+ Revision: 106281
- new version

* Tue Dec 19 2006 Frederic Crozat <fcrozat@mandriva.com> 2.17.1-3mdv2007.1
+ Revision: 99126
- Remove a11y disabling patch, at-spi is no longer crashing

* Tue Dec 05 2006 Frederic Crozat <fcrozat@mandriva.com> 2.17.1-2mdv2007.1
+ Revision: 91303
- Regenerate patch4
- Patch6 : disable a11y for now (GNOME bug #382622)

* Tue Dec 05 2006 Götz Waschk <waschk@mandriva.org> 2.17.1-1mdv2007.1
+ Revision: 91006
- new version

* Mon Nov 27 2006 Götz Waschk <waschk@mandriva.org> 2.17.0-1mdv2007.1
+ Revision: 87573
- new version
- unpack patches

* Mon Nov 27 2006 Götz Waschk <waschk@mandriva.org> 2.16.0-1mdv2007.1
+ Revision: 87543
- Import libgnome2

* Tue Sep 05 2006 G�tz Waschk <waschk@mandriva.org> 2.16.0-1mdv2007.0
- update patch 4
- New release 2.16.0

* Wed Aug 30 2006 Frederic Crozat <fcrozat@mandriva.com> 2.15.2-3mdv2007.0
- Update script for orange theme

* Fri Aug 11 2006 Frederic Crozat <fcrozat@mandriva.com> 2.15.2-2mdv2007.0
- Update patch4 for Ia Ora theme
- add post script magic to choose theme according to meta_class

* Wed Aug 09 2006 G�tz Waschk <waschk@mandriva.org> 2.15.2-1mdv2007.0
- rediff patch 4
- New release 2.15.2

* Wed Aug 02 2006 Frederic Crozat <fcrozat@mandriva.com> 2.15.1-2mdv2007.0
- Rebuild with latest dbus

* Tue Jul 11 2006 G�tz Waschk <waschk@mandriva.org> 2.15.1-1mdv2007.0
- update patch 5
- New release 2.15.1

* Thu Apr 13 2006 Frederic Crozat <fcrozat@mandriva.com> 2.14.1-1mdk
- Release 2.14.1

* Mon Feb 27 2006 Frederic Crozat <fcrozat@mandriva.com> 2.12.0.1-4mdk
- Fortify uninstall script

* Thu Feb 23 2006 Frederic Crozat <fcrozat@mandriva.com> 2.12.0.1-3mdk
- use mkrel

* Thu Nov 17 2005 Frederic Crozat <fcrozat@mandriva.com> 2.12.0.1-2mdk
- Rebuild with latest openssl

* Thu Oct 06 2005 Frederic Crozat <fcrozat@mandriva.com> 2.12.0.1-1mdk
- Release 2.12.0.1
- Regenerate patch4 (gotz)

* Thu Jul 07 2005 G�tz Waschk <waschk@mandriva.org> 2.10.1-1mdk
- New release 2.10.1

* Wed Apr 20 2005 Frederic Crozat <fcrozat@mandriva.com> 2.10.0-1mdk 
- Release 2.10.0 based on G�tz Waschk package
- Remove patch 6 (merged upstream)

* Thu Feb 24 2005 Gwenole Beauchesne <gbeauchesne@mandrakesoft.com> 2.8.1-2mdk
- varargs fixes for our supported architectures

* Mon Feb 21 2005 Frederic Crozat <fcrozat@mandrakesoft.com> 2.8.1-1mdk 
- Release 2.8.1

* Tue Jan 04 2005 Frederic Crozat <fcrozat@mandrakesoft.com> 2.8.0-4mdk 
- Rebuild with latest howl

* Wed Nov 24 2004 Frederic Crozat <fcrozat@mandrakesoft.com> 2.8.0-3mdk
- Regenerate patches 1 & 4
- Remove patch2 (merged upsteam)

* Tue Nov 23 2004 Frederic Crozat <fcrozat@mandrakesoft.com> 2.8.0-2mdk 
- Patch5 (Fedora): stat gnome_user_private_dir before doing chmod, for SELinux

* Tue Oct 19 2004 Frederic Crozat <fcrozat@mandrakesoft.com> 2.8.0-1mdk
- New release 2.8.0

* Wed Aug 11 2004 Frederic Crozat <fcrozat@mandrakesoft.com> 2.6.1.2-1mdk
- Release 2.6.1.2
- Remove patch5 (merged upstream)

* Tue Aug 10 2004 Frederic Crozat <fcrozat@mandrakesoft.com> 2.6.1.1-3mdk
- Patch5 (CVS): various fixes, including no sound event (bug #10615)
- Enable libtoolize

* Thu Apr 22 2004 Frederic Crozat <fcrozat@mandrakesoft.com> 2.6.1.1-2mdk
- Fix Buildrequires

* Thu Apr 22 2004 Goetz Waschk <waschk@linux-mandrake.com> 2.6.1.1-1mdk
- New release 2.6.1.1

* Wed Apr 21 2004 Goetz Waschk <goetz@mandrakesoft.com> 2.6.1-1mdk
- New release 2.6.1

