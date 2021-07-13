#!/usr/bin/env python3

#python3 /home/biogeoanalysis/RAD/ref_map_scripts/blacklist_parse_filter.py -b

import sys

for i in sys.argv:
	if i == "-i":
		index = sys.argv.index(i)
		input_file  = sys.argv[index+1]
	elif i == "-c":
		index = sys.argv.index(i)
		catalog_path = sys.argv[index+1]
	elif i == "-o":
		index = sys.argv.index(i)
		output_file_path = sys.argv[index+1]

organism = ""

with open (input_file, "r") as results_file:
	for i in results_file:
		organism = i.split("@")[3]
		#print(organism)
		if ("eudicots" in organism or "monocots" in organism or "seed plants" in organism or "flowering plants" in organism):
			plants_file = open ("plants", "a")
			plants_file.write(i)
			plants_file.close()
		else:
			others_file = open ("others", "a")
			others_file.write(i)
			others_file.close()

loci_list = []

with open ("others", "r") as other_file:
	for i in other_file:
		loci_list.append(int(i.split("@")[0]))

loci_list = list(set(loci_list))
loci_list.sort()

with open (catalog_path) as catalog_file:
	catalog_list = catalog_file.readlines()

output_file = open(output_file_path, 'a')
i=0
m=0
counter = 0

while i < len(loci_list):
	while loci_list[i] != catalog_list[m].lstrip('>').split(' ')[0]:
		output_file.write(catalog_list[m] + catalog_list[m+1])
		m += 2
	i += 1
	m += 2
	counter += 1


while m < len(catalog_list):
	output_file.write(catalog_list[m] + catalog_list[m+1])
	m+=2

output_file.close()

print("Number of loci removed:",counter)
