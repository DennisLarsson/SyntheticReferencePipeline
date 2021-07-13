import sys
#Made by Dennis Larsson

for i in sys.argv:
	if i == "-w":
		index = sys.argv.index(i)
		whitelist_file_path = sys.argv[index+1]
		#print (whitelist_file_path)
		
	elif i == "-i":
		index = sys.argv.index(i)
		catalog_path = sys.argv[index+1]
		#print (catalog_path)
		
	elif i == "-o":
		index = sys.argv.index(i)
		output_file_path = sys.argv[index+1]
		#print (output_file_path)
		
whitelist = []
with open (whitelist_file_path) as whitelist_file:
	for i in whitelist_file:
		whitelist.append('>' + i.rstrip())

with open (catalog_path) as catalog_file:
	catalog_list = catalog_file.readlines()

output_file = open(output_file_path, 'a')
i=0
m=0
while i < len(whitelist):
	#print (whitelist[i] + " " + catalog_list[m].split(' ')[0])
	while whitelist[i] != catalog_list[m].split(' ')[0]:
		m += 2
	output_file.write(catalog_list[m] + catalog_list[m+1])
	#print(str(i) + " " + str(m))
	i+=1
	m+=2

output_file.close()
