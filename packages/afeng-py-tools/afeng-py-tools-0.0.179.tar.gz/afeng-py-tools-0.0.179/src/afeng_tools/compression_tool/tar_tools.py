import tarfile


def run_tar(tar_file: str, input_file_list: list[tuple[str, str]]):
    """
    进行tar操作
    :param tar_file: 如：example.tar.gz
    :param input_file_list: 如：[('VPN虚拟专用网安全实践教程.pdf', 'output/191662_VPN虚拟专用网安全实践教程.pdf')]
    :return:
    """
    with tarfile.open(tar_file, 'w:gz') as tar:
        for tmp_name, tmp_file in input_file_list:
            # 使用add方法将目录添加到tar文件中，arcname参数指定了归档中的名称
            tar.add(tmp_file, arcname=tmp_name)


def run_un_tar(tar_file: str, output_dir: str):
    """
    解压tar文件到目录
    :param tar_file: 如：example.tar.gz
    :param output_dir: 解压到的目录, 如：output/example
    :return:
    """
    with tarfile.open(tar_file, 'r') as tar:
        tar.extractall(path=output_dir)


if __name__ == '__main__':
    run_tar('output/example.tar.gz',
            input_file_list=[('example.pdf', 'output/example.pdf')])
    run_un_tar('output/example.tar.gz', output_dir='output2/example')