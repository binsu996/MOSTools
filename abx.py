import streamlit as st
import fire
from pathlib import Path
import numpy as np
from dataclasses import dataclass, field
from typing import List
import pandas as pd


@dataclass
class ABXSetting:
    gt_file: List[str] = field(default_factory=list)
    exp_a: str = ""
    a_file: List[str] = field(default_factory=list)
    exp_b: str = ""
    b_file: List[str] = field(default_factory=list)

    def __len__(self):
        return len(self.gt_file)

    def __getitem__(self, idx):
        if idx > len(self.gt_file):
            raise StopIteration
        return self.gt_file[idx], self.a_file[idx], self.b_file[idx]


@dataclass
class ABXResult:
    choices: List[str] = field(default_factory=list)
    swap: List[str] = field(default_factory=list)
    name: List[str] = field(default_factory=list)


def render(abx_setting: ABXSetting):
    abx_result = ABXResult()

    st.set_page_config(page_title="ABX 评测", layout="wide")

    with st.form("ABX"):
        col_gt, col_a, col_b, col_r = st.columns(4)
        with col_gt:
            st.header("提示音频")
        with col_a:
            st.header("生成音频0")
        with col_b:
            st.header("生成音频1")
        with col_r:
            st.header("你的评价")

        for gt_file, a_file, b_file in abx_setting:
            name_id = Path(gt_file).name

            # log info
            abx_result.name.append(name_id)
            if np.random.rand() < 0.5:
                a_file, b_file = b_file, a_file
                abx_result.swap.append(True)
            else:
                abx_result.swap.append(False)

            with col_gt:
                st.audio(gt_file)
            with col_a:
                st.audio(a_file)
            with col_b:
                st.audio(b_file)
            with col_r:
                c = st.radio(
                    name_id,
                    [0, 1],
                    horizontal=True,
                    index=None,
                    key=name_id,
                    captions=["a更好", "b更好"]
                )
                abx_result.choices.append(c)

        username = st.text_input("您的名字", placeholder="输入您的名字,必须由英文字母构成")
        click = st.form_submit_button("提交结果")

        if click:
            st.write(username, abx_result)


def run_abx(prompt_dir, exp_a, exp_b, wav_format=".mp3"):
    exp_a = Path(exp_a)
    exp_b = Path(exp_b)

    abx_setting = ABXSetting()
    abx_setting.exp_a = exp_a.name
    abx_setting.exp_b = exp_b.name

    test_files = Path(prompt_dir).glob(f"*{wav_format}")
    for x in test_files:
        filename = x.name
        a_file, b_file = exp_a/filename, exp_b/filename
        if a_file.exists() and b_file.exists():
            abx_setting.gt_file.append(str(x))
            abx_setting.a_file.append(str(a_file))
            abx_setting.b_file.append(str(b_file))

    render(abx_setting)


if __name__ == "__main__":
    fire.Fire(run_abx)
