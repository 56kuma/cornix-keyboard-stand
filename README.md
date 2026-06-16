# cornix-keyboard-stand

Cornix LP キーボード用の 3D プリント収納スタンドを設計するためのリポジトリです。

現在の版は、左右の分割キーボードを本棚の本のように並べ、短辺を下にして縦置き収納する 2 スロット型の「Bento Dock」風スタンドです。CornixHub のアクセサリページと、掲載されている Cornix Bento Box / カバー兼リストレストの設計思想を参考に再設計しています。

- 設計計画: [docs/cornix-lp-bookshelf-storage-plan.md](docs/cornix-lp-bookshelf-storage-plan.md)
- STL: [stl/cornix_lp_bookshelf_storage_stand.stl](stl/cornix_lp_bookshelf_storage_stand.stl)
- 生成スクリプト: [cad/generate_bookshelf_storage_stand.py](cad/generate_bookshelf_storage_stand.py)

生成済み STL の外形は `74.164 x 120.0 x 55.0 mm` です。CornixHub 掲載のハードキャリーケースが `D120 x T55 mm` 級だったため、奥行きと高さをその外形感に寄せています。

現時点の仮寸法は、短辺 `96.0 mm`、厚み `24.0 mm`、総クリアランス `0.5 mm` です。実機でぴったり合わせる場合は、`cad/generate_bookshelf_storage_stand.py` の `KEYBOARD_SHORT_EDGE` と `KEYBOARD_THICKNESS` を実測値に変えて再生成します。
