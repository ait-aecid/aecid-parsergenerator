import unittest
import shutil
import os
import importlib
import random
import string
from _datetime import datetime
from time import time
import random
import socket
import struct

from base64 import b64encode


class AECIDpgTest(unittest.TestCase):
    """The goal of this test class is to test if the AECIDpg.py works. These tests are blackbox tests as they only give input to the
    AECIDpg.py and check if the output is correct.
    Note: AECIDpg must be imported after the setUp routine!"""

    log_file_name = 'unit/in/test1.log'
    generated_model_file_name = 'unit/out/GeneratedParserModel.py'

    def setUp(self):
        shutil.move('source/PGConfig.py', 'source/PGConfig_old.py')
        shutil.copyfile('unit/PGTestConfig.py', 'source/PGConfig.py')

    def tearDown(self):
        os.remove('source/PGConfig.py')
        shutil.move('source/PGConfig_old.py', 'source/PGConfig.py')
        os.remove(self.generated_model_file_name)
        os.remove('unit/out/logTemplates.txt')
        os.remove('unit/out/tree.txt')
        # os.remove('unit/in/test1.log')

    def test1basic_parsing_models(self):
        log_lines = [b'word'] * 100
        with open(self.log_file_name, 'wb') as f:
            for log in log_lines:
                f.write(log)
                f.write(b'\n')
        import source.AECIDpg
        generated_model = self.read_generated_parser_model()
        # self.assertEqual("model = FixedDataModelElement('fixed0', b'word')", generated_model)

        log_lines = [b'this', b'that', b'those'] * 33
        with open(self.log_file_name, 'wb') as f:
            for log in log_lines:
                f.write(log)
                f.write(b'\n')
        importlib.reload(source.AECIDpg)
        generated_model = self.read_generated_parser_model()
        # self.assertEqual("model = FixedWordlistDataModelElement('fixed0', [b'this', b'that', b'those'])", generated_model)

        log_lines = [bytes(str(i), 'utf-8') for i in range(100)]
        with open(self.log_file_name, 'wb') as f:
            for log in log_lines:
                f.write(log)
                f.write(b'\n')
        importlib.reload(source.AECIDpg)
        generated_model = self.read_generated_parser_model()
        # self.assertEqual("model = DecimalIntegerValueModelElement('integer0', value_sign_type=DecimalIntegerValueModelElement.SIGN_TYPE_"
        #                  "OPTIONAL))", generated_model)

        log_lines = [bytes(str(i / 10.0), 'utf-8') for i in range(100)]
        with open(self.log_file_name, 'wb') as f:
            for log in log_lines:
                f.write(log)
                f.write(b'\n')
        importlib.reload(source.AECIDpg)
        generated_model = self.read_generated_parser_model()
        # self.assertEqual("model = DecimalFloatValueModelElement('float0', value_sign_type=DecimalIntegerValueModelElement.SIGN_TYPE_"
        #                  "OPTIONAL))", generated_model)

        log_lines = [b64encode(bytes(self.random_string(), 'utf-8')) for _ in range(100)]
        with open(self.log_file_name, 'wb') as f:
            for log in log_lines:
                f.write(log)
                f.write(b'\n')
        importlib.reload(source.AECIDpg)
        generated_model = self.read_generated_parser_model()
        # self.assertEqual("model = Base64StringModelElement('base64encoded0')", generated_model)

        log_lines = [bytes(self.random_string(), 'utf-8') for _ in range(100)]
        with open(self.log_file_name, 'wb') as f:
            for log in log_lines:
                f.write(log)
                f.write(b'\n')
        importlib.reload(source.AECIDpg)
        generated_model = self.read_generated_parser_model()
        # self.assertEqual("model = VariableByteDataModelElement('string0')", generated_model)

        log_lines = [bytes(datetime.fromtimestamp(time() + i * 90000).strftime('%m/%d/%Y %H:%M:%S'), 'utf-8') for i in range(100)]
        with open(self.log_file_name, 'wb') as f:
            for log in log_lines:
                f.write(log)
                f.write(b'\n')
        importlib.reload(source.AECIDpg)
        generated_model = self.read_generated_parser_model()
        # self.assertEqual("model = DateTimeModelElement('datetime0')", generated_model)

        log_lines = [self.random_string(50).encode().hex().encode() for _ in range(100)]
        with open(self.log_file_name, 'wb') as f:
            for log in log_lines:
                f.write(log)
                f.write(b'\n')
        importlib.reload(source.AECIDpg)
        generated_model = self.read_generated_parser_model()
        # self.assertEqual("model = HexStringModelElement('hexstring0')", generated_model)

        log_lines = [socket.inet_ntoa(struct.pack('>I', random.randint(1, 0xffffffff))).encode() for _ in range(100)]
        with open(self.log_file_name, 'wb') as f:
            for log in log_lines:
                f.write(log)
                f.write(b'\n')
        importlib.reload(source.AECIDpg)
        generated_model = self.read_generated_parser_model()
        self.assertEqual("model = IpAddressDataModelElement('ipaddress0')", generated_model)

    def read_generated_parser_model(self):
        generated_model = ''
        with open(self.generated_model_file_name) as f:
            found = False
            for line in f.readlines():
                if 'model = ' in line:
                    found = True
                elif 'return model' in line:
                    found = False
                if found:
                    generated_model += line.strip()
        return generated_model

    def random_string(self, string_length=100):
        letters = string.ascii_lowercase
        return ''.join(random.choice(letters) for _ in range(string_length))


if __name__ == "__main__":
    unittest.main()