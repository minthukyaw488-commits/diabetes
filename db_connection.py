"""
db_connection.py — Oracle DB 접속 담당 (연결 로직만 분리)
---------------------------------------------------------------------------
핵심 개념
  * 비밀번호를 코드에 적지 않고 환경변수(.env)에서 읽습니다.  → 보안
  * 연결 실패 시 명확한 오류 메시지를 던집니다.               → 오류 처리
  * get_connection() 은 연결 '객체'만 돌려주고,
    닫는 책임은 호출한 쪽의 try/finally 가 집니다.            → 자원 정리
"""
import os
import oracledb

# .env 파일이 있으면 환경변수로 로드 (없어도 에러 없이 진행)
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass


def get_connection():
    """환경변수에서 접속 정보를 읽어 Oracle 연결을 반환한다.

    Returns: oracledb.Connection
    Raises : RuntimeError  (비밀번호 미설정 또는 연결 실패 시)
    """
    user = os.getenv("DB_USER", "system")
    password = os.getenv("DB_PASSWORD")
    dsn = os.getenv("DB_DSN", "localhost:1521/FREEPDB1")

    if not password:
        raise RuntimeError(
            "DB_PASSWORD 환경변수가 없습니다. '.env.example' 을 '.env' 로 복사하고 "
            "비밀번호를 입력하세요 (또는  export DB_PASSWORD=...)."
        )
    try:
        return oracledb.connect(user=user, password=password, dsn=dsn)
    except oracledb.DatabaseError as e:
        # 원인(비밀번호 오류/서버 미기동 등)을 그대로 보여주되 메시지를 명확히
        raise RuntimeError(f"DB 연결 실패 ({dsn}): {e}") from e
