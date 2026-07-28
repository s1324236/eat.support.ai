from google import genai
from google.genai import types
import streamlit as st
import pandas as pd


# ページ設定
st.set_page_config(
    page_title="食べもの栄養素ガイド",
    page_icon="🥗",
    layout="wide"
)


# デザイン設定
st.markdown("""
<style>

.stApp {
    background-color: #F5FBF3;
}

.block-container {
    max-width: 1200px;
    padding-top: 2rem;
    padding-bottom: 3rem;
}

h1 {
    color: #2E7D32;
    font-size: 42px;
    font-weight: 700;
}

h2, h3 {
    color: #388E3C;
}

p {
    color: #555555;
}


div[data-testid="stTextInput"] input {
    border-radius: 12px;
    border: 2px solid #A5D6A7;
    background-color: white;
}


div[data-testid="stButton"] button {
    width: 100%;
    height: 45px;
    border-radius: 25px;
    background-color: #43A047;
    color:white;
    font-size:18px;
    font-weight:bold;
}


div[data-testid="stButton"] button:hover {
    background-color:#2E7D32;
}


div[data-testid="column"] {
    background:white;
    padding:20px;
    border-radius:18px;
    box-shadow:0px 4px 12px rgba(0,0,0,0.08);
}

</style>
""", unsafe_allow_html=True)



# タイトル

st.title("🥗 食べもの栄養素ガイド")

st.write(
    "気になる食品名を入力すると、PFCバランス・栄養特徴・おすすめ度をAIが分析します。"
)



# API設定

api_key = st.secrets["GEMINI_API_KEY"]

client = genai.Client(
    api_key=api_key
)


MODEL_NAME = "gemini-2.5-flash"



# 入力

food_name = st.text_input(
    "食品名を入力してください",
    placeholder="例: アボカド、鶏胸肉、サラダチキン"
)



# 実行

if st.button(
    "🔍 栄養素を調べる",
    type="primary"
):

    if not food_name.strip():

        st.warning(
            "食品名を入力してください"
        )

    else:

        with st.spinner(
            f"「{food_name}」を分析しています..."
        ):


            prompt = f"""
「{food_name}」について、
100gまたは一般的な1食分あたりの栄養情報を教えてください。
"""


            system_instruction = """

あなたはプロの管理栄養士です。

以下の5つのセクションで回答してください。

各セクションの間には必ず

---DIVIDER---

だけを書いてください。


【概要】

食品の特徴や栄養的な特徴。


---DIVIDER---


【栄養成分表】

必ずMarkdown表で表示してください。

|項目|値|
|---|---|
|エネルギー|○○ kcal|
|たんぱく質|○○ g|
|脂質|○○ g|
|炭水化物|○○ g|
|食物繊維|○○ g|


---DIVIDER---


【健康へのメリット】

3つ程度箇条書き。


---DIVIDER---


【食べる際のアドバイス】

おすすめの食べ方、
組み合わせ、
食べるタイミング。


---DIVIDER---


【追加情報】

PFCデータ:

たんぱく質: 数字
脂質: 数字
炭水化物: 数字


おすすめ度:

ダイエット向き: ★★★★★
筋トレ向き: ★★★★★
健康・美容向き: ★★★★★


似た食品:

・食品名
・食品名
・食品名

"""


            config = types.GenerateContentConfig(
                system_instruction=system_instruction
            )


            try:

                response = client.models.generate_content(
                    model=MODEL_NAME,
                    contents=prompt,
                    config=config
                )


                st.divider()

                st.subheader(
                    f"📊 {food_name} の栄養情報"
                )


                sections = response.text.split(
                    "---DIVIDER---"
                )

                if len(sections) >= 5:


                    col1, col2 = st.columns(
                        [1,1],
                        gap="large"
                    )


                    with col1:

                        st.markdown(
                            "### 📝 概要"
                        )

                        st.markdown(
                            sections[0].strip()
                        )


                        st.markdown(
                            "### 📊 栄養成分表"
                        )


                        table = sections[1]

                        table = table.replace(
                            "```markdown",
                            ""
                        )

                        table = table.replace(
                            "```",
                            ""
                        )


                        st.markdown(
                            table.strip()
                        )



                    with col2:

                        st.markdown(
                            "### 💡 健康へのメリット"
                        )

                        st.markdown(
                            sections[2].strip()
                        )


                        st.markdown(
                            "### 🍳 食べる際のアドバイス"
                        )

                        st.markdown(
                            sections[3].strip()
                        )



                    # 追加情報

                    st.divider()


                    extra = sections[4]


                    # 下段を左右分割

                    bottom_left, bottom_right = st.columns(
                        [1,1],
                        gap="large"
                    )



                    # 左下：PFCグラフ

                    with bottom_left:

                        st.markdown(
                            "### 📈 PFCバランス"
                        )


                        try:

                            protein = float(
                                extra.split("たんぱく質:")[1]
                                .split("\n")[0]
                            )


                            fat = float(
                                extra.split("脂質:")[1]
                                .split("\n")[0]
                            )


                            carbs = float(
                                extra.split("炭水化物:")[1]
                                .split("\n")[0]
                            )


                            df = pd.DataFrame(
                                {
                                    "栄養素": [
                                        "タンパク質",
                                        "脂質",
                                        "炭水化物"
                                    ],

                                    "量(g)": [
                                        protein,
                                        fat,
                                        carbs
                                    ]
                                }
                            )


                            st.bar_chart(
                                df.set_index("栄養素")
                            )


                        except:

                            st.write(
                                "PFCデータを取得できませんでした"
                            )



                    # 右下：おすすめ度・似た食品

                    with bottom_right:


                        st.markdown(
                            "### ⭐ 食事目的別おすすめ度"
                        )


                        if "おすすめ度:" in extra:

                            recommend = extra.split(
                                "おすすめ度:"
                            )[1].split(
                                "似た食品:"
                            )[0]


                            st.info(
                                recommend.strip()
                            )


                        st.markdown(
                            "### 🔄 似た食品"
                        )


                        if "似た食品:" in extra:

                            similar = extra.split(
                                "似た食品:"
                            )[1]


                            st.write(
                                similar.strip()
                            )



                else:

                    st.markdown(
                        response.text
                    )



            except Exception as e:

                st.error(
                    f"エラーが発生しました: {e}"
                )