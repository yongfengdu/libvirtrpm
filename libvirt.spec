# -*- rpm-spec -*-

# This spec file assumes you are building on a Fedora or RHEL version
# that's still supported by the vendor. It may work on other distros
# or versions, but no effort will be made to ensure that going forward.
%define min_rhel 7
%define min_fedora 29

%if (0%{?fedora} && 0%{?fedora} >= %{min_fedora}) || (0%{?rhel} && 0%{?rhel} >= %{min_rhel})
    %define supported_platform 1
%else
    %define supported_platform 0
%endif

# Default to skipping autoreconf.  Distros can change just this one line
# (or provide a command-line override) if they backport any patches that
# touch configure.ac or Makefile.am.
%{!?enable_autotools:%global enable_autotools 0}

# The hypervisor drivers that run in libvirtd
%define with_qemu          0%{!?_without_qemu:1}
%define with_lxc           0%{!?_without_lxc:1}
%define with_libxl         0%{!?_without_libxl:1}
%define with_vbox          0%{!?_without_vbox:1}

%define with_qemu_tcg      %{with_qemu}

%define qemu_kvm_arches %{ix86} x86_64

%if 0%{?fedora}
    %define qemu_kvm_arches %{ix86} x86_64 %{power64} s390x %{arm} aarch64
%endif

%if 0%{?rhel}
    %define with_qemu_tcg 0
    %define qemu_kvm_arches x86_64 %{power64} aarch64 s390x
%endif

%ifarch %{qemu_kvm_arches}
    %define with_qemu_kvm      %{with_qemu}
%else
    %define with_qemu_kvm      0
%endif

%if ! %{with_qemu_tcg} && ! %{with_qemu_kvm}
    %define with_qemu 0
%endif

# Then the hypervisor drivers that run outside libvirtd, in libvirt.so
%define with_openvz        0%{!?_without_openvz:1}
%define with_vmware        0%{!?_without_vmware:1}
%define with_phyp          0%{!?_without_phyp:1}
%define with_esx           0%{!?_without_esx:1}
%define with_hyperv        0%{!?_without_hyperv:1}

# Then the secondary host drivers, which run inside libvirtd
%define with_storage_rbd      0%{!?_without_storage_rbd:1}
%if 0%{?fedora}
    %define with_storage_sheepdog 0%{!?_without_storage_sheepdog:1}
%else
    %define with_storage_sheepdog 0
%endif
%define with_storage_gluster 0%{!?_without_storage_gluster:1}
%define with_numactl          0%{!?_without_numactl:1}

# F25+ has zfs-fuse
%if 0%{?fedora}
    %define with_storage_zfs      0%{!?_without_storage_zfs:1}
%else
    %define with_storage_zfs      0
%endif

# We need a recent enough libiscsi (>= 1.18.0)
%if 0%{?fedora} || 0%{?rhel} > 7
    %define with_storage_iscsi_direct 0%{!?_without_storage_iscsi_direct:1}
%else
    %define with_storage_iscsi_direct 0
%endif

# A few optional bits off by default, we enable later
%define with_fuse          0%{!?_without_fuse:0}
%define with_sanlock       0%{!?_without_sanlock:0}
%define with_numad         0%{!?_without_numad:0}
%define with_firewalld     0%{!?_without_firewalld:0}
%define with_firewalld_zone 0%{!?_without_firewalld_zone:0}
%define with_libssh2       0%{!?_without_libssh2:0}
%define with_wireshark     0%{!?_without_wireshark:0}
%define with_libssh        0%{!?_without_libssh:0}
%define with_bash_completion  0%{!?_without_bash_completion:0}

# Finally set the OS / architecture specific special cases

# Xen is available only on i386 x86_64 ia64
%ifnarch %{ix86} x86_64 ia64
    %define with_libxl 0
%endif

# vbox is available only on i386 x86_64
%ifnarch %{ix86} x86_64
    %define with_vbox 0
%endif

# Numactl is not available on many non-x86 archs
%ifarch s390 s390x %{arm} riscv64
    %define with_numactl 0
%endif

# zfs-fuse is not available on some architectures
%ifarch s390 s390x aarch64 riscv64
    %define with_storage_zfs 0
%endif

# Ceph dropping support for 32-bit hosts
%if 0%{?fedora} >= 30
    %ifarch %{arm} %{ix86}
        %define with_storage_rbd 0
    %endif
%endif

# RHEL doesn't ship OpenVZ, VBox, PowerHypervisor,
# VMware, libxenserver (xenapi), libxenlight (Xen 4.1 and newer),
# or HyperV.
%if 0%{?rhel}
    %define with_openvz 0
    %define with_vbox 0
    %define with_phyp 0
    %define with_vmware 0
    %define with_xenapi 0
    %define with_libxl 0
    %define with_hyperv 0
    %define with_vz 0

    %if 0%{?rhel} > 7
        %define with_lxc 0
    %endif
%endif

%define with_firewalld 1

%if 0%{?fedora} >= 31 || 0%{?rhel} > 7
    %define with_firewalld_zone 0%{!?_without_firewalld_zone:1}
%endif


# fuse is used to provide virtualized /proc for LXC
%if %{with_lxc}
    %define with_fuse      0%{!?_without_fuse:1}
%endif

# Enable sanlock library for lock management with QEMU
# Sanlock is available only on arches where kvm is available for RHEL
%if 0%{?fedora}
    %define with_sanlock 0%{!?_without_sanlock:1}
%endif
%if 0%{?rhel}
    %ifarch %{qemu_kvm_arches}
        %define with_sanlock 0%{!?_without_sanlock:1}
    %endif
%endif

# Enable libssh2 transport for new enough distros
%if 0%{?fedora}
    %define with_libssh2 0%{!?_without_libssh2:1}
%endif

# Enable wireshark plugins for all distros shipping libvirt 1.2.2 or newer
%if 0%{?fedora}
    %define with_wireshark 0%{!?_without_wireshark:1}
    %define wireshark_plugindir %(pkg-config --variable plugindir wireshark)/epan
%endif

# Enable libssh transport for new enough distros
%if 0%{?fedora} || 0%{?rhel} > 7
    %define with_libssh 0%{!?_without_libssh:1}
%endif

%define with_bash_completion  0%{!?_without_bash_completion:1}

# Use Python 3 when possible, Python 2 otherwise
%if 0%{?fedora} || 0%{?rhel} > 7
    %define python python3
%else
    %define python python2
%endif


%if %{with_qemu} || %{with_lxc}
# numad is used to manage the CPU and memory placement dynamically,
# it's not available on many non-x86 architectures.
    %ifnarch s390 s390x %{arm} riscv64
        %define with_numad    0%{!?_without_numad:1}
    %endif
%endif

# Force QEMU to run as non-root
%define qemu_user  qemu
%define qemu_group  qemu


# RHEL releases provide stable tool chains and so it is safe to turn
# compiler warning into errors without being worried about frequent
# changes in reported warnings
%if 0%{?rhel}
    %define enable_werror --enable-werror
%else
    %define enable_werror --disable-werror
%endif

%if 0%{?rhel} == 7
    %define tls_priority "NORMAL"
%else
    %define tls_priority "@LIBVIRT,SYSTEM"
%endif


Summary: Library providing a simple virtualization API
Name: libvirt
Version: 5.6.0
Release: 1%{?dist}
License: LGPLv2+
URL: https://libvirt.org/

%if %(echo %{version} | grep -q "\.0$"; echo $?) == 1
    %define mainturl stable_updates/
%endif
Source: https://libvirt.org/sources/%{?mainturl}libvirt-%{version}.tar.xz

Requires: libvirt-daemon = %{version}-%{release}
Requires: libvirt-daemon-config-network = %{version}-%{release}
Requires: libvirt-daemon-config-nwfilter = %{version}-%{release}
%if %{with_libxl}
Requires: libvirt-daemon-driver-libxl = %{version}-%{release}
%endif
%if %{with_lxc}
Requires: libvirt-daemon-driver-lxc = %{version}-%{release}
%endif
%if %{with_qemu}
Requires: libvirt-daemon-driver-qemu = %{version}-%{release}
%endif
# We had UML driver, but we've removed it.
Obsoletes: libvirt-daemon-driver-uml <= 5.0.0
Obsoletes: libvirt-daemon-uml <= 5.0.0
%if %{with_vbox}
Requires: libvirt-daemon-driver-vbox = %{version}-%{release}
%endif
Requires: libvirt-daemon-driver-nwfilter = %{version}-%{release}

Requires: libvirt-daemon-driver-interface = %{version}-%{release}
Requires: libvirt-daemon-driver-secret = %{version}-%{release}
Requires: libvirt-daemon-driver-storage = %{version}-%{release}
Requires: libvirt-daemon-driver-network = %{version}-%{release}
Requires: libvirt-daemon-driver-nodedev = %{version}-%{release}
Requires: libvirt-client = %{version}-%{release}
Requires: libvirt-libs = %{version}-%{release}

# All build-time requirements. Run-time requirements are
# listed against each sub-RPM
%if 0%{?enable_autotools}
BuildRequires: autoconf
BuildRequires: automake
BuildRequires: gettext-devel
BuildRequires: libtool
BuildRequires: /usr/bin/pod2man
%endif
BuildRequires: gcc
BuildRequires: git
%if 0%{?fedora} || 0%{?rhel} > 7
BuildRequires: perl-interpreter
%else
BuildRequires: perl
%endif
BuildRequires: %{python}
BuildRequires: systemd-units
%if %{with_libxl}
BuildRequires: xen-devel
%endif
BuildRequires: libxml2-devel
BuildRequires: libxslt
BuildRequires: readline-devel
%if %{with_bash_completion}
BuildRequires: bash-completion >= 2.0
%endif
BuildRequires: ncurses-devel
BuildRequires: gettext
BuildRequires: libtasn1-devel
BuildRequires: gnutls-devel
BuildRequires: libattr-devel
# For pool-build probing for existing pools
BuildRequires: libblkid-devel >= 2.17
# for augparse, optionally used in testing
BuildRequires: augeas
BuildRequires: systemd-devel >= 185
BuildRequires: libpciaccess-devel >= 0.10.9
BuildRequires: yajl-devel
%if %{with_sanlock}
BuildRequires: sanlock-devel >= 2.4
%endif
BuildRequires: libpcap-devel
BuildRequires: libnl3-devel
BuildRequires: libselinux-devel
BuildRequires: dnsmasq >= 2.41
BuildRequires: iptables
BuildRequires: radvd
BuildRequires: ebtables
BuildRequires: module-init-tools
BuildRequires: cyrus-sasl-devel
BuildRequires: polkit >= 0.112
# For mount/umount in FS driver
BuildRequires: util-linux
%if %{with_qemu}
# For managing ACLs
BuildRequires: libacl-devel
# From QEMU RPMs
BuildRequires: /usr/bin/qemu-img
%endif
# For LVM drivers
BuildRequires: lvm2
# For pool type=iscsi
BuildRequires: iscsi-initiator-utils
%if %{with_storage_iscsi_direct}
# For pool type=iscsi-direct
BuildRequires: libiscsi-devel
%endif
# For disk driver
BuildRequires: parted-devel
# For Multipath support
BuildRequires: device-mapper-devel
# For XFS reflink clone support
BuildRequires: xfsprogs-devel
%if %{with_storage_rbd}
BuildRequires: librados2-devel
BuildRequires: librbd1-devel
%endif
%if %{with_storage_gluster}
BuildRequires: glusterfs-api-devel >= 3.4.1
BuildRequires: glusterfs-devel >= 3.4.1
%endif
%if %{with_storage_sheepdog}
BuildRequires: sheepdog
%endif
%if %{with_storage_zfs}
# Support any conforming implementation of zfs. On stock Fedora
# this is zfs-fuse, but could be zfsonlinux upstream RPMs
BuildRequires: /sbin/zfs
BuildRequires: /sbin/zpool
%endif
%if %{with_numactl}
# For QEMU/LXC numa info
BuildRequires: numactl-devel
%endif
BuildRequires: libcap-ng-devel >= 0.5.0
%if %{with_fuse}
BuildRequires: fuse-devel >= 2.8.6
%endif
%if %{with_phyp} || %{with_libssh2}
BuildRequires: libssh2-devel >= 1.3.0
%endif

BuildRequires: netcf-devel >= 0.2.2
%if %{with_esx}
BuildRequires: libcurl-devel
%endif
%if %{with_hyperv}
BuildRequires: libwsman-devel >= 2.2.3
%endif
BuildRequires: audit-libs-devel
# we need /usr/sbin/dtrace
BuildRequires: systemtap-sdt-devel

# For mount/umount in FS driver
BuildRequires: util-linux
# For showmount in FS driver (netfs discovery)
BuildRequires: nfs-utils

# Communication with the firewall and polkit daemons use DBus
BuildRequires: dbus-devel

# Fedora build root suckage
BuildRequires: gawk

# For storage wiping with different algorithms
BuildRequires: scrub

%if %{with_numad}
BuildRequires: numad
%endif

%if %{with_wireshark}
BuildRequires: wireshark-devel >= 2.4.0
%endif

%if %{with_libssh}
BuildRequires: libssh-devel >= 0.7.0
%endif

%if 0%{?fedora} || 0%{?rhel} > 7
BuildRequires: rpcgen
BuildRequires: libtirpc-devel
%endif

%if %{with_firewalld_zone}
BuildRequires: firewalld-filesystem
%endif

Provides: bundled(gnulib)

%description
Libvirt is a C toolkit to interact with the virtualization capabilities
of recent versions of Linux (and other OSes). The main package includes
the libvirtd server exporting the virtualization support.

%package docs
Summary: API reference and website documentation

%description docs
Includes the API reference for the libvirt C library, and a complete
copy of the libvirt.org website documentation.

%package daemon
Summary: Server side daemon and supporting files for libvirt library

# All runtime requirements for the libvirt package (runtime requrements
# for subpackages are listed later in those subpackages)

# The client side, i.e. shared libs are in a subpackage
Requires: %{name}-libs = %{version}-%{release}

# for modprobe of pci devices
Requires: module-init-tools

# for /sbin/ip & /sbin/tc
Requires: iproute
# tc is provided by iproute-tc since at least Fedora 26
%if 0%{?fedora} || 0%{?rhel} > 7
Requires: iproute-tc
%endif

Requires: polkit >= 0.112
%ifarch %{ix86} x86_64 ia64
# For virConnectGetSysinfo
Requires: dmidecode
%endif
# For service management
Requires(post): systemd-units
Requires(post): systemd-sysv
Requires(preun): systemd-units
Requires(postun): systemd-units
%if %{with_numad}
Requires: numad
%endif
# libvirtd depends on 'messagebus' service
Requires: dbus
# For uid creation during pre
Requires(pre): shadow-utils

%description daemon
Server side daemon required to manage the virtualization capabilities
of recent versions of Linux. Requires a hypervisor specific sub-RPM
for specific drivers.

%package daemon-config-network
Summary: Default configuration files for the libvirtd daemon

Requires: libvirt-daemon = %{version}-%{release}
Requires: libvirt-daemon-driver-network = %{version}-%{release}

%description daemon-config-network
Default configuration files for setting up NAT based networking

%package daemon-config-nwfilter
Summary: Network filter configuration files for the libvirtd daemon

Requires: libvirt-daemon = %{version}-%{release}
Requires: libvirt-daemon-driver-nwfilter = %{version}-%{release}

%description daemon-config-nwfilter
Network filter configuration files for cleaning guest traffic

%package daemon-driver-network
Summary: Network driver plugin for the libvirtd daemon
Requires: libvirt-daemon = %{version}-%{release}
Requires: libvirt-libs = %{version}-%{release}
Requires: dnsmasq >= 2.41
Requires: radvd
Requires: iptables

%description daemon-driver-network
The network driver plugin for the libvirtd daemon, providing
an implementation of the virtual network APIs using the Linux
bridge capabilities.


%package daemon-driver-nwfilter
Summary: Nwfilter driver plugin for the libvirtd daemon
Requires: libvirt-daemon = %{version}-%{release}
Requires: libvirt-libs = %{version}-%{release}
Requires: iptables
Requires: ebtables

%description daemon-driver-nwfilter
The nwfilter driver plugin for the libvirtd daemon, providing
an implementation of the firewall APIs using the ebtables,
iptables and ip6tables capabilities


%package daemon-driver-nodedev
Summary: Nodedev driver plugin for the libvirtd daemon
Requires: libvirt-daemon = %{version}-%{release}
Requires: libvirt-libs = %{version}-%{release}
# needed for device enumeration
Requires: systemd >= 185

%description daemon-driver-nodedev
The nodedev driver plugin for the libvirtd daemon, providing
an implementation of the node device APIs using the udev
capabilities.


%package daemon-driver-interface
Summary: Interface driver plugin for the libvirtd daemon
Requires: libvirt-daemon = %{version}-%{release}
Requires: libvirt-libs = %{version}-%{release}
Requires: netcf-libs >= 0.2.2

%description daemon-driver-interface
The interface driver plugin for the libvirtd daemon, providing
an implementation of the network interface APIs using the
netcf library


%package daemon-driver-secret
Summary: Secret driver plugin for the libvirtd daemon
Requires: libvirt-daemon = %{version}-%{release}
Requires: libvirt-libs = %{version}-%{release}

%description daemon-driver-secret
The secret driver plugin for the libvirtd daemon, providing
an implementation of the secret key APIs.

%package daemon-driver-storage-core
Summary: Storage driver plugin including base backends for the libvirtd daemon
Requires: libvirt-daemon = %{version}-%{release}
Requires: libvirt-libs = %{version}-%{release}
Requires: nfs-utils
# For mkfs
Requires: util-linux
%if %{with_qemu}
# From QEMU RPMs
Requires: /usr/bin/qemu-img
%endif
%if !%{with_storage_rbd}
Obsoletes: libvirt-daemon-driver-storage-rbd < %{version}-%{release}
%endif

%description daemon-driver-storage-core
The storage driver plugin for the libvirtd daemon, providing
an implementation of the storage APIs using files, local disks, LVM, SCSI,
iSCSI, and multipath storage.

%package daemon-driver-storage-logical
Summary: Storage driver plugin for lvm volumes
Requires: libvirt-daemon-driver-storage-core = %{version}-%{release}
Requires: libvirt-libs = %{version}-%{release}
Requires: lvm2

%description daemon-driver-storage-logical
The storage driver backend adding implementation of the storage APIs for block
volumes using lvm.


%package daemon-driver-storage-disk
Summary: Storage driver plugin for disk
Requires: libvirt-daemon-driver-storage-core = %{version}-%{release}
Requires: libvirt-libs = %{version}-%{release}
Requires: parted
Requires: device-mapper

%description daemon-driver-storage-disk
The storage driver backend adding implementation of the storage APIs for block
volumes using the host disks.


%package daemon-driver-storage-scsi
Summary: Storage driver plugin for local scsi devices
Requires: libvirt-daemon-driver-storage-core = %{version}-%{release}
Requires: libvirt-libs = %{version}-%{release}

%description daemon-driver-storage-scsi
The storage driver backend adding implementation of the storage APIs for scsi
host devices.


%package daemon-driver-storage-iscsi
Summary: Storage driver plugin for iscsi
Requires: libvirt-daemon-driver-storage-core = %{version}-%{release}
Requires: libvirt-libs = %{version}-%{release}
Requires: iscsi-initiator-utils

%description daemon-driver-storage-iscsi
The storage driver backend adding implementation of the storage APIs for iscsi
volumes using the host iscsi stack.


%if %{with_storage_iscsi_direct}
%package daemon-driver-storage-iscsi-direct
Summary: Storage driver plugin for iscsi-direct
Requires: libvirt-daemon-driver-storage-core = %{version}-%{release}
Requires: libvirt-libs = %{version}-%{release}
Requires: libiscsi

%description daemon-driver-storage-iscsi-direct
The storage driver backend adding implementation of the storage APIs for iscsi
volumes using libiscsi direct connection.
%endif


%package daemon-driver-storage-mpath
Summary: Storage driver plugin for multipath volumes
Requires: libvirt-daemon-driver-storage-core = %{version}-%{release}
Requires: libvirt-libs = %{version}-%{release}
Requires: device-mapper

%description daemon-driver-storage-mpath
The storage driver backend adding implementation of the storage APIs for
multipath storage using device mapper.


%if %{with_storage_gluster}
%package daemon-driver-storage-gluster
Summary: Storage driver plugin for gluster
Requires: libvirt-daemon-driver-storage-core = %{version}-%{release}
Requires: libvirt-libs = %{version}-%{release}
    %if 0%{?fedora}
Requires: glusterfs-client >= 2.0.1
    %endif
    %if (0%{?fedora} || 0%{?with_storage_gluster})
Requires: /usr/sbin/gluster
    %endif

%description daemon-driver-storage-gluster
The storage driver backend adding implementation of the storage APIs for gluster
volumes using libgfapi.
%endif


%if %{with_storage_rbd}
%package daemon-driver-storage-rbd
Summary: Storage driver plugin for rbd
Requires: libvirt-daemon-driver-storage-core = %{version}-%{release}
Requires: libvirt-libs = %{version}-%{release}

%description daemon-driver-storage-rbd
The storage driver backend adding implementation of the storage APIs for rbd
volumes using the ceph protocol.
%endif


%if %{with_storage_sheepdog}
%package daemon-driver-storage-sheepdog
Summary: Storage driver plugin for sheepdog
Requires: libvirt-daemon-driver-storage-core = %{version}-%{release}
Requires: libvirt-libs = %{version}-%{release}
Requires: sheepdog

%description daemon-driver-storage-sheepdog
The storage driver backend adding implementation of the storage APIs for
sheepdog volumes using.
%endif


%if %{with_storage_zfs}
%package daemon-driver-storage-zfs
Summary: Storage driver plugin for ZFS
Requires: libvirt-daemon-driver-storage-core = %{version}-%{release}
Requires: libvirt-libs = %{version}-%{release}
# Support any conforming implementation of zfs
Requires: /sbin/zfs
Requires: /sbin/zpool

%description daemon-driver-storage-zfs
The storage driver backend adding implementation of the storage APIs for
ZFS volumes.
%endif


%package daemon-driver-storage
Summary: Storage driver plugin including all backends for the libvirtd daemon
Requires: libvirt-daemon-driver-storage-core = %{version}-%{release}
Requires: libvirt-daemon-driver-storage-disk = %{version}-%{release}
Requires: libvirt-daemon-driver-storage-logical = %{version}-%{release}
Requires: libvirt-daemon-driver-storage-scsi = %{version}-%{release}
Requires: libvirt-daemon-driver-storage-iscsi = %{version}-%{release}
Requires: libvirt-daemon-driver-storage-mpath = %{version}-%{release}
%if %{with_storage_iscsi_direct}
Requires: libvirt-daemon-driver-storage-iscsi-direct = %{version}-%{release}
%endif
%if %{with_storage_gluster}
Requires: libvirt-daemon-driver-storage-gluster = %{version}-%{release}
%endif
%if %{with_storage_rbd}
Requires: libvirt-daemon-driver-storage-rbd = %{version}-%{release}
%endif
%if %{with_storage_sheepdog}
Requires: libvirt-daemon-driver-storage-sheepdog = %{version}-%{release}
%endif
%if %{with_storage_zfs}
Requires: libvirt-daemon-driver-storage-zfs = %{version}-%{release}
%endif

%description daemon-driver-storage
The storage driver plugin for the libvirtd daemon, providing
an implementation of the storage APIs using LVM, iSCSI,
parted and more.


%if %{with_qemu}
%package daemon-driver-qemu
Summary: QEMU driver plugin for the libvirtd daemon
Requires: libvirt-daemon = %{version}-%{release}
Requires: libvirt-libs = %{version}-%{release}
Requires: /usr/bin/qemu-img
# For image compression
Requires: gzip
Requires: bzip2
Requires: lzop
Requires: xz
    %if 0%{?fedora} || 0%{?rhel} > 7
Requires: systemd-container
    %endif

%description daemon-driver-qemu
The qemu driver plugin for the libvirtd daemon, providing
an implementation of the hypervisor driver APIs using
QEMU
%endif


%if %{with_lxc}
%package daemon-driver-lxc
Summary: LXC driver plugin for the libvirtd daemon
Requires: libvirt-daemon = %{version}-%{release}
Requires: libvirt-libs = %{version}-%{release}
# There really is a hard cross-driver dependency here
Requires: libvirt-daemon-driver-network = %{version}-%{release}
    %if 0%{?fedora} || 0%{?rhel} > 7
Requires: systemd-container
    %endif

%description daemon-driver-lxc
The LXC driver plugin for the libvirtd daemon, providing
an implementation of the hypervisor driver APIs using
the Linux kernel
%endif


%if %{with_vbox}
%package daemon-driver-vbox
Summary: VirtualBox driver plugin for the libvirtd daemon
Requires: libvirt-daemon = %{version}-%{release}
Requires: libvirt-libs = %{version}-%{release}

%description daemon-driver-vbox
The vbox driver plugin for the libvirtd daemon, providing
an implementation of the hypervisor driver APIs using
VirtualBox
%endif


%if %{with_libxl}
%package daemon-driver-libxl
Summary: Libxl driver plugin for the libvirtd daemon
Requires: libvirt-daemon = %{version}-%{release}
Requires: libvirt-libs = %{version}-%{release}
Obsoletes: libvirt-daemon-driver-xen < 4.3.0

%description daemon-driver-libxl
The Libxl driver plugin for the libvirtd daemon, providing
an implementation of the hypervisor driver APIs using
Libxl
%endif



%if %{with_qemu_tcg}
%package daemon-qemu
Summary: Server side daemon & driver required to run QEMU guests

Requires: libvirt-daemon = %{version}-%{release}
Requires: libvirt-daemon-driver-qemu = %{version}-%{release}
Requires: libvirt-daemon-driver-interface = %{version}-%{release}
Requires: libvirt-daemon-driver-network = %{version}-%{release}
Requires: libvirt-daemon-driver-nodedev = %{version}-%{release}
Requires: libvirt-daemon-driver-nwfilter = %{version}-%{release}
Requires: libvirt-daemon-driver-secret = %{version}-%{release}
Requires: libvirt-daemon-driver-storage = %{version}-%{release}
Requires: qemu

%description daemon-qemu
Server side daemon and driver required to manage the virtualization
capabilities of the QEMU TCG emulators
%endif


%if %{with_qemu_kvm}
%package daemon-kvm
Summary: Server side daemon & driver required to run KVM guests

Requires: libvirt-daemon = %{version}-%{release}
Requires: libvirt-daemon-driver-qemu = %{version}-%{release}
Requires: libvirt-daemon-driver-interface = %{version}-%{release}
Requires: libvirt-daemon-driver-network = %{version}-%{release}
Requires: libvirt-daemon-driver-nodedev = %{version}-%{release}
Requires: libvirt-daemon-driver-nwfilter = %{version}-%{release}
Requires: libvirt-daemon-driver-secret = %{version}-%{release}
Requires: libvirt-daemon-driver-storage = %{version}-%{release}
Requires: qemu-kvm

%description daemon-kvm
Server side daemon and driver required to manage the virtualization
capabilities of the KVM hypervisor
%endif


%if %{with_lxc}
%package daemon-lxc
Summary: Server side daemon & driver required to run LXC guests

Requires: libvirt-daemon = %{version}-%{release}
Requires: libvirt-daemon-driver-lxc = %{version}-%{release}
Requires: libvirt-daemon-driver-interface = %{version}-%{release}
Requires: libvirt-daemon-driver-network = %{version}-%{release}
Requires: libvirt-daemon-driver-nodedev = %{version}-%{release}
Requires: libvirt-daemon-driver-nwfilter = %{version}-%{release}
Requires: libvirt-daemon-driver-secret = %{version}-%{release}
Requires: libvirt-daemon-driver-storage = %{version}-%{release}

%description daemon-lxc
Server side daemon and driver required to manage the virtualization
capabilities of LXC
%endif


%if %{with_libxl}
%package daemon-xen
Summary: Server side daemon & driver required to run XEN guests

Requires: libvirt-daemon = %{version}-%{release}
    %if %{with_libxl}
Requires: libvirt-daemon-driver-libxl = %{version}-%{release}
    %endif
Requires: libvirt-daemon-driver-interface = %{version}-%{release}
Requires: libvirt-daemon-driver-network = %{version}-%{release}
Requires: libvirt-daemon-driver-nodedev = %{version}-%{release}
Requires: libvirt-daemon-driver-nwfilter = %{version}-%{release}
Requires: libvirt-daemon-driver-secret = %{version}-%{release}
Requires: libvirt-daemon-driver-storage = %{version}-%{release}
Requires: xen

%description daemon-xen
Server side daemon and driver required to manage the virtualization
capabilities of XEN
%endif

%if %{with_vbox}
%package daemon-vbox
Summary: Server side daemon & driver required to run VirtualBox guests

Requires: libvirt-daemon = %{version}-%{release}
Requires: libvirt-daemon-driver-vbox = %{version}-%{release}
Requires: libvirt-daemon-driver-interface = %{version}-%{release}
Requires: libvirt-daemon-driver-network = %{version}-%{release}
Requires: libvirt-daemon-driver-nodedev = %{version}-%{release}
Requires: libvirt-daemon-driver-nwfilter = %{version}-%{release}
Requires: libvirt-daemon-driver-secret = %{version}-%{release}
Requires: libvirt-daemon-driver-storage = %{version}-%{release}

%description daemon-vbox
Server side daemon and driver required to manage the virtualization
capabilities of VirtualBox
%endif

%package client
Summary: Client side utilities of the libvirt library
Requires: %{name}-libs = %{version}-%{release}
Requires: readline
Requires: ncurses
# Needed by /usr/libexec/libvirt-guests.sh script.
Requires: gettext
# Needed by virt-pki-validate script.
Requires: gnutls-utils
%if %{with_bash_completion}
Requires: %{name}-bash-completion = %{version}-%{release}
%endif

%description client
The client binaries needed to access the virtualization
capabilities of recent versions of Linux (and other OSes).

%package libs
Summary: Client side libraries
# So remote clients can access libvirt over SSH tunnel
# (client invokes 'nc' against the UNIX socket on the server)
Requires: nc
Requires: cyrus-sasl
# Needed by default sasl.conf - no onerous extra deps, since
# 100's of other things on a system already pull in krb5-libs
Requires: cyrus-sasl-gssapi

%description libs
Shared libraries for accessing the libvirt daemon.

%package admin
Summary: Set of tools to control libvirt daemon
Requires: %{name}-libs = %{version}-%{release}
Requires: readline
%if %{with_bash_completion}
Requires: %{name}-bash-completion = %{version}-%{release}
%endif

%description admin
The client side utilities to control the libvirt daemon.

%if %{with_bash_completion}
%package bash-completion
Summary: Bash completion script

%description bash-completion
Bash completion script stub.
%endif

%if %{with_wireshark}
%package wireshark
Summary: Wireshark dissector plugin for libvirt RPC transactions
Requires: wireshark >= 2.4.0
Requires: %{name}-libs = %{version}-%{release}

%description wireshark
Wireshark dissector plugin for better analysis of libvirt RPC traffic.
%endif

%if %{with_lxc}
%package login-shell
Summary: Login shell for connecting users to an LXC container
Requires: %{name}-libs = %{version}-%{release}

%description login-shell
Provides the set-uid virt-login-shell binary that is used to
connect a user to an LXC container when they login, by switching
namespaces.
%endif

%package devel
Summary: Libraries, includes, etc. to compile with the libvirt library
Requires: %{name}-libs = %{version}-%{release}
Requires: pkgconfig

%description devel
Include header files & development libraries for the libvirt C library.

%if %{with_sanlock}
%package lock-sanlock
Summary: Sanlock lock manager plugin for QEMU driver
Requires: sanlock >= 2.4
#for virt-sanlock-cleanup require augeas
Requires: augeas
Requires: %{name}-daemon = %{version}-%{release}
Requires: %{name}-libs = %{version}-%{release}

%description lock-sanlock
Includes the Sanlock lock manager plugin for the QEMU
driver
%endif

%package nss
Summary: Libvirt plugin for Name Service Switch
Requires: libvirt-daemon-driver-network = %{version}-%{release}

%description nss
Libvirt plugin for NSS for translating domain names into IP addresses.


%prep

%autosetup -S git_am

%build
%if ! %{supported_platform}
echo "This RPM requires either Fedora >= %{min_fedora} or RHEL >= %{min_rhel}"
exit 1
%endif

%if %{with_qemu}
    %define arg_qemu --with-qemu
%else
    %define arg_qemu --without-qemu
%endif

%if %{with_openvz}
    %define arg_openvz --with-openvz
%else
    %define arg_openvz --without-openvz
%endif

%if %{with_lxc}
    %define arg_lxc --with-lxc
    %define arg_login_shell --with-login-shell
%else
    %define arg_lxc --without-lxc
    %define arg_login_shell --without-login-shell
%endif

%if %{with_vbox}
    %define arg_vbox --with-vbox
%else
    %define arg_vbox --without-vbox
%endif

%if %{with_libxl}
    %define arg_libxl --with-libxl
%else
    %define arg_libxl --without-libxl
%endif

%if %{with_phyp}
    %define arg_phyp --with-phyp
%else
    %define arg_phyp --without-phyp
%endif

%if %{with_esx}
    %define arg_esx --with-esx
%else
    %define arg_esx --without-esx
%endif

%if %{with_hyperv}
    %define arg_hyperv --with-hyperv
%else
    %define arg_hyperv --without-hyperv
%endif

%if %{with_vmware}
    %define arg_vmware --with-vmware
%else
    %define arg_vmware --without-vmware
%endif

%if %{with_storage_rbd}
    %define arg_storage_rbd --with-storage-rbd
%else
    %define arg_storage_rbd --without-storage-rbd
%endif

%if %{with_storage_sheepdog}
    %define arg_storage_sheepdog --with-storage-sheepdog
%else
    %define arg_storage_sheepdog --without-storage-sheepdog
%endif

%if %{with_storage_gluster}
    %define arg_storage_gluster --with-storage-gluster
%else
    %define arg_storage_gluster --without-storage-gluster
%endif

%if %{with_storage_zfs}
    %define arg_storage_zfs --with-storage-zfs
%else
    %define arg_storage_zfs --without-storage-zfs
%endif

%if %{with_numactl}
    %define arg_numactl --with-numactl
%else
    %define arg_numactl --without-numactl
%endif

%if %{with_numad}
    %define arg_numad --with-numad
%else
    %define arg_numad --without-numad
%endif

%if %{with_fuse}
    %define arg_fuse --with-fuse
%else
    %define arg_fuse --without-fuse
%endif

%if %{with_sanlock}
    %define arg_sanlock --with-sanlock
%else
    %define arg_sanlock --without-sanlock
%endif

%if %{with_firewalld}
    %define arg_firewalld --with-firewalld
%else
    %define arg_firewalld --without-firewalld
%endif

%if %{with_firewalld_zone}
    %define arg_firewalld_zone --with-firewalld-zone
%else
    %define arg_firewalld_zone --without-firewalld-zone
%endif

%if %{with_wireshark}
    %define arg_wireshark --with-wireshark-dissector
%else
    %define arg_wireshark --without-wireshark-dissector
%endif

%if %{with_storage_iscsi_direct}
    %define arg_storage_iscsi_direct --with-storage-iscsi-direct
%else
    %define arg_storage_iscsi_direct --without-storage-iscsi-direct
%endif

%define when  %(date +"%%F-%%T")
%define where %(hostname)
%define who   %{?packager}%{!?packager:Unknown}
%define arg_packager --with-packager="%{who}, %{when}, %{where}"
%define arg_packager_version --with-packager-version="%{release}"

%define arg_selinux_mount --with-selinux-mount="/sys/fs/selinux"

%if 0%{?fedora}
    # Nightly edk2.git-ovmf-x64
    LOADERS="/usr/share/edk2.git/ovmf-x64/OVMF_CODE-pure-efi.fd:/usr/share/edk2.git/ovmf-x64/OVMF_VARS-pure-efi.fd"
    # Nightly edk2.git-ovmf-ia32
    LOADERS="$LOADERS:/usr/share/edk2.git/ovmf-ia32/OVMF_CODE-pure-efi.fd:/usr/share/edk2.git/ovmf-ia32/OVMF_VARS-pure-efi.fd"
    # Nightly edk2.git-aarch64
    LOADERS="$LOADERS:/usr/share/edk2.git/aarch64/QEMU_EFI-pflash.raw:/usr/share/edk2.git/aarch64/vars-template-pflash.raw"
    # Nightly edk2.git-arm
    LOADERS="$LOADERS:/usr/share/edk2.git/arm/QEMU_EFI-pflash.raw:/usr/share/edk2.git/arm/vars-template-pflash.raw"

    # Fedora edk2-ovmf
    LOADERS="$LOADERS:/usr/share/edk2/ovmf/OVMF_CODE.fd:/usr/share/edk2/ovmf/OVMF_VARS.fd"
    # Fedora edk2-ovmf-ia32
    LOADERS="$LOADERS:/usr/share/edk2/ovmf-ia32/OVMF_CODE.fd:/usr/share/edk2/ovmf-ia32/OVMF_VARS.fd"
    # Fedora edk2-aarch64
    LOADERS="$LOADERS:/usr/share/edk2/aarch64/QEMU_EFI-pflash.raw:/usr/share/edk2/aarch64/vars-template-pflash.raw"
    # Fedora edk2-arm
    LOADERS="$LOADERS:/usr/share/edk2/arm/QEMU_EFI-pflash.raw:/usr/share/edk2/arm/vars-template-pflash.raw"
    %define arg_loader_nvram --with-loader-nvram="$LOADERS"
%endif

# place macros above and build commands below this comment

export SOURCE_DATE_EPOCH=$(stat --printf='%Y' %{_specdir}/%{name}.spec)

%if 0%{?enable_autotools}
 autoreconf -if
%endif

rm -f po/stamp-po
%configure %{?arg_qemu} \
           %{?arg_openvz} \
           %{?arg_lxc} \
           %{?arg_vbox} \
           %{?arg_libxl} \
           --with-sasl \
           --with-polkit \
           --with-libvirtd \
           %{?arg_phyp} \
           %{?arg_esx} \
           %{?arg_hyperv} \
           %{?arg_vmware} \
           --without-xenapi \
           --without-vz \
           --without-bhyve \
           --with-interface \
           --with-network \
           --with-storage-fs \
           --with-storage-lvm \
           --with-storage-iscsi \
           %{?arg_storage_iscsi_direct} \
           --with-storage-scsi \
           --with-storage-disk \
           --with-storage-mpath \
           %{?arg_storage_rbd} \
           %{?arg_storage_sheepdog} \
           %{?arg_storage_gluster} \
           %{?arg_storage_zfs} \
           --without-storage-vstorage \
           %{?arg_numactl} \
           %{?arg_numad} \
           --with-capng \
           %{?arg_fuse} \
           --with-netcf \
           --with-selinux \
           %{?arg_selinux_mount} \
           --without-apparmor \
           --without-hal \
           --with-udev \
           --with-yajl \
           %{?arg_sanlock} \
           --with-libpcap \
           --with-macvtap \
           --with-audit \
           --with-dtrace \
           --with-driver-modules \
           %{?arg_firewalld} \
           %{?arg_firewalld_zone} \
           %{?arg_wireshark} \
           --without-pm-utils \
           --with-nss-plugin \
           %{arg_packager} \
           %{arg_packager_version} \
           --with-qemu-user=%{qemu_user} \
           --with-qemu-group=%{qemu_group} \
           --with-tls-priority=%{tls_priority} \
           %{?arg_loader_nvram} \
           %{?enable_werror} \
           --enable-expensive-tests \
           --with-init-script=systemd \
           %{?arg_login_shell}
make %{?_smp_mflags} V=1
gzip -9 ChangeLog

%install
rm -fr %{buildroot}

export SOURCE_DATE_EPOCH=$(stat --printf='%Y' %{_specdir}/%{name}.spec)

%make_install %{?_smp_mflags} SYSTEMD_UNIT_DIR=%{_unitdir} V=1

rm -f $RPM_BUILD_ROOT%{_libdir}/*.la
rm -f $RPM_BUILD_ROOT%{_libdir}/*.a
rm -f $RPM_BUILD_ROOT%{_libdir}/libvirt/lock-driver/*.la
rm -f $RPM_BUILD_ROOT%{_libdir}/libvirt/lock-driver/*.a
rm -f $RPM_BUILD_ROOT%{_libdir}/libvirt/connection-driver/*.la
rm -f $RPM_BUILD_ROOT%{_libdir}/libvirt/connection-driver/*.a
rm -f $RPM_BUILD_ROOT%{_libdir}/libvirt/storage-backend/*.la
rm -f $RPM_BUILD_ROOT%{_libdir}/libvirt/storage-backend/*.a
rm -f $RPM_BUILD_ROOT%{_libdir}/libvirt/storage-file/*.la
rm -f $RPM_BUILD_ROOT%{_libdir}/libvirt/storage-file/*.a
%if %{with_wireshark}
rm -f $RPM_BUILD_ROOT%{wireshark_plugindir}/libvirt.la
%endif

install -d -m 0755 $RPM_BUILD_ROOT%{_datadir}/lib/libvirt/dnsmasq/
# We don't want to install /etc/libvirt/qemu/networks in the main %files list
# because if the admin wants to delete the default network completely, we don't
# want to end up re-incarnating it on every RPM upgrade.
install -d -m 0755 $RPM_BUILD_ROOT%{_datadir}/libvirt/networks/
cp $RPM_BUILD_ROOT%{_sysconfdir}/libvirt/qemu/networks/default.xml \
   $RPM_BUILD_ROOT%{_datadir}/libvirt/networks/default.xml
# libvirt saves this file with mode 0600
chmod 0600 $RPM_BUILD_ROOT%{_sysconfdir}/libvirt/qemu/networks/default.xml

# nwfilter files are installed in /usr/share/libvirt and copied to /etc in %post
# to avoid verification errors on changed files in /etc
install -d -m 0755 $RPM_BUILD_ROOT%{_datadir}/libvirt/nwfilter/
cp -a $RPM_BUILD_ROOT%{_sysconfdir}/libvirt/nwfilter/*.xml \
    $RPM_BUILD_ROOT%{_datadir}/libvirt/nwfilter/
# libvirt saves these files with mode 600
chmod 600 $RPM_BUILD_ROOT%{_sysconfdir}/libvirt/nwfilter/*.xml

# Strip auto-generated UUID - we need it generated per-install
sed -i -e "/<uuid>/d" $RPM_BUILD_ROOT%{_datadir}/libvirt/networks/default.xml
%if ! %{with_qemu}
rm -f $RPM_BUILD_ROOT%{_datadir}/augeas/lenses/libvirtd_qemu.aug
rm -f $RPM_BUILD_ROOT%{_datadir}/augeas/lenses/tests/test_libvirtd_qemu.aug
%endif
%find_lang %{name}

%if ! %{with_sanlock}
rm -f $RPM_BUILD_ROOT%{_datadir}/augeas/lenses/libvirt_sanlock.aug
rm -f $RPM_BUILD_ROOT%{_datadir}/augeas/lenses/tests/test_libvirt_sanlock.aug
%endif

%if ! %{with_lxc}
rm -f $RPM_BUILD_ROOT%{_datadir}/augeas/lenses/libvirtd_lxc.aug
rm -f $RPM_BUILD_ROOT%{_datadir}/augeas/lenses/tests/test_libvirtd_lxc.aug
%endif

%if ! %{with_qemu}
rm -rf $RPM_BUILD_ROOT%{_sysconfdir}/libvirt/qemu.conf
rm -rf $RPM_BUILD_ROOT%{_sysconfdir}/logrotate.d/libvirtd.qemu
%endif
%if ! %{with_lxc}
rm -rf $RPM_BUILD_ROOT%{_sysconfdir}/libvirt/lxc.conf
rm -rf $RPM_BUILD_ROOT%{_sysconfdir}/logrotate.d/libvirtd.lxc
%endif
%if ! %{with_libxl}
rm -rf $RPM_BUILD_ROOT%{_sysconfdir}/libvirt/libxl.conf
rm -rf $RPM_BUILD_ROOT%{_sysconfdir}/logrotate.d/libvirtd.libxl
rm -f $RPM_BUILD_ROOT%{_datadir}/augeas/lenses/libvirtd_libxl.aug
rm -f $RPM_BUILD_ROOT%{_datadir}/augeas/lenses/tests/test_libvirtd_libxl.aug
%endif

# Copied into libvirt-docs subpackage eventually
mv $RPM_BUILD_ROOT%{_datadir}/doc/libvirt libvirt-docs

%ifarch %{power64} s390x x86_64 ia64 alpha sparc64
mv $RPM_BUILD_ROOT%{_datadir}/systemtap/tapset/libvirt_probes.stp \
   $RPM_BUILD_ROOT%{_datadir}/systemtap/tapset/libvirt_probes-64.stp

    %if %{with_qemu}
mv $RPM_BUILD_ROOT%{_datadir}/systemtap/tapset/libvirt_qemu_probes.stp \
   $RPM_BUILD_ROOT%{_datadir}/systemtap/tapset/libvirt_qemu_probes-64.stp
    %endif
%endif

%check
cd tests
# These tests don't current work in a mock build root
for i in nodeinfotest seclabeltest
do
  rm -f $i
  printf 'int main(void) { return 0; }' > $i.c
  printf '#!/bin/sh\nexit 0\n' > $i
  chmod +x $i
done
if ! make %{?_smp_mflags} check VIR_TEST_DEBUG=1
then
  cat test-suite.log || true
  exit 1
fi

%post libs
%if 0%{?rhel} == 7
/sbin/ldconfig
%endif

%postun libs
%if 0%{?rhel} == 7
/sbin/ldconfig
%endif

%pre daemon
# 'libvirt' group is just to allow password-less polkit access to
# libvirtd. The uid number is irrelevant, so we use dynamic allocation
# described at the above link.
getent group libvirt >/dev/null || groupadd -r libvirt

exit 0

%post daemon

%systemd_post virtlockd.socket virtlockd-admin.socket
%systemd_post virtlogd.socket virtlogd-admin.socket
%systemd_post libvirtd.socket libvirtd-ro.socket libvirtd-admin.socket
%systemd_post libvirtd-tcp.socket libvirtd-tls.socket
%systemd_post libvirtd.service

# request daemon restart in posttrans
mkdir -p %{_localstatedir}/lib/rpm-state/libvirt || :
touch %{_localstatedir}/lib/rpm-state/libvirt/restart || :

%preun daemon
%systemd_preun libvirtd.service
%systemd_preun libvirtd-tcp.socket libvirtd-tls.socket
%systemd_preun libvirtd.socket libvirtd-ro.socket libvirtd-admin.socket
%systemd_preun virtlogd.socket virtlogd-admin.socket virtlogd.service
%systemd_preun virtlockd.socket virtlockd-admin.socket virtlockd.service

%postun daemon
/bin/systemctl daemon-reload >/dev/null 2>&1 || :
if [ $1 -ge 1 ] ; then
    /bin/systemctl reload-or-try-restart virtlockd.service >/dev/null 2>&1 || :
    /bin/systemctl reload-or-try-restart virtlogd.service >/dev/null 2>&1 || :
fi

# In upgrade scenario we must explicitly enable virtlockd/virtlogd
# sockets, if libvirtd is already enabled and start them if
# libvirtd is running, otherwise you'll get failures to start
# guests
%triggerpostun daemon -- libvirt-daemon < 1.3.0
if [ $1 -ge 1 ] ; then
    /bin/systemctl is-enabled libvirtd.service 1>/dev/null 2>&1 &&
        /bin/systemctl enable virtlogd.socket virtlogd-admin.socket || :
    /bin/systemctl is-active libvirtd.service 1>/dev/null 2>&1 &&
        /bin/systemctl start virtlogd.socket virtlogd-admin.socket || :
fi

%posttrans daemon
if [ -f %{_localstatedir}/lib/rpm-state/libvirt/restart ]; then
    # Old libvirtd owns the sockets and will delete them on
    # shutdown. Can't use a try-restart as libvirtd will simply
    # own the sockets again when it comes back up. Thus we must
    # do this particular ordering
    /bin/systemctl is-active libvirtd.service 1>/dev/null 2>&1
    if test $? = 0 ; then
        /bin/systemctl stop libvirtd.service >/dev/null 2>&1 || :

        /bin/systemctl try-restart libvirtd.socket >/dev/null 2>&1 || :
        /bin/systemctl try-restart libvirtd-ro.socket >/dev/null 2>&1 || :
        /bin/systemctl try-restart libvirtd-admin.socket >/dev/null 2>&1 || :

        /bin/systemctl start libvirtd.service >/dev/null 2>&1 || :
    fi
fi
rm -rf %{_localstatedir}/lib/rpm-state/libvirt || :

%post daemon-driver-network
%if %{with_firewalld_zone}
    %firewalld_reload
%endif

%postun daemon-driver-network
%if %{with_firewalld_zone}
    %firewalld_reload
%endif

%post daemon-config-network
if test $1 -eq 1 && test ! -f %{_sysconfdir}/libvirt/qemu/networks/default.xml ; then
    # see if the network used by default network creates a conflict,
    # and try to resolve it
    # NB: 192.168.122.0/24 is used in the default.xml template file;
    # do not modify any of those values here without also modifying
    # them in the template.
    orig_sub=122
    sub=${orig_sub}
    nl='
'
    routes="${nl}$(ip route show | cut -d' ' -f1)${nl}"
    case ${routes} in
      *"${nl}192.168.${orig_sub}.0/24${nl}"*)
        # there was a match, so we need to look for an unused subnet
        for new_sub in $(seq 124 254); do
          case ${routes} in
          *"${nl}192.168.${new_sub}.0/24${nl}"*)
            ;;
          *)
            sub=$new_sub
            break;
            ;;
          esac
        done
        ;;
      *)
        ;;
    esac

    UUID=`/usr/bin/uuidgen`
    sed -e "s/${orig_sub}/${sub}/g" \
        -e "s,</name>,</name>\n  <uuid>$UUID</uuid>," \
         < %{_datadir}/libvirt/networks/default.xml \
         > %{_sysconfdir}/libvirt/qemu/networks/default.xml
    ln -s ../default.xml %{_sysconfdir}/libvirt/qemu/networks/autostart/default.xml
    # libvirt saves this file with mode 0600
    chmod 0600 %{_sysconfdir}/libvirt/qemu/networks/default.xml

    # Make sure libvirt picks up the new network defininiton
    mkdir -p %{_localstatedir}/lib/rpm-state/libvirt || :
    touch %{_localstatedir}/lib/rpm-state/libvirt/restart || :
fi

%posttrans daemon-config-network
if [ -f %{_localstatedir}/lib/rpm-state/libvirt/restart ]; then
    /bin/systemctl try-restart libvirtd.service >/dev/null 2>&1 || :
fi
rm -rf %{_localstatedir}/lib/rpm-state/libvirt || :

%post daemon-config-nwfilter
cp %{_datadir}/libvirt/nwfilter/*.xml %{_sysconfdir}/libvirt/nwfilter/
# libvirt saves these files with mode 600
chmod 600 %{_sysconfdir}/libvirt/nwfilter/*.xml
# Make sure libvirt picks up the new nwfilter defininitons
mkdir -p %{_localstatedir}/lib/rpm-state/libvirt || :
touch %{_localstatedir}/lib/rpm-state/libvirt/restart || :

%posttrans daemon-config-nwfilter
if [ -f %{_localstatedir}/lib/rpm-state/libvirt/restart ]; then
    /bin/systemctl try-restart libvirtd.service >/dev/null 2>&1 || :
fi
rm -rf %{_localstatedir}/lib/rpm-state/libvirt || :


%if %{with_qemu}
%pre daemon-driver-qemu
# We want soft static allocation of well-known ids, as disk images
# are commonly shared across NFS mounts by id rather than name; see
# https://fedoraproject.org/wiki/Packaging:UsersAndGroups
getent group kvm >/dev/null || groupadd -f -g 36 -r kvm
getent group qemu >/dev/null || groupadd -f -g 107 -r qemu
if ! getent passwd qemu >/dev/null; then
  if ! getent passwd 107 >/dev/null; then
    useradd -r -u 107 -g qemu -G kvm -d / -s /sbin/nologin -c "qemu user" qemu
  else
    useradd -r -g qemu -G kvm -d / -s /sbin/nologin -c "qemu user" qemu
  fi
fi
exit 0
%endif

%preun client

%systemd_preun libvirt-guests.service

%post client
%systemd_post libvirt-guests.service

%postun client
%systemd_postun libvirt-guests.service

%if %{with_lxc}
%pre login-shell
getent group virtlogin >/dev/null || groupadd -r virtlogin
exit 0
%endif

%files

%files docs
%doc AUTHORS ChangeLog.gz NEWS README README.md
%doc libvirt-docs/*

# API docs
%dir %{_datadir}/gtk-doc/html/libvirt/
%doc %{_datadir}/gtk-doc/html/libvirt/*.devhelp
%doc %{_datadir}/gtk-doc/html/libvirt/*.html
%doc %{_datadir}/gtk-doc/html/libvirt/*.png
%doc %{_datadir}/gtk-doc/html/libvirt/*.css


%files daemon

%dir %attr(0700, root, root) %{_sysconfdir}/libvirt/

%{_unitdir}/libvirtd.service
%{_unitdir}/libvirtd.socket
%{_unitdir}/libvirtd-ro.socket
%{_unitdir}/libvirtd-admin.socket
%{_unitdir}/libvirtd-tcp.socket
%{_unitdir}/libvirtd-tls.socket
%{_unitdir}/virt-guest-shutdown.target
%{_unitdir}/virtlogd.service
%{_unitdir}/virtlogd.socket
%{_unitdir}/virtlogd-admin.socket
%{_unitdir}/virtlockd.service
%{_unitdir}/virtlockd.socket
%{_unitdir}/virtlockd-admin.socket
%config(noreplace) %{_sysconfdir}/sysconfig/libvirtd
%config(noreplace) %{_sysconfdir}/sysconfig/virtlogd
%config(noreplace) %{_sysconfdir}/sysconfig/virtlockd
%config(noreplace) %{_sysconfdir}/libvirt/libvirtd.conf
%config(noreplace) %{_sysconfdir}/libvirt/virtlogd.conf
%config(noreplace) %{_sysconfdir}/libvirt/virtlockd.conf
%config(noreplace) %{_sysconfdir}/sasl2/libvirt.conf
%config(noreplace) %{_prefix}/lib/sysctl.d/60-libvirtd.conf

%config(noreplace) %{_sysconfdir}/logrotate.d/libvirtd
%dir %{_datadir}/libvirt/

%ghost %dir %{_localstatedir}/run/libvirt/

%dir %attr(0711, root, root) %{_localstatedir}/lib/libvirt/images/
%dir %attr(0711, root, root) %{_localstatedir}/lib/libvirt/filesystems/
%dir %attr(0711, root, root) %{_localstatedir}/lib/libvirt/boot/
%dir %attr(0711, root, root) %{_localstatedir}/cache/libvirt/


%dir %attr(0755, root, root) %{_libdir}/libvirt/
%dir %attr(0755, root, root) %{_libdir}/libvirt/connection-driver/
%dir %attr(0755, root, root) %{_libdir}/libvirt/lock-driver
%attr(0755, root, root) %{_libdir}/libvirt/lock-driver/lockd.so

%{_datadir}/augeas/lenses/libvirtd.aug
%{_datadir}/augeas/lenses/tests/test_libvirtd.aug
%{_datadir}/augeas/lenses/virtlogd.aug
%{_datadir}/augeas/lenses/tests/test_virtlogd.aug
%{_datadir}/augeas/lenses/virtlockd.aug
%{_datadir}/augeas/lenses/tests/test_virtlockd.aug
%{_datadir}/augeas/lenses/libvirt_lockd.aug
%if %{with_qemu}
%{_datadir}/augeas/lenses/tests/test_libvirt_lockd.aug
%endif

%{_datadir}/polkit-1/actions/org.libvirt.unix.policy
%{_datadir}/polkit-1/actions/org.libvirt.api.policy
%{_datadir}/polkit-1/rules.d/50-libvirt.rules

%dir %attr(0700, root, root) %{_localstatedir}/log/libvirt/

%attr(0755, root, root) %{_libexecdir}/libvirt_iohelper

%attr(0755, root, root) %{_sbindir}/libvirtd
%attr(0755, root, root) %{_sbindir}/virtlogd
%attr(0755, root, root) %{_sbindir}/virtlockd

%{_mandir}/man8/libvirtd.8*
%{_mandir}/man8/virtlogd.8*
%{_mandir}/man8/virtlockd.8*
%{_mandir}/man7/virkey*.7*

%files daemon-config-network
%dir %{_datadir}/libvirt/networks/
%{_datadir}/libvirt/networks/default.xml
%ghost %{_sysconfdir}/libvirt/qemu/networks/default.xml
%ghost %{_sysconfdir}/libvirt/qemu/networks/autostart/default.xml

%files daemon-config-nwfilter
%dir %{_datadir}/libvirt/nwfilter/
%{_datadir}/libvirt/nwfilter/*.xml
%ghost %{_sysconfdir}/libvirt/nwfilter/*.xml

%files daemon-driver-interface
%{_libdir}/%{name}/connection-driver/libvirt_driver_interface.so

%files daemon-driver-network
%dir %attr(0700, root, root) %{_sysconfdir}/libvirt/qemu/
%dir %attr(0700, root, root) %{_sysconfdir}/libvirt/qemu/networks/
%dir %attr(0700, root, root) %{_sysconfdir}/libvirt/qemu/networks/autostart
%ghost %dir %{_localstatedir}/run/libvirt/network/
%dir %attr(0700, root, root) %{_localstatedir}/lib/libvirt/network/
%dir %attr(0755, root, root) %{_localstatedir}/lib/libvirt/dnsmasq/
%attr(0755, root, root) %{_libexecdir}/libvirt_leaseshelper
%{_libdir}/%{name}/connection-driver/libvirt_driver_network.so

%if %{with_firewalld_zone}
%{_prefix}/lib/firewalld/zones/libvirt.xml
%endif

%files daemon-driver-nodedev
%{_libdir}/%{name}/connection-driver/libvirt_driver_nodedev.so

%files daemon-driver-nwfilter
%dir %attr(0700, root, root) %{_sysconfdir}/libvirt/nwfilter/
%ghost %dir %{_localstatedir}/run/libvirt/network/
%{_libdir}/%{name}/connection-driver/libvirt_driver_nwfilter.so

%files daemon-driver-secret
%{_libdir}/%{name}/connection-driver/libvirt_driver_secret.so

%files daemon-driver-storage

%files daemon-driver-storage-core
%attr(0755, root, root) %{_libexecdir}/libvirt_parthelper
%{_libdir}/%{name}/connection-driver/libvirt_driver_storage.so
%{_libdir}/%{name}/storage-backend/libvirt_storage_backend_fs.so
%{_libdir}/%{name}/storage-file/libvirt_storage_file_fs.so

%files daemon-driver-storage-disk
%{_libdir}/%{name}/storage-backend/libvirt_storage_backend_disk.so

%files daemon-driver-storage-logical
%{_libdir}/%{name}/storage-backend/libvirt_storage_backend_logical.so

%files daemon-driver-storage-scsi
%{_libdir}/%{name}/storage-backend/libvirt_storage_backend_scsi.so

%files daemon-driver-storage-iscsi
%{_libdir}/%{name}/storage-backend/libvirt_storage_backend_iscsi.so

%if %{with_storage_iscsi_direct}
%files daemon-driver-storage-iscsi-direct
%{_libdir}/%{name}/storage-backend/libvirt_storage_backend_iscsi-direct.so
%endif

%files daemon-driver-storage-mpath
%{_libdir}/%{name}/storage-backend/libvirt_storage_backend_mpath.so

%if %{with_storage_gluster}
%files daemon-driver-storage-gluster
%{_libdir}/%{name}/storage-backend/libvirt_storage_backend_gluster.so
%{_libdir}/%{name}/storage-file/libvirt_storage_file_gluster.so
%endif

%if %{with_storage_rbd}
%files daemon-driver-storage-rbd
%{_libdir}/%{name}/storage-backend/libvirt_storage_backend_rbd.so
%endif

%if %{with_storage_sheepdog}
%files daemon-driver-storage-sheepdog
%{_libdir}/%{name}/storage-backend/libvirt_storage_backend_sheepdog.so
%endif

%if %{with_storage_zfs}
%files daemon-driver-storage-zfs
%{_libdir}/%{name}/storage-backend/libvirt_storage_backend_zfs.so
%endif

%if %{with_qemu}
%files daemon-driver-qemu
%dir %attr(0700, root, root) %{_sysconfdir}/libvirt/qemu/
%dir %attr(0700, root, root) %{_localstatedir}/log/libvirt/qemu/
%config(noreplace) %{_sysconfdir}/libvirt/qemu.conf
%config(noreplace) %{_sysconfdir}/libvirt/qemu-lockd.conf
%config(noreplace) %{_sysconfdir}/logrotate.d/libvirtd.qemu
%ghost %dir %{_localstatedir}/run/libvirt/qemu/
%dir %attr(0751, %{qemu_user}, %{qemu_group}) %{_localstatedir}/lib/libvirt/qemu/
%dir %attr(0750, %{qemu_user}, %{qemu_group}) %{_localstatedir}/cache/libvirt/qemu/
%{_datadir}/augeas/lenses/libvirtd_qemu.aug
%{_datadir}/augeas/lenses/tests/test_libvirtd_qemu.aug
%{_libdir}/%{name}/connection-driver/libvirt_driver_qemu.so
%dir %attr(0711, root, root) %{_localstatedir}/lib/libvirt/swtpm/
%dir %attr(0711, root, root) %{_localstatedir}/log/swtpm/libvirt/qemu/
%endif

%if %{with_lxc}
%files daemon-driver-lxc
%dir %attr(0700, root, root) %{_localstatedir}/log/libvirt/lxc/
%config(noreplace) %{_sysconfdir}/libvirt/lxc.conf
%config(noreplace) %{_sysconfdir}/logrotate.d/libvirtd.lxc
%ghost %dir %{_localstatedir}/run/libvirt/lxc/
%dir %attr(0700, root, root) %{_localstatedir}/lib/libvirt/lxc/
%{_datadir}/augeas/lenses/libvirtd_lxc.aug
%{_datadir}/augeas/lenses/tests/test_libvirtd_lxc.aug
%attr(0755, root, root) %{_libexecdir}/libvirt_lxc
%{_libdir}/%{name}/connection-driver/libvirt_driver_lxc.so
%endif

%if %{with_libxl}
%files daemon-driver-libxl
%config(noreplace) %{_sysconfdir}/libvirt/libxl.conf
%config(noreplace) %{_sysconfdir}/logrotate.d/libvirtd.libxl
%config(noreplace) %{_sysconfdir}/libvirt/libxl-lockd.conf
%{_datadir}/augeas/lenses/libvirtd_libxl.aug
%{_datadir}/augeas/lenses/tests/test_libvirtd_libxl.aug
%dir %attr(0700, root, root) %{_localstatedir}/log/libvirt/libxl/
%ghost %dir %{_localstatedir}/run/libvirt/libxl/
%dir %attr(0700, root, root) %{_localstatedir}/lib/libvirt/libxl/
%{_libdir}/%{name}/connection-driver/libvirt_driver_libxl.so
%endif

%if %{with_vbox}
%files daemon-driver-vbox
%{_libdir}/%{name}/connection-driver/libvirt_driver_vbox.so
%endif

%if %{with_qemu_tcg}
%files daemon-qemu
%endif

%if %{with_qemu_kvm}
%files daemon-kvm
%endif

%if %{with_lxc}
%files daemon-lxc
%endif

%if %{with_libxl}
%files daemon-xen
%endif

%if %{with_vbox}
%files daemon-vbox
%endif

%if %{with_sanlock}
%files lock-sanlock
    %if %{with_qemu}
%config(noreplace) %{_sysconfdir}/libvirt/qemu-sanlock.conf
    %endif
    %if %{with_libxl}
%config(noreplace) %{_sysconfdir}/libvirt/libxl-sanlock.conf
    %endif
%attr(0755, root, root) %{_libdir}/libvirt/lock-driver/sanlock.so
%{_datadir}/augeas/lenses/libvirt_sanlock.aug
%{_datadir}/augeas/lenses/tests/test_libvirt_sanlock.aug
%dir %attr(0770, root, sanlock) %{_localstatedir}/lib/libvirt/sanlock
%{_sbindir}/virt-sanlock-cleanup
%{_mandir}/man8/virt-sanlock-cleanup.8*
%attr(0755, root, root) %{_libexecdir}/libvirt_sanlock_helper
%endif

%files client
%{_mandir}/man1/virsh.1*
%{_mandir}/man1/virt-xml-validate.1*
%{_mandir}/man1/virt-pki-validate.1*
%{_mandir}/man1/virt-host-validate.1*
%{_bindir}/virsh
%{_bindir}/virt-xml-validate
%{_bindir}/virt-pki-validate
%{_bindir}/virt-host-validate

%{_datadir}/systemtap/tapset/libvirt_probes*.stp
%{_datadir}/systemtap/tapset/libvirt_functions.stp
%if %{with_qemu}
%{_datadir}/systemtap/tapset/libvirt_qemu_probes*.stp
%endif

%if %{with_bash_completion}
%{_datadir}/bash-completion/completions/virsh
%endif


%{_unitdir}/libvirt-guests.service
%config(noreplace) %{_sysconfdir}/sysconfig/libvirt-guests
%attr(0755, root, root) %{_libexecdir}/libvirt-guests.sh

%files libs -f %{name}.lang
%license COPYING COPYING.LESSER
%config(noreplace) %{_sysconfdir}/libvirt/libvirt.conf
%config(noreplace) %{_sysconfdir}/libvirt/libvirt-admin.conf
%{_libdir}/libvirt.so.*
%{_libdir}/libvirt-qemu.so.*
%{_libdir}/libvirt-lxc.so.*
%{_libdir}/libvirt-admin.so.*
%dir %{_datadir}/libvirt/
%dir %{_datadir}/libvirt/schemas/
%dir %attr(0755, root, root) %{_localstatedir}/lib/libvirt/

%{_datadir}/libvirt/schemas/basictypes.rng
%{_datadir}/libvirt/schemas/capability.rng
%{_datadir}/libvirt/schemas/cputypes.rng
%{_datadir}/libvirt/schemas/domain.rng
%{_datadir}/libvirt/schemas/domaincaps.rng
%{_datadir}/libvirt/schemas/domaincheckpoint.rng
%{_datadir}/libvirt/schemas/domaincommon.rng
%{_datadir}/libvirt/schemas/domainsnapshot.rng
%{_datadir}/libvirt/schemas/interface.rng
%{_datadir}/libvirt/schemas/network.rng
%{_datadir}/libvirt/schemas/networkcommon.rng
%{_datadir}/libvirt/schemas/networkport.rng
%{_datadir}/libvirt/schemas/nodedev.rng
%{_datadir}/libvirt/schemas/nwfilter.rng
%{_datadir}/libvirt/schemas/nwfilter_params.rng
%{_datadir}/libvirt/schemas/nwfilterbinding.rng
%{_datadir}/libvirt/schemas/secret.rng
%{_datadir}/libvirt/schemas/storagecommon.rng
%{_datadir}/libvirt/schemas/storagepool.rng
%{_datadir}/libvirt/schemas/storagepoolcaps.rng
%{_datadir}/libvirt/schemas/storagevol.rng

%{_datadir}/libvirt/cpu_map/*.xml

%{_datadir}/libvirt/test-screenshot.png

%files admin
%{_mandir}/man1/virt-admin.1*
%{_bindir}/virt-admin
%if %{with_bash_completion}
%{_datadir}/bash-completion/completions/virt-admin
%endif

%if %{with_bash_completion}
%files bash-completion
%{_datadir}/bash-completion/completions/vsh
%endif

%if %{with_wireshark}
%files wireshark
%{wireshark_plugindir}/libvirt.so
%endif

%files nss
%{_libdir}/libnss_libvirt.so.2
%{_libdir}/libnss_libvirt_guest.so.2

%if %{with_lxc}
%files login-shell
%attr(4750, root, virtlogin) %{_bindir}/virt-login-shell
%config(noreplace) %{_sysconfdir}/libvirt/virt-login-shell.conf
%{_mandir}/man1/virt-login-shell.1*
%endif

%files devel
%{_libdir}/libvirt.so
%{_libdir}/libvirt-admin.so
%{_libdir}/libvirt-qemu.so
%{_libdir}/libvirt-lxc.so
%dir %{_includedir}/libvirt
%{_includedir}/libvirt/virterror.h
%{_includedir}/libvirt/libvirt.h
%{_includedir}/libvirt/libvirt-admin.h
%{_includedir}/libvirt/libvirt-common.h
%{_includedir}/libvirt/libvirt-domain.h
%{_includedir}/libvirt/libvirt-domain-checkpoint.h
%{_includedir}/libvirt/libvirt-domain-snapshot.h
%{_includedir}/libvirt/libvirt-event.h
%{_includedir}/libvirt/libvirt-host.h
%{_includedir}/libvirt/libvirt-interface.h
%{_includedir}/libvirt/libvirt-network.h
%{_includedir}/libvirt/libvirt-nodedev.h
%{_includedir}/libvirt/libvirt-nwfilter.h
%{_includedir}/libvirt/libvirt-secret.h
%{_includedir}/libvirt/libvirt-storage.h
%{_includedir}/libvirt/libvirt-stream.h
%{_includedir}/libvirt/libvirt-qemu.h
%{_includedir}/libvirt/libvirt-lxc.h
%{_libdir}/pkgconfig/libvirt.pc
%{_libdir}/pkgconfig/libvirt-admin.pc
%{_libdir}/pkgconfig/libvirt-qemu.pc
%{_libdir}/pkgconfig/libvirt-lxc.pc

%dir %{_datadir}/libvirt/api/
%{_datadir}/libvirt/api/libvirt-api.xml
%{_datadir}/libvirt/api/libvirt-admin-api.xml
%{_datadir}/libvirt/api/libvirt-qemu-api.xml
%{_datadir}/libvirt/api/libvirt-lxc-api.xml


%changelog
* Tue Aug 06 2019 Cole Robinson <crobinso@redhat.com> - 5.6.0-1
- Update to version 5.6.0

* Thu Jul 25 2019 Fedora Release Engineering <releng@fedoraproject.org> - 5.5.0-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_31_Mass_Rebuild

* Wed Jul 03 2019 Cole Robinson <crobinso@redhat.com> - 5.5.0-1
- Rebased to version 5.5.0

* Thu Jun 20 2019 Cole Robinson <crobinso@redhat.com> - 5.4.0-2
- CVE-2019-10161: arbitrary file read/exec via virDomainSaveImageGetXMLDesc
  API (bz #1722463, bz #1720115)
- CVE-2019-10166: virDomainManagedSaveDefineXML API exposed to readonly
  clients (bz #1722462, bz #1720114)
- CVE-2019-10167: arbitrary command execution via
  virConnectGetDomainCapabilities API (bz #1722464, bz #1720117)
- CVE-2019-10168: arbitrary command execution via
  virConnectBaselineHypervisorCPU and virConnectCompareHypervisorCPU APIs (bz
  #1722466, bz #1720118)

* Wed Jun 12 2019 Daniel P. Berrangé <berrange@redhat.com> - 5.4.0-1
- Update to 5.4.0 release

* Tue May 21 2019 Daniel P. Berrangé <berrange@redhat.com> - 5.3.0-3
- Fix systemd socket permissions
- Resolves: rhbz #1712498 (CVE-2019-10132)

* Tue May 14 2019 Daniel P. Berrangé <berrange@redhat.com> - 5.3.0-2
- Define md-clear CPUID bit
- Resolves: rhbz #1709977 (CVE-2018-12126), rhbz #1709979 (CVE-2018-12127),
  rhbz #1709997 (CVE-2018-12130), rhbz #1709984 (CVE-2019-11091)

* Tue May  7 2019 Daniel P. Berrangé <berrange@redhat.com> - 5.3.0-1
- Update to 5.3.0 release

* Mon Apr 08 2019 Cole Robinson <crobinso@redhat.com> - 5.2.0-2
- Rebuild for xen 4.12 soname bump

* Wed Apr  3 2019 Daniel P. Berrangé <berrange@redhat.com> - 5.2.0-1
- Update to 5.2.0 release

* Wed Mar 20 2019 Daniel P. Berrangé <berrange@redhat.com> - 5.1.0-3
- Fix upgrades for rbd on i686 (rhbz #1688121)
- Add missing xfsprogs-devel dep
- Fix use of deprecated RBD features
- Avoid using firewalld if unprivileged
- Don't require ipv6 firewall support at startup (rhbz #1688968)

* Wed Mar 06 2019 Igor Gnatenko <ignatenkobrain@fedoraproject.org> - 5.1.0-2
- Remove obsolete scriptlets

* Mon Mar  4 2019 Daniel P. Berrangé <berrange@redhat.com> - 5.1.0-1
- Update to 5.1.0 release

* Sun Feb 17 2019 Igor Gnatenko <ignatenkobrain@fedoraproject.org> - 5.0.0-3
- Rebuild for readline 8.0

* Fri Feb 01 2019 Fedora Release Engineering <releng@fedoraproject.org> - 5.0.0-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_30_Mass_Rebuild

* Mon Jan 21 2019 Daniel P. Berrangé <berrange@redhat.com> - 5.0.0-1
- Update to 5.0.0 release

* Mon Dec 10 2018 Daniel P. Berrangé <berrange@redhat.com> - 4.10.0-2
- Disable RBD on 32-bit arches (rhbz #1657928)

* Mon Dec  3 2018 Daniel P. Berrangé <berrange@redhat.com> - 4.10.0-1
- Update to 4.10.0 release

* Mon Nov 12 2018 Daniel P. Berrangé <berrange@redhat.com> - 4.9.0-1
- Update to 4.9.0 release

* Fri Oct  5 2018 Daniel P. Berrangé <berrange@redhat.com> - 4.8.0-1
- Update to 4.8.0 release

* Tue Sep  4 2018 Daniel P. Berrangé <berrange@redhat.com> - 4.7.0-1
- Update to 4.7.0 release

* Sat Aug 18 2018 David Abdurachmanov <david.abdurachmanov@gmail.com> - 4.6.0-2
- Add support for RISC-V (riscv64)

* Mon Aug  6 2018 Daniel P. Berrangé <berrange@redhat.com> - 4.6.0-1
- Update to 4.6.0 release

* Fri Jul 13 2018 Fedora Release Engineering <releng@fedoraproject.org> - 4.5.0-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_29_Mass_Rebuild

* Fri Jul  6 2018 Daniel P. Berrangé <berrange@redhat.com> - 4.5.0-2
- Fix regressions with chardev handling

* Tue Jul  3 2018 Daniel P. Berrangé <berrange@redhat.com> - 4.5.0-1
- Update to 4.5.0 release

* Tue Jun  5 2018 Daniel P. Berrangé <berrange@redhat.com> - 4.4.0-1
- Update to 4.4.0 release

* Thu May  3 2018 Daniel P. Berrangé <berrange@redhat.com> - 4.3.0-1
- Update to 4.3.0 release

* Tue Apr  3 2018 Daniel P. Berrangé <berrange@redhat.com> - 4.2.0-1
- Update to 4.2.0 release

* Fri Mar 23 2018 Iryna Shcherbina <ishcherb@redhat.com> - 4.1.0-3
- Update Python 2 dependency declarations to new packaging standards
  (See https://fedoraproject.org/wiki/FinalizingFedoraSwitchtoPython3)

* Wed Mar 21 2018 Daniel P. Berrangé <berrange@redhat.com> - 4.1.0-2
- Fix systemd macro argument with line continuations (rhbz#1558648)

* Mon Mar  5 2018 Daniel Berrange <berrange@redhat.com> - 4.1.0-1
- Rebase to version 4.1.0

* Wed Feb 07 2018 Fedora Release Engineering <releng@fedoraproject.org> - 4.0.0-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_28_Mass_Rebuild

* Fri Jan 19 2018 Daniel P. Berrange <berrange@redhat.com> - 4.0.0-1
- Rebase to version 4.0.0
