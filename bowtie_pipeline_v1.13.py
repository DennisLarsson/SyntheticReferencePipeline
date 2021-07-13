#!/usr/bin/env python3
# Requires:
	#stacks 2.4
	#samtools
	#picard
	#bowtie2
	#gatk 3.8

#Example: python3 /home/biogeoanalysis/RAD/ref_map_scripts/bowtie_pipeline_v1.13.py -o /home/biogeoanalysis/RAD/phyteumaRAD1-9/bowtie_aligned -s /home/biogeoanalysis/RAD/RAD_samples -r /home/biogeoanalysis/RAD/phyteumaRAD1-9/bowtie_aligned/reference/catalog_10snp_60miss_filtered.fa -D phyteuma -p /home/biogeoanalysis/RAD/phyteumaRAD1-9/bowtie_aligned/popmap_opti -t 12 --ref --map --sort --RG --realign --ref_map --pop

import os
import subprocess
import sys
import math

os.system('echo "' + str(sys.argv) + '" > logfile')
os.system('echo "start of assembly at: " > logfile')
os.system('date "+%H:%M:%S   %d/%m/%y" >> logfile')

def check_folder (folder):
		folder_name = (output_folder + "/" + folder + "/")
		if os.path.exists(folder_name) == 0: ### Make sure it doesn't exit if folder exists!!!!
			os.mkdir(folder)
		else:
			print("Folder exists")

def execute_command (command):
	print(command)
	os.system('echo "' + command + '" >> logfile')
	retcode = subprocess.call(command.split())
	if retcode == 1 or retcode== -1:
		sys.exit("something went wrong.")

make_reference = False
do_mapping = False
do_sort = False
do_readgroup = False
do_realign = False
do_ref_map = False
do_populations = False

threads = ""
ref_name = ""
output_folder = ""
sample_folder = ""
popmap_path = ""

for i in sys.argv:
	if i == "--ref":
		make_reference = True

	elif i == "--map":
		do_mapping = True

	elif i == "--sort":
		do_sort = True

	elif i == "--RG":
		do_readgroup = True

	elif i == "--realign":
		do_realign = True

	elif i == "--ref_map":
		do_ref_map = True

	elif i == "--pop":
		do_populations = True

	elif i == "-t":
		index = sys.argv.index(i)
		threads  = sys.argv[index+1]

	elif i == "-r":
		index = sys.argv.index(i)
		ref_file  = sys.argv[index+1]

	elif i == "-D":
		index = sys.argv.index(i)
		ref_name  = sys.argv[index+1]

	elif i == "-o":
		index = sys.argv.index(i)
		output_folder  = sys.argv[index+1].rstrip("/")
		
	elif i == "-s":
		index = sys.argv.index(i)
		sample_folder  = sys.argv[index+1]

	elif i == "-p":
		index = sys.argv.index(i)
		popmap_path  = sys.argv[index+1]

os.chdir(output_folder)

popmap = []
with open (popmap_path) as popmap_file:
	for i in popmap_file:
		popmap.append(i.split("\t")[0])

#---------------Make reference--------------------------------------

if make_reference == True:
	ref_ending = ref_file.split(".")[-1]
	if ref_ending == "gz":
		ref_ending = ".fa.gz"
	else:
		ref_ending = ".fa"
	path_ref = output_folder + "/00reference/" + ref_name + ref_ending
	check_folder('00reference')
	execute_command("cp " + ref_file + " " + path_ref)
	execute_command("samtools faidx " + path_ref)
	execute_command("nice -n 19 java -Xmx60G -jar /home/biogeoanalysis/Programs/picard/picard.jar CreateSequenceDictionary R=" + path_ref + " O=" + path_ref.split(".")[0] + ".dict")
	execute_command("nice -n 19 bowtie2-build " + path_ref + " " + path_ref)

#---------------Map individuals to reference--------------------------------------

if do_mapping == True:
	check_folder('01mapped')
	check_folder('alignment_metrics')
	if make_reference == False:
		if os.path.isfile(output_folder + "/00reference/" + ref_name + ".fa") == True:
			path_ref = output_folder + "/00reference/" + ref_name + ".fa"
		elif os.path.isfile(output_folder + "/00reference/" + ref_name + ".fa.gz") == True:
			path_ref = output_folder + "/00reference/" + ref_name + ".fa".gz
		else:
			sys.exit("reference is required.")
	for indv in popmap:
		#execute_command("nice -n 19 bowtie2 -p " + threads + " --omit-sec-seq --score-min L,-0.8,-0.3 --met-file ./alignment_metrics/" + indv + ".log -x " + path_ref + " -U " + sample_folder + "/" + indv + ".fq.gz -S " + output_folder + "/01mapped/" + indv + ".sam")
		execute_command("nice -n 19 bowtie2 -p " + threads + " --omit-sec-seq --met-file ./alignment_metrics/" + indv + ".log -x " + path_ref + " -U " + sample_folder + "/" + indv + ".fq.gz -S " + output_folder + "/01mapped/" + indv + ".sam")

#---------------sort and convert sam files to bam--------------------------------------

if do_sort == True:
	check_folder("02sorted")
	for indv in popmap:
		execute_command("nice -n 19 java -Xmx60G -jar /home/biogeoanalysis/Programs/picard/picard.jar SortSam I=" + output_folder + "/01mapped/" + indv + ".sam O= " + output_folder + "/02sorted/" + indv + ".bam SO=coordinate")

#---------------Add readgroups to bam files (necessary for indel realigment)--------------------------------------

if do_readgroup == True:
	check_folder("03mappedSortGroup")
	for indv in popmap:
		execute_command("nice -n 19 java -Xmx60G -jar /home/biogeoanalysis/Programs/picard/picard.jar AddOrReplaceReadGroups I=" + output_folder + "/02sorted/" + indv + ".bam O=" + output_folder + "/03mappedSortGroup/" + indv + ".bam RGID=" + indv + ".bam RGLB=" + indv + ".bam RGPL=illumina RGPU=" + indv + ".bam RGSM=" + indv + ".bam")

#---------------index bam files and realign indels--------------------------------------

if do_realign == True:
	check_folder("04realigned")
	for indv in popmap:
		execute_command("samtools index " + output_folder + "/03mappedSortGroup/" + indv + ".bam")
		#Use GATK 3.8.1!!
		execute_command("nice -n 19 java -Xmx60G -jar /bin/GATK3.8 -T RealignerTargetCreator -nt " + threads + " -R " + path_ref + " -I " + output_folder + "/03mappedSortGroup/" + indv + ".bam -o " + output_folder + "/03mappedSortGroup/" + indv + ".bam.intervals")
		#Use GATK 3.8.1!!
		execute_command("nice -n 19 java -Xmx60G -jar /bin/GATK3.8 -T IndelRealigner -R " + path_ref + " -I " + output_folder + "/03mappedSortGroup/" + indv + ".bam -targetIntervals " + output_folder + "/03mappedSortGroup/" + indv + ".bam.intervals -maxReads 100000 -o " + output_folder + "/04realigned/" + indv + ".bam")

#---------------align and call snps using ref_map.pl (stacks 2.4)--------------------------------------

if do_ref_map == True:
	check_folder("05ref_map")
	execute_command('ref_map.pl -T ' + threads + ' --popmap ' + popmap_path + ' -o ' + output_folder + '/05ref_map --samples ' + output_folder + '/04realigned/')

#---------------select and filter snps using populations (stacks 2.4)--------------------------------------

if do_populations == True: 
	f_c = 'cat ' + output_folder + '/05ref_map/populations.sumstats.tsv | grep -v "^#" | cut -f 1,4 | sort -n | uniq | cut -f 1 | uniq -c | awk \'$1 <= 10 {print $2}\' > whitelist_refmap'
	print(f_c)
	os.system('echo "' + f_c + '" >> logfile')
	os.system(f_c) #using execute_commmand does not work. Not sure why but I suspect that subprocess.call doesn't handle the arguments as expected.
	
	check_folder("06populations") 
	execute_command('nice -n 19 populations --in_path ' + output_folder + '/05ref_map --out_path ' + output_folder + '/06populations --popmap ' + popmap_path + ' -R 0.5 --max_obs_het 0.65 --batch_size 15000 --vcf --threads ' + threads + ' --write_random_snp -W ' + output_folder + '/whitelist_refmap')

