
%define gtk2_version 2.4.0
%define glib2_version 2.4.0
%define nautilus_version 2.2.0
%define desktop_file_utils_version 0.9
%define gphoto_version 2.1.3
%define gconf_version 2.14

Summary: Image viewer, editor, organizer
Name: gthumb
Version: 2.10.11
Release: 8%{?dist}
URL: http://gthumb.sourceforge.net
Source0: http://download.gnome.org/sources/gthumb/2.10/%{name}-%{version}.tar.bz2
Source1: gthumb-importer
Source2: gthumb-importer.desktop
# new upstream icon
Source3: gthumb.png
License: GPLv2+
Group: User Interface/X
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

BuildRequires: gtk2-devel >= %{gtk2_version}
BuildRequires: glib2-devel >= %{glib2_version}
BuildRequires: nautilus >= %{nautilus_version}
BuildRequires: libexif-devel
BuildRequires: libiptcdata-devel
BuildRequires: libopenraw-gnome-devel
BuildRequires: libgnomeui-devel >= 2.2.0
BuildRequires: libpng-devel
BuildRequires: gettext
BuildRequires: automake
BuildRequires: autoconf
BuildRequires: libtool
BuildRequires: intltool
BuildRequires: gnome-doc-utils >= 0.3.2

# Needed or features are missing
%ifnarch s390 s390x
BuildRequires: gphoto2-devel >= %{gphoto_version}
%endif

BuildRequires: libjpeg-devel
BuildRequires: libtiff-devel

Requires(post): scrollkeeper
Requires(post): desktop-file-utils >= %{desktop_file_utils_version}
Requires(pre): GConf2 >= %{gconf_version}
Requires(post): GConf2 >= %{gconf_version}
Requires(preun): GConf2 >= %{gconf_version}

Requires(postun): scrollkeeper
Requires(postun): desktop-file-utils >= %{desktop_file_utils_version}

Patch0: gthumb-libdir.patch
# http://bugzilla.gnome.org/show_bug.cgi?id=577042
Patch1: gthumb-import-dir.patch

# make docs show up in rarian/yelp
Patch2: gthumb-doc-category.patch

%description
gthumb is an application for viewing, editing, and organizing
collections of images.

%prep
%setup -q
%patch0 -p1 -b .libdir
%patch1 -p1 -b .import-dir
%patch2 -p1 -b .doc-category

# force regeneration
rm data/gthumb.schemas

cp %{SOURCE3} data/

autoreconf -i -f

%build

%ifarch s390 s390x
%define gphoto_flags --disable-gphoto2
%else
%define gphoto_flags  %{nil}
%endif
%configure %{gphoto_flags}

# drop unneeded direct library deps with --as-needed
# libtool doesn't make this easy, so we do it the hard way
sed -i -e 's/ -shared / -Wl,-O1,--as-needed\0 /g' -e 's/    if test "$export_dynamic" = yes && test -n "$export_dynamic_flag_spec"; then/      func_append compile_command " -Wl,-O1,--as-needed"\n      func_append finalize_command " -Wl,-O1,--as-needed"\n\0/' libtool

make %{?_smp_mflags}

%install
rm -rf $RPM_BUILD_ROOT

export GCONF_DISABLE_MAKEFILE_SCHEMA_INSTALL=1
make install DESTDIR=$RPM_BUILD_ROOT
unset GCONF_DISABLE_MAKEFILE_SCHEMA_INSTALL

rm -rf $RPM_BUILD_ROOT/var/lib/scrollkeeper
find $RPM_BUILD_ROOT -name "*.a" -exec rm {} \;
find $RPM_BUILD_ROOT -name "*.la" -exec rm {} \;

install -p -m 755 %SOURCE1 $RPM_BUILD_ROOT/%{_bindir}
install -p -m 644 %SOURCE2 $RPM_BUILD_ROOT/%{_datadir}/applications

%find_lang %{name} --with-gnome

%clean
rm -rf $RPM_BUILD_ROOT

%post
scrollkeeper-update -q
update-desktop-database -q
export GCONF_CONFIG_SOURCE=`gconftool-2 --get-default-source`
gconftool-2 --makefile-install-rule %{_sysconfdir}/gconf/schemas/gthumb.schemas > /dev/null || :
touch --no-create %{_datadir}/icons/hicolor
if [ -x /usr/bin/gtk-update-icon-cache ]; then
  gtk-update-icon-cache -q %{_datadir}/icons/hicolor
fi

%pre
if [ "$1" -gt 1 ]; then
  export GCONF_CONFIG_SOURCE=`gconftool-2 --get-default-source`
  gconftool-2 --makefile-uninstall-rule %{_sysconfdir}/gconf/schemas/gthumb.schemas > /dev/null || :
fi

%preun
if [ "$1" -eq 0 ]; then
  export GCONF_CONFIG_SOURCE=`gconftool-2 --get-default-source`
  gconftool-2 --makefile-uninstall-rule %{_sysconfdir}/gconf/schemas/gthumb.schemas > /dev/null || :
fi

%postun
scrollkeeper-update -q
update-desktop-database -q
touch --no-create %{_datadir}/icons/hicolor
if [ -x /usr/bin/gtk-update-icon-cache ]; then
  gtk-update-icon-cache -q %{_datadir}/icons/hicolor
fi

%files -f %{name}.lang
%defattr(-,root,root)

%{_bindir}/*
%{_sysconfdir}/gconf/schemas/*
%{_libdir}/gthumb
%{_libdir}/bonobo/servers/GNOME_GThumb.server
%{_datadir}/gthumb
%{_datadir}/applications/*
%{_mandir}/man*/*
%{_datadir}/icons/hicolor/48x48/apps/gthumb.png

%changelog
* Wed May  5 2010 Matthias Clasen <mclasen@redhat.com> 2.10.11-8
- Use the new upstream icon for gthumb
Resolves: #588885

* Mon May  3 2010 Matthias Clasen <mclasen@redhat.com> 2.10.11-7
- Make docs show up in yelp
Resolves: #588544

* Mon Nov 30 2009 Dennis Gregorovic <dgregor@redhat.com> - 2.10.11-6.1
- Rebuilt for RHEL 6

* Mon Aug  3 2009 Matthias Clasen <mclasen@redhat.com> - 2.10.11-6
- Drop unneeded direct deps

* Fri Jul 24 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.10.11-5
- Rebuilt for https://fedoraproject.org/wiki/Fedora_12_Mass_Rebuild

* Thu Jul  2 2009 Matthias Clasen <mclasen@redhat.com> - 2.10.11-4
- Rebuild to shrink GConf schemas

* Fri Apr 10 2009 Matthias Clasen <mclasen@redhat.com> - 2.10.11-3
- Fix directory ownership

* Fri Mar 27 2009 Matthias Clasen <mclasen@redhat.com> - 2.10.11-2
- Fix the photo import location (#492179)

* Fri Feb 27 2009 Matthias Clasen <mclasen@redhat.com> - 2.10.11-1
- Update to 2.10.11

* Thu Feb 26 2009 Matthias Clasen <mclasen@redhat.com> - 2.10.10-5
- Make it build

* Tue Feb 24 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.10.10-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_11_Mass_Rebuild

* Thu Oct 23 2008 Matthias Clasen  <mclasen@redhat.com> - 2.10.10-3
- Avoid tons of GTK+ warnings

* Mon Sep 22 2008 Matthias Clasen  <mclasen@redhat.com> - 2.10.10-1
- Update to 2.10.10

* Tue Aug  5 2008 Matthias Clasen  <mclasen@redhat.com> - 2.10.9-1
- Update to 2.10.9

* Fri Jul 18 2008 Matthias Clasen  <mclasen@redhat.com> - 2.10.8-4
- Try to fix a crash (#453181)

* Fri May  2 2008 David Zeuthen <davidz@redhat.com> - 2.10.8-3
- Drop x-content patch and provide gthumb-importer and a desktop
  file for it (#444635)

* Mon Feb 18 2008 Fedora Release Engineering <rel-eng@fedoraproject.org> - 2.10.8-2
- Autorebuild for GCC 4.3

* Sun Jan 20 2008 Matthias Clasen <mclasen@redhat.com> - 2.10.8-1
- Update to 2.10.8

* Fri Jan 18 2008 Matthias Clasen <mclasen@redhat.com> - 2.10.7-2
- Add content-type support

* Mon Oct 15 2007 Matthias Clasen <mclasen@redhat.com> - 2.10.7-1
- Update to 2.10.7 (bug fixes)

* Thu Oct  2 2007 Matthias Clasen <mclasen@redhat.com> - 2.10.6-2
- Fix rotation of images with # in their name (#248708)

* Tue Sep  4 2007 Matthias Clasen <mclasen@redhat.com> - 2.10.6-1
- Update to 2.10.6

* Tue Aug 28 2007 Fedora Release Engineering <rel-eng at fedoraproject dot org> - 2.10.5-5
- Rebuild for selinux ppc32 issue.

* Wed Aug 22 2007 Adam Jackson <ajax@redhat.com> - 2.10.5-4
- Rebuild for PPC toolchain bug

* Tue Aug  7 2007 Matthias Clasen <mclasen@redhat.com> - 2.10.5-3
- Update the license field
- Use %%find_lang for help files

* Fri Jul  6 2007 Matthias Clasen <mclasen@redhat.com> - 2.10.5-2
- Fix a directory ownership issue

* Wed Jun 27 2007 Matthias Clasen <mclasen@redhat.com> - 2.10.5-1
- Update to 2.10.5

* Tue Jun 19 2007 Matthias Clasen <mclasen@redhat.com> - 2.10.4-1
- Update to 2.10.4

* Sat May 19 2007 Matthias Clasen <mclasen@redhat.com> - 2.10.3-1
- Update to 2.10.3
- Drop upstreamed patch

* Wed May  9 2007 Matthias Clasen <mclasen@redhat.com> - 2.10.2-3
- Add dependency on libopenraw-gnome (#236184)

* Thu May  3 2007 Matthias Clasen <mclasen@redhat.com> - 2.10.2-2
- Add dependency on libiptcdata (#127690)

* Fri Apr 20 2007 Matthias Clasen <mclasen@redhat.com> - 2.10.2-1
- Update to 2.10.2
- 
* Mon Apr  2 2007 Matthias Clasen <mclasen@redhat.com> - 2.10.0-3
- Use the PICTURES user dir as default location for photo import

* Fri Mar 23 2007 Matthias Clasen <mclasen@redhat.com> - 2.10.0-2
- Remove a no-longer needed patch (#233350)

* Tue Mar 20 2007 Matthias Clasen <mclasen@redhat.com> - 2.10.0-1
- Update to 2.10.0

* Tue Feb 27 2007 Matthias Clasen <mclasen@redhat.com> - 2.9.3-1
- Update to 2.9.3

* Wed Feb 21 2007 Matthias Clasen <mclasen@redhat.com> - 2.9.2-1
- Update to 2.9.2
- Move libgthumb.so out of libdir

* Wed Jan 10 2007 Matthias Clasen <mclasen@redhat.com> - 2.9.1-1
- Update to 2.9.1

* Sun Oct 22 2006 Matthias Clasen <mclasen@redhat.com> - 2.7.9-1
- Update to 2.7.9

* Wed Oct 18 2006 Matthias Clasen <mclasen@redhat.com> - 2.7.8-4
- fix up requires (#202549)

* Thu Sep  7 2006 Matthias Clasen <mclasen@redhat.com> - 2.7.8-3
- fix directory ownership issues (#205682)

* Mon Aug  7 2006 Jindrich Novy <jnovy@redhat.com> - 2.7.8-2.fc6
- fix URL in Source0

* Wed Aug  2 2006 Matthias Clasen <mclasen@redhat.com> - 2.7.8-1.fc6
- Update to 2.7.8
- Fix some documentation inaccuracies (#175165)

* Fri Jul 14 2006 Matthias Clasen <mclasen@redhat.com> - 2.7.7-4
- Don't BR gphoto2-devel on s390

* Wed Jul 12 2006 Jesse Keating <jkeating@redhat.com> - 2.7.7-3
- rebuild
- Don't get gphoto2 on s390(x)

* Mon May 22 2006 Matthias Clasen <mclasen@redhat.com> - 2.7.7-2  
- Update to 2.7.7  

* Thu Apr 20 2006 Matthias Clasen <mclasen@redhat.com> - 2.7.6-2  
- Update to 2.7.6  

* Fri Mar 24 2006 Matthias Clasen <mclasen@redhat.com> - 2.7.5.1-2
- Update to 2.7.5.1

* Mon Mar 20 2006 Matthias Clasen <mclasen@redhat.com> - 2.7.5-1
- Update to 2.7.5

* Thu Mar  2 2006 Ray Strode <rstrode@redhat.com> - 2.7.3-2
- Make saving work again (bug 183141)

* Wed Feb 15 2006 Matthias Clasen <mclasen@redhat.com> - 2.7.3-1
- Update to 2.7.3
- BuildRequire libgphoto2

* Fri Feb 10 2006 Jesse Keating <jkeating@redhat.com> - 2.7.2-2.2
- bump again for double-long bug on ppc(64)

* Tue Feb 07 2006 Jesse Keating <jkeating@redhat.com> - 2.7.2-2.1
- rebuilt for new gcc4.1 snapshot and glibc changes

* Fri Jan 27 2006 Ray Strode <rstrode@redhat.com> - 2.7.2-2
- drop redhat-menus buildrequires
- use make install DESTDIR instead %%makeinstall

* Wed Jan  4 2006 Matthias Clasen <mclasen@redhat.com> - 2.7.2-1
- Update to 2.7.2
- Drop upstreamed patches

* Fri Dec 09 2005 Jesse Keating <jkeating@redhat.com> - 2.7.1-1.1
- rebuilt

* Sun Nov 13 2005 Matthias Clasen <mclasen@redhat.com> - 2.7.1-1
- Update to 2.7.1

* Wed Oct 12 2005 Matthias Clasen <mclasen@redhat.com> - 2.6.8-2
- Use GTK+ stock icons where available

* Thu Sep 29 2005 Matthias Clasen <mclasen@redhat.com> - 2.6.8-1
- Update to 2.6.8

* Thu Sep  8 2005 Matthias Clasen <mclasen@redhat.com> - 2.6.7-1
- Update to 2.6.7

* Tue Aug 18 2005 John (J5) Palmieri <johnp@redhat.com> - 2.6.2-2
- Bump and rebuild for cairo ABI changes

* Fri Jul 15 2005 Matthias Clasen <mclasen@redhat.com> - 2.6.6-1
- Newer upstream version

* Mon May 16 2005 John (J5) Palmieri <johnp@redhat.com> - 2.6.5-1
- Minor updated that fixes a couple of bugs and adds some translations

* Mon Mar 28 2005 Matthias Clasen <mclasen@redhat.com> 
- Rebuild against newer libexif

* Wed Mar 16 2005 John (J5) Palmieri <johnp@redhat.com> - 2.6.4-1
- Update to upstream version 2.6.4

* Thu Mar  3 2005 Marco Pesenti Gritti <mpg@redhat.com> 2.6.3-2
- Rebuild

* Mon Jan 31 2005 Matthias Clasen <mclasen@redhat.com> 2.6.3
- Update to 2.6.3

* Tue Nov  9 2004 Marco Pesenti Gritti <mpg@redhat.com> 2.6.0.1-2
- Use upstream desktop file, it has translations and mime

* Sun Oct 31 2004 Christopher Aillon <caillon@redhat.com> 2.6.0.1-1
- Update to 2.6.0.1

* Thu Sep 30 2004 Christopher Aillon <caillon@redhat.com> 2.4.2-3
- PreReq desktop-file-utils >= 0.9

* Wed Sep 29 2004 Ray Strode <rstrode@redhat.com> 2.4.2-2
- Move gthumb.desktop to redhat-menus (#131726)
- Require recent desktop-file-utils
- Call update-desktop-database from %postun

* Mon Sep 13 2004 Christopher Aillon <caillon@redhat.com> 2.4.2-1
  - gthumb.desktop: Add supported mime types (#131740)
  - gthumb.spec: Run update-desktop-database (#131740)
  - Update to 2.4.2

* Mon Aug 23 2004 Christopher Aillon <caillon@redhat.com> 2.4.1-2
- Only use catalog view if the directory has an image file present (alexl)

* Wed Aug 11 2004 Christopher Aillon <caillon@redhat.com> 2.4.1-1
- Update to 2.4.1

* Tue Jun 29 2004 Christopher Aillon <caillon@redhat.com> 2.4.0-1
- Update to 2.4.0

* Tue Jun 15 2004 Elliot Lee <sopwith@redhat.com>
- rebuilt

* Tue Apr 13 2004 Warren Togami <wtogami@redhat.com> 2.3.2-2
- #111001 BR: libgnomeui-devel gettext libpng-devel
  BR or missing features: gphoto2-devel libjpeg-devel libtiff-devel

* Fri Apr  2 2004 Mark McLoughlin <markmc@redhat.com> 2.3.2-1
- Update to 2.3.2

* Tue Mar 02 2004 Elliot Lee <sopwith@redhat.com>
- rebuilt

* Wed Feb 25 2004 Alexander Larsson <alexl@redhat.com> 2.3.1-1
- update to 2.3.1

* Fri Feb 13 2004 Elliot Lee <sopwith@redhat.com>
- rebuilt

* Mon Dec 22 2003 Matt Wilson <msw@redhat.com> 2.2.0-1
- 2.2.0

* Wed Jul  9 2003 Havoc Pennington <hp@redhat.com> 2.0.2-1
- 2.0.2
- buildreq libgnomeprint

* Wed Jun 04 2003 Elliot Lee <sopwith@redhat.com>
- rebuilt

* Wed Feb  5 2003 Havoc Pennington <hp@redhat.com> 2.0.1-1
- 2.0.1

* Wed Jan 22 2003 Tim Powers <timp@redhat.com>
- rebuilt

* Tue Jan  7 2003 Havoc Pennington <hp@redhat.com>
- 1.108
- disable schema install during makeinstall

* Thu Jan 02 2003 Florian La Roche <Florian.LaRoche@redhat.de>
- require scrollkeeper

* Mon Dec 16 2002 Havoc Pennington <hp@redhat.com>
- rebuild

* Thu Dec 12 2002 Havoc Pennington <hp@redhat.com>
- Initial build.


