#!/bin/bash
#
# check-files-efi.sh
# Copyright 2017 Peter Jones <pjones@redhat.com>
#
# Distributed under terms of the GPLv3 license.
#

set -e
set -u
RPM_BUILD_DIR=$1 && shift
( cat ; cat $RPM_BUILD_DIR/debugfiles-efi.list ) | $@

# vim:fenc=utf-8:tw=75
