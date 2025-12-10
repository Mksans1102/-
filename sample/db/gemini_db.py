# 必要なライブラリのインポート
import os  # 環境変数にアクセスするために使用
import sqlite3  # SQLiteデータベース操作のために使用
from datetime import datetime  # タイムスタンプのために使用
from google import genai  # Google GenAI APIのメインモジュール
from google.genai import types  # APIリクエストとレスポンスの型定義

# 環境変数からGemini APIキーを取得
# セキュリティのため、APIキーはコードに直接記述せず環境変数から取得する
api_key = os.environ.get("GEMINI_API_KEY")

# Google GenAI クライアントの初期化
# このクライアントを通じてGemini APIとやり取りする
client = genai.Client(
    api_key=api_key,
)

# 使用するモデルの指定
# gemini-flash-lite-latestは高速で軽量なFlashモデルの最新版
model = "gemini-flash-lite-latest"

# データベースファイルのパス
# このスクリプトと同じディレクトリにhaiku.dbを作成<- kaidan.dbに変更
db_path = os.path.join(os.path.dirname(__file__), "kaidan.db")


def init_database():
    """
    データベースとテーブルを初期化する関数
    テーブルが存在しない場合のみ作成する
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 俳句を保存するテーブルを作成
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS kaidan (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            haiku TEXT NOT NULL,
            created_at TIMESTAMP NOT NULL
        )
    """)
    
    conn.commit()
    conn.close()


def save_kaidan(kaidan: str) -> int:
    """
    俳句をタイムスタンプとともにデータベースに保存する関数
    
    Args:
        kaidan: 保存する俳句のテキスト
    
    Returns:
        保存されたレコードのID
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 現在のタイムスタンプを取得
    timestamp = datetime.now()
    
    # 俳句とタイムスタンプをデータベースに挿入<- 怪談に変更
    cursor.execute(
        "INSERT INTO kaidan (kaidan, created_at) VALUES (?, ?)",
        (kaidan, timestamp)
    )
    
    # 挿入されたレコードのIDを取得
    record_id = cursor.lastrowid
    
    conn.commit()
    conn.close()
    
    return record_id


def get_all_kaidans():
    """
    保存されているすべての俳句を取得する関数
    
    Returns:
        俳句のリスト（id, kaidan, created_at）
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute("SELECT id, kaidan, created_at FROM kaidan ORDER BY created_at DESC")
    kaidan = cursor.fetchall()
    
    conn.close()
    
    return kaidan

def generate_kaidan() -> str:
    """
    Gemini APIを使用して怪談を生成する関数
    
    Returns:
        生成された怪談のテキスト
    """
    # プロンプト（ユーザーからの入力）の構築
    # Contentオブジェクトのリストとして会話履歴を表現する
    contents = [
        types.Content(
            role="user",  # メッセージの送信者（ユーザー）を指定
            parts=[
                # Part.from_text()でテキスト形式のメッセージを作成
                types.Part.from_text(text="怪談話を作成してください。怪談話のみです。"),
            ],
        ),
    ]

    # コンテンツ生成の設定
    # GenerateContentConfigで生成時の詳細なパラメータを指定できる
    generate_content_config = types.GenerateContentConfig()

    # Gemini APIを呼び出してコンテンツを生成
    # generate_content()メソッドでモデルにプロンプトを送信し、レスポンスを受け取る
    response = client.models.generate_content(
        model=model,  # 使用するモデル
        contents=contents,  # プロンプト内容
        config=generate_content_config,  # 生成設定
    )
    
    return response.text


# データベースを初期化
init_database()

# 俳句を生成<- 怪談に変更
print("--- 怪談話を生成中 ---")
kaidan = generate_kaidan()
print(f"生成された俳句:\n{kaidan}")

# 俳句をデータベースに保存
record_id = save_kaidan(kaidan)
print(f"\n--- データベースに保存しました (ID: {record_id}) ---")

# 保存されているすべての俳句を表示<- 怪談に変更
print("\n--- 保存されている怪談一覧 ---")
all_kaidan = get_all_kaidan()
for kaidan_record in all_kaidan:
    id_, kaidan_text, created_at = kaidan_record
    print(f"[ID: {id_}] {created_at}")
    print(f"{kaidan_text}")
    print("-" * 30)