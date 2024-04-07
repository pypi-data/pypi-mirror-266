from setuptools import setup, find_packages

# PyPIの説明文にREADME.mdを使うように読み込みをする
with open("README.md", "r", encoding="utf-8") as fp:
	readme = fp.read()

setup(
	# 開発者
	author="Hideo Nukada",
	# ライブラリの名前
	name="hideocardgames",
	# ライブラリのバージョン
	version="0.1.0",
	long_description=readme,
	long_description_content_type="text/markdown",
	# パッケージの名前を自動で取得してくれる
	packages=find_packages(),
	# 依存関係がある場合ここにリストアップ
	install_requires=[
	],
	# PyPIで検索時に利用されるライセンスやPythonバージョンのキーワード
	classifiers=[
		"Development Status :: 3 - Alpha",
		"License :: OSI Approved :: MIT License",
		"Programming Language :: Python :: 3",
		"Programming Language :: Python :: 3.6",
		"Programming Language :: Python :: 3.7",
		"Programming Language :: Python :: 3.8",
		"Programming Language :: Python :: 3.9",
	],
	# インストール時のPythonバージョンの制約
	python_requires=">=3.6",
)