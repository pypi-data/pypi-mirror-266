# Waylake Utils

## 개요

`waylake-utils`는 Python 애플리케이션을 위한 다양한 유틸리티 모듈을 제공하는 패키지입니다. 현재는 사용자 정의 로깅 설정을 포함하고 있으며, 향후 여러 유용한 기능들이 추가될 예정입니다. 이 패키지를 통해 애플리케이션 개발 과정에서 필요한 여러 기능들을 쉽고 효율적으로 구현할 수 있습니다.

## 주요 기능

- **사용자 정의 로깅** : 애플리케이션의 다양한 부분에 일관된 로깅 설정을 적용할 수 있습니다. 로그 파일은 호출하는 스크립트의 위치에 따라 생성됩니다.
- **추후 추가** : 향후 다양한 유틸리티 기능들이 추가될 예정입니다. 각 기능은 쉽게 통합하고 사용할 수 있도록 설계됩니다.

## 설치 방법

```bash
pip install waylake-utils
```

`waylake-utils`는 pip을 통해 쉽게 설치할 수 있습니다. 현재 GitHub 레포지토리나 내부 패키지 저장소를 통해 관리되고 있습니다.

## 사용 방법

### 로깅 설정

1. 로깅 기능을 import합니다.

```python
from waylake.utils import setup_logger
# or
from waylake import setup_logger
```

2. 로거를 설정합니다. `__file__`을 인자로 전달하여 현재 스크립트 위치에 로그 파일을 생성합니다.

```python
logger = setup_logger('my_logger_name', __file__)

logger = setup_logger(name='logger_name', caller_file=__file__, log_dir='./logs')
```

3. 로그를 기록합니다.

```python
logger.debug("This is a debug message")
logger.info("This is an info message")
logger.warning("This is a warning message")
logger.error("This is an error message")
logger.critical("This is a critical message")
```

### 추가 기능 (향후 업데이트 예정)

- 추가되는 기능들에 대한 설명과 사용 방법을 이곳에 기재합니다.
