import os
import cv2
import numpy as np
import PySide6.QtWidgets as Qw
import PySide6.QtGui as Qg
import PySide6.QtCore as Qc
import re

class MainWindow(Qw.QMainWindow):
  def __init__(self):
    super().__init__()

    self.setWindowTitle('画像ビューワー')
    self.setGeometry(100, 50, 800, 600)

    # 画像の拡大率（初期値: 100%）
    self.scale_factor = 1.0
    self.rotation_angle = 0  # 回転角度
    self.img_original = None  # 元の画像
    self.img_display = None  # 表示用のリサイズ画像

    # メインウィジェット
    main_widget = Qw.QWidget(self)
    self.setCentralWidget(main_widget)

    # メインレイアウト
    main_layout = Qw.QVBoxLayout(main_widget)

    # 画像表示ラベル
    self.lb_img = Qw.QLabel(self)
    self.lb_img.setAlignment(Qc.Qt.AlignmentFlag.AlignCenter)

    # スクロールエリアを追加
    self.scroll_area = Qw.QScrollArea()
    self.scroll_area.setWidget(self.lb_img)
    self.scroll_area.setWidgetResizable(True)  # 画像サイズに応じて自動調整
    self.scroll_area.setAlignment(Qc.Qt.AlignmentFlag.AlignCenter)

    # ナビゲーションラベル
    self.init_navi_msg = '[開く] ボタンを押下してファイルを選択してください。'
    self.lb_navi = Qw.QLabel(self.init_navi_msg, self)
    self.lb_navi.setAlignment(Qc.Qt.AlignmentFlag.AlignCenter)

    # 拡大率スライダーエリア
    slider_layout = Qw.QHBoxLayout()
    self.lb_zoom = Qw.QLabel("拡大率: 100%", self)
    self.lb_zoom.setFixedWidth(100)

    self.slider_zoom = Qw.QSlider(Qc.Qt.Orientation.Horizontal)
    self.slider_zoom.setRange(50, 200)  # 50% ～ 200%
    self.slider_zoom.setValue(100)  # 初期値 100%
    self.slider_zoom.setTickInterval(10)
    self.slider_zoom.setTickPosition(Qw.QSlider.TickPosition.TicksBelow)
    self.slider_zoom.valueChanged.connect(self.zoom_image)

    slider_layout.addWidget(self.lb_zoom)
    slider_layout.addWidget(self.slider_zoom)

    # ボタンエリア
    btn_layout = Qw.QHBoxLayout()
    self.btn_open = Qw.QPushButton('開く')
    self.btn_open.clicked.connect(self.btn_open_clicked)
    self.btn_clear = Qw.QPushButton('クリア')
    self.btn_clear.clicked.connect(self.btn_clear_clicked)
    self.btn_rotate_left = Qw.QPushButton('左に回転')
    self.btn_rotate_left.clicked.connect(
        lambda: self.rotate_image(45))  # 45度右回転
    self.btn_rotate_right = Qw.QPushButton('右に回転')
    self.btn_rotate_right.clicked.connect(
        lambda: self.rotate_image(-45))  # 45度左回転
    self.btn_save = Qw.QPushButton('保存')
    self.btn_save.clicked.connect(self.save_image)

    # ボタンのサイズを固定
    for btn in [self.btn_open, self.btn_clear, self.btn_rotate_left, self.btn_rotate_right, self.btn_save]:
      btn.setFixedSize(120, 40)

    # ボタンを左詰めで配置
    btn_layout.addWidget(self.btn_open)
    btn_layout.addWidget(self.btn_clear)
    btn_layout.addWidget(self.btn_rotate_left)
    btn_layout.addWidget(self.btn_rotate_right)
    btn_layout.addWidget(self.btn_save)
    btn_layout.addStretch()

    # レスポンシブ調整
    main_layout.addWidget(self.scroll_area)  # 画像エリアをスクロール可能に
    main_layout.addWidget(self.lb_navi)
    main_layout.addLayout(slider_layout)
    main_layout.addLayout(btn_layout)

  def btn_open_clicked(self):
    title = "画像ファイルを開く"
    init_path = os.path.expanduser('~/Pictures')
    filter = 'Image Files (*.png *.jpg *.jpeg *.bmp *.gif)'
    path, _ = Qw.QFileDialog.getOpenFileName(self, title, init_path, filter)

    if path == "":
      self.lb_navi.setText(self.init_navi_msg)
      return

    self.load_image(path)

  def btn_clear_clicked(self):
    self.lb_img.clear()
    self.lb_navi.setText(self.init_navi_msg)
    self.img_original = None
    self.img_display = None
    self.scale_factor = 1.0
    self.rotation_angle = 0
    self.slider_zoom.setValue(100)

  def contains_japanese(self, text):
    # 日本語の正規表現パターン
    japanese_pattern = re.compile(
        r'[\u3040-\u309F\u30A0-\u30FF\u4E00-\u9FAF]')
    # 日本語が含まれているかをチェック
    return bool(japanese_pattern.search(text))

  def load_image(self, file_path):
    img = cv2.imread(file_path)

    if img is None:
      message = f"画像 '{os.path.basename(file_path)}' を読み込むことができません。\n"
      if self.contains_japanese(file_path):
        message += " ファイル名もしくはパスに日本語が含まれている可能性があります。"
      self.file_loadError(message)
      return

    self.img_original = img
    self.img_display = img.copy()
    self.scale_factor = 1.0
    self.rotation_angle = 0
    self.slider_zoom.setValue(100)
    self.update_image()

    self.lb_navi.setText(f"表示中: {os.path.basename(file_path)}")

  def file_loadError(self, message):
    msgBox = Qw.QMessageBox(self)
    msgBox.setWindowTitle('エラー')
    msgBox.setText(message)
    msgBox.setIcon(Qw.QMessageBox.Icon.Critical)
    msgBox.setStandardButtons(Qw.QMessageBox.StandardButton.Ok)
    msgBox.exec()

  def zoom_image(self, value):
    self.scale_factor = value / 100.0
    self.lb_zoom.setText(f"拡大率: {value}%")
    self.update_image()

  def rotate_image(self, angle):
    if self.img_display is None:
      return

    self.rotation_angle = (self.rotation_angle + angle) % 360
    self.update_image()

  def update_image(self):
    if self.img_display is None:
      return

    # 回転行列を計算
    height, width = self.img_display.shape[:2]
    matrix = cv2.getRotationMatrix2D(
        (width // 2, height // 2), self.rotation_angle, self.scale_factor)

    # 新しい画像サイズを取得
    abs_cos = abs(matrix[0, 0])
    abs_sin = abs(matrix[0, 1])
    new_width = int(height * abs_sin + width * abs_cos)
    new_height = int(height * abs_cos + width * abs_sin)

    # 画像の中心を補正
    matrix[0, 2] += (new_width - width) / 2
    matrix[1, 2] += (new_height - height) / 2

    img_rotated = cv2.warpAffine(
        self.img_display, matrix, (new_width, new_height), borderValue=(255, 255, 255))

    img_rgb = cv2.cvtColor(img_rotated, cv2.COLOR_BGR2RGB)
    qimg = Qg.QImage(
        img_rgb.data, img_rgb.shape[1], img_rgb.shape[0], img_rgb.strides[0], Qg.QImage.Format.Format_RGB888)
    self.lb_img.setPixmap(Qg.QPixmap.fromImage(qimg))
    self.lb_img.setFixedSize(new_width, new_height)  # 画像サイズを固定してスクロール可能に

  def save_image(self):
    if self.img_original is None:
      return

    # 回転行列を計算
    height, width = self.img_original.shape[:2]
    matrix = cv2.getRotationMatrix2D(
        (width // 2, height // 2), self.rotation_angle, self.scale_factor)

    # 新しい画像サイズを取得
    abs_cos = abs(matrix[0, 0])
    abs_sin = abs(matrix[0, 1])
    new_width = int(height * abs_sin + width * abs_cos)
    new_height = int(height * abs_cos + width * abs_sin)

    # 画像の中心を補正
    matrix[0, 2] += (new_width - width) / 2
    matrix[1, 2] += (new_height - height) / 2

    # 透明な背景を持つ画像を作成
    img_rotated = cv2.warpAffine(
        self.img_original, matrix, (new_width, new_height), borderMode=cv2.BORDER_CONSTANT, borderValue=(0, 0, 0, 0))

    # アルファチャンネルを追加
    if img_rotated.shape[2] == 3:
      img_rotated = cv2.cvtColor(img_rotated, cv2.COLOR_BGR2BGRA)

    file_path, _ = Qw.QFileDialog.getSaveFileName(
        self, "画像を保存", "", "PNG Files (*.png);;JPEG Files (*.jpg);;BMP Files (*.bmp)")
    if file_path:
      cv2.imwrite(file_path, img_rotated)
