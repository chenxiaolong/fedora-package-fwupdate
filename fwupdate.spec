%global efivar_version 0.19-1
%global efibootmgr_version 0.12-1

Name:           fwupdate
Version:        0.4
Release:        1%{?dist}
Summary:        Tools to manage UEFI firmware updates
License:        GPLv2+
URL:            https://github.com/rhinstaller/fwupdate
Requires:       %{name}-libs%{?_isa} = %{version}-%{release}
BuildRequires:  efivar-devel >= %{efivar_version}
BuildRequires:  gnu-efi gnu-efi-devel
BuildRequires:  pesign
BuildRequires:  popt-devel git gettext pkgconfig
ExclusiveArch:  x86_64 %{ix86} aarch64

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
%global efidir %(eval grep ^ID= /etc/os-release | sed -e 's/^ID=//' -e 's/rhel/redhat/')

Source0:        https://github.com/rhinstaller/fwupdate/releases/download/%{name}-%{version}/%{name}-%{version}.tar.bz2

%description
fwupdate provides a simple command line interface to the UEFI firmware updates.

%package libs
Summary: Library to manage UEFI firmware updates

%description libs
Library to allow for the simple manipulation of UEFI firmware updates.

%package devel
Summary: Development headers for libfwup
Requires: %{name}-libs%{?_isa} = %{version}-%{release}
Requires: efivar-devel >= %{efivar_version}

%description devel
development headers required to use libfwup.

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

%install
rm -rf $RPM_BUILD_ROOT
%makeinstall EFIDIR=%{efidir} DESTDIR=${RPM_BUILD_ROOT}

%post libs -p /sbin/ldconfig

%postun libs -p /sbin/ldconfig

%files
%defattr(-,root,root,-)
%{!?_licensedir:%global license %%doc}
%license COPYING
# %%doc README
%{_bindir}/fwupdate
%attr(0700,root,root) %dir /boot/efi
%dir /boot/efi/EFI/%{efidir}/
/boot/efi/EFI/%{efidir}/fwupdate.efi
%dir /boot/efi/EFI/%{efidir}/fw/
%{_datadir}/locale/en/*.po
%doc %{_mandir}/man1/*

%files devel
%defattr(-,root,root,-)
%doc %{_mandir}/man3/*
%{_includedir}/*
%{_libdir}/*.so
%{_libdir}/pkgconfig/*.pc

%files libs
%defattr(-,root,root,-)
%{_libdir}/*.so.*

%changelog
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
