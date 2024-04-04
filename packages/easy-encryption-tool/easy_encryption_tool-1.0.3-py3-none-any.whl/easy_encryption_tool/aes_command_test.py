import base64
import random
import unittest

from click.testing import CliRunner

import aes_command
import random_str


class AESTestCase(unittest.TestCase):

    def test_generate_key(self):
        key_set = set()
        for i in range(0, 10):
            key = aes_command.generate_random_key()
            print(key)
            self.assertTrue(len(key) == aes_command.aes_key_len_256)
            key_set.add(key)
        self.assertTrue(len(key_set), 10)

    def test_generate_iv_nonce(self):
        iv_set = set()
        for i in range(0, 10):
            iv = aes_command.generate_random_iv_nonce(aes_command.aes_cbc_mode)
            print(iv)
            iv_set.add(iv)
            self.assertTrue(len(iv) == aes_command.aes_iv_len_128)

        nonce_set = set()
        for i in range(0, 10):
            nonce = aes_command.generate_random_iv_nonce(aes_command.aes_gcm_mode)
            print(nonce)
            nonce_set.add(nonce)
            self.assertTrue(len(nonce) == aes_command.aes_nonce_len_128)

    def test_process_key_iv(self):
        key, iv = aes_command.process_key_iv(True, 'abc1234', 'abc', aes_command.aes_cbc_mode)
        print('key:', key, '\niv:', iv)
        self.assertTrue(len(key), aes_command.aes_key_len_256)
        self.assertTrue(len(iv), aes_command.aes_iv_len_128)

        key, nonce = aes_command.process_key_iv(True, 'abc1234', 'abc', aes_command.aes_gcm_mode)
        print('key:', key, '\nnonce:', nonce)
        self.assertTrue(len(key), aes_command.aes_key_len_256)
        self.assertTrue(len(nonce), aes_command.aes_nonce_len_128)

        key, iv = aes_command.process_key_iv(False, 'abc1234', 'abc', aes_command.aes_cbc_mode)
        print('key:', key, '\niv:', iv)
        self.assertTrue(len(key), aes_command.aes_key_len_256)
        self.assertTrue(len(iv), aes_command.aes_iv_len_128)
        self.assertTrue(key.startswith('abc1234'))
        self.assertTrue(iv.startswith('abc'))

        key, nonce = aes_command.process_key_iv(False, 'abc1234', 'abc', aes_command.aes_gcm_mode)
        print('key:', key, '\nnonce:', nonce)
        self.assertTrue(len(key), aes_command.aes_key_len_256)
        self.assertTrue(len(nonce), aes_command.aes_nonce_len_128)
        self.assertTrue(key.startswith('abc1234'))
        self.assertTrue(iv.startswith('abc'))

        key, iv = aes_command.process_key_iv(False, 'k' * 33, 'v' * 17, aes_command.aes_cbc_mode)
        print('key:', key, '\niv:', iv)
        self.assertTrue(len(key), aes_command.aes_key_len_256)
        self.assertTrue(len(iv), aes_command.aes_iv_len_128)
        self.assertTrue(key == 'k' * aes_command.aes_key_len_256)
        self.assertTrue(iv == 'v' * aes_command.aes_iv_len_128)

        key, nonce = aes_command.process_key_iv(False, 'k' * 33, 'v' * 17, aes_command.aes_gcm_mode)
        print('key:', key, '\nnonce:', nonce)
        self.assertTrue(len(key), aes_command.aes_key_len_256)
        self.assertTrue(len(nonce), aes_command.aes_nonce_len_128)
        self.assertTrue(key == 'k' * aes_command.aes_key_len_256)
        self.assertTrue(nonce == 'v' * aes_command.aes_nonce_len_128)

    def test_padding_data(self):
        ret = aes_command.padding_data(b'hello')
        data = aes_command.remove_padding_data(ret)
        self.assertTrue(data == b'hello')

        ret = aes_command.padding_data(b'')
        print(ret == bytes([0x10 for _ in range(0, 16)]))

        data = aes_command.remove_padding_data(b'')
        self.assertTrue(data == b'')

    def test_aes_cbc_encrypt_decrypt(self):
        k = aes_command.generate_random_key()
        v = aes_command.generate_random_iv_nonce(aes_command.aes_cbc_mode)
        enc = aes_command.aes_operator(aes_command.aes_cbc_mode, aes_command.aes_encrypt_action, k.encode('utf-8'),
                                       v.encode('utf-8'), b'')
        original_plain = random_str.generate_random_str(random.randint(17, 27)).encode('utf-8')
        cipher = enc.process_data(aes_command.padding_data(original_plain))
        cipher_final, _ = enc.finalize()
        cipher += cipher_final

        dec = aes_command.aes_operator(aes_command.aes_cbc_mode, aes_command.aes_decrypt_action, k.encode('utf-8'),
                                       v.encode('utf-8'), b'')
        plain = dec.process_data(cipher)
        ret, _ = dec.finalize()
        plain += ret
        plain = aes_command.remove_padding_data(plain)
        self.assertTrue(plain == original_plain)

    def test_aes_cbc_padding(self):
        k = aes_command.generate_random_key()
        v = aes_command.generate_random_iv_nonce(aes_command.aes_cbc_mode)
        enc = aes_command.aes_operator(aes_command.aes_cbc_mode, aes_command.aes_encrypt_action, k.encode('utf-8'),
                                       v.encode('utf-8'), b'')
        # 当最后一个 block 刚好为 aes block 大小时也需要 padding 一下，否则解密时无法判断是否需要去除 padding
        original_plain = random_str.generate_random_str(16).encode('utf-8')
        cipher = enc.process_data(aes_command.padding_data(original_plain))
        cipher_final, _ = enc.finalize()
        cipher += cipher_final

        dec = aes_command.aes_operator(aes_command.aes_cbc_mode, aes_command.aes_decrypt_action, k.encode('utf-8'),
                                       v.encode('utf-8'), b'')
        plain = dec.process_data(cipher)
        ret, _ = dec.finalize()
        plain += ret
        plain = aes_command.remove_padding_data(plain)
        self.assertTrue(plain == original_plain)

    def test_aes_gcm_encrypt_decrypt(self):
        k = aes_command.generate_random_key()
        v = aes_command.generate_random_iv_nonce(aes_command.aes_gcm_mode)
        enc = aes_command.aes_operator(aes_command.aes_gcm_mode, aes_command.aes_encrypt_action, k.encode('utf-8'),
                                       v.encode('utf-8'), b'')
        original_plain = random_str.generate_random_str(random.randint(17, 27)).encode('utf-8')
        cipher = enc.process_data(aes_command.padding_data(original_plain))
        cipher_final, tags = enc.finalize()
        cipher += cipher_final

        dec = aes_command.aes_operator(aes_command.aes_gcm_mode, aes_command.aes_decrypt_action, k.encode('utf-8'),
                                       v.encode('utf-8'), tags)
        plain = dec.process_data(cipher)
        ret, _ = dec.finalize()
        plain += ret
        plain = aes_command.remove_padding_data(plain)
        self.assertTrue(plain == original_plain)


class AESCommandTestCase(unittest.TestCase):
    def test_mode(self):
        runner = CliRunner()
        result = runner.invoke(cli = aes_command.aes_command, args = ['-m', 'cbc', '-r', '-i', 'hello,world'])
        print(result.output)
        self.assertTrue(result.exit_code == 0)

        result = runner.invoke(cli = aes_command.aes_command, args = ['-m', 'abc', '-r', '-i', 'hello,world'])
        print(result.output, result.exit_code)
        self.assertTrue(result.exit_code != 0)

    def test_action(self):
        runner = CliRunner()
        result = runner.invoke(cli = aes_command.aes_command, args = ['-m', 'cbc', '-r', '-i', 'hello,world', '-a', 'encrypt'])
        print(result.output)
        self.assertTrue(result.exit_code == 0)

        result = runner.invoke(cli = aes_command.aes_command, args = ['-m', 'gcm', '-r', '-i', 'hello,world', '-a', 'abc'])
        print(result.output, result.exit_code)
        self.assertTrue(result.exit_code != 0)

    def test_encrypt_input_data_str(self):
        # 测试输入的是长度正常的字符串明文
        runner = CliRunner()
        result = runner.invoke(cli = aes_command.aes_command, args = ['-m', 'cbc', '-i', 'hello,world', '-a', 'encrypt'])
        print(result.output)
        self.assertTrue(result.exit_code == 0)

        # 测试输入数据过长
        result = runner.invoke(cli = aes_command.aes_command, args = ['-m', 'cbc',
                                                                      '-i', random_str.generate_random_str(1 * 1024 * 1024 + 1),
                                                                      '-a', 'encrypt'])
        print(result.output)
        self.assertTrue(result.exit_code == 0)

        # 测试输入数据过短
        result = runner.invoke(cli = aes_command.aes_command, args = ['-m', 'cbc',
                                                                      '-i', '',
                                                                      '-a', 'encrypt'])
        print(result.output)
        self.assertTrue(result.exit_code == 0)

    def test_encrypt_input_data_base64_str(self):
        """"
        测试输入的是 base64 编码后的字符串明文
        """
        runner = CliRunner()

        # 测试长度正常的 base64 编码数据
        result = runner.invoke(cli = aes_command.aes_command,
                               args = ['-m', 'cbc', '-i', 'PcgHm88aPtUjwVx+SDvMqw==', '-e', '-a', 'encrypt'])
        print(result.output)
        self.assertTrue(result.exit_code == 0)

        # 测试长度正常的 base64 编码数据
        # 解码 "Cg==" 后得到的二进制数据是：0x0A 这对应于 ASCII 中的换行符 (LF, Line Feed)
        result = runner.invoke(cli = aes_command.aes_command,
                               args = ['-m', 'cbc', '-i', 'Cg==', '-e', '-a', 'encrypt'])
        print(result.output)
        self.assertTrue(result.exit_code == 0)

        # 既标记为 base64数据，又标记为文件
        result = runner.invoke(cli = aes_command.aes_command,
                               args = ['-m', 'cbc', '-i', 'Cg==', '-e', '-f', '-a', 'encrypt'])
        print(result.output)
        self.assertTrue(result.exit_code == 0)

        # 测试长度超长的数据
        result = runner.invoke(cli = aes_command.aes_command,
                               args = ['-m', 'cbc', '-i',
                                       base64.b64encode(random_str.generate_random_str(1024 * 1024 + 1).encode('utf-8')).decode(
                                           'utf-8'),
                                       '-e', '-a', 'encrypt'])
        print(result.output)
        self.assertTrue(result.exit_code == 0)

    def test_encrypt_str_to_file(self):
        runner = CliRunner()
        result = runner.invoke(cli = aes_command.aes_command,
                               args = ['-m', 'cbc', '-i', 'hello,world',
                                       '-a', 'encrypt', '-o', './test_data/test_cipher.bin'])
        print(result.output)
        self.assertTrue(result.exit_code == 0)

        result = runner.invoke(cli = aes_command.aes_command,
                               args = ['-m', 'gcm', '-i', 'hello,world',
                                       '-a', 'encrypt', '-o', './test_data/test_cipher.bin'])
        print(result.output)
        self.assertTrue(result.exit_code == 0)

        result = runner.invoke(cli = aes_command.aes_command,
                               args = ['-m', 'cbc', '-i', 'PcgHm88aPtUjwVx+SDvMqw==',
                                       '-e', '-a', 'encrypt',
                                       '-o', './test_data/test_cipher.bin'])
        print(result.output)
        self.assertTrue(result.exit_code == 0)

        result = runner.invoke(cli = aes_command.aes_command,
                               args = ['-m', 'gcm', '-i', 'PcgHm88aPtUjwVx+SDvMqw==',
                                       '-e', '-a', 'encrypt',
                                       '-o', './test_data/test_cipher.bin'])
        print(result.output)
        self.assertTrue(result.exit_code == 0)

    def test_encrypt_file_data_to_file(self):
        runner = CliRunner()
        result = runner.invoke(cli = aes_command.aes_command,
                               args = ['-m', 'cbc', '-i', './test_data/test_plain.txt', '-f',
                                       '-a', 'encrypt', '-o', './test_data/test_cipher_2.bin'])
        print(result.output)
        self.assertTrue(result.exit_code == 0)

        result = runner.invoke(cli = aes_command.aes_command,
                               args = ['-m', 'cbc', '-i', './test_data/test_cipher_2.bin', '-f',
                                       '-a', 'decrypt', '-o', './test_data/test_cipher_2_decrypted.bin'])
        print(result.output)
        self.assertTrue(result.exit_code == 0)

        result = runner.invoke(cli = aes_command.aes_command,
                               args = ['-m', 'gcm', '-i', './test_data/test_plain.txt', '-f',
                                       '-a', 'encrypt', '-o', './test_data/test_cipher_3.bin'])
        print(result.output)
        self.assertTrue(result.exit_code == 0)

        result = runner.invoke(cli = aes_command.aes_command,
                               args = ['-m', 'gcm', '-i', './test_data/test_cipher_3.bin', '-f',
                                       '-a', 'decrypt', '-o', './test_data/test_cipher_3_decrypted.bin',
                                       '-t', 'krJchuyaDRYHnu5tsy8UzA=='])
        print(result.output)
        self.assertTrue(result.exit_code == 0)

    def test_decrypt_valid_str(self):
        runner = CliRunner()
        # cbc 解密
        result = runner.invoke(cli = aes_command.aes_command,
                               args = ['-m', 'cbc', '-i', 'lgLFcgGNsHs1QYrN5SyJlw==', '-e',
                                       '-a', 'decrypt',
                                       '-k', '(^$yjhI16$NmXr99qjpVk^bJ7ZoU2)m4',
                                       '-v', 'xkZ&448)Xn`+K*7e'])
        print(result.output)
        self.assertTrue(result.exit_code == 0)

        # gcm 解密
        result = runner.invoke(cli = aes_command.aes_command,
                               args = ['-m', 'gcm', '-i', 'Ym1MfuuAzCuR+vl+oagoVA==', '-e',
                                       '-a', 'decrypt',
                                       '-k', '1+9cMhK#t6f^w1Bhj1WB&^L5#0hCGBf4',
                                       '-v', 'und19Z&o(%X&',
                                       '-t', 'Ofp8MwUwibrVKmw+2iYBfQ=='])
        print(result.output)
        self.assertTrue(result.exit_code == 0)

    def test_decrypt_invalid_str(self):
        runner = CliRunner()

        # 密文非 base64编码
        result = runner.invoke(cli = aes_command.aes_command,
                               args = ['-m', 'cbc', '-i', '1234567890', '-e',
                                       '-a', 'decrypt',
                                       '-k', '(^$yjhI16$NmXr99qjpVk^bJ7ZoU2)m4',
                                       '-v', 'xkZ&448)Xn`+K*7e'])
        print(result.output)
        self.assertTrue(result.exit_code == 0)

        # 密钥或 iv 不对
        result = runner.invoke(cli = aes_command.aes_command,
                               args = ['-m', 'cbc', '-i', 'lgLFcgGNsHs1QYrN5SyJlw==', '-e',
                                       '-a', 'decrypt'])
        print(result.output)
        self.assertTrue(result.exit_code == 0)

        # 密文不对
        result = runner.invoke(cli = aes_command.aes_command,
                               args = ['-m', 'cbc', '-i', 'aGVsbG8sd29ybGQK', '-e',
                                       '-a', 'decrypt',
                                       '-k', '(^$yjhI16$NmXr99qjpVk^bJ7ZoU2)m4',
                                       '-v', 'xkZ&448)Xn`+K*7e'])
        print(result.output)
        self.assertTrue(result.exit_code == 0)

    def test_decrypt_from_file(self):
        runner = CliRunner()
        result = runner.invoke(cli = aes_command.aes_command,
                               args = ['-m', 'cbc', '-i', './test_data/cbc_valid_cipher.bin', '-f',
                                       '-a', 'decrypt',
                                       '-o', './test_data/test_dec_plain_cbc.bin'])
        print(result.output)
        self.assertTrue(result.exit_code == 0)
        result = runner.invoke(cli = aes_command.aes_command,
                               args = ['-m', 'gcm', '-i', './test_data/gcm_valid_cipher.bin', '-f',
                                       '-a', 'decrypt',
                                       '-o', './test_data/test_dec_plain_gcm.bin',
                                       '-t', '2TzyuRfkeZTjn8nQlePbzg=='])
        print(result.output)
        self.assertTrue(result.exit_code == 0)

    def test_decrypt_invalid_file(self):
        runner = CliRunner()
        result = runner.invoke(cli = aes_command.aes_command,
                               args = ['-m', 'cbc', '-i', './test_data/gcm_valid_cipher.bin', '-f',
                                       '-a', 'decrypt',
                                       '-o', './test_data/test_dec_plain_cbc.bin'])
        print(result.output)
        self.assertTrue(result.exit_code == 0)

        result = runner.invoke(cli = aes_command.aes_command,
                               args = ['-m', 'gcm', '-i', './test_data/cbc_valid_cipher.bin', '-f',
                                       '-a', 'decrypt',
                                       '-o', './test_data/test_dec_plain_gcm.bin',
                                       '-t', '2TzyuRfkeZTjn8nQlePbzg=='])
        print(result.output)
        self.assertTrue(result.exit_code == 0)

        result = runner.invoke(cli = aes_command.aes_command,
                               args = ['-m', 'cbc', '-i', './test_data/invalid_cipher_length.bin', '-f',
                                       '-a', 'decrypt',
                                       '-o', './test_data/test_dec_plain_gcm.bin',
                                       '-t', '2TzyuRfkeZTjn8nQlePbzg=='])
        print(result.output)
        self.assertTrue(result.exit_code == 0)

        result = runner.invoke(cli = aes_command.aes_command,
                               args = ['-m', 'gcm', '-i', './test_data/invalid_cipher_length.bin', '-f',
                                       '-a', 'decrypt',
                                       '-o', './test_data/test_dec_plain_gcm.bin',
                                       '-t', '2TzyuRfkeZTjn8nQlePbzg=='])
        print(result.output)
        self.assertTrue(result.exit_code == 0)


if __name__ == '__main__':
    unittest.main()
