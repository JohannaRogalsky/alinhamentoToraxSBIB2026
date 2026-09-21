#!/bin/python3
# date:
# @author:

import os
import sys
import SimpleITK as sitk

from PyQt5.QtWidgets import (
	QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
	QLabel, QSlider, QPushButton, QListWidget, QSplitter
)
from PyQt5.QtCore import Qt

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure


class MultiPlaneWidget(QWidget):
	def __init__(self, image, title=""):
		super().__init__()
		self.image = image
		self.array = sitk.GetArrayFromImage(image)  # (z, y, x)
		self.spacing = image.GetSpacing()  # (sx, sy, sz)

		self.z_max, self.y_max, self.x_max = self.array.shape
		self.z = self.z_max // 2
		self.y = self.y_max // 2
		self.x = self.x_max // 2

		self.setWindowTitle(title)
		self.init_ui()
		self.update_display()

	def init_ui(self):
		self.fig = Figure(figsize=(18, 7))
		self.canvas = FigureCanvas(self.fig)
		self.ax_axial = self.fig.add_subplot(1, 3, 1)
		self.ax_coronal = self.fig.add_subplot(1, 3, 2)
		self.ax_sagittal = self.fig.add_subplot(1, 3, 3)
		self.fig.tight_layout()

		self.slider_z = self.make_slider(0, self.z_max - 1, self.z, self.on_z_change)
		self.slider_y = self.make_slider(0, self.y_max - 1, self.y, self.on_y_change)
		self.slider_x = self.make_slider(0, self.x_max - 1, self.x, self.on_x_change)

		self.label_z = QLabel(f"Axial (z): {self.z}")
		self.label_y = QLabel(f"Coronal (y): {self.y}")
		self.label_x = QLabel(f"Sagital (x): {self.x}")

		sliders_layout = QHBoxLayout()
		sliders_layout.setContentsMargins(4, 0, 4, 0)
		sliders_layout.setSpacing(12)

		for lbl_widget, sld in [
			(self.label_z, self.slider_z),
			(self.label_y, self.slider_y),
			(self.label_x, self.slider_x),
		]:
			col = QVBoxLayout()
			col.setContentsMargins(0, 0, 0, 0)
			col.setSpacing(2)
			lbl_widget.setStyleSheet("font-size: 10px;")
			col.addWidget(lbl_widget)
			col.addWidget(sld)
			sliders_layout.addLayout(col)

		sliders_container = QWidget()
		sliders_container.setLayout(sliders_layout)
		sliders_container.setMaximumHeight(50)

		main_layout = QVBoxLayout()
		main_layout.addWidget(self.canvas, stretch=1)
		main_layout.addWidget(sliders_container, stretch=0)
		self.setLayout(main_layout)

	def make_slider(self, minimum, maximum, value, callback):
		slider = QSlider(Qt.Horizontal)
		slider.setMinimum(minimum)
		slider.setMaximum(maximum)
		slider.setValue(value)
		slider.valueChanged.connect(callback)
		return slider

	def on_z_change(self, value):
		self.z = value
		self.update_display()

	def on_y_change(self, value):
		self.y = value
		self.update_display()

	def on_x_change(self, value):
		self.x = value
		self.update_display()

	def update_display(self):
		sx, sy, sz = self.spacing

		self.ax_axial.clear()
		self.ax_axial.imshow(self.array[self.z, :, :], cmap='gray')
		self.ax_axial.set_title(f'Axial (z={self.z}/{self.z_max - 1})')
		self.ax_axial.axis('off')

		self.ax_coronal.clear()
		self.ax_coronal.imshow(self.array[:, self.y, :], cmap='gray',
								origin='lower', aspect=sz / sx)
		self.ax_coronal.set_title(f'Coronal (y={self.y}/{self.y_max - 1})')
		self.ax_coronal.axis('off')

		self.ax_sagittal.clear()
		self.ax_sagittal.imshow(self.array[:, :, self.x], cmap='gray',
								 origin='lower', aspect=sz / sy)
		self.ax_sagittal.set_title(f'Sagital (x={self.x}/{self.x_max - 1})')
		self.ax_sagittal.axis('off')

		self.label_z.setText(str(self.z))
		self.label_y.setText(str(self.y))
		self.label_x.setText(str(self.x))

		self.canvas.draw()


class MainWindow(QMainWindow):
	def __init__(self, root_directory):
		super().__init__()
		self.root_directory = root_directory
		self.mhd_files = self.find_mhd_files()
		self.current_index = 0

		self.setWindowTitle("Visualizador MHD - Multiplanar")
		self.resize(1800, 850)

		# Lista lateral com os arquivos encontrados (caminho relativo)
		self.file_list = QListWidget()
		for path in self.mhd_files:
			rel_path = os.path.relpath(path, self.root_directory)
			self.file_list.addItem(rel_path)
		self.file_list.currentRowChanged.connect(self.on_file_selected)
		self.file_list.setMaximumWidth(350)

		self.viewer_container = QWidget()
		self.viewer_layout = QVBoxLayout()
		self.viewer_container.setLayout(self.viewer_layout)

		self.btn_prev = QPushButton("<< Anterior")
		self.btn_next = QPushButton("Próximo >>")
		self.btn_prev.clicked.connect(self.load_previous)
		self.btn_next.clicked.connect(self.load_next)

		nav_layout = QHBoxLayout()
		nav_layout.addWidget(self.btn_prev)
		nav_layout.addWidget(self.btn_next)

		right_side = QWidget()
		right_layout = QVBoxLayout()
		right_layout.addWidget(self.viewer_container)
		right_layout.addLayout(nav_layout)
		right_side.setLayout(right_layout)

		splitter = QSplitter(Qt.Horizontal)
		splitter.addWidget(self.file_list)
		splitter.addWidget(right_side)
		splitter.setStretchFactor(1, 1)

		self.setCentralWidget(splitter)

		if self.mhd_files:
			self.file_list.setCurrentRow(0)  # dispara load_current via on_file_selected
		else:
			print("Nenhum arquivo .mhd encontrado em:", root_directory)

	def find_mhd_files(self):
		"""
		Percorre root_directory e todos os subdiretórios recursivamente
		procurando arquivos .mhd.
		"""
		files = []
		for root, _, filenames in os.walk(self.root_directory):
			print (filenames)
			for f in filenames:
				if f.endswith('.mhd'):
					files.append(os.path.join(root, f))
		files.sort()
		return files

	def clear_viewer(self):
		while self.viewer_layout.count():
			item = self.viewer_layout.takeAt(0)
			widget = item.widget()
			if widget:
				widget.setParent(None)

	def load_current(self):
		if not self.mhd_files:
			return
		mhd_path = self.mhd_files[self.current_index]
		print(f"Carregando: {mhd_path}")
		try:
			image = sitk.ReadImage(mhd_path)
			self.clear_viewer()
			viewer = MultiPlaneWidget(image, title=os.path.basename(mhd_path))
			self.viewer_layout.addWidget(viewer)
		except Exception as e:
			print(f"Erro ao carregar {mhd_path}: {e}")

	def on_file_selected(self, row):
		if row < 0:
			return
		self.current_index = row
		self.load_current()

	def load_next(self):
		if self.current_index < len(self.mhd_files) - 1:
			self.file_list.setCurrentRow(self.current_index + 1)

	def load_previous(self):
		if self.current_index > 0:
			self.file_list.setCurrentRow(self.current_index - 1)


if __name__ == "__main__":
	root_directory = "./mhdScans"
	root_directory = "./registeredScans/pairwise/affine_1/"

	app = QApplication(sys.argv)
	window = MainWindow(root_directory)
	window.show()
	sys.exit(app.exec_())