"""
GZIP压缩工具
"""
import gzip


def run_compress(input_filename: str, output_filename: str):
    with open(input_filename, 'rb') as f_in:
        with gzip.open(output_filename, 'wb') as f_out:
            f_out.writelines(f_in)


def run_decompress(input_filename: str, output_filename: str):
    with gzip.open(input_filename, 'rb') as f_in:
        with open(output_filename, 'wb') as f_out:
            f_out.writelines(f_in)


if __name__ == '__main__':
    # 压缩
    run_compress('example.txt', 'example.txt.gz')
    # 解压
    run_decompress('example.txt.gz', 'example_decompressed.txt')
