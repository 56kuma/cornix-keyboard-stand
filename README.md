# cornix-keyboard-stand

Cornix LP キーボード用の 3D プリント収納スタンドを設計するためのリポジトリです。

現在の版は、Scaniverse で 3D スキャンした Cornix LP のメッシュを参考に再設計した、短辺下向き収納用の 2 スロット型「Lattice Bento Dock」です。材料費を抑えつつ見た目を良くするため、台座・側壁・中央ディバイダーを格子状フレームにしています。Bambu Lab でそのまま扱いやすいように、底面には `0.6 mm` の一体スキンを入れ、溝・ストッパー・格子が宙に浮かず台座へ連続する構造にしています。

- 設計計画: [docs/cornix-lp-bookshelf-storage-plan.md](docs/cornix-lp-bookshelf-storage-plan.md)
- STL: [stl/cornix_lp_bookshelf_storage_stand.stl](stl/cornix_lp_bookshelf_storage_stand.stl)
- 生成スクリプト: [cad/generate_bookshelf_storage_stand.py](cad/generate_bookshelf_storage_stand.py)
- Scaniverse解析: [docs/scan-analysis/scaniverse-pca-projections.jpg](docs/scan-analysis/scaniverse-pca-projections.jpg)
- 採寸ガイド図: [docs/cornix-lp-measurement-guide.svg](docs/cornix-lp-measurement-guide.svg)
- 写真ベース採寸図: [docs/photo-guides/photo1-measurement-annotated.jpg](docs/photo-guides/photo1-measurement-annotated.jpg), [docs/photo-guides/photo2-measurement-annotated.jpg](docs/photo-guides/photo2-measurement-annotated.jpg)
- iPhone確認用ページ: [download.html](download.html)

生成済み STL の外形は `74.2 x 129.3 x 55.0 mm` です。挿し込み口内寸は `88.8 x 21.8 mm`、底部のはめ込み溝は `88.8 x 10.8 x 1.0 mm` です。挿し込み口は中心側へ `4.0 mm`、外側へ `7.0 mm` 広げています。一体底スキンは `0.6 mm`、底部溝の総クリアランスは `0.8 mm` です。

Scaniverse解析からの推定値は、張り出し込み長辺最大 `163.9 mm`、張り出し込み短辺最大 `111.3 mm`、厚み最大 `26.4 mm` です。実測値を優先し、スタンド設計で見る矩形部は長辺 `144.0 mm`、短辺 `88.0 mm`、収納厚み `10.0 mm` として再設計しました。全高 `55.0 mm` は長辺矩形部 `144.0 mm` の約 `1 / φ²` です。スキャン値はノイズや欠けを含む可能性があるため、最終印刷前はノギスで `KEYBOARD_LONG_EDGE_CONTACT`、`KEYBOARD_SHORT_EDGE_CONTACT`、`KEYBOARD_THICKNESS` を確認してください。
