#!/usr/bin/env python
# -*- coding: utf8 -*-
from __future__ import (
    absolute_import,
    division,
    generators,
    nested_scopes,
    print_function,
    unicode_literals,
    with_statement,
)
from zenutils.sixutils import *

import os
import random
import unittest
from zenutils import numericutils


class TestNumericUtils(unittest.TestCase):
    def test01(self):
        assert numericutils.binary_decompose(0) == set([])
        assert numericutils.binary_decompose(1) == set([1])
        assert numericutils.binary_decompose(2) == set([2])
        assert numericutils.binary_decompose(3) == set([1, 2])
        assert numericutils.binary_decompose(4) == set([4])
        assert numericutils.binary_decompose(5) == set([1, 4])
        assert numericutils.binary_decompose(6) == set([2, 4])
        assert numericutils.binary_decompose(7) == set([1, 2, 4])
        assert numericutils.binary_decompose(8) == set([8])

    def test02(self):
        assert numericutils.decimal_change_base(0, 10) == "0"
        assert numericutils.decimal_change_base(1, 10) == "1"
        assert numericutils.decimal_change_base(2, 10) == "2"
        assert numericutils.decimal_change_base(3, 10) == "3"
        assert numericutils.decimal_change_base(4, 10) == "4"
        assert numericutils.decimal_change_base(5, 10) == "5"
        assert numericutils.decimal_change_base(6, 10) == "6"
        assert numericutils.decimal_change_base(7, 10) == "7"
        assert numericutils.decimal_change_base(8, 10) == "8"
        assert numericutils.decimal_change_base(9, 10) == "9"
        assert numericutils.decimal_change_base(10, 10) == "10"
        assert numericutils.decimal_change_base(11, 10) == "11"

    def test03(self):
        assert numericutils.decimal_change_base(0, 2) == "0"
        assert numericutils.decimal_change_base(1, 2) == "1"
        assert numericutils.decimal_change_base(2, 2) == "10"
        assert numericutils.decimal_change_base(3, 2) == "11"
        assert numericutils.decimal_change_base(4, 2) == "100"
        assert numericutils.decimal_change_base(5, 2) == "101"
        assert numericutils.decimal_change_base(6, 2) == "110"
        assert numericutils.decimal_change_base(7, 2) == "111"
        assert numericutils.decimal_change_base(8, 2) == "1000"
        assert numericutils.decimal_change_base(9, 2) == "1001"
        assert numericutils.decimal_change_base(10, 2) == "1010"
        assert numericutils.decimal_change_base(11, 2) == "1011"

    def test04(self):
        assert numericutils.decimal_change_base(0, 16) == "0"
        assert numericutils.decimal_change_base(1, 16) == "1"
        assert numericutils.decimal_change_base(2, 16) == "2"
        assert numericutils.decimal_change_base(3, 16) == "3"
        assert numericutils.decimal_change_base(4, 16) == "4"
        assert numericutils.decimal_change_base(5, 16) == "5"
        assert numericutils.decimal_change_base(6, 16) == "6"
        assert numericutils.decimal_change_base(7, 16) == "7"
        assert numericutils.decimal_change_base(8, 16) == "8"
        assert numericutils.decimal_change_base(9, 16) == "9"
        assert numericutils.decimal_change_base(10, 16) == "a"
        assert numericutils.decimal_change_base(11, 16) == "b"
        assert numericutils.decimal_change_base(12, 16) == "c"
        assert numericutils.decimal_change_base(13, 16) == "d"
        assert numericutils.decimal_change_base(14, 16) == "e"
        assert numericutils.decimal_change_base(15, 16) == "f"
        assert numericutils.decimal_change_base(16, 16) == "10"

    def test05(self):
        assert numericutils.get_float_part(0) == 0
        assert numericutils.get_float_part(1) == 0
        assert numericutils.get_float_part(-0) == 0
        assert numericutils.get_float_part(-1) == 0
        assert numericutils.get_float_part(1.0) == 0
        assert numericutils.get_float_part(1.1) == 1000000
        assert numericutils.get_float_part(1.12) == 1200000
        assert numericutils.get_float_part(1.123) == 1230000
        assert numericutils.get_float_part(0.0) == 0
        assert numericutils.get_float_part(0.1) == 1000000
        assert numericutils.get_float_part(0.12) == 1200000
        assert numericutils.get_float_part(0.123) == 1230000
        assert numericutils.get_float_part(-1.0) == 0
        assert numericutils.get_float_part(-1.1) == 1000000
        assert numericutils.get_float_part(-1.12) == 1200000
        assert numericutils.get_float_part(-1.123) == 1230000
        assert numericutils.get_float_part(-0.0) == 0
        assert numericutils.get_float_part(-0.12) == 1200000
        assert numericutils.get_float_part(-0.123) == 1230000
        assert numericutils.get_float_part(-0.1) == 1000000
        assert numericutils.get_float_part(-0.01) == 100000
        assert numericutils.get_float_part(-0.001) == 10000
        assert numericutils.get_float_part(-0.0001) == 1000
        assert numericutils.get_float_part(-0.00001) == 100
        assert numericutils.get_float_part(-0.000001) == 10
        assert numericutils.get_float_part(-0.0000001) == 1
        assert numericutils.get_float_part(-0.00000001, 9) == 10

    def test06(self):
        assert numericutils.float_split(0) == (1, 0, 0)
        assert numericutils.float_split(1) == (1, 1, 0)
        assert numericutils.float_split(-0) == (1, 0, 0)
        assert numericutils.float_split(-1) == (-1, 1, 0)
        assert numericutils.float_split(1.0) == (1, 1, 0)
        assert numericutils.float_split(1.1) == (1, 1, 1000000)
        assert numericutils.float_split(1.12) == (1, 1, 1200000)
        assert numericutils.float_split(1.123) == (1, 1, 1230000)
        assert numericutils.float_split(0.0) == (1, 0, 0)
        assert numericutils.float_split(0.1) == (1, 0, 1000000)
        assert numericutils.float_split(0.12) == (1, 0, 1200000)
        assert numericutils.float_split(0.123) == (1, 0, 1230000)
        assert numericutils.float_split(-1.0) == (-1, 1, 0)
        assert numericutils.float_split(-1.1) == (-1, 1, 1000000)
        assert numericutils.float_split(-1.12) == (-1, 1, 1200000)
        assert numericutils.float_split(-1.123) == (-1, 1, 1230000)
        assert numericutils.float_split(-0.0) == (1, 0, 0)
        assert numericutils.float_split(-0.1) == (-1, 0, 1000000)
        assert numericutils.float_split(-0.12) == (-1, 0, 1200000)
        assert numericutils.float_split(-0.123) == (-1, 0, 1230000)
        assert numericutils.float_split(-0.01) == (-1, 0, 100000)
        assert numericutils.float_split(-0.12345678) == (-1, 0, 1234567)

    def test07(self):
        assert numericutils.is_infinity(float("inf")) is True
        assert numericutils.is_infinity(float("-inf")) is True
        assert numericutils.is_infinity(0.0) is False
        assert numericutils.is_infinity(0.1) is False

    def test08(self):
        assert numericutils._from_bytes(b"hello", "big") == 448378203247
        assert numericutils._from_bytes(b"hello", "big", signed=True) == 448378203247
        assert numericutils._from_bytes(b"hello", "little") == 478560413032
        assert numericutils._from_bytes(b"hello", "little", signed=True) == 478560413032

        assert numericutils._from_bytes(b"abc", "big") == 6382179
        assert numericutils._from_bytes(b"abc", "big", signed=True) == 6382179
        assert numericutils._from_bytes(b"abc", "little") == 6513249
        assert numericutils._from_bytes(b"abc", "little", signed=True) == 6513249

        assert numericutils._from_bytes(b"", "big") == 0
        assert numericutils._from_bytes(b"", "big", signed=True) == 0
        assert numericutils._from_bytes(b"", "little") == 0
        assert numericutils._from_bytes(b"", "little", signed=True) == 0

        assert numericutils._from_bytes(b"\xff", "big") == 255
        assert numericutils._from_bytes(b"\xff", "big", signed=True) == -1
        assert numericutils._from_bytes(b"\xff", "little") == 255
        assert numericutils._from_bytes(b"\xff", "little", signed=True) == -1

        assert numericutils._from_bytes(b"\xff\xaa", "big") == 65450
        assert numericutils._from_bytes(b"\xff\xaa", "big", signed=True) == -86
        assert numericutils._from_bytes(b"\xff\xaa", "little") == 43775
        assert numericutils._from_bytes(b"\xff\xaa", "little", signed=True) == -21761

    def test09(self):
        data = b"\xfbv\x9dq6\x94\xa1\xe2\xa0P\xa8\x96\xac\xe3O\x8b\x0bi\x9a\xe9\xea\x92@\x08)\xee\x8a\x15\t%\xe6\x90\xa8\xcfJ\nX\xe6\x12\x96\x97G\xa5'm\x8b\x13\xc5m\xaf\xb9\x9f"
        value = 166231341758227121687846500029642935057146082350369973176474181511812540102287508707676189261858076641625610704832490992810399
        assert numericutils._from_bytes(data, "big", signed=False) == value

    def test10(self):
        if hasattr(int, "from_bytes"):
            for i in range(1024):
                length = random.randint(0, 1024)
                data = os.urandom(length)
                assert int.from_bytes(
                    data, "big", signed=False
                ) == numericutils._from_bytes(data, "big", signed=False)
                assert int.from_bytes(
                    data, "big", signed=True
                ) == numericutils._from_bytes(data, "big", signed=True)
                assert int.from_bytes(
                    data, "little", signed=False
                ) == numericutils._from_bytes(data, "little", signed=False)
                assert int.from_bytes(
                    data, "little", signed=True
                ) == numericutils._from_bytes(data, "little", signed=True)

    def test11(self):
        for i in range(1024):
            length = random.randint(0, 1024)
            data1 = os.urandom(length)
            data2 = numericutils.from_bytes(data1)
            data3 = numericutils.int2bytes(data2)
            assert data1.strip(b"\x00") == data3.strip(b"\x00")

    def test12(self):
        assert numericutils.int2bytes(0) == b"\x00"
        assert numericutils.int2bytes(1) == b"\x01"
        assert numericutils.int2bytes(127) == b"\x7f"
        assert numericutils.int2bytes(128) == b"\x80"
        assert numericutils.int2bytes(255) == b"\xff"
        assert numericutils.int2bytes(256) == b"\x01\x00"
        assert numericutils.int2bytes(512) == b"\x02\x00"
        assert numericutils.int2bytes(513) == b"\x02\x01"
        assert numericutils.int2bytes(1023) == b"\x03\xff"
        assert numericutils.int2bytes(1024) == b"\x04\x00"
        assert numericutils.int2bytes(1025) == b"\x04\x01"

    def test13(self):
        assert numericutils._int2bytes(0) == b"\x00"
        assert numericutils._int2bytes(1) == b"\x01"
        assert numericutils._int2bytes(127) == b"\x7f"
        assert numericutils._int2bytes(128) == b"\x80"
        assert numericutils._int2bytes(255) == b"\xff"
        assert numericutils._int2bytes(256) == b"\x01\x00"
        assert numericutils._int2bytes(512) == b"\x02\x00"
        assert numericutils._int2bytes(513) == b"\x02\x01"
        assert numericutils._int2bytes(1023) == b"\x03\xff"
        assert numericutils._int2bytes(1024) == b"\x04\x00"
        assert numericutils._int2bytes(1025) == b"\x04\x01"

    def test14(self):
        if hasattr(int, "to_bytes"):
            for i in range(2048):
                length = random.randint(8, 16)
                assert numericutils.int2bytes(i, length) == i.to_bytes(length, "big")
                assert numericutils.int2bytes(i, length, "little") == i.to_bytes(
                    length, "little"
                )
            for i in range(2048):
                i *= -1
                length = random.randint(8, 16)
                assert numericutils.int2bytes(i, length, signed=True) == i.to_bytes(
                    length, "big", signed=True
                )
                assert numericutils.int2bytes(
                    i, length, "little", signed=True
                ) == i.to_bytes(length, "little", signed=True)

    def test15(self):
        assert numericutils._int2bytes(-1, signed=True) == b"\xff"
        assert numericutils._int2bytes(-2, signed=True) == b"\xfe"
        assert numericutils._int2bytes(-127, signed=True) == b"\x81"
        assert numericutils._int2bytes(-128, signed=True) == b"\x80"
        assert numericutils._int2bytes(-129, signed=True) == b"\xff\x7f"
        assert numericutils._int2bytes(-255, signed=True) == b"\xff\x01"
        assert numericutils._int2bytes(-256, signed=True) == b"\xff\x00"
        assert numericutils._int2bytes(-257, signed=True) == b"\xfe\xff"
        assert numericutils._int2bytes(-511, signed=True) == b"\xfe\x01"
        assert numericutils._int2bytes(-512, signed=True) == b"\xfe\x00"
        assert numericutils._int2bytes(-513, signed=True) == b"\xfd\xff"
        assert numericutils._int2bytes(-1023, signed=True) == b"\xfc\x01"
        assert numericutils._int2bytes(-1024, signed=True) == b"\xfc\x00"
        assert numericutils._int2bytes(-1025, signed=True) == b"\xfb\xff"

    def test16(self):
        assert numericutils.int2bytes(-1, signed=True) == b"\xff"
        assert numericutils.int2bytes(-2, signed=True) == b"\xfe"
        assert numericutils.int2bytes(-127, signed=True) == b"\x81"
        assert numericutils.int2bytes(-128, signed=True) == b"\x80"
        assert numericutils.int2bytes(-129, signed=True) == b"\xff\x7f"
        assert numericutils.int2bytes(-255, signed=True) == b"\xff\x01"
        assert numericutils.int2bytes(-256, signed=True) == b"\xff\x00"
        assert numericutils.int2bytes(-257, signed=True) == b"\xfe\xff"
        assert numericutils.int2bytes(-511, signed=True) == b"\xfe\x01"
        assert numericutils.int2bytes(-512, signed=True) == b"\xfe\x00"
        assert numericutils.int2bytes(-513, signed=True) == b"\xfd\xff"
        assert numericutils.int2bytes(-1023, signed=True) == b"\xfc\x01"
        assert numericutils.int2bytes(-1024, signed=True) == b"\xfc\x00"
        assert numericutils.int2bytes(-1025, signed=True) == b"\xfb\xff"
