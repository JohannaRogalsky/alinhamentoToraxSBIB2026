#!/bin/python3
# date:
# @author: 

import collections
from pathlib import Path


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
