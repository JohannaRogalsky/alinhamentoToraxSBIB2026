#!/bin/python3
# date:
# @author:

import os
import itk


def pairwiseIndependenteITK(paths, registration_folder, log):
	"""
	Faz o corregistro de cada exame do paciente com seu posterior (par-a-par independente).
	Calcula a imagem diferença entre uma série com a posterior alinhada.
	(imagem (alvo/fixed) - imagem posterior alinhada (fonte/moving))
	"""
	log.append(f"{"-" * 134}")
	log.append(f'Par a par independente')

	registration_folder = f"{registration_folder}"
	os.makedirs(registration_folder, exist_ok=True)
	# Cria o diretório da saida do pairwise
	pairwise_folder = f"{registration_folder}/pairwise/teste"
	os.makedirs(pairwise_folder, exist_ok=True)

	scan_number = len(paths['series'])
	for idx in range(11, scan_number - 3):
		previous_exam_number = str(idx).zfill(3)
		current_exam_number = str(idx+1).zfill(3)
		log.append(f'\t{previous_exam_number} e {current_exam_number}')

		# Carrega duas séries (de exames de tempos diferentes)		
		fixed_image_path = paths['series'][idx+1]
		fixed_mask_path = paths['lungmask'][idx+1]
		moving_image_path = paths['series'][idx]
		moving_mask_path = paths['lungmask'][idx+1]
		# print (fixed_image_path, moving_image_path)
		# print (fixed_mask_path, moving_mask_path)

		fixed_image = itk.imread(fixed_image_path, itk.F)
		moving_image = itk.imread(moving_image_path, itk.F)
		fixed_mask = itk.imread(fixed_mask_path, itk.UC)
		moving_mask = itk.imread(moving_mask_path, itk.UC)
		# print(fixed_image_path, fixed_image.GetOrigin(), fixed_image.GetSpacing(), fixed_image.GetDirection())
		# print(moving_image_path, moving_image.GetOrigin(), moving_image.GetSpacing(), moving_image.GetDirection())
		
		# Cria o diretório da saida dos exame_xxx e exame_yyy do paciente
		scans_elastix_folder = f"{pairwise_folder}/exame_{previous_exam_number}_{current_exam_number}/"
		os.makedirs(scans_elastix_folder, exist_ok=True)

		parameter_object = itk.ParameterObject.New()
		parameter_object.AddParameterFile("parametros/affine_3.txt")
		# parameter_object.AddParameterFile("parametros/bspline_1.txt")

		# Faz o corregistro de duas mascaras
		result_registered_image, transform_result_parameters = itk.elastix_registration_method(
			fixed_image=fixed_image,
			moving_image=moving_image,
			parameter_object=parameter_object,
			output_directory=scans_elastix_folder,
			fixed_mask=fixed_mask,
			# moving_mask=moving_mask,
			log_to_file=True
		)

		subtract_filter = itk.SubtractImageFilter.New(
			Input1=result_registered_image,
			Input2=fixed_image
		)

		subtract_filter.Update()
		difference_image = subtract_filter.GetOutput()
		itk.imwrite(difference_image, f"{scans_elastix_folder}/difference_result.mhd", compression=True)
		