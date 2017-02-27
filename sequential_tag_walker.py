import os
import re
import sys
import subprocess
import shutil
import datetime
from datetime import datetime

# get all tags from the git repository in order and with date
git_log_result = subprocess.check_output(["git", "log", "--tags", "--date-order",  "--reverse",  "--simplify-by-decoration", "--pretty=%ai %d"])

# # get directory name and project name to create folders dynamically
directory = subprocess.check_output(["pwd"]).split()[0]
project_name = directory.decode('utf-8').split('/')[-1]

# # create folder to keep all the tags
#subprocess.call(["mkdir", "../"+project_name+"_tags"])

# #regex to eliminate folders that is not relevant for the analysis, like third party libraries and invisible files
file_regex = '\..*|sonar\.py' 
directory_regex = '\..*|vendor|thirdparty|(:?ex|s)amples|doc(:?s|uments)|bin|node' 
tags_regex = r"(\d\d\d\d\-\d\d\-\d\d\s\d\d:\d\d:\d\d)|\((tag: release-\d(?:[._-]\d+)+)\)"

counter = 0
last_tag = None
#last_tag = "4.0.0"
for line in git_log_result.decode('utf-8').split('\n'):
    # for each line has matches
    if re.search(tags_regex, line) is not None:
        m = re.findall(tags_regex, line)
        # has match fot tag and date (merge has date but not tag)
        if len(m) == 2:
            skip_tag = False
            # get result from the first tuple, first item (date)
            tag_date = m[0][0].split(' ')[0]
            # get result from the second tuple, second item (tag)
            tag = m[1][1].split(' ')[1]
            #These two comments are for debuggins porpuses only
            #print (m) 
            #print(tag)
            tag_number = re.findall(r"\d(?:[._-]\d+)+", tag)
            if last_tag is not None:
              tag_integers = tag_number[0].split('.')
              last_tag_integers = last_tag[0].split('.')
              #Uncomment following line for debugging
              #print (tag_integers)
              #print (last_tag_integers)
              sortest_lenght = len(tag_integers) if len(tag_integers) <= len(last_tag_integers) else len(last_tag_integers)
              for i in range(0,sortest_lenght):
                if int(tag_integers[i]) > int (last_tag_integers[i]):
                  break
                if int(tag_integers[i]) < int (last_tag_integers[i]):
                  #Uncomment this for debugging
                  #print ("skipping because {} < {}".format(tag_integers[i], last_tag_integers[i]) )
                  skip_tag = True
                  break
            if skip_tag:
              continue
            last_tag = tag_number
            #print(tag)
            # checkout into each of them
            subprocess.call(["git", "checkout" , tag])
    
            # create directory to place all the tags
            #folder_path = "../"+ project_name +"_tags/"+str(counter)+"."+tag
            #subprocess.call(["mkdir", folder_path])

            ## create sub directory src, to run sonar analysis
            #subprocess.call(["mkdir", folder_path+"/src"])

            ## copy checkout tag to its specific directory
            #subprocess.call(["cp", "-r",  "./" , folder_path+"/src"])

            # walk the folder to remove unwanted files and folders (invisible files and third party) 
            #for root, dirs, files in os.walk(folder_path +"/src"):
                #for f in files:
                    ## removes invisible files
                    #if re.match(file_regex, f) is not None:
                        #os.unlink(os.path.join(root, f))
                #for d in dirs:
                    ## regex to eliminate unwanted folders, like third party libraries and invisible files   
                    #if re.match(directory_regex, d) is not None:
                        #shutil.rmtree(os.path.join(root, d))
                        
            # create sonar-project.properties file 
            
            f = open("sonar-project.properties", "w")
            f.write("# Required metadata\n")
            
            f.write("sonar.projectBaseDir=" +os.getcwd()+"\n")
            f.write("sonar.projectDate=" + tag_date + "\n")

            f.write("sonar.projectKey=" +project_name+ "\n")
            f.write("sonar.projectName=" +project_name+ "\n")
            f.write("sonar.cfamily.build-wrapper-output.bypass=true\n")
            f.write("sonar.projectVersion=" +tag+ "\n")
            f.write("# Comma-separated paths to directories with sources (required)\n")
            f.write("sonar.sources=. \n")
            f.write("sonar.exclusions=sequential_tag_walker.py\n"

            # f.write("sonar.tests=" +project_name+ "\n")
            f.write("# Language\n")

            # project language should be changed accordingly
            #f.write("sonar.language=js\n")
            
            f.write("# Encoding of sources files\n")
            f.write("sonar.sourceEncoding=UTF-8\n")
            f.close()

            #subprocess.call(["sonar-scanner", '-X'])
            counter = counter + 1

            #print " # checkout: " + str(tag)
