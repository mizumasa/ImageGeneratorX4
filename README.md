# 2x2 Image Editor

A PyQt-based tool for placing up to four images in a 2×2 layout, with simple brightness adjustments and clipboard paste functionality. Below you will find instructions in both **English** and **日本語**.

---

## English

### Overview
This 2x2 Image Editor is a PyQt application that allows you to:
- Load up to four images (JPEG/PNG).
- Automatically center-crop them to a 16:9 ratio.
- Adjust brightness via sliders (exposure, shadow, highlight).
- Swap images between slots via drag & drop.
- Paste an image from your clipboard directly into any slot.
- Export the final 2×2 layout at either 1920×1080 or 3840×2160.

A live preview of the 2×2 merged image is displayed on the right side of the window.

### Features
1. **Drag & Drop**:  
   - Drop a `.jpg` or `.png` file onto any of the four slots.
2. **Clipboard Paste**:  
   - Each slot has a **Paste** button to import an image currently in your clipboard.
3. **16:9 Cropping**:  
   - The image is automatically cropped (centered) to a 16:9 aspect ratio.
4. **Brightness Sliders**:  
   - Each slot has sliders for **Exposure**, **Shadow**, and **Highlight**, which update the image in real time.
5. **Live Preview**:  
   - On the right side of the window, a merged 2×2 preview updates as you load or adjust images.
6. **Swapping**:  
   - You can drag an image from one slot to another to **swap** both the images and their slider values.
7. **Export**:  
   - **Export 1920×1080** or **Export 3840×2160** to generate a final 2×2 image at your chosen resolution.  
   - The output file name is composed by joining the base file names of the four images with underscores.  
   - Empty slots are treated as black images.
8. **Clear**:  
   - Click **Clear** to reset all images and sliders.

### How to Use
1. **Run the Application**  
   - Execute `python main.py` (or the relevant script) to launch the 1000×600 window.
2. **Load Images**  
   - Drag and drop a `.jpg` or `.png` file into any slot, **or**  
   - Click the **Paste** button if an image is stored in your clipboard.
3. **Adjust Brightness**  
   - Use the sliders (exposure, shadow, highlight) under each image to tweak brightness. The preview updates automatically.
4. **Swap Images**  
   - Click and drag one slot’s image onto another slot. The images (and slider settings) will be exchanged.
5. **Export**  
   - Click either **Export 1920×1080** or **Export 3840×2160** to save the final merged 2×2 image.  
   - The file is saved in the same directory as the script, named by concatenating the four images’ base names.
6. **Clear**  
   - Press **Clear** to reset all images, sliders, and the preview.

---

## 日本語

### 概要
この 2×2 画像エディタは、PyQt で作られたアプリケーションです。  
- 最大4枚の JPEG/PNG 画像を読み込めます。  
- 読み込んだ画像は中央を維持して 16:9 にトリミング。  
- 露出、シャドウ、ハイライトのスライダーで明るさを簡易調整。  
- スロット間をドラッグ＆ドロップで画像を入れ替え。  
- クリップボードにある画像も直接貼り付け可能。  
- 最終的に 1920×1080 または 3840×2160 サイズで 2×2 レイアウトとして書き出し。  

画面右側には常に 2×2 合成プレビューが表示されます。

### 特徴
1. **ドラッグ＆ドロップ**:  
   - 4つのスロットいずれかに `.jpg` や `.png` をドロップ。  
2. **クリップボードから貼り付け**:  
   - 各スロットには **Paste** ボタンがあり、クリップボード内の画像を貼り付けられます。  
3. **16:9 クロップ**:  
   - 読み込んだ画像は常に中央を維持して 16:9 にトリミング。  
4. **明るさ調整スライダー**:  
   - 露出・シャドウ・ハイライトの値を変えるとスロット画像がリアルタイムで更新。  
5. **リアルタイムプレビュー**:  
   - ウィンドウ右側に常に 2×2 の合成イメージを表示。  
6. **入れ替え (スワップ)**:  
   - あるスロットから画像をドラッグし、他のスロットへドロップすると、画像とスライダー設定が交換されます。  
7. **エクスポート**:  
   - **Export 1920×1080**, **Export 3840×2160** を押すと、2×2 レイアウトを指定解像度で書き出し。  
   - 出力ファイルはアプリと同じディレクトリに保存され、ファイル名は画像ファイル名を `_` で連結したものになります。  
   - 未使用スロットは黒の 16:9 画像として扱われます。  
8. **クリア**:  
   - **Clear** ボタンを押せばすべてのスロットがリセットされ、プレビューも初期化。

### 使い方
1. **アプリケーションの起動**  
   - `python main.py` などでスクリプトを実行すると、横 1000 × 縦 600 のウィンドウが表示されます。  
2. **画像の読み込み**  
   - `.jpg` または `.png` ファイルを対応するスロットへドラッグ＆ドロップ  
   - または **Paste** ボタンで、クリップボード内の画像を貼り付け  
3. **明るさの調整**  
   - スロット下のスライダー（露出・シャドウ・ハイライト）を操作すると即時にスロット画像と右側のプレビューが更新されます。  
4. **画像の入れ替え**  
   - スロットから画像をドラッグして別のスロットへドロップすると、両スロットの画像とスライダー設定が入れ替わります。  
5. **エクスポート**  
   - **Export 1920×1080** または **Export 3840×2160** を押すと、4枚の画像が 2×2 に合成されて保存。  
   - 出力ファイル名は読み込んだ画像のファイル名を `_` で連結したものになります。  
6. **クリア**  
   - **Clear** を押すと、全スロットとプレビューが初期化されます。

---

Enjoy the 2x2 Image Editor! / ご利用ありがとうございます。
