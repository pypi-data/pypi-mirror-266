import unittest

from switcore.action.activity_router import PathResolver


class PathResolverTest(unittest.TestCase):
    def test_combined_path(self):
        path_resolver: PathResolver = PathResolver("test_action_id01", ["a"])
        self.assertEqual(str(path_resolver), "test_action_id01/a")
        self.assertEqual(path_resolver.id, "test_action_id01")
        self.assertEqual(path_resolver.paths, ["a"])

    def test_from_combined01(self):
        path_resolver: PathResolver = PathResolver.from_combined("test_action_id01/a/b")
        self.assertEqual(str(path_resolver), "test_action_id01/a/b")
        self.assertEqual(path_resolver.id, "test_action_id01")
        self.assertEqual(path_resolver.paths, ["a", "b"])

    def test_from_combined02(self):
        path_resolver: PathResolver = PathResolver.from_combined("test_action_id01/a/b/1")
        self.assertEqual(str(path_resolver), "test_action_id01/a/b/1")
        self.assertEqual(path_resolver.id, "test_action_id01")
        self.assertEqual(path_resolver.paths, ["a", "b", 1])

    def test_convert_int(self):
        path_resolver: PathResolver = PathResolver("test_action_id01", [1, "a"])
        self.assertEqual(str(path_resolver), "test_action_id01/1/a")
        self.assertEqual(path_resolver.paths, [1, "a"])

    def test_escape01(self):
        path_resolver: PathResolver = PathResolver("test_escape_action_id/escape", ["a"])
        self.assertEqual(path_resolver.combined_path, "test_escape_action_id%2Fescape/a")
        self.assertEqual(path_resolver.id, "test_escape_action_id/escape")
        self.assertEqual(path_resolver.paths, ["a"])

        path_resolver: PathResolver = PathResolver("test_escape_action_id/escape", ["a/b"])
        self.assertEqual(path_resolver.combined_path, "test_escape_action_id%2Fescape/a%2Fb")
        self.assertEqual(path_resolver.id, "test_escape_action_id/escape")
        self.assertEqual(path_resolver.paths, ["a/b"])

        path_resolver: PathResolver = PathResolver("test_action_id01/aa/bb", ["a/b"])
        self.assertEqual(path_resolver.combined_path, "test_action_id01%2Faa%2Fbb/a%2Fb")
        self.assertEqual(path_resolver.id, "test_action_id01/aa/bb")
        self.assertEqual(path_resolver.paths, ["a/b"])
