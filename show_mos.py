import fire
from pathlib import Path
import pandas as pd
import streamlit as st
import seaborn as sns
import matplotlib.pyplot as plt
sns.set_theme(style="ticks")

df = sns.load_dataset("penguins")


def main(res_folder):
    dfs = [pd.read_excel(str(x), index_col=0)
           for x in Path(res_folder).glob("*.xlsx")]
    df = pd.concat(dfs)

    for metric,sub_df in df.groupby("metric"):
        st.header(metric)
        st.dataframe(sub_df[["audio","score"]])
        fig=plt.figure()
        hue_order=sorted(set(sub_df["name"].values))
        sns.countplot(sub_df, x="score",hue="name",hue_order=hue_order)
        plt.title(metric)
        st.pyplot(fig)

if __name__ == "__main__":
    fire.Fire(main)
