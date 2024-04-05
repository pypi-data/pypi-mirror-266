import pathlib
from unittest import TestCase

from bai2 import bai2
from bai2.models import Bai2File

from tests.test_writers import Bai2FileWriterTestCase


class ParseTestCase(TestCase):
    @classmethod
    def open_test_file(cls, name):
        path = pathlib.Path(__file__).parent / 'data' / f'{name}.bai2'
        return path.open()

    def test_parse_from_lines(self):
        lines = [
            '01,CITIDIRECT,8888888,150716,0713,00131100,,,2/',
            '02,8888888,CITIGB00,1,150715,2340,GBP,2/',
            '03,77777777,GBP,010,10000,,,015,10000,,,/',
            '16,191,001,V,150715,,1234567890,RP12312312312312/',
            '88,FR:FP SIP INCOMING',
            '88,ENDT:20150715',
            '88,TRID:RP12312312312312',
            '88,PY:RP1231231231231200                 A1234BC 22/03/66',
            '88,BI:22222222',
            '88,OB:111111 BUCKINGHAM PALACE OB3:BARCLAYS BANK PLC',
            '88,BO:11111111 BO1:DOE JO',
            '49,20001,10/',
            '98,20001,1,12/',
            '99,20001,1,14/',
        ]

        bai2_file = bai2.parse_from_lines(lines)
        self.assertTrue(isinstance(bai2_file, Bai2File))

    def test_parse_from_string(self):
        s = (
            '01,CITIDIRECT,8888888,150716,0713,00131100,,,2/\n'
            '02,8888888,CITIGB00,1,150715,2340,GBP,2/\n'
            '03,77777777,GBP,010,10000,,,015,10000,,,/\n'
            '16,191,001,V,150715,,1234567890,RP12312312312312/\n'
            '88,FR:FP SIP INCOMING\n'
            '88,ENDT:20150715\n'
            '88,TRID:RP12312312312312\n'
            '88,PY:RP1231231231231200                 A1234BC 22/03/66\n'
            '88,BI:22222222\n'
            '88,OB:111111 BUCKINGHAM PALACE OB3:BARCLAYS BANK PLC\n'
            '88,BO:11111111 BO1:DOE JO\n'
            '49,20001,10/\n'
            '98,20001,1,12/\n'
            '99,20001,1,14/\n'
        )

        bai2_file = bai2.parse_from_string(s)
        self.assertTrue(isinstance(bai2_file, Bai2File))

    def test_parse_from_file(self):
        with self.open_test_file('citi_example') as f:
            bai2_file = bai2.parse_from_file(f)
            self.assertTrue(isinstance(bai2_file, Bai2File))

    def test_parse_from_file_2(self):
        with self.open_test_file('nwb_example') as f:
            bai2_file = bai2.parse_from_file(f)
            self.assertTrue(isinstance(bai2_file, Bai2File))

    def test_parse_from_file_3(self):
        with self.open_test_file('svb_us_example') as f:
            bai2_file = bai2.parse_from_file(f)
            self.assertTrue(isinstance(bai2_file, Bai2File))

    def test_parse_from_file_with_known_parsing_issue(self):
        with self.open_test_file('account_trailer_amount_blank_example') as f:
            bai2_file = bai2.parse_from_file(f)
            self.assertTrue(isinstance(bai2_file, Bai2File))

    def test_as_string(self):
        original = (
            '01,CITIDIRECT,8888888,150716,0713,00131100,,,2/\n'
            '02,8888888,CITIGB00,1,150715,2340,GBP,2/\n'
            '03,77777777,GBP,010,10000,,,015,10000,,,/\n'
            '16,191,001,V,150715,,1234567890,RP12312312312312/\n'
            '88,FR:FP SIP INCOMING\n'
            '88,ENDT:20150715\n'
            '88,TRID:RP12312312312312\n'
            '88,PY:RP1231231231231200                 A1234BC 22/03/66\n'
            '88,BI:22222222\n'
            '88,OB:111111 BUCKINGHAM PALACE OB3:BARCLAYS BANK PLC\n'
            '88,BO:11111111 BO1:DOE JO\n'
            '49,20001,10/\n'
            '98,20001,1,12/\n'
            '99,20001,1,14/'
        )

        bai2_file = bai2.parse_from_string(original)
        self.assertTrue(isinstance(bai2_file, Bai2File))

        from_model = bai2_file.as_string()

        self.assertEqual(original, from_model)

    def test_parse_files_with_trailing_whitespaces(self):
        original = (
            '01,123456,123456,220310,0022,1,,,2/                                             \n'
            '02,,123456,1,220309,,USD,2/                                                     \n'
            '03,654321,USD,010,10372793,,,015,11384293,,/                                    \n'
            '16,195,1011500,,12345678912345,Test Transaction/                                \n'
            '49,22768586,3/                                                                  \n'
            '98,22768586,1,5/                                                                \n'
            '99,22768586,1,7/                                                                \n'
        )

        bai2_file = bai2.parse_from_string(original)
        self.assertTrue(isinstance(bai2_file, Bai2File))

        from_model = bai2_file.as_string()
        original_stripped = '\n'.join(['{}'.format(s.strip()) for s in original.splitlines()])

        self.assertEqual(original_stripped, from_model)

    def test_parse_files_with_blank_lines(self):
        original = (
            '01,123456,123456,220310,0022,1,,,2/                                             \n'
            '\n'
            '02,,123456,1,220309,,USD,2/                                                     \n'
            '\n'
            '03,654321,USD,010,10372793,,,015,11384293,,/                                    \n'
            '\n'
            '16,195,1011500,,12345678912345,Test Transaction/                                \n'
            '\n'
            '49,22768586,3/                                                                  \n'
            '\n'
            '98,22768586,1,5/                                                                \n'
            '\n'
            '99,22768586,1,7/                                                                \n'
        )

        bai2_file = bai2.parse_from_string(original)
        self.assertTrue(isinstance(bai2_file, Bai2File))

        from_model = bai2_file.as_string()
        original_stripped = '\n'.join(['{}'.format(s.strip()) for s in original.splitlines() if s.strip()])

        self.assertEqual(original_stripped, from_model)


class WriteTestCase(TestCase):
    def test_write(self):
        bai2_file = Bai2FileWriterTestCase.create_bai2_file()

        output = bai2.write(bai2_file)
        self.assertEqual(
            output,
            (
                '01,CITIDIRECT,8888888,150715,2340,00131100,,,2/\n'
                '02,8888888,CITIGB00,1,150715,2340,GBP,2/\n'
                '03,77777777,GBP,010,10000,,,015,10000,,/\n'
                '16,399,2599,,,,BILLS BILLS BILLS BILLS BILLS BILLS BILLS BILLS BILLS BILLS BILLS\n'
                '88, BILLS\n'
                '16,399,1000,0,,,OTHER\n'
                '49,23599,5/\n'
                '03,77777777,GBP,010,10000,,,015,10000,,/\n'
                '16,399,2599,,,,BILLS BILLS BILLS BILLS BILLS BILLS BILLS BILLS BILLS BILLS BILLS\n'
                '88, BILLS\n'
                '16,399,1000,0,,,OTHER\n'
                '49,23599,5/\n'
                '98,47198,2,12/\n'
                '02,8888888,CITIGB00,1,150715,2340,GBP,2/\n'
                '03,77777777,GBP,010,10000,,,015,10000,,/\n'
                '16,399,2599,,,,BILLS BILLS BILLS BILLS BILLS BILLS BILLS BILLS BILLS BILLS BILLS\n'
                '88, BILLS\n'
                '16,399,1000,0,,,OTHER\n'
                '49,23599,5/\n'
                '03,77777777,GBP,010,10000,,,015,10000,,/\n'
                '16,399,2599,,,,BILLS BILLS BILLS BILLS BILLS BILLS BILLS BILLS BILLS BILLS BILLS\n'
                '88, BILLS\n'
                '16,399,1000,0,,,OTHER\n'
                '49,23599,5/\n'
                '98,47198,2,12/\n'
                '99,94396,2,26/'
            ),
        )
