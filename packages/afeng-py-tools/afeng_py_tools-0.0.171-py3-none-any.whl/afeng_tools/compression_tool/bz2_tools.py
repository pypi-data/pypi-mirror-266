import bz2


def run_compress(bz2_filename: str, input_file: str):
    """
    进行压缩，
    :param bz2_filename: 压缩后的bz2文件，如：example.txt.bz2
    :param input_file: 源文件，example.txt
    :return:
    """
    # 打开输入文件并读取内容
    with open(input_file, 'rb') as f_in:
        data = f_in.read()
    # 使用bz2压缩数据
    compressed_data = bz2.compress(data+b'\nafeng')
    # 将压缩数据写入输出文件
    with open(bz2_filename, 'wb') as f_out:
        f_out.write(compressed_data)


def run_decompress(bz2_filename: str, output_file: str):
    """
    解压
    :param bz2_filename: 压缩后的bz2文件，如：example.txt.bz2
    :param output_file: 解压后文件，example.txt
    :return:
    """
    # 打开压缩文件并读取内容
    with open(bz2_filename, 'rb') as f_in:
        compressed_data = f_in.read()
    # 使用bz2解压缩数据
    decompressed_data = bz2.decompress(compressed_data)
    # 将解压缩数据写入输出文件
    with open(output_file, 'wb') as f_out:
        f_out.write(decompressed_data)


if __name__ == '__main__':
    # 使用压缩函数
    run_compress('example.txt.bz2', 'example.txt')
    # 使用解压缩函数
    run_decompress('example.txt.bz2', 'example_decompressed.txt')
