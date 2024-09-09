import fire
from pathlib import Path
import pandas as pd
import streamlit as st
import seaborn as sns
import matplotlib.pyplot as plt
from scipy.stats import ttest_rel
from itertools import product
from pathlib import Path
import numpy as np

sns.set_theme(style="ticks")


def highlight(x, p_value):
    return np.where(p_value is not None and p_value < 0.05, f"background-color: rgb(215,96,146,0.3) ", None)


def main(res_folder):
    dfs = [pd.read_excel(str(x), index_col=0)
           for x in Path(res_folder).glob("*.xlsx")]
    df = pd.concat(dfs)

    for metric, sub_df in df.groupby("metric"):
        st.header(metric)
        # st.dataframe(sub_df)
        fig = plt.figure()
        hue_order = sorted(set(sub_df["name"].values))
        sns.countplot(sub_df, x="score", hue="name", hue_order=hue_order)
        plt.title(metric)
        st.pyplot(fig)

        sub_df["baseaudio"] = list(
            map(lambda x: Path(x).stem, sub_df["audio"]))
        wide_sub_df = pd.pivot(
            sub_df, index=["baseaudio", "username"], columns='name', values='score').reset_index()

        st.dataframe(wide_sub_df.describe(
        ).loc["mean"], use_container_width=True)

        # 计算均值差异，以及pvalue，将结果绘制在表格中
        diff_df = pd.DataFrame(index=hue_order, columns=hue_order)
        pvalue_df = pd.DataFrame(index=hue_order, columns=hue_order)

        n = len(hue_order)
        for i, j in product(range(n), repeat=2):
            if i > j:
                name_i = hue_order[i]
                name_j = hue_order[j]
                sj = wide_sub_df[name_j].values
                si = wide_sub_df[name_i].values
                diff_df[name_i][name_j] = sj.mean()-si.mean()
                _, pvalue_df[name_i][name_j] = ttest_rel(sj, si)

        st.dataframe(diff_df.style.apply(
            highlight, p_value=pvalue_df.values, axis=None), use_container_width=True)


if __name__ == "__main__":
    fire.Fire(main)
