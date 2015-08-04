#
import unittest

from afew import utils


class TestUtils(unittest.TestCase):

    def test_strip_signatures_base(self):
        lines = ['Huhu', '--', 'Ikke']
        self.assertEqual(['Huhu'], utils.strip_signatures(lines))

    def test_strip_signatures_base_maxsig(self):
        lines = [
            'Huhu',
            '--',
            'Ikke',
            '**',
            "Sponsored by PowerDoh'",
            "Sponsored by PowerDoh'",
            "Sponsored by PowerDoh'",
            "Sponsored by PowerDoh'",
            "Sponsored by PowerDoh'",
        ]
        self.assertEqual(['Huhu'],
                         utils.strip_signatures(lines, max_signature_size=5))

    def test_strip_signatures_no_signature(self):
        """no signature, nothing should be stripped"""
        lines = '''
        bla
        bla
        bla
        '''.splitlines()
        self.assertEqual(lines,
                         utils.strip_signatures(lines, max_signature_size=2))


if __name__ == '__main__':
    unittest.main()
