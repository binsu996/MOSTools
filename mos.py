import streamlit as st
from pathlib import Path
import pandas as pd
import fire
import numpy as np
from functools import partial
from omegaconf import OmegaConf


def read_url_table(filename):
    df = pd.read_excel(filename, index_col=0)
    return df


def gen_one_page(df, metrics, save_to_dir, page_id=0, first_is_gt=False, shuffle=True, show_name=False):
    np.random.seed(666)
    data = df.values
    ngroup = len(df.columns)
    n_metrics = len(metrics)

    r = []

    with st.form(f"MOS_{page_id}"):

        for i, audios in enumerate(data):
            cols = st.columns(ngroup)
            audio_with_names = list(zip(audios, df.columns))
            if shuffle:
                if first_is_gt:
                    sub_part = audio_with_names[1:]
                    np.random.shuffle(sub_part)
                    audio_with_names = [audio_with_names[0], *sub_part]
                else:
                    np.random.shuffle(audio_with_names)

            for j, (col, audio_with_name) in enumerate(zip(cols, audio_with_names)):
                audio, name = audio_with_name
                with col:
                    if not shuffle or show_name:
                        st.write(name)
                    st.audio(
                        audio, format="audio/{}".format(audio.split(".")[-1]))

                    if first_is_gt and j == 0:
                        continue

                    for metric in metrics:
                        score = st.selectbox(
                            metric, [1, 2, 3, 4, 5], key=f"{metric}_{i}_{j}_{page_id}", index=None)
                        r.append(
                            [audio, name, metric, score]
                        )
            st.divider()

        username = st.text_input("您的名字", placeholder="输入您的名字,必须由英文字母构成")
        click = st.form_submit_button("提交结果")

        if click:
            df_r = pd.DataFrame(
                r, columns=["audio", "name", "metric", "score"])

            if len(df_r) == len(df_r['score'].dropna()):
                if username is None:
                    st.error("请填写您的姓名，必须使用英文字母构成")
                else:
                    df_r["username"] = [username]*len(df_r)
                    st.dataframe(df_r)
                    save_path = Path(save_to_dir)/f"{username}_{page_id}.xlsx"
                    if save_path.exists():
                        st.warning("你已经做过该评测了")
                    else:
                        df_r.to_excel(str(save_path))
                        st.write(f"已经收到您的反馈，谢谢！")
            else:
                st.error("请检查表单确保所有选项都有填写!")


def login_page():
    username = st.text_input("用户名", placeholder="你的名字")
    login = st.button("登陆")
    if login and username:
        st.write(username)
        return username


def render(filename, metrics, first_is_gt, save_to_dir, shuffle, show_name=True):
    st.set_page_config(page_title="MOS 评测", layout="wide")
    df = read_url_table(filename)
    n = np.ceil(len(df)/5)
    dfs = np.array_split(df, n)

    options = st.sidebar.radio("测评任务子集", range(len(dfs)))
    pages = [partial(gen_one_page, sub_df, metrics, save_to_dir, idx, first_is_gt, shuffle, show_name)
             for idx, sub_df in enumerate(dfs)]
    pages[options]()


def run_mos(filename, save_to_dir="tmp", shuffle=True, first_is_gt=False, config="config/default.yaml", show_name=False):
    Path(save_to_dir).mkdir(exist_ok=True, parents=True)
    config = OmegaConf.load(config)
    render(filename, metrics=config.metrics,
           first_is_gt=first_is_gt, save_to_dir=save_to_dir, shuffle=shuffle, show_name=show_name)


if __name__ == "__main__":
    fire.Fire(run_mos)
