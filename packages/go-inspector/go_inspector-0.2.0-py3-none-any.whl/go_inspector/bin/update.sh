#!/usr/bin/env bash
#
# Copyright (c) nexB Inc. and others. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/go-inspector for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.

# Use this script to update GoReSym binary to a new version

set +e
GORESYM_VERSION=v2.7.2

rm -rf GoReSym.zip goresymzip

wget https://github.com/mandiant/GoReSym/releases/download/$GORESYM_VERSION/GoReSym.zip

# recompute the sha256 by hand with:
# sha256sum GoReSym.zip > GoReSym.zip.sums
sha256sum -c GoReSym.zip.sums

unzip -qd goresymzip GoReSym.zip
mv goresymzip/GoReSym_lin .
chmod u+x GoReSym_lin

rm -rf GoReSym.zip goresymzip

# finally run a binary analysis on this GoReSym executable and update the ABOUT files accordingly 
