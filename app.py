#%%
import streamlit as st
import pandas as pd
import io
import datetime
import glob
import hjson
import numpy as np

st.set_page_config(layout="wide")

# CSSでDeployボタンを非表示にする
hide_streamlit_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            .stActionButton {visibility: hidden;}
            </style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# 選択ボックス
# メンバの一覧
member_files = glob.glob("./member/*.hjson")
member_info_dict = {}
member_names = []
for member_file in member_files:
    with open(member_file, "r", encoding="UTF-8") as f:
        json_data = hjson.load(f)
        temp_dict = {}
        temp_dict["id"] = str(json_data["id"]).replace(",", "")
        temp_dict["name"] = json_data["name"].replace(",", "")
        for key, value in json_data["skills"].items():
            temp_dict[key] = [value]
        temp_df = pd.DataFrame(temp_dict)
        member_info_dict[temp_dict["id"]] = temp_df
        member_names.append(f"{json_data['id']} {json_data['name']}".replace(",", ""))

# プロジェクトの一覧
project_files = glob.glob("./project/*.hjson")
project_info_dict = {}
project_names = []
for project_file in project_files:
    with open(project_file, "r", encoding="UTF-8") as f:
        json_data = hjson.load(f)
        temp_dict = {}
        temp_dict["id"] = json_data["id"].replace(",", "")
        temp_dict["name"] = json_data["name"]
        temp_dict["skills"] = json_data["skills"]
        project_info_dict[temp_dict["id"]] = temp_dict
        project_names.append(f"{json_data['id']} {json_data['name']}".replace(",", ""))

member_names.append("all")
project_names.append("all")

col1, col2, col3 = st.columns(3)

with col1:
    selected_members = st.multiselect(
        "メンバを選んでください",
        member_names
    )
with col2:
    selected_projects = st.multiselect(
        "プロジェクトを選んでください",
        project_names
    )
with col3:
    options = st.radio(
        "表示オプションを選んでください",
        ["指定メンバ・指定プロジェクトのスキルすべて", "指定プロジェクトで定義されたスキルだけ"]
    )

# 選択メンバについてDataFrameに結合
members_df = pd.DataFrame()
if "all" in selected_members:
    for key, value in member_info_dict.items():
        members_df = pd.concat([members_df, member_info_dict[key]], axis=0)
else:
    for member in selected_members:
        member_id = member.split(" ")[0]
        members_df = pd.concat([members_df, member_info_dict[member_id]], axis=0)

# 選択プロジェクトのスキルを取得
target_skills = []
if "all" in selected_projects:
    for key, value in project_info_dict.items():
        target_skills += value["skills"]
else:
    for project in selected_projects:
        id = project.split(" ")[0]
        target_skills += project_info_dict[id]["skills"]
target_skills = [x.replace(",", "") for x in target_skills]
target_skills = list(set(target_skills))

if len(members_df) > 0:
    # オプションによって表示の方法を変更
    if options == "指定プロジェクトで定義されたスキルだけ":
        # プロジェクトで必要なスキルに絞って表示
        # 一度スキル列を足してから絞り込む
        for target_skill in target_skills:
            if target_skill not in members_df.columns:
                members_df[target_skill] = np.nan
        target_skills = ["id", "name"] + target_skills
        members_df = members_df[target_skills]
    elif options == "指定メンバ・指定プロジェクトのスキルすべて":
        # スキル列を足すが絞り込まない
        for target_skill in target_skills:
            if target_skill not in members_df.columns:
                members_df[target_skill] = np.nan
    else:
        # 未指定の状態
        # 指定されたメンバの情報をそのまま表示するので何もしない
        pass

    # html = members_df.to_html(index=False)
    # st.write(html, unsafe_allow_html=True)
    st.write(members_df.reset_index(drop=True))
