#!/usr/bin/env python

# Copyright (C) 2015  Explorys, Inc.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from __future__ import print_function
import argparse
import struct
import sys

STAGE2_ONCEONLY_ENTRY = 0x10000
STAGE2_DEFAULT_PATH = '/boot/grub/stage2'


def get_raw_default(filename):
    with open(filename, 'rb') as f:
        f.seek(0x200 + 0xc)
        data = f.read(4)

    raw_default = struct.unpack('<I', data)[0]
    return raw_default


def set_raw_default(filename, raw_default):
    data = struct.pack('<I', raw_default)

    with open(filename, 'r+b') as f:
        f.seek(0x200 + 0xc)
        f.write(data)


def new_raw_default(old_raw_default, new_value, once):
    if once:
        raw_default = old_raw_default & 0xff
        raw_default += (new_value << 8) | STAGE2_ONCEONLY_ENTRY
    else:
        raw_default = new_value
    return raw_default


def dump_raw_default(raw_default):
    boot_once = (raw_default & STAGE2_ONCEONLY_ENTRY) != 0
    entry = raw_default & 0xff
    if boot_once:
        entry_once = (raw_default & ~STAGE2_ONCEONLY_ENTRY) >> 8
    print('Raw default value:    0x%08x' % raw_default)
    print('Boot once only:       %s' % str(boot_once))
    if boot_once:
        print('Default entry (once): %d' % entry_once)
    print('Default entry:        %d' % entry)


def positive_number(string):
    msg = '%r is not a positive value <= 0xFF' % string
    try:
        value = int(string, 0)
        if value < 0 or value > 0xff:
            raise argparse.ArgumentTypeError(msg)
        return value
    except ValueError as err:
        raise argparse.ArgumentTypeError(msg)


def main():
    parser = argparse.ArgumentParser(description='Read or change the GRUB 0.97 default boot entry')
    parser.add_argument('--path', dest='path', default=STAGE2_DEFAULT_PATH,
                        help='Path to GRUB\'s stage 2 binary (default: %s)' % STAGE2_DEFAULT_PATH)
    subparsers = parser.add_subparsers(dest='action', help='Action')
    parser_get = subparsers.add_parser('get', help='Get the default boot entry')
    parser_set = subparsers.add_parser('set', help='Set the default boot entry')
    parser_set.add_argument('value', type=positive_number,
                            help='Default boot entry value')
    parser_set.add_argument('--once', dest='once', action='store_true',
                            help='Set the default entry for once boot')
    args = parser.parse_args()

    raw_default = get_raw_default(args.path)
    if args.action == 'get':
        dump_raw_default(raw_default)
    elif args.action == 'set':
        raw_default = new_raw_default(raw_default, args.value, args.once)
        dump_raw_default(raw_default)
        set_raw_default(args.path, raw_default)

if __name__ == '__main__':
    main()
