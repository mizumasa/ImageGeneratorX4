import sys
import os
from PyQt5.QtCore import Qt, QMimeData
from PyQt5.QtGui import QPixmap, QImage, QDrag
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QGridLayout, QVBoxLayout,
    QHBoxLayout, QPushButton, QSlider
)
import numpy as np
from PIL import Image

def qimage_to_np(qimg):
    """QImage -> numpy配列(RGB)に変換する(行アライメント対応版)"""
    qimg = qimg.convertToFormat(QImage.Format_RGB888)
    w = qimg.width()
    h = qimg.height()

    ptr = qimg.bits()
    ptr.setsize(qimg.byteCount())

    bytes_per_line = qimg.bytesPerLine()
    buf = np.array(ptr, dtype=np.uint8).reshape((h, bytes_per_line))
    buf = buf[:, : (w * 3)]  # 幅×3チャンネル分だけ取り出す
    arr = buf.reshape((h, w, 3))
    return arr


class ImageWidget(QWidget):
    """
    1つの画像スロットを管理するクラス。
    - ドラッグ&ドロップ (ファイル or アプリ内スワップ)
    - クリップボード貼り付け (Paste)
    - スライダー(露出/シャドウ/ハイライト)
    - メインウィンドウへリアルタイムにプレビュー更新を通知
    """
    def __init__(self, main_window, widget_id=0):
        super().__init__()
        self.main_window = main_window
        self.widget_id = widget_id

        self.setAcceptDrops(True)

        # 画像情報
        self.image = None
        self.displayed_qimage = None
        self.image_path = ""

        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        self.setLayout(layout)

        # 画像表示
        self.image_label = QLabel("Drop Image Here")
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setFixedSize(200, 110)
        self.image_label.setStyleSheet("border: 1px solid gray;")
        layout.addWidget(self.image_label)

        # クリップボードから画像をペーストするボタン
        self.btn_paste = QPushButton("Paste")
        self.btn_paste.clicked.connect(self.paste_from_clipboard)
        layout.addWidget(self.btn_paste)

        # スライダー(露出)
        self.slider_exposure = QSlider(Qt.Horizontal)
        self.slider_exposure.setRange(-50, 50)
        self.slider_exposure.valueChanged.connect(self.update_image)
        layout.addWidget(self.slider_exposure)

        # スライダー(シャドウ)
        self.slider_shadow = QSlider(Qt.Horizontal)
        self.slider_shadow.setRange(-50, 50)
        self.slider_shadow.valueChanged.connect(self.update_image)
        layout.addWidget(self.slider_shadow)

        # スライダー(ハイライト)
        self.slider_highlight = QSlider(Qt.Horizontal)
        self.slider_highlight.setRange(-50, 50)
        self.slider_highlight.valueChanged.connect(self.update_image)
        layout.addWidget(self.slider_highlight)

    # ---- クリップボードからペースト ----
    def paste_from_clipboard(self):
        clipboard = QApplication.clipboard()
        if clipboard.mimeData().hasImage():
            qimg_clip = clipboard.image()
            if not qimg_clip.isNull():
                # QImage -> numpy -> PIL
                arr = qimage_to_np(qimg_clip)
                pil_img = Image.fromarray(arr).convert("RGB")

                # 16:9クロップ
                pil_img = self.crop_to_16_9_center(pil_img)

                # *********** テンポラリファイルとして保存 ***********
                # 同じwidget_idごとにファイル名を変えておく: clipboard_tmp_0.png etc.
                tmp_filename = f"clipboard_tmp_{self.widget_id}.png"
                pil_img.save(tmp_filename)

                # そのパスを元に、通常の load_image で読み込む
                self.load_image(tmp_filename)
            else:
                print("Clipboard image is null.")
        else:
            print("Clipboard has no image data.")

    # ----------【ドラッグ開始】----------
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton and self.image is not None:
            drag = QDrag(self)
            mime_data = QMimeData()

            # MIMEデータに「このスロットのID」「画像パス」「スライダー値」をまとめる
            data_str = f"{self.widget_id}|{self.image_path}|{self.slider_exposure.value()}|{self.slider_shadow.value()}|{self.slider_highlight.value()}"
            mime_data.setText(data_str)

            drag.setMimeData(mime_data)

            # ドラッグ時のサムネイル
            if self.displayed_qimage is not None:
                pix = QPixmap.fromImage(self.displayed_qimage)
                drag.setPixmap(
                    pix.scaled(80, 45, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                )

            drag.exec_(Qt.MoveAction)

    # ----------【ドロップ受け入れ】----------
    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls() or event.mimeData().hasText():
            event.acceptProposedAction()

    def dropEvent(self, event):
        # OSからのファイルドロップ
        if event.mimeData().hasUrls():
            urls = event.mimeData().urls()
            if not urls:
                return
            file_path = urls[0].toLocalFile()
            ext = os.path.splitext(file_path)[1].lower()
            if ext not in [".jpg", ".jpeg", ".png"]:
                return
            self.load_image(file_path)
            event.acceptProposedAction()

        # アプリ内部のドラッグ（画像スワップ）
        elif event.mimeData().hasText():
            data_str = event.mimeData().text()
            parts = data_str.split("|")
            if len(parts) == 5:
                src_id_str, path, expo, shad, high = parts
                source_id = int(src_id_str)

                # 自分(ドロップ先) の「旧データ」を退避
                old_img = self.image
                old_path = self.image_path
                old_expo = self.slider_exposure.value()
                old_shd = self.slider_shadow.value()
                old_hlt = self.slider_highlight.value()

                # ドロップされた新画像を、自分にロード
                self.load_image(path)
                self.slider_exposure.setValue(int(expo))
                self.slider_shadow.setValue(int(shad))
                self.slider_highlight.setValue(int(high))

                # スワップ元（source_id）を特定して、そこに旧データをセット
                source_widget = self.main_window.widget_list[source_id]
                source_widget.image = old_img
                source_widget.image_path = old_path
                source_widget.slider_exposure.setValue(old_expo)
                source_widget.slider_shadow.setValue(old_shd)
                source_widget.slider_highlight.setValue(old_hlt)
                source_widget.update_image()

                event.acceptProposedAction()

    # ----------【画像読み込み】----------
    def load_image(self, file_path):
        # ここで必ずファイルから開くので、
        # "clipboard_tmp_XXX.png" というパスでもOK (実ファイルがある)
        pil_img = Image.open(file_path).convert("RGB")
        pil_img = self.crop_to_16_9_center(pil_img)
        self.image = pil_img
        self.image_path = file_path
        self.update_image()

    def crop_to_16_9_center(self, pil_img):
        """
        元画像の中心を変えずに16:9にクロップする。
        """
        w, h = pil_img.size
        target_ratio = 16 / 9
        current_ratio = w / h

        if abs(current_ratio - target_ratio) < 1e-9:
            return pil_img  # ほぼ16:9ならそのまま

        if current_ratio > target_ratio:
            # 横長 -> 幅を削る
            new_width = int(h * target_ratio)
            x1 = (w - new_width) // 2
            x2 = x1 + new_width
            y1 = 0
            y2 = h
        else:
            # 縦長 -> 高さを削る
            new_height = int(w / target_ratio)
            x1 = 0
            x2 = w
            y1 = (h - new_height) // 2
            y2 = y1 + new_height

        return pil_img.crop((x1, y1, x2, y2))

    # ----------【画像を更新して表示】----------
    def update_image(self):
        if self.image is None:
            self.image_label.setPixmap(QPixmap())
            self.image_label.setText("Drop Image Here")
            self.main_window.update_preview()
            return

        # スライダー値
        exp_val = self.slider_exposure.value()
        shd_val = self.slider_shadow.value()
        hlt_val = self.slider_highlight.value()

        arr = np.array(self.image, dtype=np.float32)

        # 露出(全体)
        arr += exp_val
        # シャドウ(暗部)
        shadow_mask = (arr < 128)
        arr[shadow_mask] += shd_val
        # ハイライト(明部)
        highlight_mask = (arr >= 128)
        arr[highlight_mask] += hlt_val

        arr = np.clip(arr, 0, 255).astype(np.uint8)

        # QImage へ
        h, w, c = arr.shape
        qimg = QImage(arr.data, w, h, 3 * w, QImage.Format_RGB888)
        self.displayed_qimage = qimg.copy()

        # ラベルへ表示
        pixmap = QPixmap.fromImage(self.displayed_qimage)
        pixmap_for_label = pixmap.scaled(
            self.image_label.width(),
            self.image_label.height(),
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation
        )
        self.image_label.setPixmap(pixmap_for_label)

        # メインウィンドウのプレビュー更新を呼ぶ
        self.main_window.update_preview()

    # ----------【クリア】----------
    def clear_image(self):
        # （必要に応じてテンポラリファイルを削除するならここで）
        # if self.image_path.startswith("clipboard_tmp_") and os.path.exists(self.image_path):
        #     os.remove(self.image_path)

        self.image = None
        self.displayed_qimage = None
        self.image_path = ""
        self.image_label.setPixmap(QPixmap())
        self.image_label.setText("Drop Image Here")
        self.slider_exposure.setValue(0)
        self.slider_shadow.setValue(0)
        self.slider_highlight.setValue(0)
        self.main_window.update_preview()


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("2x2 Image Editor")
        # ウィンドウサイズを 1000 x 600 に
        self.setFixedSize(1000, 600)

        self.widget_list = []  # 4つの ImageWidget を保持

        self.init_ui()

    def init_ui(self):
        # 全体レイアウト: 横に2分割 (左: 2x2スロット, 右: プレビュー表示)
        from PyQt5.QtWidgets import QHBoxLayout
        main_layout = QHBoxLayout(self)
        self.setLayout(main_layout)

        # --- 左側コンテナ ---
        left_container = QWidget()
        left_layout = QVBoxLayout(left_container)

        # 2x2 Grid
        grid = QGridLayout()
        left_layout.addLayout(grid)

        # 4つのImageWidgetを配置
        for i in range(4):
            w = ImageWidget(main_window=self, widget_id=i)
            self.widget_list.append(w)

        grid.addWidget(self.widget_list[0], 0, 0)
        grid.addWidget(self.widget_list[1], 0, 1)
        grid.addWidget(self.widget_list[2], 1, 0)
        grid.addWidget(self.widget_list[3], 1, 1)

        # Export & Clear ボタン
        btn_layout = QHBoxLayout()
        left_layout.addLayout(btn_layout)

        btn_export_1080 = QPushButton("Export 1920x1080")
        btn_export_1080.clicked.connect(lambda: self.export_images(1920, 1080))
        btn_layout.addWidget(btn_export_1080)

        btn_export_2160 = QPushButton("Export 3840x2160")
        btn_export_2160.clicked.connect(lambda: self.export_images(3840, 2160))
        btn_layout.addWidget(btn_export_2160)

        btn_clear = QPushButton("Clear")
        btn_clear.clicked.connect(self.clear_images)
        btn_layout.addWidget(btn_clear)

        main_layout.addWidget(left_container, stretch=1)

        # --- 右側: プレビュー表示 ---
        self.preview_label = QLabel("Merged Preview")
        self.preview_label.setAlignment(Qt.AlignCenter)
        self.preview_label.setStyleSheet("border: 1px solid darkgray;")
        self.preview_label.setFixedSize(450, 400)

        main_layout.addWidget(self.preview_label, stretch=0)

        # 初期のプレビュー更新
        self.update_preview()

    def update_preview(self):
        """
        4つの ImageWidget の表示用 QImage を2x2に合成し、
        右側の preview_label にリアルタイム表示する
        """
        from PIL import Image
        # 4つの QImage を取り出す (Noneは黒扱い)
        qimgs = []
        for w in self.widget_list:
            if w.displayed_qimage is not None:
                qimgs.append(w.displayed_qimage)
            else:
                qimgs.append(None)

        # PIL.Image化
        pil_images = []
        for qimg in qimgs:
            if qimg is None:
                blank = Image.new("RGB", (160, 90), color=(0, 0, 0))
                pil_images.append(blank)
            else:
                arr = qimage_to_np(qimg)
                pil_img = Image.fromarray(arr)
                pil_images.append(pil_img)

        # プレビュー用の大きさを適当に設定（例：全体640x360、1タイル=320x180）
        preview_w = 640
        preview_h = 360
        tile_w = preview_w // 2
        tile_h = preview_h // 2

        # 4枚をタイルサイズにリサイズして合成
        for i in range(4):
            pil_images[i] = pil_images[i].resize((tile_w, tile_h), Image.LANCZOS)

        merged = Image.new("RGB", (preview_w, preview_h))
        merged.paste(pil_images[0], (0, 0))
        merged.paste(pil_images[1], (tile_w, 0))
        merged.paste(pil_images[2], (0, tile_h))
        merged.paste(pil_images[3], (tile_w, tile_h))

        # QImageに戻してラベルへ表示
        arr_merged = np.array(merged, dtype=np.uint8)
        h_, w_, c_ = arr_merged.shape
        preview_qimg = QImage(arr_merged.data, w_, h_, 3 * w_, QImage.Format_RGB888).copy()

        # ラベルサイズにフィット
        pixmap = QPixmap.fromImage(preview_qimg)
        scaled_pixmap = pixmap.scaled(
            self.preview_label.width(),
            self.preview_label.height(),
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation
        )
        self.preview_label.setPixmap(scaled_pixmap)

    def export_images(self, target_w, target_h):
        """
        4枚の画像を target_w x target_h で2x2に合成し、ファイル保存。
        """
        imgs = []
        names = []
        for w in self.widget_list:
            if w.image is not None:
                imgs.append(w.displayed_qimage)
                base_name = os.path.splitext(os.path.basename(w.image_path))[0]
                names.append(base_name)
            else:
                imgs.append(None)
                names.append("none")

        if all(i is None for i in imgs):
            return  # 全部空なら書き出さない

        filename_concat = "_".join(names) + f"_{target_w}x{target_h}.jpg"
        save_dir = os.path.dirname(os.path.abspath(__file__))
        save_path = os.path.join(save_dir, filename_concat)

        pil_images = []
        for qimg in imgs:
            if qimg is None:
                blank = Image.new("RGB", (160, 90), color=(0, 0, 0))
                pil_images.append(blank)
            else:
                arr = qimage_to_np(qimg)
                pil_img = Image.fromarray(arr)
                pil_images.append(pil_img)

        # タイルサイズ (target_w // 2, target_h // 2)
        tile_w = target_w // 2
        tile_h = target_h // 2
        for i in range(4):
            pil_images[i] = pil_images[i].resize((tile_w, tile_h), Image.LANCZOS)

        merged = Image.new("RGB", (target_w, target_h))
        merged.paste(pil_images[0], (0, 0))
        merged.paste(pil_images[1], (tile_w, 0))
        merged.paste(pil_images[2], (0, tile_h))
        merged.paste(pil_images[3], (tile_w, tile_h))

        merged.save(save_path, "JPEG")
        print(f"Exported: {save_path}")

    def clear_images(self):
        for w in self.widget_list:
            w.clear_image()


def main():
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
