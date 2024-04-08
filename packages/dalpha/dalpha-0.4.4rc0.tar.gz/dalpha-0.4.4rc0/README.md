# internal-sdk

## How to install

- pip 으로 설치하는 경우
  - install.sh 를 프로젝트에 복재해 사용합니다.

- poetry 로 설치하는 경우
  - install_poetry.sh 를 프로젝트에 복재해 사용합니다.

- CI 에 설정하는 법
  - CI 에 다음 step 을 추가합니다.

## How to use

``` python
import dalpha
```

## SDK 개발자가 교체하는 법
- `make build`
- version 맞춰서 S3 업로드 (`dalpha-internal-sdk`)

## 배포 방법
`pip install build twine`
`git pull origin main`
`python3 -m build`
`python3 -m twine upload dist/*`
