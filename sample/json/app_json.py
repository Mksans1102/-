import os
import json
import streamlit as st
from google import genai
from google.genai import types

# ページ設定
st.set_page_config(page_title="怪談話", page_icon="👻")

# CSS でページ背景をカスタマイズ
st.markdown("""
<style>
    body {
        background: linear-gradient(135deg, #0f0c29 0%, #302b63 50%, #24243e 100%);
        background-attachment: fixed;
    }
    .stApp {
        background: linear-gradient(135deg, #0f0c29 0%, #302b63 50%, #24243e 100%);
        background-attachment: fixed;
    }
    h1 {
        color: white !important;
    }
    p, div {
        color: white !important;
    }
</style>
""", unsafe_allow_html=True)

# タイトル
st.title("👻怪談話")
st.write("テキストを入力すると、AIが怖い話を作成します")

# テキスト入力
input_text = st.text_area(
    "テキストを入力してください",
    placeholder="例: 深夜のコンビニで起きた不思議な出来事について怖い話を作って。",
    height=120
)

# 生成ボタン
if st.button("怪談を生成", type="primary"):
    if not input_text:
        st.warning("テキストを入力してください")
    else:
        with st.spinner("怪談を生成中..."):
            try:
                # APIキー取得
                api_key = os.environ.get("GEMINI_API_KEY")
                if not api_key:
                    st.error("GEMINI_API_KEYが設定されていません")
                    st.stop()

                # クライアント初期化
                client = genai.Client(api_key=api_key)

                # プロンプト作成（出力はJSON）
                contents = [
                    types.Content(
                        role="user",
                        parts=[
                            types.Part.from_text(
                                text=(
                                    f"次のテキストについて怪談を作成してください:\n{input_text}\n\n"
                                    "出力はJSON形式で次のキーのみを含めてください:\n"
                                    "{'story': 'ここに怪談の本文', 'tone': '不気味or恐怖or悲哀or不明'}\n"
                                    "他の情報や説明は含めないでください。"
                                )
                            ),
                        ],
                    ),
                ]

                # API呼び出し
                response = client.models.generate_content(
                    model="gemini-flash-lite-latest",
                    contents=contents,
                    config=types.GenerateContentConfig(),
                )

                # レスポンス整形（コードブロックを除去）
                response_text = response.text.strip()
                if response_text.startswith("```"):
                    lines = response_text.split("\n")
                    if lines[0].startswith("```"):
                        lines = lines[1:]
                    if lines and lines[-1].strip() == "```":
                        lines = lines[:-1]
                    response_text = "\n".join(lines)

                # JSONパース
                story_data = json.loads(response_text)
                story = story_data.get("story", "").strip()
                tone = story_data.get("tone", "不明").strip()

                # トーンごとの色・アイコン設定
                tone_config = {
                    "不気味": {
                        "icon": "👁️",
                        "bg_color": "#1a1a2e",
                        "text_color": "#00d4ff",
                        "border_color": "#00d4ff"
                    },
                    "恐怖": {
                        "icon": "😱",
                        "bg_color": "#2d0a0a",
                        "text_color": "#ff6b6b",
                        "border_color": "#ff6b6b"
                    },
                    "悲哀": {
                        "icon": "😢",
                        "bg_color": "#1a0f2e",
                        "text_color": "#b19cd9",
                        "border_color": "#b19cd9"
                    },
                    "不明": {
                        "icon": "❓",
                        "bg_color": "#2a2a2a",
                        "text_color": "#cccccc",
                        "border_color": "#666666"
                    }
                    
                }
                
                config = tone_config.get(tone, tone_config["不明"])

                # 結果表示
                st.success("ﾋｭｰﾄﾞﾛﾄﾞﾛﾄﾞﾛ…")
                
                # トーン表示
                st.markdown(f"### {config['icon']} トーン: {tone}")
                
                # 怪談本文を見やすく表示
                st.markdown(
                    f'<div style="'
                    f'background-color: {config["bg_color"]}; '
                    f'padding: 25px; '
                    f'border-radius: 12px; '
                    f'border-left: 5px solid {config["border_color"]}; '
                    f'text-align: left; '
                    f'box-shadow: 0 4px 6px rgba(0,0,0,0.3);'
                    f'">'
                    f'<p style="'
                    f'color: {config["text_color"]}; '
                    f'white-space: pre-wrap; '
                    f'line-height: 1.8; '
                    f'margin: 0; '
                    f'font-size: 16px;'
                    f'">{story}</p>'
                    f'</div>',
                    unsafe_allow_html=True
                )

            except json.JSONDecodeError as e:
                st.error(f"JSONパースエラー: {e}")
                st.code(response.text)
            except Exception as e:
                st.error(f"エラーが発生しました: {e}")

