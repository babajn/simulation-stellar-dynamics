# シミュレーション天文学の数値実験

総研大2024年度「シミュレーション天文学」で用いた教材をもとに、常微分方程式の数値解法、天体の軌道積分、重力計算を扱うJupyter Notebook教材を学習・復習のために公開しています。

数式で学んだ計算手法を自分で実装・実行し、計算精度や保存量、計算時間を比較しながら、天文学における数値シミュレーションの基礎を身につけることを目指します。

**教材作成：馬場淳一（鹿児島大学/国立天文台)**

## 学生の皆さんへ

Pythonの基本的な文法、微積分、ベクトル、Newton力学の初歩を前提としています。各Notebookの説明と数式を読み、コードを上から順に実行してください。図が描けたら、刻み幅や初期条件を変え、結果がどう変わるか、その理由まで考えてみましょう。[演習ガイド](docs/exercises.md) に、確認してほしい点と発展課題をまとめています。

初めて取り組む場合は、以下の学習順序に沿って進めてください。講義の復習では、必要なNotebookを個別に実行することもできます。

## 学習順序

| Notebook | 内容 | 必要な前提 |
|---|---|---|
| [ex01 euler_accuracy](notebooks/ex01%20euler_accuracy.ipynb) | 前進・後退Euler、線形／非線形減衰 | 微分、Taylor展開 |
| [ex02 rk2_accuracy](notebooks/ex02%20rk2_accuracy.ipynb) | Heunと陽的中点法 | ex01 |
| [ex03 rk4_accuracy](notebooks/ex03%20rk4_accuracy.ipynb) | 古典RK4の収束 | ex02 |
| [ex04 adams_accuracy](notebooks/ex04%20adams_accuracy.ipynb) | 2次・4次Adams予測修正 | ex03 |
| [ex05 kepler](notebooks/ex05%20kepler.ipynb) | Kepler軌道、保存量、Leapfrog | ベクトル力学、ex01–04 |
| [ex06a tree](notebooks/ex06a%20tree.ipynb) | 四分木の分割・可視化 | 再帰、質量中心 |
| [ex06b tree_gravity](notebooks/ex06b%20tree_gravity.ipynb) | Barnes–Hutと直接和の比較 | ex06a、Newton重力 |
| [ex07b spheharm](notebooks/ex07b%20spheharm.ipynb) | 球面調和関数の可視化 | 複素数、球座標 |
| [ex07a spheharm_expand](notebooks/ex07a%20spheharm_expand.ipynb) | 密度射影と重力ポテンシャル | ex07b、積分 |
| [ex08 bfe_ho92](notebooks/ex08%20bfe_ho92.ipynb) | Hernquist–Ostriker基底展開 | ex07a、Poisson方程式 |

Notebookの番号は講義時のものを使用しています。球面調和関数は、まずex07bで形を確認してからex07aの重力ポテンシャル計算へ進むと理解しやすくなります。

## 実行方法

まず、このページの **Code → Download ZIP** から教材をダウンロードして展開するか、Gitでリポジトリを取得してください。Python 3.12を用意し、ターミナルで教材フォルダ（README.mdがある場所）を開いて、次の手順で実行環境を作成します。

```sh
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m jupyter lab
```

Windowsでは有効化を `.venv\Scripts\activate` に置き換えます。別案として `conda env create -f environment.yml`、`conda activate simulation-astronomy` を利用できます。検証したのはmacOS arm64 / Python 3.12で、Windows/Linux/Colabの実機検証はしていません。

検証環境の間接依存も固定する場合は `python -m pip install -r requirements-lock.txt` を使用します。

JupyterLabが開いたら、`notebooks/` から学習するNotebookを選んでください。各Notebookは独立しています。新しいカーネルで上から全セルを実行してください。外部データやAPIキーは不要です。ex06aは実行ディレクトリにGIFを保存します。ex05末尾には各手法100万ステップの比較が2組あり、数分以上かかる場合があります。実行時間はCPUや同時負荷によって変わり、乱数を固定しても時間測定は一致しません。

## 数値検証を行う場合

教材の計算結果や実行環境を確認したい場合は、以下を実行できます。通常の学習は、上記のJupyterLabで進められます。

```sh
python scripts/validate_physics.py
python scripts/validate_ellipsoid.py
python scripts/execute_notebooks.py --timeout 900
python scripts/check_release.py
```

数値検証はNotebookの関数定義自体を読み込みます。全実行はNotebookごとに現在のPython環境の新規カーネルを起動し、元の出力を使わず実行します。実行済みNotebook・GIF・ログは `build/` に保存し、Git管理から除外します。配布Notebookの出力欄は空です。

## 計算モデルと演習

[演習ガイド](docs/exercises.md) に、期待する収束次数・誤差の評価方法・発展課題を示します。計算結果を解釈する際は、モデルの仮定と数値誤差にも注目してください。例えば、ツリー計算の例では重力のsoftening（近距離での力の緩和）を用いておらず、基底展開は有限の領域・次数で計算しています。研究に応用する場合は、対象問題に応じて精度と適用範囲を検証してください。

## 教材の更新と利用条件

2026年11月12日に、数値計算・実行環境・説明を見直し、Notebook全10本の全セル実行と数値検証を行いました。修正内容と検証の範囲は [検証報告](docs/validation.md) にまとめています。

このリポジトリではNotebookと演習・実行用ファイルを配布しています。講義PDFは含みません。誤りや説明が分かりにくい箇所を見つけた場合は、[Issues](https://github.com/babajn/simulation-astronomy/issues) で、該当するNotebook名と箇所をお知らせください。

ライセンスは現在未設定です。再配布・改変物の公開などに関する利用条件は、正式なライセンスを定めた際に明記します。参考資料の権利は各権利者に帰属します。

## 参考資料

- [Dehnen & Read (2011), N-body simulations of gravitational dynamics](https://arxiv.org/abs/1105.1082)
- [Hernquist & Ostriker (1992), A self-consistent field method for galactic dynamics](https://adsabs.harvard.edu/abs/1992ApJ...386..375H)
- [SciPyの球面調和関数の定義](https://docs.scipy.org/doc/scipy/reference/generated/scipy.special.sph_harm_y.html)

論文PDFの再配布はせず、出典へのリンクを掲載しています。
