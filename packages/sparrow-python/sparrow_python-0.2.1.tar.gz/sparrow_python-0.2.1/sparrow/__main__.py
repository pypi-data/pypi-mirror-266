from __future__ import annotations

import os
import pretty_errors
import rich
from typing import Literal


class Cli:
    def __init__(self):
        ...

    def deduplicate(self, in_file: str, out_file: str, target_col='data', chunk_size = 200, threshold=None, method:Literal["edit", "rouge", "bleu"]='edit', use_jieba=False):
        if method == "edit":
            from .nlp.deduplicate import EditSimilarity
            simi = EditSimilarity()
            if threshold is None:
                threshold = 0.7
        elif method == "rouge":
            from .nlp.deduplicate import RougeSimilarity
            simi = RougeSimilarity(use_jieba=use_jieba)
            if threshold is None:
                threshold = 0.5
        elif method == "bleu":
            from .nlp.deduplicate import BleuSimilarity
            simi = BleuSimilarity(use_jieba=use_jieba)
            if threshold is None:
                threshold = 0.5
        else:
            raise ValueError(f"method should be one of 'edit', 'rouge', 'bleu', but got {method}")
        simi.load_data(in_file, target_col=target_col)
        simi.deduplicate(chunk_size=chunk_size, save_to_file=out_file, threshold=threshold)

    @staticmethod
    def post(url: str, data: dict, concurrent: int = 10, ):
        import asyncio
        from .api.fetch import run
        asyncio.run(
            run(url=url, data=data, concurrent=concurrent, method="POST")
        )

    @staticmethod
    def get(url, data=None, concurrent=10):
        import asyncio
        from .api.fetch import run
        if data is None:
            data = {}
        asyncio.run(
            run(url=url, data=data, concurrent=concurrent, method="GET")
        )

    @staticmethod
    def timer(dt=0.01):
        from .widgets import timer
        return timer(dt)

    @staticmethod
    def auto_commit(
            repo_path='.',
            remote_repo_name: str | None = None,
            name="K.Y.Bot", email="beidongjiedeguang@gmail.com",
            interval=60
    ):
        from .git.monitor import start_watcher
        start_watcher(repo_path=repo_path, remote_repo_name=remote_repo_name,
                      name=name, email=email,
                      interval=interval)

    @staticmethod
    def install_node(version=16):
        from .cli.script import install_node_with_nvm
        install_node_with_nvm(version=version)

    @staticmethod
    def install_nvim(version='0.9.2'):
        from .cli.script import install_nvim
        install_nvim(version=version)

    @staticmethod
    def uninstall_nvim():
        from .cli.script import uninstall_nvim
        uninstall_nvim()

    @staticmethod
    def save_docker_images(filedir='.', skip_exists=True, use_stream=False):
        kwargs = locals()
        from .docker import save_docker_images
        return save_docker_images(**kwargs)

    @staticmethod
    def load_docker_images(filename_pattern="./*", skip_exists=True):
        kwargs = locals()
        from .docker import load_docker_images
        return load_docker_images(**kwargs)

    @staticmethod
    def docker_gpu_stat():
        from .docker.nvidia_stat import docker_gpu_stat
        return docker_gpu_stat()

    @staticmethod
    def pack(source_path: str, target_path=None, format='gztar'):
        kwargs = locals()
        from .utils.compress import pack
        return pack(**kwargs)

    @staticmethod
    def unpack(filename: str, extract_dir=None, format=None):
        kwargs = locals()
        from .utils.compress import unpack
        return unpack(**kwargs)

    @staticmethod
    def start_server(port=50001, deque_maxlen=None):
        kwargs = locals()
        from .multiprocess import start_server
        return start_server(**kwargs)

    @staticmethod
    def kill(*ports: int, view=False):
        from .multiprocess import kill
        return kill(*ports, view)

    @staticmethod
    def clone(url: str, save_path=None, branch=None, proxy=False):
        kwargs = locals()
        from .cli.git import clone
        return clone(**kwargs)

    @staticmethod
    def get_ip(env="inner"):
        kwargs = locals()
        from .utils.net import get_ip
        return get_ip(**kwargs)

    @staticmethod
    def create(project_name: str, out=None):
        """创建项目
        Parameter
        ---------
        project_name : str
            package name
        out : str | None
            项目生成路径
        """
        if out is None:
            out = project_name
        from .template.scaffold.core import create_project
        return create_project(project_name, out)

    @staticmethod
    def milvus(flag='start'):
        kwargs = locals()
        from .ann import milvus
        return milvus(**kwargs)

    @staticmethod
    def reminder(port=50001):
        import uvicorn
        uvicorn.run(
            app="sparrow.espec.app:app",
            host="0.0.0.0",
            port=port,
            workers=1,
            app_dir="..",
        )

    @staticmethod
    def subtitles(video: str):
        from .subtitles import transcribe, translate, merge_subs_with_video
        origin_srt = transcribe(video)
        translated_srt = translate(origin_srt)
        merge_subs_with_video(video, origin_srt, translated_srt)

    @staticmethod
    def merge_subtitles(srt_en: str, srt_zh: str):
        from .subtitles import merge_subs
        merge_subs(srt_en=srt_en, srt_zh=srt_zh)

    @staticmethod
    def translate_subt(srt_name: str):
        """translate english srt file to chinese srt file"""
        from .subtitles import translate
        translate(subtitles_file=srt_name)

    @staticmethod
    def latexocr():
        os.system("latexocr")

    @staticmethod
    def test_torch():
        from sparrow.experimental import test_torch

    @staticmethod
    def gen_key(rsa_name: str, email='beidongjiedeguang@gmail.com'):
        """
        Generate an SSH key pair for a given RSA name.

        Parameters:
            rsa_name (str): The name to be used for the RSA key pair.
            email (str): The email address to associate with the key pair. Default is 'beidongjiedeguang@gmail.com'.

        Returns:
            None

        """
        from pathlib import Path
        rsa_path = str(Path.home() / '.ssh' / f'id_rsa_{rsa_name}')
        command = f"ssh-keygen -t rsa -C {email} -f {rsa_path}"
        os.system(command)

        with open(rsa_path + '.pub', 'r', encoding='utf8') as f:
            rich.print("pub key:\n")
            print(f.read())

        config_path = str(Path.home() / '.ssh' / 'config')
        rich.print(f"""你可能需要将新添加的key 写入 {config_path}文件中，内容大概是：
# 如果是远程服务器
Host {rsa_name}
  HostName 198.211.51.254
  User root
  Port 22
  IdentityFile {rsa_path}
  
# 或者 git
Host {rsa_name}
  HostName github.com
  User git
  IdentityFile {rsa_path}
  IdentitiesOnly yes
""")


def fire_commands():
    import fire
    fire.Fire(Cli)


def typer_commands():
    import typer
    app = typer.Typer()
    # [app.command()(i) for i in func_list]
    # app()


def main():
    use_fire = 1
    if use_fire:
        fire_commands()
    else:
        # Fixme *形参 传入会出错，参考这里 https://typer.tiangolo.com/tutorial/multiple-values/arguments-with-multiple-values/
        typer_commands()
