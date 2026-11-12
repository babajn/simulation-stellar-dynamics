# シミュレーション天文学：銀河動力学を中心に

総研大2024年度「シミュレーション天文学」で用いた教材をもとに、常微分方程式の数値解法、天体の軌道積分、重力計算を扱うJupyter Notebook教材を学習・復習のために公開しています。

各Notebookは、講義で解説した数式や計算手法の動作を示す実演コードです。用意されたコードを実行し、図や計算結果を通して、数値解法の精度、軌道の保存量、重力計算の特徴などを確認できます。講義内容と実装を対応づけながら理解を深めるために活用してください。

**教材作成：馬場淳一（鹿児島大学/国立天文台)**

## 学生の皆さんへ

Pythonの基本的な文法、微積分、ベクトル、Newton力学の初歩を前提としています。講義で扱った数式をNotebookの説明・コードと照らし合わせ、上から順に実行して結果を確認してください。さらに理解を深めたい場合は、刻み幅や初期条件を変えて結果を比較してみてください。[演習ガイド](docs/exercises.md) は、そのための確認事項や発展課題をまとめた補助資料です。

初めて取り組む場合は、以下の学習順序に沿って進めてください。講義の復習では、必要なNotebookを個別に実行することもできます。

## 講義スライド

[講義スライドPDF](docs/lecture_baba_all.pdf)（89ページ、約31 MB）と、[正誤表・Notebookとの対応](docs/lecture-slides.md) を公開しています。PDFは2024年度の講義資料から、講義案内や付録などを省いた公開版です。数式の訂正や改訂Notebookとの違いを正誤表にまとめていますので、必ず併せて参照してください。

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

JupyterLabが開いたら、`notebooks/` から学習するNotebookを選んでください。各Notebookは個別に実行できます。ex06a・ex06bは同じフォルダの `tree_core.py` を使用するため、Notebookだけでなく教材フォルダ全体をダウンロードしてください。新しいカーネルで上から全セルを実行してください。外部データやAPIキーは不要です。ex06aは実行ディレクトリにGIFを保存します。ex05末尾には各手法100万ステップの比較が2組あり、数分以上かかる場合があります。ex05冒頭で `QUICK_DEMO = True` にすると、この2組の終了時刻だけを1/10に短縮できます（既定値は `False`）。実行時間はCPUや同時負荷によって変わり、乱数を固定しても時間測定は一致しません。

## 数値検証を行う場合

教材の計算結果や実行環境を確認したい場合は、以下を実行できます。通常の学習は、上記のJupyterLabで進められます。

```sh
python scripts/validate_physics.py
python scripts/validate_ellipsoid.py
python scripts/execute_notebooks.py --timeout 900
python scripts/check_release.py
```

数値検証はNotebookの関数定義自体を読み込みます。全実行はNotebookごとに現在のPython環境の新規カーネルを起動し、元の出力を使わず実行します。実行済みNotebook・GIF・ログは `build/` に保存し、Git管理から除外します。配布Notebookの出力欄は空です。Jupyterカーネルを起動できない環境では `python scripts/execute_python.py` で各Notebookのコードセルを独立したPythonプロセスで実行し、図を `build/python-executed/` に保存できます。この方法はJupyter上の数式やウィジェットの表示を検証するものではありません。

## 実演の計算モデルと発展的な学習

実演結果をさらに調べたい方に向けて、[演習ガイド](docs/exercises.md) に期待する収束次数・誤差の評価方法・発展課題を示しています。計算結果を解釈する際は、モデルの仮定と数値誤差にも注目してください。例えば、ツリー計算の例では重力のsoftening（近距離での力の緩和）を用いておらず、基底展開は有限の領域・次数で計算しています。研究に応用する場合は、対象問題に応じて精度と適用範囲を検証してください。

## 教材の更新と利用条件

2026年11月12日に、数値計算・実行環境・説明を見直しました。査読後の改訂では、解法の説明、誤差図、四分木の共通実装、検証方法を更新しています。修正内容と検証の範囲は [検証報告](docs/validation.md) にまとめています。

このリポジトリでは講義スライドと正誤表、実演用Notebook、実行・検証用ファイル、発展的な学習のための補助資料を配布しています。誤りや説明が分かりにくい箇所を見つけた場合は、[Issues](https://github.com/babajn/simulation-stellar-dynamics/issues) で、該当するNotebook名と箇所をお知らせください。

ライセンスは現在未設定です。再配布・改変物の公開などに関する利用条件は、正式なライセンスを定めた際に明記します。参考資料の権利は各権利者に帰属します。

## 参考資料

講義スライドで紹介した教科書を、学習する内容に合わせて以下にまとめます。まず全体像を『シミュレーション天文学』で確認し、銀河動力学には *Galactic Dynamics*、数値解法の理論には *Solving Ordinary Differential Equations I* を参照すると、本教材と対応づけて読み進められます。

### 教科書

- **全体像**：富阪幸治・花輪知幸・牧野淳一郎 編『シミュレーション天文学』、シリーズ現代の天文学14、日本評論社（[出版社案内：第2版](https://www.nippyo.co.jp/shop/book/9774.html)）
  数値計算の基礎と天文学への応用。ex01–08の背景。

- **微分方程式の基礎**：Erwin Kreyszig, [*Advanced Engineering Mathematics*](https://www.wiley.com/en-us/advanced-engineering-mathematics-10th-edition-p-9781119455929), Wiley。邦訳『技術者のための高等数学1 常微分方程式』、培風館
  ODEの解析的な扱い、初期値問題。ex01–04の前提。

- **ODEの数値解法**：Ernst Hairer, Syvert P. Nørsett & Gerhard Wanner, [*Solving Ordinary Differential Equations I: Nonstiff Problems*](https://link.springer.com/book/10.1007/978-3-540-78862-1), 2nd ed., Springer, 1993。邦訳『常微分方程式の数値解析 I 基礎編』
  Runge–Kutta法、多段階法、誤差・収束。ex01–05。

- **銀河動力学**：James Binney & Scott Tremaine, [*Galactic Dynamics*](https://press.princeton.edu/books/paperback/9780691130279/galactic-dynamics), 2nd ed., Princeton University Press, 2008
  軌道、重力ポテンシャル、無衝突系と緩和。ex05–08の物理的背景。

- **星団の力学**：Lyman Spitzer, Jr., [*Dynamical Evolution of Globular Clusters*](https://press.princeton.edu/books/ebook/9781400858736/dynamical-evolution-of-globular-clusters-pdf), Princeton University Press, 1987
  二体緩和と球状星団の進化。講義の衝突系の説明。

- **重力多体系**：Douglas Heggie & Piet Hut, [*The Gravitational Million-Body Problem*](https://assets.cambridge.org/97805217/74864/frontmatter/9780521774864_frontmatter.pdf), Cambridge University Press, 2003（リンクは出版社の序文）
  星団の重力多体問題と数値的な扱い。軌道積分・緩和の発展学習。

- **粒子法と重力計算**：R. W. Hockney & J. W. Eastwood, [*Computer Simulation Using Particles*](https://www.routledge.com/Computer-Simulation-Using-Particles/Hockney-Eastwood/p/book/9780367806934), 1988
  Particle–Mesh法、FFT、粒子間相互作用。講義のPM法と重力計算。

- **解析力学**：L. D. Landau & E. M. Lifshitz, [*Mechanics*](https://shop.elsevier.com/books/mechanics/landau/978-0-08-050347-9), Course of Theoretical Physics, Vol. 1。邦訳『力学』、東京図書
  保存則、中心力運動、Hamilton形式。ex05の前提と発展。

- **古典力学**：Herbert Goldstein, *Classical Mechanics*（[出版社案内：Goldstein, Poole & Safkoによる第3版](https://www.pearson.com/en-gb/subject-catalog/p/classical-mechanics-pearson-new-international-edition/P200000004309/9781292038933)）。邦訳『古典力学 上・下』、吉岡書店
  中心力問題、正準方程式、解析力学。ex05とシンプレクティック法の背景。

出版社リンクには講義当時とは異なる版も含まれます。『シミュレーション天文学』のリンク先は2026年刊行の第2版です。邦訳と原著の対応する版・章番号は、利用する本で確認してください。

### 論文・実装資料

- [Dehnen & Read (2011), N-body simulations of gravitational dynamics](https://arxiv.org/abs/1105.1082)
- [Hernquist & Ostriker (1992), A self-consistent field method for galactic dynamics](https://adsabs.harvard.edu/abs/1992ApJ...386..375H)
- [SciPyの球面調和関数の定義](https://docs.scipy.org/doc/scipy/reference/generated/scipy.special.sph_harm_y.html)

論文PDFの再配布はせず、出典へのリンクを掲載しています。
