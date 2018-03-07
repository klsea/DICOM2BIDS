#! /bin/bash
# Script uses dcm2niix to convert dicoms to .nii files
# 8.21.17 KLS MG
# Create a file called subList.txt with a list of subject folder names
# Edit line 13 with location of dcm2niix and location/organization of dicoms
SUBS=$(cat 'subList.txt')

#mkdir ../BIDS
cd ../BIDS/
for SUB in $SUBS; do
	mkdir sub-$SUB
	cd sub-$SUB
	/Applications/MRIcroGL/dcm2niix -z y -f sub-${SUB}_%p -o . ../../$SUB/MRI/mri_raw
	cd ..
done
