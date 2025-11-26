import os
import json
import streamlit as st
from google import genai
from google.genai import types

# ページ設定
st.set_page_config(page_title="怪談話", page_icon="👻")

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

                # トーンごとの色設定
                tone_colors = {
                    "不気味": "#2F4F4F",   # ダークグレー
                    "恐怖": "#8B0000",     # ダークレッド
                    "悲哀": "#4B0082",     # インディゴ
                    "不明": "#A9A9A9"      # グレー
                }
                bg_color = tone_colors.get(tone, "#A9A9A9")
                text_color = "white" if tone != "不明" else "black"

                # 結果表示
                st.success("生成完了！")
                st.markdown(f"### トーン: {tone}")
                st.markdown(
                    f'<div style="background-color: {bg_color}; padding: 20px; border-radius: 10px; text-align: left;">'
                    f'<p style="color: {text_color}; white-space: pre-wrap; line-height: 1.6; margin: 0;">{story}</p>'
                    f'</div>',
                    unsafe_allow_html=True
                )

            except json.JSONDecodeError as e:
                st.error(f"JSONパースエラー: {e}")
                st.code(response.text)
            except Exception as e:
                st.error(f"エラーが発生しました: {e}")

