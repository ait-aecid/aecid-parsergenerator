import unittest
import shutil
import os
import importlib
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
    maxDiff = None

    def setUp(self):
        shutil.move('source/PGConfig.py', 'source/PGConfig_old.py')
        shutil.copyfile('unit/PGTestConfig.py', 'source/PGConfig.py')

    def tearDown(self):
        os.remove('source/PGConfig.py')
        shutil.move('source/PGConfig_old.py', 'source/PGConfig.py')
        os.remove(self.generated_model_file_name)
        os.remove('unit/out/logTemplates.txt')
        os.remove('unit/out/tree.txt')
        os.remove(self.log_file_name)

    def test1basic_parsing_models(self):
        """This unittest checks if basic parsing ModelElements are discovered properly"""
        log_lines = [b'word'] * 100
        with open(self.log_file_name, 'wb') as f:
            for log in log_lines:
                f.write(log)
                f.write(b'\n')
        import source.AECIDpg
        generated_model = self.read_generated_parser_model()
        self.assertEqual("model = FixedDataModelElement('fixed0', b'word')", generated_model)

        log_lines = [b'this', b'that', b'those'] * 33
        with open(self.log_file_name, 'wb') as f:
            for log in log_lines:
                f.write(log)
                f.write(b'\n')
        importlib.reload(source.AECIDpg)
        generated_model = self.read_generated_parser_model()
        self.assertEqual("model = FixedWordlistDataModelElement('fixed0', [b'this', b'that', b'those'])", generated_model)

        log_lines = [bytes(str(i), 'utf-8') for i in range(100)]
        with open(self.log_file_name, 'wb') as f:
            for log in log_lines:
                f.write(log)
                f.write(b'\n')
        importlib.reload(source.AECIDpg)
        generated_model = self.read_generated_parser_model()
        self.assertEqual("model = DecimalIntegerValueModelElement('integer0', value_sign_type=DecimalIntegerValueModelElement.SIGN_TYPE_"
                         "OPTIONAL))", generated_model)

        log_lines = [bytes(str(i / 10.0), 'utf-8') for i in range(100)]
        with open(self.log_file_name, 'wb') as f:
            for log in log_lines:
                f.write(log)
                f.write(b'\n')
        importlib.reload(source.AECIDpg)
        generated_model = self.read_generated_parser_model()
        self.assertEqual("model = DecimalFloatValueModelElement('float0', value_sign_type=DecimalIntegerValueModelElement.SIGN_TYPE_"
                         "OPTIONAL))", generated_model)

        log_lines = [b64encode(bytes(self.random_string(), 'utf-8')) for _ in range(100)]
        with open(self.log_file_name, 'wb') as f:
            for log in log_lines:
                f.write(log)
                f.write(b'\n')
        importlib.reload(source.AECIDpg)
        generated_model = self.read_generated_parser_model()
        self.assertEqual("model = Base64StringModelElement('base64encoded0')", generated_model)

        log_lines = [bytes(self.random_string(), 'utf-8') for _ in range(100)]
        with open(self.log_file_name, 'wb') as f:
            for log in log_lines:
                f.write(log)
                f.write(b'\n')
        importlib.reload(source.AECIDpg)
        generated_model = self.read_generated_parser_model()
        self.assertEqual("model = VariableByteDataModelElement('string0', alphabet)", generated_model)

        log_lines = [bytes(datetime.fromtimestamp(time() + i * 90000).strftime('%m/%d/%Y %H:%M:%S'), 'utf-8') for i in range(100)]
        with open(self.log_file_name, 'wb') as f:
            for log in log_lines:
                f.write(log)
                f.write(b'\n')
        importlib.reload(source.AECIDpg)
        generated_model = self.read_generated_parser_model()
        self.assertEqual("model = DateTimeModelElement('datetime0')", generated_model)

        log_lines = [self.random_string(50).encode().hex().encode() for _ in range(100)]
        with open(self.log_file_name, 'wb') as f:
            for log in log_lines:
                f.write(log)
                f.write(b'\n')
        importlib.reload(source.AECIDpg)
        generated_model = self.read_generated_parser_model()
        self.assertEqual("model = HexStringModelElement('hexstring0')", generated_model)

        log_lines = [socket.inet_ntoa(struct.pack('>I', random.randint(1, 0xffffffff))).encode() for _ in range(100)]
        with open(self.log_file_name, 'wb') as f:
            for log in log_lines:
                f.write(log)
                f.write(b'\n')
        importlib.reload(source.AECIDpg)
        generated_model = self.read_generated_parser_model()
        self.assertEqual("model = IpAddressDataModelElement('ipaddress0')", generated_model)

    def test2combined_parsing_models(self):
        """This unittest checks if advanced ModelElements like FirstMatchModelElement, SequenceModelElement and OptionalMatchModelElement
        are discovered properly."""
        wordlist = [b'this', b'that', b'those']
        wordlist.sort()
        log_lines = []
        i = 0
        log_lines.append(b'word ' + wordlist[random.randint(0, len(wordlist) - 1)] + b' ' + bytes(str(i), 'utf-8') + b' ' +
                         bytes(str(i / 10.0), 'utf-8') + b' ' + b64encode(bytes(self.random_string(), 'utf-8')) + b' '+
                         bytes(self.random_string(), 'utf-8') + b' ' +
                         socket.inet_ntoa(struct.pack('>I', random.randint(1, 0xffffffff))).encode())
        for i in range(1000):
            log_lines.append(b'word ' + wordlist[random.randint(0, len(wordlist) - 1)] + b' ' + bytes(str(i), 'utf-8') + b' ' +
                             bytes(str(i / 10.0), 'utf-8') + b' ' + b64encode(bytes(self.random_string(), 'utf-8')) + b' ' +
                             bytes(self.random_string(), 'utf-8') + b' ' +
                             socket.inet_ntoa(struct.pack('>I', random.randint(1, 0xffffffff))).encode())
        with open(self.log_file_name, 'wb') as f:
            for log in log_lines:
                f.write(log)
                f.write(b'\n')
        import source.AECIDpg
        importlib.reload(source.AECIDpg)
        generated_model = self.read_generated_parser_model()
        generated_model = generated_model.replace(', ', ',')
        self.assertEqual(
            "model = SequenceModelElement('sequence0',[FixedDataModelElement('fixed1',b'word '),FixedWordlistDataModelElement('fixed2',"
            "[b'this',b'that',b'those']),FixedDataModelElement('fixed3',b' '),DecimalIntegerValueModelElement(integer4,"
            "value_sign_type=DecimalIntegerValueModelElement.SIGN_TYPE_OPTIONAL),FixedDataModelElement('fixed5',b' '),"
            "DecimalFloatValueModelElement('float6',value_sign_type=DecimalFloatValueModelElement.SIGN_TYPE_OPTIONAL),"
            "FixedDataModelElement('fixed7',b' '),Base64StringModelElement('base64encoded8'),FixedDataModelElement('fixed9',b' '),"
            "VariableByteDataModelElement('string10', alphabet), FixedDataModelElement('fixed11', b' '),"
            "IpAddressDataModelElement('ipaddress12')]", generated_model)

        log_lines = []
        for i in range(10000):
            r = random.randint(0, 1)
            if r == 0:
                log_lines.append(b'word ' + wordlist[random.randint(0, len(wordlist) - 1)] + b' ' + bytes(str(i), 'utf-8') + b' ' +
                                 bytes(str(i / 10.0), 'utf-8') + b' ' + b64encode(bytes(self.random_string(), 'utf-8')) + b' ' +
                                 bytes(self.random_string(), 'utf-8') + b' ' +
                                 socket.inet_ntoa(struct.pack('>I', random.randint(1, 0xffffffff))).encode())
            else:
                r = random.randint(0, 1)
                log_line = 'System started at %s.' % datetime.fromtimestamp(time() + i * 90000).strftime('%m/%d/%Y %H:%M:%S')
                if r == 1:
                    log_line += ' This is an optional part of the log line.'
                log_lines.append(log_line.encode())
        with open(self.log_file_name, 'wb') as f:
            for log in log_lines:
                f.write(log)
                f.write(b'\n')
        importlib.reload(source.AECIDpg)
        generated_model = self.read_generated_parser_model()
        generated_model = generated_model.replace(', ', ',')
        self.assertEqual(
            "model = FirstMatchModelElement('firstmatch0',[SequenceModelElement('sequence1',[FixedDataModelElement('fixed2',b'word '),"
            "FixedWordlistDataModelElement('fixed3',[b'this',b'that',b'those']),FixedDataModelElement('fixed4',b' '),"
            "DecimalIntegerValueModelElement(integer5,value_sign_type=DecimalIntegerValueModelElement.SIGN_TYPE_OPTIONAL),"
            "FixedDataModelElement('fixed6',b' '),DecimalFloatValueModelElement('float7',"
            "value_sign_type=DecimalFloatValueModelElement.SIGN_TYPE_OPTIONAL),FixedDataModelElement('fixed8',b' '),"
            "Base64StringModelElement('base64encoded9'),FixedDataModelElement('fixed10',b' '),"
            "VariableByteDataModelElement('string11',alphabet),FixedDataModelElement('fixed12',b' '),"
            "IpAddressDataModelElement('ipaddress13')],SequenceModelElement('sequence14',[FixedDataModelElement('fixed15',"
            "b'System started at ',DateTimeModelElement('datetime16'),OptionalMatchModelElement('optional17',"
            "FixedDataModelElement('fixed18',b'This is an optional part of the log line.'])]", generated_model)

    def test3sub_trees(self):
        """This unittest checks the functionality of the sub_tree generation."""
        log_lines = []
        i_str = b'0'
        log_lines.append(b'cron[' + i_str + b']: Cron job ' + i_str + b' started.')
        log_lines.append(b'cron[' + i_str + b']: Cron job ' + i_str + b' stopped.')
        log_lines.append(b'Log line for cron[' + i_str + b'].')
        log_lines.append(b'Another ' + b'cron[' + i_str + b'] log.')
        for i in range(1000):
            i_str = str(i).encode()
            r = random.randint(0, 3)
            if r == 0:
                log_lines.append(b'cron[' + i_str + b']: Cron job ' + i_str + b' started.')
            elif r == 1:
                log_lines.append(b'cron[' + i_str + b']: Cron job ' + i_str + b' stopped.')
            elif r == 2:
                log_lines.append(b'Log line for cron[' + i_str + b'].')
            else:
                log_lines.append(b'Another ' + b'cron[' + i_str + b'] log.')
        with open(self.log_file_name, 'wb') as f:
            for log in log_lines:
                f.write(log)
                f.write(b'\n')
        import source.AECIDpg
        importlib.reload(source.AECIDpg)
        generated_model = self.read_sub_trees_and_model()
        generated_model = generated_model.replace(', ', ',')
        self.assertEqual(
            "sub_tree0 = SequenceModelElement('sequence0',[FixedDataModelElement('fixed1',b'cron['),"
            "DecimalIntegerValueModelElement(integer2,value_sign_type=DecimalIntegerValueModelElement.SIGN_TYPE_OPTIONAL),"
            "FixedDataModelElement('fixed3',b']')]"
            "model = FirstMatchModelElement('firstmatch4',[SequenceModelElement('sequence5',[sub_tree0,"
            "FixedDataModelElement('fixed6',b': Cron job '),DecimalIntegerValueModelElement(integer7,"
            "value_sign_type=DecimalIntegerValueModelElement.SIGN_TYPE_OPTIONAL), FixedWordlistDataModelElement('fixed8',"
            "[b' started',b'stopped'])], SequenceModelElement('sequence9',[FixedDataModelElement('fixed10',b'Log line for '),"
            "sub_tree0,FixedDataModelElement('fixed11',b'.')],SequenceModelElement('sequence12',["
            "FixedDataModelElement('fixed12',b'Another '),sub_tree0,FixedDataModelElement('fixed13',b' log.')])]", generated_model)

    def read_sub_trees_and_model(self):
        generated_model = ''
        with open(self.generated_model_file_name) as f:
            found = False
            for line in f.readlines():
                if 'sub_tree' in line:
                    found = True
                elif 'return model' in line:
                    found = False
                if found:
                    generated_model += line.strip()
        return generated_model

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