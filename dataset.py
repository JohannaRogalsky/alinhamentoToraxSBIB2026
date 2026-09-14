#!/bin/python3
# date:
# @author: 

import numpy as np
import os
import pydicom
import SimpleITK as sitk
import matplotlib.pyplot as plt
import collections
from pathlib import Path
import glob

from datetime import datetime
import conversion as convert
import segmentation as segment


series_descriptions_insp = ['INSPIRACAO', 'MED INSPIRACAO Body 1.0', 'MEDIASTINO, iDose (4)', 'MEDIASTINO Body 1.0']
def selectInspSeries(series):
	"""
	Seleciona série de inspiração usando as quatro aparições mais frenquentes para inspiração.
	Se não encontrar, seleciona a com maior número de slices e resolução 512x512.
	"""

	best_series = None
	insp = False
	max_slices = 200
	for s in series:
		# print (s)
		if s["Series Description"] in series_descriptions_insp and not insp:
			if s["Number of Slices"] >= max_slices:
				max_slices = s["Number of Slices"]
				best_series = s
				insp = True
		if s["Series Description"] in series_descriptions_insp and insp:
			if s["Number of Slices"] > max_slices:
				max_slices = s["Number of Slices"]
				best_series = s
				# insp = True
		elif s["Rows"] == 512 and s["Columns"] == 512 and not insp:
			if s["Number of Slices"] >= max_slices:
				# print (s["Series Description"])
				max_slices = s["Number of Slices"]
				best_series = s

	return best_series

def loadSeriesVolume(folder_path):
	"""
	Carrega a série dicom a partir do seu caminho.
	"""

	# Lê os arquivos
	slices = [pydicom.dcmread(os.path.join(folder_path, f)) for f in os.listdir(folder_path) if f.endswith('.dcm')]
	# Ordena pelo eixo Z
	slices.sort(key=lambda x: float(x.ImagePositionPatient[2]))

	# Metadados da primeira imagem
	ds = slices[0]

	# Garante pixels com mesmo tipo e a compatibilidade dos valores HU
	volume = np.stack([s.pixel_array for s in slices]).astype(np.int16)
	volume = volume * ds.RescaleSlope + ds.RescaleIntercept

	return volume

def patientSeriesConvCalcMask(patient_id, studies, root_folder, conv_folder, lung_segmentation_folder, thorax_segmentation_folder, prog_log):
	"""
	Para todo estudo: seleciona a série, converte para mhd, calcula as máscaras de pulmão e tórax. Opcionalmente a máscara do que não é pulmão. 
	"""
	prog_log.append(f'-------------------------------------------------------------------------------------------------------------------------------------')
	prog_log.append(f'Séries e máscaras.')

	patient_conv_folder = f"{conv_folder}"
	os.makedirs(f"{patient_conv_folder}", exist_ok=True)
	patient_lungmask_folder = f"{lung_segmentation_folder}"
	os.makedirs(f"{patient_lungmask_folder}", exist_ok=True)

	for idx, study in enumerate(studies):
		study_date = study["Study Date"]
		study_uid = study["Study Instance UID"]
		study_insp_serie = selectInspSeries(study['Series'])
		series_uid = study_insp_serie["Series Instance UID"]

		original_series_path = f"{root_folder}/{patient_id}/{study_uid}/{series_uid}"
		conv_series_path = f"{patient_conv_folder}/scan_{idx:04d}.mhd"
		lung_mask_path = f"{patient_lungmask_folder}/scan_{idx:04d}.mhd"
	
		convert.convDCMtoMHD(original_series_path, conv_series_path, prog_log)
		segment.lungMask(conv_series_path, lung_mask_path, lung_segmentation_folder, prog_log)

		# break

def patientSeriesMaskPaths(mhd_folder, lung_folder, prog_log):
	"""
	Para todo estudo, devolve os caminhos:
		series_image (convertida)
		torax_mask
		lung_mask
		non_lung_mask (opcional, não sei se uso)
	"""
	prog_log.append(f'-------------------------------------------------------------------------------------------------------------------------------------')
	prog_log.append(f'Caminho das séries e máscaras.')

	studies = sorted(Path(mhd_folder).glob("*.mhd"))
	# print (studies)

	paths = collections.defaultdict(list)
	for idx in range(len(studies)):
		prog_log.append(f'\t{idx:04d}')
		
		# Série convertida
		series_path = f"{mhd_folder}/scan_{idx:04d}.mhd"
		paths['series'].append(series_path)
		# Máscara dos pulmões
		lung_mask_path = f"{lung_folder}/scan_{idx:04d}.mhd"
		paths['lungmask'].append(lung_mask_path)

		# break

	return paths
