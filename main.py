#!/bin/python3
# date:
# @author:

import json
import time
import dataset as data
import registration as register


if __name__ == '__main__':
	"""
	Função principal.
	"""

	# Carrega o arquivo de configuração
	config_json_path = "configs.json"
	with open(config_json_path, 'r') as f:
		config = json.load(f)

	# Extrai parâmetros de configuração
	mhd_folder = config['conv_root_folder_home']
	lung_segmentation_folder = config["lung_segmentation_folder_home"]
	image_registration_folder = config["image_registration_folder_home"]
	progress_log_file = "progress.log"

	start = time.time()

	progress_log = []
	progress_log.append(f"#{'=' * 134}#")

	patient_paths = data.patientSeriesMaskPaths(mhd_folder, lung_segmentation_folder, progress_log)
	# Faz os alinhamentos
	register.pairwiseIndependenteITK(patient_paths, image_registration_folder, progress_log)		

	end= time.time()
	elapsed = end - start
	hours = int(elapsed // 3600)
	minutes = int((elapsed % 3600) // 60)
	seconds = elapsed % 60

	progress_log.append(f"{"-" * 134}")
	progress_log.append(f"Tempo total: {hours:02d}:{minutes:02d}:{seconds:05.2f}")

	with open(progress_log_file, 'a') as f:
		for line in progress_log:
			f.write(line)
			f.write('\n')
	
	# break
