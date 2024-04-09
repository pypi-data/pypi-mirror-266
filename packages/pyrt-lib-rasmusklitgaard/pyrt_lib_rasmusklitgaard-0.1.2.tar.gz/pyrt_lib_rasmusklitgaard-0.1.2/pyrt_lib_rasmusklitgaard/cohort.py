from asyncore import write
from dataclasses import is_dataclass
import pydicom as pd
import numpy as np
import os
import openpyxl
import string
import operator
from typing import List, Dict
from .helpers import *
from scipy.spatial import Delaunay
import copy
import SimpleITK as sitk
import time
import copy


class Cohort():
	def __init__(self):
		self.list_of_patients : List[Patient]
		self.list_of_patients = []
		self.dict_of_patients_by_id : Dict[Patient]
		self.dict_of_patients_by_id = {}
		self.n = 0
	def add_patient(self, patient : 'Patient'):
		self.list_of_patients.append(patient)
		self.dict_of_patients_by_id[patient.patient_id] = patient
		self.n += 1
	def get_patient_by_id(self, id : str) -> 'Patient':
		return self.dict_of_patients_by_id[id]
	def merge_cohorts(self, other_cohort : 'Cohort'):
		for patient in other_cohort.list_of_patients:
			self.add_patient(patient)
	def merge_many_cohorts(self, list_of_other_cohorts : List['Cohort']):
		for cohort in list_of_other_cohorts:
			self.merge_cohorts(cohort)
	def make_subcohort_gamma(self, requirements : list) -> 'Cohort':

		ops = {'>': operator.gt,
			   '<': operator.lt,
		  	   '>=': operator.ge,
		  	   '<=': operator.le,
		  	   '==': operator.eq}

		subcohort = Cohort()

		struct  = 	 requirements[0]
		criterium = 	 requirements[1]
		comp 	  =  ops[requirements[2]]
		req_value = 	 requirements[3]
		for patient in self.list_of_patients:
			if comp(patient.dict_of_gamma_passes[struct][criterium], float(req_value)):
				subcohort.add_patient(patient)
		return subcohort

	def make_subcohort_uncert(self, requirements : list) -> 'Cohort':

		ops = {'>': operator.gt,
			   '<': operator.lt,
		  	   '>=': operator.ge,
		  	   '<=': operator.le,
		  	   '==': operator.eq}

		measures = {"mean" : np.mean,
			        "max"  : np.max,
					"min"  : np.min}

		subcohort = Cohort()

		struct    = 	 requirements[0]
		measure   = 	 requirements[1]
		comp 	  =  ops[requirements[2]]
		req_value = 	 requirements[3]
		measure_calculator = measures[measure]
		for patient in self.list_of_patients:
			uncert_file = [a for a in patient.list_of_dicom_file_paths if "Uncert_percent" in a][0]
			uncert_grid = pd.read_file(uncert_file)
			uncert_grid = uncert_grid.DoseGridScaling * uncert_grid.pixel_array
			uncert_grid = uncert_grid[patient.structure_indices[patient.actual_structure_names[struct]]]
			uncert_measure = measure_calculator(uncert_grid)
			if comp(uncert_measure, float(req_value)):
				subcohort.add_patient(patient)
		return subcohort

		
	def make_subcohort_dvh(self, requirements) -> 'Cohort':
		# makes a subcohort of all patients that fulfill the requirement
		# requirement is list of strings like [struct, model, dvh_param, comparator, value]
		# so something like, ["rectal_wall", "carabe", "v20gy", ">=", "20"]

		subcohort = Cohort()
		ops = {'>': operator.gt,
			   '<': operator.lt,
		  	   '>=': operator.ge,
		  	   '<=': operator.le,
		  	   '==': operator.eq}

		struct 		= 		requirements[0]
		model 		= 		requirements[1]
		dvh_key 	= 		requirements[2]
		comp 		= 	ops[requirements[3]]
		req_value 	= 		requirements[4]
		
		for patient in self.list_of_patients:
			# code_interact(globals(),locals())
			if comp(patient.get_dvh_param(struct, model, dvh_key), float(req_value)):
				subcohort.add_patient(patient)
		return subcohort
	
	def make_subcohort_meta(self, requirement) -> 'Cohort':
		# requirement is [meta data key, comparator, meta data value]
		subcohort = Cohort()
		ops = {'>': operator.gt,
			   '<': operator.lt,
		  	   '>=': operator.ge,
		  	   '<=': operator.le,
		  	   '==': operator.eq}

		meta_data_key 	= 		requirement[0]
		comp 			= 	ops[requirement[1]]
		meta_data_value = 		requirement[2]

		for patient in self.list_of_patients:
			if comp(str(patient.metadata[meta_data_key]), str(meta_data_value)):
				subcohort.add_patient(patient)
		return subcohort
	
	def get_dvh_param_for_all(self, structure, model, key):
		# returns a list of this dvh param for all the patients
		return np.array([patient.get_dvh_param(structure, model, key) for patient in self.list_of_patients])