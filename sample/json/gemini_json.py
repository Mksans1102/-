# 必要なライブラリのインポート
import os
import json
from google import genai
from google.genai import types

# 環境変数からGemini APIキーを取得
# セキュリティのため、APIキーはコードに直接記述せず環境変数から取得する
api_key = os.environ.get("GEMINI_API_KEY")

# Google GenAI クライアントの初期化
# このクライアントを通じてGemini APIとやり取りする
client = genai.Client(api_key=api_key)

# 使用するモデルの指定
# gemini-flash-lite-latestは高速で軽量なFlashモデルの最新版
model = "gemini-flash-lite-latest"

# サンプルテキスト（入力例）
sample_text = "深夜のコンビニで起きた不思議な出来事について怖い話を作ってください。"

# プロンプトを怪談生成用に変更（出力はJSONで'story'と'tone'のみ）
contents = [
    types.Content(
        role="user",
        parts=[
            types.Part.from_text(
                text=(
                    f"次のテキストについて怪談を作成してください:\n{sample_text}\n\n"
                    "出力はJSON形式で次のキーのみを含めてください:\n"
                    "{'story': 'ここに怪談の本文', 'tone': '不気味or恐怖or悲哀or不明'}\n"
                    "他の情報や説明は含めないでください。"
                )
            ),
        ],
    ),
]

# コンテンツ生成の設定
# GenerateContentConfigで生成時の詳細なパラメータを指定できる
generate_content_config = types.GenerateContentConfig()

# Gemini APIを呼び出してコンテンツを生成
# generate_content()メソッドでモデルにプロンプトを送信し、レスポンスを受け取る
response = client.models.generate_content(
    model=model,
    contents=contents,
    config=generate_content_config,
)

# 生成結果の表示
print("--- 生成結果 (JSON形式) ---")
# response.textで生成されたテキストを取得
print(response.text)
print("------\n")

# 生成結果をJSONとして解析
try:
    # レスポンステキストを取得
    response_text = response.text.strip()

    # マークダウン形式のコードブロックを除去
    # ```json ... ``` や ``` ... ``` の形式に対応
    if response_text.startswith("```"):
        # 最初の```とその行を除去
        lines = response_text.split("\n")
        # 最初の行が```jsonまたは```の場合は除去
        if lines[0].startswith("```"):
            lines = lines[1:]
        # 最後の行が```の場合は除去
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        response_text = "\n".join(lines)

    # JSONとしてパース
    story_data = json.loads(response_text)

    # 怪談とトーンの表示
    if "story" in story_data and "tone" in story_data:
        print("--- パース成功 ---")
        print(f"怪談: {story_data['story']}")
        print(f"トーン: {story_data['tone']}")
        print("------\n")
    else:
        print("--- エラー: 'story'または'tone'キーが見つかりません ---")
        print(f"取得したデータ: {story_data}")
        print("------\n")

except json.JSONDecodeError as e:
    print("--- JSONパースエラー ---")
    print(f"エラー: {e}")
    print(f"受信したテキスト:\n{response.text}")
    print("------\n")
