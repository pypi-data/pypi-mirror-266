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


import unittest
from zenutils import treeutils


class TestTreeUtils(unittest.TestCase):
    def test01(self):
        thelist = [
            {"id": 1, "title": "a"},
            {"id": 2, "title": "b"},
            {"id": 3, "title": "a.a", "parent_id": 1},
            {"id": 4, "title": "b.a", "parent_id": 2},
            {"id": 5, "title": "a.a.a", "parent_id": 3},
            {"id": 6, "title": "a.a.b", "parent_id": 3},
            {"id": 7, "title": "a.a.c", "parent_id": 3},
            {"id": 8, "title": "c"},
            {"id": 9, "title": "a.a.b.a", "parent_id": 6},
            {"id": 10, "title": "b.a.a", "parent_id": 4},
            {"id": 11, "title": "d"},
        ]
        tree = treeutils.build_tree(thelist)
        treeutils.print_tree(tree)
        title = tree[0]["children"][0]["children"][1]["children"][0]["title"]
        assert title == "a.a.b.a"

    def test02(self):
        ## if the node's parent_id is not in current list, then the node is treated as root node.
        thelist = [
            {"id": 1, "title": "a", "parent_id": 4},
            {"id": 2, "title": "b", "parent_id": 4},
            {"id": 3, "title": "c", "parent_id": 5},
        ]
        tree = treeutils.build_tree(thelist)
        assert tree[0]["title"] == "a"
        assert tree[1]["title"] == "b"
        assert tree[2]["title"] == "c"

    def test03(self):
        srt = treeutils.SimpleRouterTree()
        srt.index("/api/v1/uc/", 1)
        srt.index("/api/v1/uc/token/new", 2)
        srt.index("/api/v1/biz/", 3)
        srt.index("/api/v1/biz/jump", 4)

        p1, r1 = srt.get_best_match("/api/v1/uc/ping")  # 前缀匹配
        p2, r2 = srt.get_best_match("/api/v1/uc/token/new")  # 精确匹配
        p3, r3 = srt.get_best_match("/api/v1/biz/go")  # 前缀匹配
        p4, r4 = srt.get_best_match("/api/v1/biz/jump")  # 精确匹配
        p5, r5 = srt.get_best_match("/api/v1/foo")  # 前缀匹配，无
        r6 = srt.get("/api/v1/uc/ping")  # 精确匹配，没有
        ps1 = srt.get_all_paths()

        srt.delete("/api/v1/uc/token/new")  # 删除索引
        p7, r7 = srt.get_best_match(
            "/api/v1/uc/token/new"
        )  # 无法精确匹配，降级为前缀匹配
        ps2 = srt.get_all_paths()

        assert r1 == 1
        assert p1 == "/api/v1/uc/"
        assert r2 == 2
        assert p2 == "/api/v1/uc/token/new"
        assert r3 == 3
        assert p3 == "/api/v1/biz/"
        assert r4 == 4
        assert p4 == "/api/v1/biz/jump"
        assert r5 is None
        assert p5 is None
        assert r6 is None
        assert r7 == 1
        assert p7 == "/api/v1/uc/"
        assert "/api/v1/uc/" in ps1
        assert "/api/v1/uc/token/new" in ps1
        assert "/api/v1/biz/" in ps1
        assert "/api/v1/biz/jump" in ps1
        assert not "/api/v1/uc/ping" in ps1
        assert not "/api/v1/uc/token/new" in ps2
