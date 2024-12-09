import os
from pathlib import Path

import pytest
from dotenv import load_dotenv

@pytest.fixture(scope="session", autouse=True)
def set_env_vars():
    env_file_path = Path(os.getenv("ENV_FILE_PATH")).resolve()
    print(f'env path: {env_file_path}')
    if env_file_path.exists():
        load_dotenv(dotenv_path=env_file_path)
        print(f".env загружен из {env_file_path}")
    else:
        print(f".env не найден по пути {env_file_path}")