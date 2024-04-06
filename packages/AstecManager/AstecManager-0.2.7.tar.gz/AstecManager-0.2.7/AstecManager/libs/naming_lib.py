import os
from morphonet.tools import imread
from numpy import np
from datetime import datetime
import xml.etree.ElementTree as ET

def backup_xml(xml_file):
    split_name = xml_file[1:len(xml_file)].split(".")
    backup_name = split_name[0] + "_backup." + split_name[1]
    os.system("cp " + str(xml_file) + " ." + str(backup_name))

def compute_cell_count(mars_path):
    count = -1
    image_first = imread(mars_path)
    if mars_path is not None:
        count = len(np.unique(image_first)) - 1
    return count

def compute_atlas():
    path = []
    path.append("./atlas/pm1.xml")
    path.append("./atlas/pm3.xml")
    path.append("./atlas/pm4.xml")
    path.append("./atlas/pm5.xml")
    path.append("./atlas/pm7.xml")
    path.append("./atlas/pm8.xml")
    path.append("./atlas/pm9.xml")
    return path

def generate_surface(exp_fuse, exp_post, begin, end, xmloutput, embryo_name, exp_intrareg):
    fuse_path =  "./"+embryo_name+"/INTRAREG/INTRAREG_" + str(exp_intrareg) + "/FUSE/FUSE_" + str(exp_fuse)
    fuse_template = os.path.join(fuse_path, embryo_name + "_intrareg_fuse_t%03d.nii").replace("'", "").replace('"', '')
    post_path = "./"+embryo_name+"/INTRAREG/INTRAREG_" + str(exp_intrareg) + "/POST/POST_" + str(exp_post)
    post_template = os.path.join(post_path, embryo_name + "_intrareg_post_t%03d.nii").replace("'", "").replace('"', '')
    os.system("conda run -n astec mc-cellProperties  -fusion-format " + str(
            fuse_template) + " -segmentation-format " + str(post_template) + " -first " + str(
            begin) + " -last " + str(end) + " -o " + str(
            xmloutput) + " -feature contact-surface -feature barycenter -v -v -v -v -v")

def generate_init_naming_parameters(cell_count, xml_folder, xml_file, embryo_name):
    atlas_path = compute_atlas()
    now = datetime.now()
    parameters_name = "init_naming" + str(now.timestamp()).replace('.', '') + ".py"
    final_file = os.path.join(xml_folder.replace(str(embryo_name) + "/", ""), xml_file)
    txt = ""
    txt += "inputFile = '" + str(final_file) + "'" + "\n"
    txt += "outputFile = '" + str(final_file) + "'" + "\n"
    txt += "cell_number = " + str(cell_count) + "\n"
    txt += 'atlasFiles = ' + str(atlas_path) + "\n"
    txt += "check_volume=False" + "\n"
    f = open(parameters_name, "w+")
    f.write(txt)
    f.close()
    return parameters_name

def generate_init_naming(xml_folder, xml_file, begin_time_name, embryo_name, exp_fuse, exp_post, begin, end,
                         exp_intrareg):
    print(" -> Generate init naming")
    xml_path = os.path.join(xml_folder, xml_file)
    mars_path = os.path.join(xml_folder, begin_time_name)
    source = open(xml_path)
    tree = ET.parse(source)
    tree = tree.getroot()
    lineage_elem = tree.find("cell_contact_surface")
    print("     - backup xml")
    backup_xml(xml_path)
    surface_xml = xml_path.replace("lineage", "lineage_surfaces")
    if lineage_elem is None:
        print("     - generate surfaces in side xml")
        generate_surface(exp_fuse, exp_post, begin, end, surface_xml, embryo_name, exp_intrareg)
        print("     - merging 2 xml")
        os.system(
            "conda run -n astec astec_embryoproperties -i " + xml_path + " " + surface_xml + " -o " + xml_path)
        print("     - cleaning temp xml")
        os.system("rm " + str(surface_xml))
    print("     - compute cell count from mars")
    cell_count = compute_cell_count(mars_path)
    print("     - generate naming parameter file")
    parameter_file = generate_init_naming_parameters(cell_count, xml_folder, xml_file, embryo_name)
    print("     - running naming")
    os.system("conda run -n ascidian ascidian_atlas_init_naming -v -v -v -p " + str(
        parameter_file))
    os.system("rm " + str(parameter_file))

def propagate_naming(xml_folder, xml_file, embryo_name):
    print(" -> Propagate naming")
    print("     - generate parameters")
    parameter_file,atlases_files = generate_prop_naming_parameters(xml_folder, xml_file, embryo_name)
    print("     - propagation of naming")
    os.system("conda run -n ascidian ascidian_atlas_naming -v -v -v -p " + str(
        parameter_file))
    print("     - cleaning")
    os.system("rm " + str(parameter_file))
    return atlases_files

def generate_prop_naming_parameters(xml_folder, xml_file, embryo_name):
    atlas_path = compute_atlas()
    atlases_files = []
    now = datetime.now()
    parameters_name = "prop_naming" + str(now.timestamp()).replace('.', '') + ".py"
    txt = ""
    final_file = os.path.join(xml_folder.replace(str(embryo_name) + "/", ""), xml_file)
    txt += "inputFile = '" + str(final_file) + "'" + "\n"
    txt += "outputFile = '" + str(final_file) + "'" + "\n"
    txt += "confidence_atlases_nmin = 2" + "\n"
    txt += "confidence_atlases_percentage = 0" + "\n"
    txt += 'atlasFiles = '+str(atlas_path) + "\n"
    atlases_files.append("pm9.xml")
    f = open(parameters_name, "w+")
    f.write(txt)
    f.close()
    return parameters_name,atlas_path