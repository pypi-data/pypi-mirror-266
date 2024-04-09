# Point Cloud Library for Python

## How to install

```bash
pip install git+https://github.com/turingmotors/PyPcl.git
```

## How to build [WIP]

依存パッケージをインストール

```bash
sudo apt install libpcl-dev
```

wheel ファイルの作成

```bash
git clone https://github.com/turingmotors/PyPcl.git
cd PyPcl
poetry install
poetry run python setup.py bdist_wheel
```

`/dist` 下の whl ファイルを pip でインストールできる。
