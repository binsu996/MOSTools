import streamlit as st
import fire
from pathlib import Path
import numpy as np
from dataclasses import dataclass, field, asdict
from typing import List, Tuple
import pandas as pd
from uuid import uuid4


@dataclass
class MOSSetting:
    gt_audio: List[List[str]] = field(default_factory=list)
    eval_audio: List[List[Tuple[str, str]]] = field(default_factory=list)

    def add_gt_audio(self, folder, wav_format=".mp3"):
        item = []
        for filename in Path(folder).glob(f"*{wav_format}"):
            item.append(str(filename))
        self.gt_audio.append(item)

    def add_eval_audio(self, expnames, folders, wav_format=".mp3"):
        item = []
        for expname, folder in zip(expnames, folders):
            for filename in Path(folder).glob(f"*{wav_format}"):
                item.append((str(filename), expname))
        self.eval_audio.append(item)

    def __len__(self):
        return len(self.gt_audio)

    def __getitem__(self, idx):
        if idx > len(self.gt_audio):
            raise StopIteration
        return self.gt_audio[idx], self.eval_audio[idx]


@dataclass
class MOSResult:
    filename: List = field(default_factory=list)
    expname: List = field(default_factory=list)
    score: List = field(default_factory=list)
    username: List = field(default_factory=list)

    def add_item(self, filename, expname, score, username):
        self.filename.append(filename)
        self.expname.append(expname)
        self.score.append(score)
        self.username.append(username)

    def check_valid(self):
        if None in self.score or "" in self.username:
            return False
        else:
            return True


def render(mos_setting: MOSSetting, save_path: str):
    mos_result = MOSResult()
    st.set_page_config(page_title="MOS 评测")
    with st.form("MOS"):

        username = st.text_input("您的名字", placeholder="输入您的名字,必须由英文字母构成")

        for gt_audio, eval_audio in mos_setting:
            col_gt, col_eval = st.columns(2)
            with col_gt:
                st.subheader("提示音频")
            with col_eval:
                st.subheader("生成音频")

            np.random.shuffle(eval_audio)

            with col_gt:
                for filename in gt_audio:
                    st.audio(filename)
            with col_eval:
                for filename, expname in eval_audio:
                    st.audio(filename)
                    c = st.radio(
                        "音色相似度",
                        [1, 2, 3, 4, 5],
                        horizontal=True,
                        index=None,
                        key=filename
                    )
                    mos_result.add_item(filename, expname, c, username)

        click = st.form_submit_button("提交结果")

        if click:
            if mos_result.check_valid():
                save_path = Path(save_path)
                save_path.mkdir(exist_ok=True, parents=True)
                save_file = save_path/f"{username}.csv"
                pd.DataFrame(asdict(mos_result)).to_csv(str(save_file))
                st.write(f"已经收到您的反馈，谢谢！")
            else:
                st.write(f"请检查表单，确保每一项都有被评价，且用户名有被正确填写")


def run_mos(save_path, prompt_dir, *exps, wav_format=".mp3"):
    exps = [Path(x) for x in exps]
    expnames = [x.name for x in exps]

    mos_setting = MOSSetting()
    spk_folders = list(Path(prompt_dir).glob("*"))

    for spk_folder in spk_folders:
        spk = spk_folder.name
        mos_setting.add_gt_audio(spk_folder)
        exp_folders = [x/spk for x in exps]
        mos_setting.add_eval_audio(expnames, exp_folders)

    render(mos_setting, save_path)


if __name__ == "__main__":
    fire.Fire(run_mos)
