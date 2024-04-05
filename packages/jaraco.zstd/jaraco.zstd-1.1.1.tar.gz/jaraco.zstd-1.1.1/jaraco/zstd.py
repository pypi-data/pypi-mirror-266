import argparse
import pathlib
import tarfile

import zstandard


def build_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-e', '--extract', type=pathlib.Path, required=True, dest='source'
    )
    parser.add_argument('--out-dir', default=pathlib.Path(), type=pathlib.Path)
    return parser


def extract(args):
    with args.source.open('rb') as ifh:
        dctx = zstandard.ZstdDecompressor()
        with dctx.stream_reader(ifh) as reader:
            with tarfile.open(mode="r|", fileobj=reader) as tf:
                tf.extractall(args.out_dir)


def main():
    extract(build_parser().parse_args())


__name__ == '__main__' and main()
