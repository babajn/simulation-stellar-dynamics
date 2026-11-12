# シミュレーション天文学の数値実験

総研大2024年度「シミュレーション天文学」のうち、常微分方程式・軌道積分・重力計算を扱うNotebook 10本です。原教材の著者は馬場淳一氏。2026年11月12日の検証で数値計算・実行環境・説明を修正しました。変更点は [検証報告](docs/validation.md) にまとめています。

**ライセンスは未選択です。このリポジトリでは、新たな利用許諾を付与していません。** PDFは今回の検証・配布対象に含みません。

## 学習順序

| Notebook | 内容 | 必要な前提 |
|---|---|---|
| ex01 euler_accuracy | 前進・後退Euler、線形／非線形減衰 | 微分、Taylor展開 |
| ex02 rk2_accuracy | Heunと陽的中点法 | ex01 |
| ex03 rk4_accuracy | 古典RK4の収束 | ex02 |
| ex04 adams_accuracy | 2次・4次Adams予測修正 | ex03 |
| ex05 kepler | Kepler軌道、保存量、Leapfrog | ベクトル力学、ex01–04 |
| ex06a tree | 四分木の分割・可視化 | 再帰、質量中心 |
| ex06b tree_gravity | Barnes–Hutと直接和の比較 | ex06a、Newton重力 |
| ex07b spheharm | 球面調和関数の可視化 | 複素数、球座標 |
| ex07a spheharm_expand | 密度射影と重力ポテンシャル | ex07b、積分 |
| ex08 bfe_ho92 | Hernquist–Ostriker基底展開 | ex07a、Poisson方程式 |

番号は原本との照合のため維持しています。初学者にはex07b→ex07aの順を推奨します。Hermite法、PM法、流体計算のNotebookは含まれません。

## 実行方法

Python 3.12で、リポジトリ直下から実行します。

```sh
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m jupyter lab
```

Windowsでは有効化を `.venv\Scripts\activate` に置き換えます。別案として `conda env create -f environment.yml`、`conda activate simulation-astronomy` を利用できます。検証したのはmacOS arm64 / Python 3.12で、Windows/Linux/Colabの実機検証はしていません。

検証環境の間接依存も固定する場合は `python -m pip install -r requirements-lock.txt` を使用します。

各Notebookは独立しています。新しいカーネルで上から全セルを実行してください。外部データやAPIキーは不要です。ex06aは実行ディレクトリにGIFを保存します。ex05末尾には各手法100万ステップの比較が2組あり、数分以上かかる場合があります。実行時間はCPUや同時負荷によって変わり、乱数を固定しても時間測定は一致しません。

```sh
python scripts/validate_physics.py
python scripts/validate_ellipsoid.py
python scripts/execute_notebooks.py --timeout 900
python scripts/check_release.py
```

数値検証はNotebookの関数定義自体を読み込みます。全実行はNotebookごとに現在のPython環境の新規カーネルを起動し、元の出力を使わず実行します。実行済みNotebook・GIF・ログは `build/` に保存し、Git管理から除外します。配布Notebookの出力欄は空です。

## 計算モデルと演習

[演習ガイド](docs/exercises.md) に、期待する収束次数・誤差の評価方法・発展課題を示します。全セルが完走しても物理モデルの適用範囲が広がるわけではありません。ツリー例はsofteningなし、基底展開は有限領域・有限次数です。研究利用には対象問題に応じた独立検証が必要です。

## 公開と利用条件

[ライセンス候補](docs/license-options.md) と [公開対象](docs/publication.md) を確認してください。著者表示は保持し、メールアドレスと保存済み出力・実行環境メタデータは配布ファイルから除いています。元ファイルは変更していません。

## 参考資料

- [Dehnen & Read (2011), N-body simulations of gravitational dynamics](https://arxiv.org/abs/1105.1082)
- [Hernquist & Ostriker (1992), A self-consistent field method for galactic dynamics](https://adsabs.harvard.edu/abs/1992ApJ...386..375H)
- [SciPyの球面調和関数の定義](https://docs.scipy.org/doc/scipy/reference/generated/scipy.special.sph_harm_y.html)

論文PDFの再配布はせず、出典へのリンクを掲載しています。
