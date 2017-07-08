%global efivar_version 30-1
%global efibootmgr_version 13-1

Name:           fwupdate
Version:        8
Release:        4%{?dist}
Summary:        Tools to manage UEFI firmware updates
License:        GPLv2+
URL:            https://github.com/rhinstaller/fwupdate
Requires:       %{name}-libs%{?_isa} = %{version}-%{release}
BuildRequires:  efivar-devel >= %{efivar_version}
BuildRequires:  gnu-efi gnu-efi-devel
BuildRequires:  pesign
BuildRequires:  elfutils popt-devel git gettext pkgconfig
BuildRequires:  systemd
%ifarch x86_64 %{ix86}
BuildRequires: libsmbios-devel
%endif
ExclusiveArch:  x86_64 %{ix86} aarch64
Source0:        https://github.com/rhinstaller/fwupdate/releases/download/%{name}-%{version}/%{name}-%{version}.tar.bz2
Patch0001:	0001-Require-newer-efivar-for-bug-fixes.patch

%ifarch x86_64
%global efiarch x64
%endif
%ifarch %{ix86}
%global efiarch ia32
%endif
%ifarch aarch64
%global efiarch aa64
%endif

# Figure out the right file path to use
%global efidir %(eval echo $(grep ^ID= /etc/os-release | sed -e 's/^ID=//' -e 's/rhel/redhat/'))

%description
fwupdate provides a simple command line interface to the UEFI firmware updates.

%package libs
Summary: Library to manage UEFI firmware updates
%ifnarch %{ix86}
Requires: shim
%endif
Requires: %{name}-efi = %{version}-%{release}

%description libs
Library to allow for the simple manipulation of UEFI firmware updates.

%package devel
Summary: Development headers for libfwup
Requires: %{name}-libs%{?_isa} = %{version}-%{release}
Requires: efivar-devel >= %{efivar_version}

%description devel
development headers required to use libfwup.

%package efi
Summary: UEFI binaries used by libfwup
Requires: %{name}-libs = %{version}-%{release}

%description efi
UEFI binaries used by libfwup.

%prep
%setup -q -n %{name}-%{version}
git init
git config user.email "%{name}-owner@fedoraproject.org"
git config user.name "Fedora Ninjas"
git add .
git commit -a -q -m "%{version} baseline."
git am %{patches} </dev/null
git config --unset user.email
git config --unset user.name

%build
make OPT_FLAGS="$RPM_OPT_FLAGS" libdir=%{_libdir} bindir=%{_bindir} \
     EFIDIR=%{efidir} %{?_smp_mflags}
mv -v efi/fwup%{efiarch}.efi efi/fwup%{efiarch}.unsigned.efi
%pesign -s -i efi/fwup%{efiarch}.unsigned.efi -o efi/fwup%{efiarch}.efi

%install
rm -rf $RPM_BUILD_ROOT
%make_install EFIDIR=%{efidir} libdir=%{_libdir} \
       bindir=%{_bindir} mandir=%{_mandir} localedir=%{_datadir}/locale/ \
       includedir=%{_includedir} libexecdir=%{_libexecdir} \
       datadir=%{_datadir}

%post libs
/sbin/ldconfig
%systemd_post fwupdate-cleanup.service

%preun libs
%systemd_preun fwupdate-cleanup.service

%postun libs
/sbin/ldconfig
%systemd_postun_with_restart pesign.service

%files
%defattr(-,root,root,-)
%{!?_licensedir:%global license %%doc}
%license COPYING
# %%doc README
%{_bindir}/fwupdate
%{_datadir}/locale/en/fwupdate.po
%doc %{_mandir}/man1/*
%dir %{_datadir}/bash-completion/completions
%{_datadir}/bash-completion/completions/fwupdate

%files devel
%defattr(-,root,root,-)
%doc %{_mandir}/man3/*
%{_includedir}/*
%{_libdir}/*.so
%{_libdir}/pkgconfig/*.pc

%files libs
%defattr(-,root,root,-)
%{_libdir}/*.so.*
%{_datadir}/locale/en/libfwup.po
%{_unitdir}/fwupdate-cleanup.service
%attr(0755,root,root) %dir %{_datadir}/fwupdate/
%config(noreplace) %ghost %{_datadir}/fwupdate/done
%attr(0755,root,root) %dir %{_libexecdir}/fwupdate/
%{_libexecdir}/fwupdate/cleanup

%files efi
%defattr(-,root,root,-)
%attr(0700,root,root) %dir /boot/efi
%dir /boot/efi/EFI/%{efidir}/
%dir /boot/efi/EFI/%{efidir}/fw/
/boot/efi/EFI/%{efidir}/fwup%{efiarch}.efi

%changelog
* Sat Jul 08 2017 Peter Jones <pjones@redhat.com> - 8-4
- Rebuild for efivar-31-1.fc26
  Related: rhbz#1468841

* Fri Feb 10 2017 Fedora Release Engineering <releng@fedoraproject.org> - 8-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_26_Mass_Rebuild

* Tue Sep 27 2016 Peter Jones <pjones@redhat.com> - 8-2
- Rebuild for efivar 30.

* Fri Aug 19 2016 Peter Jones <pjones@redhat.com> - 8-1
- Update to fwupdate 8
- Fix some i686 build errors
- Be less stupid about SONAMEs so in the future we'll only have to rebuild
  dependent things on actual ABI changes.
- Only depend on libsmbios on x86, for now, because it hasn't been ported to
  Aarch64.

* Wed Aug 17 2016 Peter Jones <pjones@redhat.com> - 7-1
- Update to fwupdate 7
- Fix the fix for ae7b85
- fix one place where a second "rc" varibale is clobbering a result.

* Tue Aug 16 2016 Peter Jones <pjones@redhat.com> - 6-1
- Update to fwupdate 6
- lots of build fixes for newer compilers and such
- Use libsmbios on some systems to enable firmware updates (Mario Limonciello)
- Use the correct reset type from the QueryCapsuleInfo data
- Lots of fixes from auditing
- Use efivar's error reporting infrastructure

* Fri Aug 12 2016 Adam Williamson <awilliam@redhat.com> - 0.5-5
- backport a couple of commits to fix build against efivar 26

* Wed Feb 03 2016 Fedora Release Engineering <releng@fedoraproject.org> - 0.5-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_24_Mass_Rebuild

* Wed Nov 18 2015 Peter Jones <pjones@redhat.com> - 0.5-3
- Temporarily don't require shim on i?86 - we've never built it there, and
  libfwup knows how to handle it not being there just fine.

* Wed Nov 18 2015 Peter Jones <pjones@redhat.com> - 0.5-2
- Fix missing -libs Requires: due to editing error

* Wed Nov 18 2015 Peter Jones <pjones@redhat.com> - 0.5-1
- Rebase to 0.5
- Highlights in 0.5:
  - fwupdate.efi is called fwup$EFI_ARCH.efi now so weird platforms can have
    them coexist.  "Platform" here might mean "distro tools that care about
    multilib".  Anyway, it's needed to support things like baytrail.
  - Worked around shim command line bug where we need to treat LOAD_OPTIONS
    differently if we're invoked from the shell vs BDS
  - various debug features - SHIM_DEBUG and FWUPDATE_VERBOSE UEFI variables
    that'll let you get some debugging info some times
  - oh yeah, the actual debuginfo is useful
  - Automatically cleans up old instances on fresh OS installs
  - valgrind --leak-check=full on fwupdate doesn't show any errors at all
  - covscan shows only two things; one *really* doesn't matter, the other is
    because it doesn't understand our firmware variable data structure and
    can't work out that we have guaranteed the length of some data in a code
    path it isn't considering.
  - fwup_set_up_update() API improvements
  - killed fwup_sterror() and friends entirely
  - Should work on x64, ia32, and aarch64.

* Wed Jun 17 2015 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.4-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_23_Mass_Rebuild

* Tue Jun 02 2015 Peter Jones <pjones@redhat.com> - 0.4-1
- Update to 0.4
- Set DESTDIR so it's more consistently respected
- Always use upper case for Boot#### names.
- Create abbreviated device paths for our BootNext entry.
- Make subdir Makefiles get the version right.
- Fix ucs2len() to handle max=-1 correctly.
- Compare the right blobs when we're searching old boot entries.
- Fix .efi generation on non-x86 platforms.
- Use a relative path for fwupdate.efi when launched from shim.
- Show fewer debugging messages.
- Set BootNext when we find an old Boot#### variable as well.
- Add fwup_get_fw_type().

* Mon Jun 01 2015 Peter Jones <pjones@redhat.com> - 0.3-4
- Make abbreviated device paths work in the BootNext entry.
- Fix a ucs2 parsing bug.

* Mon Jun 01 2015 Peter Jones <pjones@redhat.com> - 0.3-3
- Always use abbreviated device paths for Boot#### entries.

* Mon Jun 01 2015 Peter Jones <pjones@redhat.com> - 0.3-2
- Fix boot entry naming.

* Thu May 28 2015 Peter Jones <pjones@redhat.com> - 0.3-1
- Here we go again.
