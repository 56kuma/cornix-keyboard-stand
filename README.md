# cornix-keyboard-stand

Cornix LP キーボード用の 3D プリント収納スタンドを設計するためのリポジトリです。

現在の版は、Scaniverse で 3D スキャンした Cornix LP のメッシュを参考に再設計した、短辺下向き収納用の 2 スロット型「Golden Ratio Airframe Dock」です。支柱まわりの空間と薄い膜だけの面をなくすため、台座は外周と同じ八角形アウトラインの `5.0 mm` 一体ソリッドベースにしています。Bambu Lab でそのまま扱いやすいように、溝・ストッパー・外周の 2 本支柱・中央の 2 枚フィンがすべてベースへ連続する構造にしています。中央保持部は、低いレールと 2 枚フィンを 1 つの連続スイープ形状として生成し、斜めガセットなしでスライサー上の別シェル化を抑える構成にしました。

- 設計計画: [docs/cornix-lp-bookshelf-storage-plan.md](docs/cornix-lp-bookshelf-storage-plan.md)
- STL: [stl/cornix_lp_bookshelf_storage_stand.stl](stl/cornix_lp_bookshelf_storage_stand.stl)
- サイズ確認用 STL: [stl/cornix_lp_fit_check_coupon.stl](stl/cornix_lp_fit_check_coupon.stl)
- 生成スクリプト: [cad/generate_bookshelf_storage_stand.py](cad/generate_bookshelf_storage_stand.py)
- サイズ確認用生成スクリプト: [cad/generate_fit_check_coupon.py](cad/generate_fit_check_coupon.py)
- Scaniverse解析: [docs/scan-analysis/scaniverse-pca-projections.jpg](docs/scan-analysis/scaniverse-pca-projections.jpg)
- 採寸ガイド図: [docs/cornix-lp-measurement-guide.svg](docs/cornix-lp-measurement-guide.svg)
- 写真ベース採寸図: [docs/photo-guides/photo1-measurement-annotated.jpg](docs/photo-guides/photo1-measurement-annotated.jpg), [docs/photo-guides/photo2-measurement-annotated.jpg](docs/photo-guides/photo2-measurement-annotated.jpg)
- iPhone確認用ページ: [download.html](download.html)

生成済み STL の外形は `74.2 x 128.3 x 55.0 mm` です。押し込み口内寸は `89.8 x 22.8 mm`、底部のはめ込み溝は `88.8 x 10.8 x 1.0 mm` です。押し込み口は縦方向へ `1.0 mm`、中心側へ `4.0 mm`、外側へ `8.0 mm` 広げています。台座は `5.0 mm` 厚の一体八角形ベースで、底部溝の総クリアランスは `0.8 mm` です。左右外周は片側 2 本の独立した斜め支柱のみにし、支柱幅を中央フィン厚みと同じ `4.5 mm` に揃えました。大外側の短い補強支柱は削除しています。中央保持部は外観上はベース面から立ち上がる 2 枚フィンのまま、下部レールから垂直に立ち上がる一体スイープ形状にしています。側面はまっすぐ、先端の丸めた三角形状は維持しています。STL 三角形数は `352` です。

材料を抑えてサイズ感だけ確認する場合は、1スロットの低いテストピース `cornix_lp_fit_check_coupon.stl` を先に印刷してください。外形は `27.6 x 95.8 x 8.0 mm` で、押し込み口 `89.8 x 22.8 mm` と底部溝 `88.8 x 10.8 x 1.0 mm` は本番と同じです。

Scaniverse解析からの推定値は、張り出し込み長辺最大 `163.9 mm`、張り出し込み短辺最大 `111.3 mm`、厚み最大 `26.4 mm` です。実測値を優先し、スタンド設計で見る矩形部は長辺 `144.0 mm`、短辺 `88.0 mm`、収納厚み `10.0 mm` として再設計しました。全高 `55.0 mm` は長辺矩形部 `144.0 mm` の約 `1 / φ²` です。スキャン値はノイズや欠けを含む可能性があるため、最終印刷前はノギスで `KEYBOARD_LONG_EDGE_CONTACT`、`KEYBOARD_SHORT_EDGE_CONTACT`、`KEYBOARD_THICKNESS` を確認してください。
