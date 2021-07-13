#!/bin/bash

#Made by Dennis Larsson

#set current directory to variable wd (work directory)
wd=`pwd`
denovo_pw="/home/biogeoanalysis/RAD/spic28"
stacksfolder="stacks_m7n5M4"
popmap="popmap_spicGroup_splatche_sorted_spic28"

# denovo assembly + populations with -R 0.4 (max 60% missingness) and -max_obs_het 0.65 (max 65% obs. het.)
mkdir $denovo_pw/$stacksfolder
mkdir $denovo_pw/populations_R04_maxhet
denovo_map.pl -m 7 -M 4 -n 5 -T 12 -o $denovo_pw/$stacksfolder --samples /home/biogeoanalysis/RAD/RAD_samples --popmap $denovo_pw/${popmap}_opti -X populations:"-R 0.4 --max_obs_het 0.65"
populations --threads 12 --in_path $denovo_pw/$stacksfolder/ --out_path $denovo_pw/populations_R04_maxhet --popmap $denovo_pw/${popmap}_opti -R 0.4 --max_obs_het 0.65
# create whitelist of loci with max 10 snp from populations sumstat
cat $denovo_pw/$stacksfolder/populations.sumstats.tsv | grep -v "^#" | cut -f 1,4 | sort -n | uniq | cut -f 1 | uniq -c | awk '$1 <= 5 {print $2}' > $denovo_pw/whitelist_final_bowtie

# use whitelist to filter catalog using filter_catalog.py (this step also removes duplicates in catalog)
cp $denovo_pw/$stacksfolder/catalog.fa.gz $denovo_pw/
gunzip $denovo_pw/catalog.fa.gz
python3 ~/RAD/ref_map_scripts/filter_catalog.py -i $denovo_pw/catalog.fa -w $denovo_pw/whitelist_final_bowtie -o $denovo_pw/catalog_max10snp_60miss_hetfilt.fa

# Blast filtered_catalog and remove loci that belong to anything but spermatophyta
cd /home/biogeoanalysis/Programs/ncbi-blast-2.9.0+/bin 
./blastn -db "nt env_nt est_human htgs sts" -query $denovo_pw/catalog_max10snp_60miss_hetfilt.fa -out $denovo_pw/results.out -outfmt "10 delim=@ qseqid qlen ssciname sblastname sskingdom stitle evalue bitscore score length nident qcovs" -max_target_seqs 1 -num_threads 12
cd $wd
# parse and filter the blast blacklist (two first commented lines are obselete scripts)
#python3 ~/RAD/ref_map_scripts/blast_result_parse.py -i $denovo_pw/results.out
#python3 ~/RAD/ref_map_scripts/blacklist_filter.py -b $wd/blacklist -i $denovo_pw/catalog_max10snp_60miss_hetfilt.fa -o $denovo_pw/catalog_max10snp_60miss_hetfilt_blasted.fa
python3 ~/RAD/ref_map_scripts/blacklist_parse_filter.py -b $denovo_pw/results.out -c $denovo_pw/catalog_max10snp_60miss_hetfilt.fa -o $denovo_pw/catalog_max10snp_60miss_hetfilt_blasted.fa

## Run standard bowtie pseudo-refmap pipeline 
## read top of script to ensure you have installed the dependent programs properly
python3 ~/RAD/ref_map_scripts/bowtie_pipeline_v1.13.py -o $denovo_pw -s ~/RAD/RAD_samples -r $denovo_pw/catalog_max10snp_60miss_hetfilt_blasted.fa -D spicatum28_splatche -p $denovo_pw/${popmap} -t 12  --ref --map --sort --RG --realign --ref_map --pop

# Run additional snp filtering with populations if you want to use different settings 
mkdir $denovo_pw/06populations_pop_50miss
nice -n 19 populations --in_path $denovo_pw/05ref_map --out_path $denovo_pw/06populations_pop_50miss --popmap $wd/popmap_final_tet -r 0.65 -p 13 --max_obs_het 0.65 --batch_size 15000 --vcf --threads 12 --write_random_snp -W $denovo_pw/whitelist_refmap


