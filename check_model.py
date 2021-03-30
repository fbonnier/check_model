import os
from hbp_validation_framework import ModelCatalog
import numpy as np
import requests
from io import BytesIO
import json

main_repo = {"github": {"pattern": "https://github.com", "tar_url":"", "source": "", "file": "git-download.txt", "download_command": "git clone "},
             "cscs": {"pattern": "https://object.cscs.ch", "tar_url":"", "source": "", "file": "cscs-download.txt", "download_command": "wget -N "},
             "testing": {"pattern": "http://example.com", "tar_url":"", "source": "", "file": "no-download.txt", "download_command": ""},
             }

WORKDIR = os.environ["HOME"]

def get_repository_location(var_i_instance):
    # If source is archive, WGET archive file
    if (var_i_instance["source"].endswith(".tar") or var_i_instance["source"].endswith(".tar.gz") or var_i_instance["source"].endswith(".zip")):
        response = requests.get(tar_url, stream=True)
        if (response.ok):
            return ("wget -N --directory-prefix=" + WORKDIR + " " + tar_url)
        else :
            print ("Error :: '" + tar_url + "' Response status = " + str(response.status_code))

    # If source is git repo
    else :
        if (var_i_instance["source"].startswith(main_repo["github"]["pattern"])):
            # If model has version number, try to get archive file of version
            if (var_i_instance["version"]):
                tar_url = var_i_instance["source"] + "/archive/v" + var_i_instance["version"] + ".tar.gz"
                response = requests.get(tar_url, stream=True)
                if(response.ok):
                    return ("wget -N --directory-prefix=" + WORKDIR + " " + tar_url)

                else :
                    print("Error :: " + tar_url + " does not exists, try to clone git project.")
                    return ("git clone " + var_i_instance["source"] + " " + WORKDIR)
            else :
                # Git clone project
                return ("git clone " + var_i_instance["source"] + " " + WORKDIR)

    # Error :: the source does not exists or source pattern not taken into account
    print("Error :: Source '" + var_i_instance["source"] + " (" + var_i_instance["version"] + ")' does not exist or service not available.\n----- Exit FAIL")
    exit (1)

def get_unzip_instruction(var_download_command):
    if (var_download_command.endswith(".tar") or var_download_command.endswith(".tar.gz") or var_download_command.endswith(".zip")):
        filename = var_download_command.split("/")
        return ("arc -overwrite unarchive " + WORKDIR + "/" + filename[len(filename)-1] + " " + WORKDIR + "/" + os.environ["HBP_INSTANCE_ID"])

def generate_scriptfile (var_instance):

    f = open (WORKDIR + "/run_me.sh", "a")
    f.write("#!/bin/bash\n")
    runscript_file = os.environ["HBP_INSTANCE_ID"] + ".sh"

    # write download link into script file
    download_command = get_repository_location(var_instance)
    f.write(download_command + ";\n")

    # write extract command into script file
    instruction = get_unzip_instruction(download_command)
    f.write(instruction + ";\n")

    # CD to project base folder
    f.write("cd " + WORKDIR + "/" + os.environ["HBP_INSTANCE_ID"] + ";\n")
    f.write("while [ $(ls -l | grep -v ^d | wc -l) -lt 2 ]\ndo\nif [ -d $(ls) ]; then \ncd $(ls);\nfi\ndone" + "\n")

    # Error if 'HBP_INSTANCE_ID.sh' does not exists
    if (not os.path.isfile(WORKDIR + "/" + runscript_file)):
        print("Error :: " + WORKDIR + "/" + runscript_file + " does not exist.\n----- Exit FAIL")
        exit(1)
    f.write("mv " + WORKDIR + "/" + runscript_file + " ." + "\n")
    f.write("pwd; ls -alh;" + "\n")
    f.write("chmod +x ./" + runscript_file + "\n")
    f.write("echo \"TODO : Get INPUT and RESULTS\"" + "\n")
    f.write("./" + runscript_file + "\n")

    f.close()

def check_1_model_instance (var_mc, var_instance_id):

    # Error if model-instance-id does not exist
    i_instance = var_mc.get_model_instance(instance_id=var_instance_id)
    if (len(i_instance)>0):
        # Write script that download model
        generate_scriptfile (i_instance)

    else :# Error :: the instance does not exist
        print("Error :: Instance '" + var_instance_id + "' does not exists.\n----- Exit FAIL")
        exit (1)



def check_1_model (var_mc, var_model_id):

    # Error when the model does not exists
    # TODO
    var_list_model_instance = var_mc.list_model_instances(model_id=var_model_id)

    # Error when the model does not have any instance
    if (len(var_list_model_instance) == 0):
        print ("Error :: Model '" + var_model_id + "' does not have any instance.\n----- Exit FAIL")
        exit (1)

    for i_instance in var_list_model_instance:
        check_1_model_instance (var_mc, i_instance["id"])


if __name__ == "__main__":


    # Check Environment variables exist
    if (not os.environ.get("HBP_INSTANCE_ID")):
        print ("Error :: HBP_INSTANCE_ID must be set.\n----- Exit FAIL")
        exit (1)
    if (not os.environ.get("HBP_USER")):
        print ("Error :: HBP_USER must be set.\n----- Exit FAIL")
        exit (1)
    if (not os.environ.get("HBP_PASS")):
        print ("Error :: HBP_PASS must be set.\n----- Exit FAIL")
        exit (1)

    # Connect to HBP Model Catalog
    mc = ModelCatalog(os.environ["HBP_USER"], os.environ["HBP_PASS"])
    os.environ["HBP_AUTH_TOKEN"]=mc.auth.token

    open ("run_me.sh", "w").close()

    # Check if WORKDIR environment variable exists and set WORKDIR
    WORKDIR = os.environ.get("WORKDIR", os.environ["HOME"])

    print (WORKDIR)
    # check_1_model (mc, os.environ["HBP_MODEL_ID"])
    check_1_model_instance (mc, os.environ["HBP_INSTANCE_ID"])

    # Exit Done ?
    print ("Done.\n ----- Exit SUCCESS")
