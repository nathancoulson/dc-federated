"""
Simple utility to generate public/private keypair for a worker that
may be sent to the federated learning server for authentication.
"""

import sys
import argparse

from nacl.signing import SigningKey, VerifyKey
from nacl.encoding import HexEncoder
from nacl.exceptions import BadSignatureError

GENERATE_MODE = 'generate'
VERIFY_MODE = 'verify'


def get_args():
    """
    Parse the argument for generating and verifying the key
    """
    # Make parser object
    p = argparse.ArgumentParser(
        description="Utitlity to generate and verify public/private keypair for a worker\n")
    p.set_defaults()
    sub_parsers = p.add_subparsers(help='sub-command help', dest='command')

    parser_gen = sub_parsers.add_parser(GENERATE_MODE,
                                        help="Generate a public/private key-pair "
                                             "for a worker using curve25519.")
    parser_gen.add_argument("--filename",
                            help="The name of the key files. Public key in <filename>.pub, "
                                 "private key without extension.",
                            type=str,
                            required=True)

    parser_ver = sub_parsers.add_parser(VERIFY_MODE,
                                        help="Verify a key-pair previously generated by this tool.")
    parser_ver.add_argument("--filename",
                            help="The name of the private key file. The public key is expected to be "
                                 "in the corresponding .pub file.",
                            type=str,
                            required=True)

    if len(sys.argv) == 1:
        p.print_help()
        return None

    return p.parse_args()


def gen_pair(filename):
    """
    Function to generate a public/private key pair using digital signing.

    Parameters
    ----------

    filename: str
        Name of the files to write the public and private key to.

    Returns
    -------

    SigningKey, VerifyKey:
        The public, private key generated.
    """
    with open(filename, 'w') as f:
        sk = SigningKey.generate()
        hex_seed = sk.encode(encoder=HexEncoder)
        f.write(hex_seed.decode('utf-8'))
        print(f'Wrote private key to {filename}')

    pub_filename = filename + '.pub'
    with open(pub_filename, 'w') as f:
        vk = sk.verify_key
        hex_seed = vk.encode(encoder=HexEncoder)
        f.write(hex_seed.decode('utf-8'))
        print(f'Wrote public key to {pub_filename}')

    return sk, vk


def verify_pair(filename):
    """
    Function to verify a public/private key pair previously generated by this
    tool.

    Parameters
    ----------

    filename: str
        Name of the files to write the public and private key to.
    """
    with open(filename, 'r') as f:
        hex_read = f.read().encode()
        sk_read = SigningKey(hex_read, encoder=HexEncoder)

    pub_filename = filename + '.pub'
    with open(pub_filename, 'r') as f:
        hex_read = f.read().encode()
        vk_read = VerifyKey(hex_read, encoder=HexEncoder)

    phrase_to_sign = b'phrase to sign'
    try:
        signed_phrase = sk_read.sign(phrase_to_sign)
        vk_read.verify(signed_phrase)
    except BadSignatureError as be:
        print(f"Private key in {filename} does not match public key in {pub_filename}.")
        return False

    print(f"Private key in {filename} matches public key in {pub_filename}.")
    return True


def run():
    args = get_args()

    if args is None:
        return
    elif args.command == GENERATE_MODE:
        gen_pair(args.filename)
    elif args.command == VERIFY_MODE:
        verify_pair(args.filename)


if __name__ == '__main__':
    run()