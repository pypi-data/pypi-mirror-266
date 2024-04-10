"""This module implements the Navam's Encryption Technique (NET)"""

def encrypt(path_to_file: str) -> None:
    """Encrypts the file present in the path"""

    bin_str = ''
    with open(path_to_file, 'rb') as file:
        hex_str = file.read()
        for byte in hex_str:
            bin_str += bin(byte).lstrip('0b').zfill(8)
    enc_str = bin_str[0]
    count = 0
    for index, char in enumerate(bin_str):
        count += 1
        if index < len(bin_str)-1:
            if char != bin_str[index+1]:
                seq = bin(count).lstrip('0b')
                for ind, bit in enumerate(seq):
                    enc_str += bit
                    enc_str += '0' if ind < len(seq)-1 else '1'
                count = 0
        else:
            seq = bin(count).lstrip('0b')
            for ind, bit in enumerate(seq):
                enc_str += bit
                enc_str += '0' if ind < len(seq)-1 else '1'
    with open('encrypted.nvm', 'w') as file:
        file.write(enc_str)

def decrypt(path_to_file: str) -> None:
    """Decrypts the file present in the path"""

    with open(path_to_file, 'r') as file:
        enc_str = file.read()
    starts_with = '1' if enc_str.startswith('1') else '0'
    enc_str = enc_str[1:]
    bin_str = ''
    bin_num = ''
    for index in range(0, len(enc_str), 2):
        bin_num += enc_str[index]
        if enc_str[index+1] == '1':
            for _ in range(int(bin_num, 2)):
                bin_str += starts_with
            bin_num = ''
            starts_with = '0' if starts_with=='1' else '1'
    hex_str = ''
    for index in range(0, len(bin_str), 8):
        hex_str += chr(int(bin_str[index:index+8], 2))
    with open('decrypted.nvm', 'wb') as file:
        file.write(hex_str.encode())
