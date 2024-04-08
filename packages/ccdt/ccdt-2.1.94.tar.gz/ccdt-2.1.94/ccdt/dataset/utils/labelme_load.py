# 计算机登录用户: jk
# 系统日期: 2023/5/17 9:55
# 项目名称: async_ccdt
# 开发者: zhanyong
# import aiofiles
import asyncio
import os
from pathlib import Path
import hashlib
import json
from tqdm import tqdm
from PIL import Image
from typing import List, Optional, Union
import aiofiles
from concurrent.futures import ThreadPoolExecutor
from tqdm.asyncio import tqdm_asyncio  # 引入 tqdm 的异步版本
import shutil
from pypinyin import pinyin, Style
import zipfile


# from googletrans import Translator


class LabelmeLoad(object):
    """
    利用asyncio模块提供的异步API，实现了异步读取文件路径、异步计算文件MD5值、异步加载JSON文件内容和处理文件的功能，并利用异步并发的特性，提高了计算速度。同时也采用了缓存技术，避免了计算重复的操作。
    """

    def __init__(self, *args, **kwargs):
        self.parameter = args[0]
        self.type_args = args[1]
        self.group_error_path = ''
        self.out_of_bounds_path = ''
        self.error_path = ''
        self.dirs = list()
        # 线程池大小以当前计算机CPU逻辑核心数为准
        thread_pool_size = os.cpu_count() or 1
        self._executor = ThreadPoolExecutor(max_workers=thread_pool_size)
        # self.max_concurrency = max_concurrency = 5
        # 一个BoundedSemaphore信号量来限制并发度，即最大并发量。这可以避免对文件系统造成过大的并发读写负荷，从而提高程序的健壮性。
        # self.semaphore = asyncio.BoundedSemaphore(max_concurrency)

    async def read_directory(self, root_dir: str) -> List[str]:
        """
        异步并发读取目录下的所有图像文件路径，排除json文件
        """
        # file_paths = []
        # for entry in os.scandir(root_dir):
        #     if entry.is_dir():
        #         if entry.path.endswith('01.labelme'):  # 忽略以 01.labelme结尾的目录
        #             continue
        #         sub_paths = await self.read_directory(entry.path)
        #         file_paths.extend(sub_paths)
        #     else:
        #         file_paths.append(entry.path)
        # return file_paths
        file_paths = []
        for entry in os.scandir(root_dir):
            if entry.is_file() and entry.name.endswith(tuple(self.parameter.file_formats)):
                file_paths.append(entry.path)
            elif entry.is_dir() and not entry.name.endswith('01.labelme'):  # endswith检查字符串结尾的方法
                sub_paths = await self.read_directory(entry.path)
                file_paths.extend(sub_paths)
        return file_paths

    async def creat_directory(self, root_dir: str) -> List[str]:
        """
        获取json和图像路径
        @param root_dir:
        @return:
        """
        valid_extensions = ['.jpg', '.jpeg', '.png', '.JPEG', '.JPG', '.PNG', '.webp', '.json']
        # valid_extensions = ['.jpg', '.jpeg', '.png', '.JPEG', '.JPG', '.PNG', '.webp']
        file_all_paths = []
        for entry in os.scandir(root_dir):
            if entry.is_file() and entry.name.endswith(tuple(valid_extensions)):
                file_all_paths.append(entry.path)
            elif entry.is_dir():  # endswith检查字符串结尾的方法
                sub_paths = await self.creat_directory(entry.path)
                file_all_paths.extend(sub_paths)
        return file_all_paths

    def linshi_directory(self, root_dir: str) -> List[str]:
        ok_path = list()
        for root, dirs, files in tqdm(os.walk(root_dir, topdown=True)):
            print(root)
            if root.count('00.images') == 2 or root.count('01.labelme') == 1:  # 设计规则，根据00.images目录，做唯一判断
                # if path_name not in file_path:
                if not os.listdir(root):  # 判断目录是否为空，如果目录下不存在文件就删除目录
                    os.rmdir(root)
                    # ok_path.append(root)
            # for file in files:
            #     path_name = os.path.join(root, file).replace('\\', '/')
            #     obj_path = Path(file)  # 初始化路径对象为对象
            #     if obj_path.suffix in self.parameter.file_formats:
            #         # 所有labelme数据集存放规则为：图像必须存放在00.images目录中，图像对应的json文件必须存放在01.labelme中

        # file_all_paths = []
        # ok_path = list()
        # # visited_dirs = set()  # 存储已访问的目录名称
        # for entry in os.scandir(root_dir):
        #     # if entry.is_file() and entry.name.endswith(tuple(valid_extensions)):
        #     #     file_all_paths.append(entry.path)
        #     if entry.is_dir():
        #         # if "00.images" in entry.path or "01.labelme" in entry.path:
        #         print(entry.path)
        # ok_path.append(entry.path)
        # if entry.path not in file_all_paths:
        #     file_all_paths.append(entry.path)
        # if "00.images" not in entry.name:  # 检查是否已访问过该目录
        # visited_dirs.add(entry.name)  # 将已访问的目录添加到集合中
        # sub_paths = await self.linshi_directory(entry.path)
        # print(sub_paths)
        # file_all_paths.extend(sub_paths)
        # file_all_paths.extend(sub_paths)
        return ok_path

    @staticmethod
    def has_duplicate_folder_name(path, folder_name):
        folders = path.split('\\')  # 以'\\'拆分路径名
        count = 0

        for folder in folders:
            if folder == folder_name:
                count += 1
                if count >= 2:
                    return True
        return False

    @staticmethod
    async def calculate_file_md5(file_path: str) -> str:
        """
        functools.lru_cache装饰器对文件的MD5值进行了缓存，暂时没有用
        采用最近最少使用的缓存策略，最多缓存128个不同的文件的MD5值
        这样可以大大减少重复计算MD5值的次数，节约计算资源，提高程序性能。
        """
        async with aiofiles.open(file_path, 'rb') as f:
            hasher = hashlib.md5()
            buf = await f.read(8192)
            while buf:
                hasher.update(buf)
                buf = await f.read(8192)
            return hasher.hexdigest()

    @staticmethod
    async def read_file(file_path: str) -> Optional[bytes]:
        """
        异步读取单个文件的内容
        Optional 类型用于标注一个变量的值或返回值可能为空（None）的情况。
        """
        if not os.path.isfile(file_path):
            print(f"Error: {file_path} is not a file!")
        async with aiofiles.open(file_path, "rb") as f:
            content = await f.read()
        return content

    async def calculate_file_md5_async(self, file_path: str) -> str:
        """
        在线程池中异步计算文件的MD5值
        使用了线程池执行 MD5 值计算的任务，从而充分利用了 CPU 的多核能力，可以更快地完成计算
        """
        content = await self.read_file(file_path)
        if content is None:
            print(f'图像文件内容为空，请核对该文件路径{file_path}')
            exit()
        # md5_value = await asyncio.get_running_loop().run_in_executor(self._executor, hashlib.md5, content)
        # return md5_value.hexdigest()
        # 修改MD5算法，使用SHA3-512算法，碰撞抵抗性，提供足够的安全性
        sha3_512_value = await asyncio.get_running_loop().run_in_executor(self._executor, self.calculate_sha3_512, content)
        return sha3_512_value

    @staticmethod
    def calculate_sha3_512(data: bytes) -> str:
        sha3_512_hash = hashlib.sha3_512(data)
        return sha3_512_hash.hexdigest()

    @staticmethod
    async def load_labelme(data_path: dict) -> dict:
        """
        异步加载json文件内容
        """
        # 组合加载json文件的路径
        labelme_path = os.path.join(data_path['original_json_path'])
        # print(labelme_path)
        try:
            async with aiofiles.open(labelme_path, 'r', encoding='UTF-8') as labelme_fp:
                content = await labelme_fp.read()
                data_path['labelme_info'] = json.loads(content)
                if data_path['labelme_info']['imageData'] is not None:
                    data_path['labelme_info']['imageData'] = None
                if not data_path['labelme_info']['shapes']:
                    data_path['background'] = False
        except Exception as e:  # 这里发现一个bug，自己根据图像封装的json文件路径，会存在有图像，但并没有json的情况，这样自己封装的json文件路径是找不到的，需要跳过，针对修改MD5值和相对图像路径需要跳过
            # 如果没有json文件，读取就跳过，并设置为背景
            if 'No such file or directory' in e.args:
                data_path['background'] = False
                data_path['labelme_file'] = None
                # return#突然想到这里可以不用改变，在具体实现的时候修改逻辑。
            else:  # 如果是其它情况错误（内容为空、格式错误），就删除json文件并打印错误信息
                print(e)
                print(labelme_path)
                # os.remove(labelme_path)
            data_path['background'] = False
        return data_path

    async def process_file(self, file_path: str, root_dir: str) -> Union[dict, str]:  # 返回两种类型之一，要么是一个字典（dict），要么是一个字符串（str）。
        """
        异步处理文件，返回封装后的数据结构
        针对一次性加载许多数据到内存导致，内存超载问题，方案如下。
        1、分批处理：将文件分成小批量，逐批处理。您可以将文件分为几个子集，然后逐一处理每个子集。这可以减少内存使用，并允许您逐步完成任务。
        2、使用数据库：将文件数据导入数据库，然后使用数据库查询来处理数据。数据库可以优化大规模数据的存储和检索。（最优推荐）
        """
        obj_path = Path(file_path)
        if obj_path.suffix in self.parameter.file_formats:
            # 设计规则，根据图片文件查找json文件，同时根据约定的目录规则封装labelme数据集
            if file_path.count('00.images') == 1 or self.parameter.output_format == 'voc' or self.parameter.output_format == 'sys':
                # relative_path = os.path.join('..', obj_path.parent.name, obj_path.name)
                relative_path = Path('..', obj_path.parent.name, obj_path.name)
                # image_dir = str(obj_path.parent).replace('\\', '/').replace(root_dir, '').strip('\\/')
                image_dir = obj_path.parent.relative_to(root_dir)
                labelme_dir = Path(image_dir.parent, '01.labelme')
                # labelme_dir = os.path.join(image_dir.replace('00.images', '').strip('\\/'), '01.labelme')
                labelme_file = obj_path.stem + '.json'
                json_path = None
                output_dir = Path(self.parameter.output_dir)
                if self.parameter.output_dir:
                    # 打印的时候不需要用到，非打印功能，都会用到
                    json_path = Path(self.parameter.output_dir, labelme_dir, labelme_file)
                original_json_path = Path(root_dir, labelme_dir, labelme_file)
                md5_value = await self.calculate_file_md5_async(file_path)  # 如果不是图像，这里获取MD5值是无法获取的，会直接跳转，存在未知图像后缀格式数据的逻辑
                if self.parameter.output_dir:  # 如果有输出路径，则自定义错误输出目录
                    self.group_error_path = Path(self.parameter.output_dir, 'group_error_path')
                    self.out_of_bounds_path = Path(self.parameter.output_dir, 'out_of_bounds_path')
                    self.error_path = Path(self.parameter.output_dir, 'error_path')
                image = Image.open(file_path)
                # image, check = self.is_valid_image(file_path)  # 暂时不用
                data_path = dict(image_dir=image_dir,  # 封装图像目录相对路径，方便后期路径重组及拼接
                                 image_file=obj_path.name,  # 封装图像文件名称
                                 image_width=image.width,  # 封装图像宽度
                                 image_height=image.height,  # 封装图像高度
                                 labelme_dir=labelme_dir,  # 封装json文件相对目录
                                 labelme_file=labelme_file,  # 封装json文件名称
                                 input_dir=root_dir,  # 封装输入路径目录
                                 output_dir=output_dir,  # 封装输出路径目录
                                 group_error_path=self.group_error_path,  # 标注分组出错路径
                                 out_of_bounds_path=self.out_of_bounds_path,  # 标注超出图像边界错误路径
                                 error_path=self.error_path,  # 错误数据存放总目录，不分错误类别
                                 http_url=self.parameter.http_url,  # 封装http对象存储服务访问服务地址
                                 point_number=self.parameter.point_number,
                                 # 封装数据处理类型，包含base_labelme基类和coco基类
                                 data_type=self.type_args[0].get('type'),
                                 labelme_info=None,  # 封装一张图像标注属性信息
                                 background=True,  # 封装一张图像属于负样本还是正样本，默认为True，正样本，有标注
                                 full_path=obj_path,  # 封装一张图像绝对路径
                                 json_path=json_path,  # 封装一张图像对应json文件绝对路径，用于输出时写文件的路径使用
                                 original_json_path=original_json_path,  # 封装原始json文件绝对路径
                                 md5_value=md5_value,  # 封装一张图像MD5值，用于唯一性判断
                                 relative_path=relative_path,
                                 # check=check,  # 图像校验结果记录，true为合格图像，false为不合格图像
                                 # 封装图像使用标注工具读取相对路径，格式为：..\\00.images\\000000000419.jpg
                                 only_annotation=False, )  # 封装是图像还是处理图像对应标注内容的判断条件，默认图片和注释文件一起处理
                labelme_info = await self.load_labelme(data_path)  # 异步加载json文件
                return labelme_info
            else:
                # if self.parameter.function == 'change':  # 如果功能属于，系统输出结果，转labelme可用格式，直接追加图像路径，通过图像路径找到json路径，读取内容，转换格式
                #     return file_path
                # else:
                print(f'文件夹目录不符合约定标准，请检查{file_path}')
        else:
            print(f'存在未知图像后缀格式数据{file_path}')

    async def recursive_walk(self, root_dir: str, args) -> List[str]:  # 增加函数注解，函数的返回值类型被指定为List[dict]，表示返回值是一个字典列表。
        """
        异步非阻塞并发遍历多级目录
        """
        all_images_file_path = []

        print("异步读取文件路径完成")
        # tasks = [self.process_file(file_path, root_dir) for file_path in file_paths]  # 列表推导式处理文件异步任务列表，与下面的三行代码区别不大
        if args == "create_dir" or args == "move":
            file_all_paths = await self.creat_directory(root_dir)  # 异步读取文件路径,包含图像和json路径
            # file_all_paths = self.linshi_directory(root_dir)  # 临时删除目录方法
            return file_all_paths
        else:
            file_paths = await self.read_directory(root_dir)  # 异步读取文件路径，只获取图像路径
            semaphore = asyncio.Semaphore(80000)  # 限制并发数为80000，根据实际情况调整
            tasks = [self.process_file_with_semaphore(file_path, root_dir, semaphore) for file_path in tqdm(file_paths)]
            # tasks = list()
            print("异步封装数据开始")
            # for file_path in tqdm(file_paths):
            #     # 使用 ensure_future() 函数能够确保协程一定被封装成任务对象，即使协程返回的是普通值而不是协程对象，该值也会被封装为一个 Future 对象，成为可调度的任务。
            #     tasks.append(asyncio.ensure_future(self.process_file(file_path, root_dir)))
            # 使用 asyncio.gather() 函数同时运行多个异步任务
            results = await asyncio.gather(*tasks)
            # 使用 tqdm.asyncio.tqdm() 上下文管理器将异步任务的执行过程打印到进度条中
            with tqdm_asyncio(total=len(tasks), desc="读取文件数据并封装为新的数据结构进度条", unit="file") as progress_bar:
                for result in results:
                    if result is not None:
                        all_images_file_path.append(result)
                    progress_bar.update(1)
            return all_images_file_path

    async def process_file_with_semaphore(self, file_path: str, root_dir: str, semaphore: asyncio.Semaphore) -> Union[dict, str]:
        async with semaphore:
            return await self.process_file(file_path, root_dir)
        # tasks = [self.process_file(file_path, root_dir) for file_path in
        #          file_paths]  # 处理文件异步任务列表
        # results = await asyncio.gather(*tasks)  # 并发处理文件
        # # 把并发处理的字典元素，追加到列表中
        # for result in tqdm(results):
        #     if result is not None:
        #         all_images_file_path.append(result)
        # return all_images_file_path

    def compress_labelme(self):
        """
        封装压缩对象为字典，注意只对输入目录遍历一次，如果输入目录不对，封装结果就会出错
        :return:
        """
        print(f'封装压缩对象')
        for root, dirs, files in tqdm(os.walk(self.type_args[0].get('input_dir'), topdown=True)):
            zip_data = {}
            for directory in dirs:
                rebuild_input_dir = os.path.join(self.type_args[0].get('input_dir'), directory)
                zipfile_obj = os.path.join(self.parameter.output_dir, directory + '.zip')
                zip_data.update({rebuild_input_dir: zipfile_obj})
            return zip_data

    @staticmethod
    def make_compress(zip_package):
        """
        针对封装好的压缩目录进行迭代写入压缩对象包中
        该算法可以跨平台解压
        :param zip_package:
        """
        print(f'开始压缩')
        for zip_key, zip_value in tqdm(zip_package.items()):
            # zip_value：压缩包名称路径
            os.makedirs(os.path.dirname(zip_value), exist_ok=True)
            with zipfile.ZipFile(zip_value, 'w', zipfile.ZIP_DEFLATED, allowZip64=True) as zip:  # 创建一个压缩文件对象
                for root, dirs, files in os.walk(zip_key):  # 递归遍历写入压缩文件到指定压缩文件对象中
                    for file in files:
                        file_path = os.path.join(root, file)
                        relative_path = os.path.join(os.path.basename(zip_key), os.path.relpath(file_path, zip_key))
                        # file_path：压缩文件绝对路径，relative_path：压缩文件相对路径，相对于压缩目录
                        zip.write(file_path, relative_path)

    def hanzi_to_pinyin(self):
        """
        汉字转拼音功能实现
        """
        file_path = list()
        for root, dirs, files in tqdm(os.walk(self.type_args[0].get('input_dir'), topdown=True)):
            for file in files:
                path_name = os.path.join(root, file).replace('\\', '/')
                obj_path = Path(file)  # 初始化路径对象为对象
                if obj_path.suffix in self.parameter.file_formats:
                    # 所有labelme数据集存放规则为：图像必须存放在00.images目录中，图像对应的json文件必须存放在01.labelme中
                    if root.count('00.images') == 1:  # 设计规则，根据00.images目录，做唯一判断
                        if path_name not in file_path:
                            file_path.append(path_name)
        # 重命名路径
        print(f'重命名中文路径为英文开始')
        for rename_dir in tqdm(file_path):
            obj_path = Path(rename_dir)  # 初始化路径对象为对象
            input_dir = self.type_args[0].get('input_dir').replace('\\', '/')
            replace_path = str(obj_path.parent).replace('\\', '/')
            relateve_path = replace_path.replace(input_dir, '').strip('\\/')
            rebuild_output_dir = os.path.join(self.parameter.output_dir, relateve_path)
            rebuild_new_dir = self.convert_path_to_pinyin(rebuild_output_dir)
            labelme_dir = os.path.join(os.path.dirname(rebuild_new_dir), '01.labelme')
            json_file_name = obj_path.stem + '.json'
            src_json_file_path = os.path.join(obj_path.parent.parent, '01.labelme', json_file_name)
            # 创建输出目录
            os.makedirs(labelme_dir, exist_ok=True)
            os.makedirs(rebuild_new_dir, exist_ok=True)
            try:
                shutil.copy(rename_dir, rebuild_new_dir)
                shutil.copy(src_json_file_path, labelme_dir)
            except Exception as e:
                print(f"拷贝 {rename_dir} 失败: {e}")

    @staticmethod
    def convert_path_to_pinyin(path):
        """
        将给定路径中的汉字转换为拼音。
        path: 需要转换的路径。
        """
        # 获取路径的父目录和文件名
        parent_path, filename = os.path.split(path)
        # 将路径中的汉字转换为拼音并拼接成新的路径
        pinyin_list = pinyin(parent_path, style=Style.NORMAL)
        pinyin_path = ''.join([py[0] for py in pinyin_list])  # 提取每个汉字的首字母拼接成新的路径
        new_path = os.path.join(pinyin_path, filename)
        return new_path

    @classmethod
    def get_videos_path(cls, root_dir, file_formats):
        """
        视频帧提取组合路径
        :param root_dir:
        :param file_formats:
        :return:
        """
        file_path_name = list()  # 文件路径
        for root, dirs, files in os.walk(root_dir, topdown=True):
            dirs.sort()
            files.sort()
            # 遍历文件名称列表
            for file in files:
                # 获取文件后缀
                file_suffix = os.path.splitext(file)[-1]
                # 如果读取的文件后缀，在指定的后缀列表中，则返回真继续往下执行
                if file_suffix in file_formats:
                    # 如果文件在文件列表中，则返回真继续往下执行
                    file_path_name.append(os.path.join(root, file))
        return file_path_name

    @staticmethod
    def get_txt_path(root_dir):
        file_path_name = list()  # 文件路径
        for root, dirs, files in os.walk(root_dir, topdown=True):
            dirs.sort()
            files.sort()
            # 遍历文件名称列表
            for file in files:
                txt_dict = dict()  # 定义字典，存储key为关键判断值，value为路径
                obj_path = Path(file)
                key = obj_path.stem.split("_")[0]
                value = os.path.join(root, file)
                txt_dict[key] = value
                # 如果读取的文件后缀，在指定的后缀列表中，则返回真继续往下执行
                file_path_name.append(txt_dict)
        return file_path_name

    def get_english_name(self):
        file_name = list()
        for root, dirs, files in tqdm(os.walk(self.type_args[0].get('input_dir'), topdown=True)):
            for file in files:
                path_name = os.path.join(root, file).replace('\\', '/')
                obj_path = Path(file)  # 初始化路径对象为对象
                if obj_path.suffix in self.parameter.file_formats:
                    # 所有labelme数据集存放规则为：图像必须存放在00.images目录中，图像对应的json文件必须存放在01.labelme中
                    if root.count('00.images') == 1:  # 设计规则，根据00.images目录，做唯一判断
                        if path_name not in file_name:
                            file_name.append(path_name)
        print(file_name)

    @staticmethod
    def is_valid_image(file_path, check=True):
        """
        验证图像格式及图像通道
        @param check: 默认为合格图像
        @param file_path:
        @return:
        """
        try:
            image = Image.open(file_path)
            # 验证图像格式是否为TIFF,# 验证图像是否为RGB格式
            if image.format == "TIFF" or image.mode == "RGB":
                print("图像校验存在问题" + file_path)
                return image, False  # 代表不符合标准的图像
            else:
                return image, check  # 代表正常符合标准的图像
        except Exception as e:
            print(e)
            print("图像校验存在未知情况问题" + file_path)
            # 捕获任何异常，包括文件格式不正确或文件损坏

    def check_images_format(self):
        """
        找出图像格式后缀
        """
        other_format = list()
        for root, dirs, files in tqdm(os.walk(self.type_args[0].get('input_dir'), topdown=True)):
            for file in files:
                path_name = os.path.join(root, file).replace('\\', '/')
                obj_path = Path(file)  # 初始化路径对象为对象
                if obj_path.suffix not in self.parameter.file_formats and obj_path.suffix != '.json':
                    other_format.append(obj_path.suffix)
                    print(path_name)
        print(list(set(other_format)))
