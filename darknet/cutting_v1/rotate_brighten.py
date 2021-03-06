import os
from PIL import Image, ImageEnhance
import xml.dom.minidom
from random import uniform
from shutil import copy2

def scan_files(directory, prefix=None, postfix=None):
    files_list = []

    for root, sub_dirs, files in os.walk(directory):
        for special_file in files:
            if postfix:
                if special_file.endswith(postfix):
                    files_list.append(os.path.join(root, special_file))
            elif prefix:
                if special_file.startswith(prefix):
                    files_list.append(os.path.join(root, special_file))
            else:
                files_list.append(os.path.join(root, special_file))

    return files_list
    
def rotate(xml_name):
    jpg_name_pre = os.path.splitext(xml_name)[0]
    jpg = Image.open(jpg_name_pre + ".jpg")
    jpg.rotate(90).save(jpg_name_pre + "_r90.jpg")
    jpg.rotate(180).save(jpg_name_pre + "_r180.jpg")
    jpg.rotate(270).save(jpg_name_pre + "_r270.jpg")
    jpg.close()

def gen_xml(xml_name):
    DOMTree = xml.dom.minidom.parse(xml_name)
    collection = DOMTree.documentElement
    filename = collection.getElementsByTagName("filename")
    objects = collection.getElementsByTagName("object")
    
    w = collection.getElementsByTagName("width")[0]
    w_val = int(w.firstChild.nodeValue)
    h = collection.getElementsByTagName("height")[0]
    h_val = int(h.firstChild.nodeValue)
    
    xmins, ymins, xmaxs, ymaxs = [], [], [], []
    for object in objects:
        xmin = object.getElementsByTagName("xmin")[0]
        xmins.append(int(xmin.firstChild.nodeValue))
        xmax = object.getElementsByTagName("xmax")[0]
        xmaxs.append(int(xmax.firstChild.nodeValue))
        ymin = object.getElementsByTagName("ymin")[0]
        ymins.append(int(ymin.firstChild.nodeValue))
        ymax = object.getElementsByTagName("ymax")[0]
        ymaxs.append(int(ymax.firstChild.nodeValue))
        
    # rotate 90
    xml_name_new = os.path.splitext(xml_name)[0] + "_r90.xml"
    filename[0].firstChild.replaceWholeText(os.path.basename(xml_name_new))
    i = 0
    for object in objects:
        xmin_val, ymin_val, xmax_val, ymax_val = xmins[i], ymins[i], xmaxs[i], ymaxs[i]
        i += 1
        xmin = object.getElementsByTagName("xmin")[0]
        xmax = object.getElementsByTagName("xmax")[0]
        ymin = object.getElementsByTagName("ymin")[0]
        ymax = object.getElementsByTagName("ymax")[0]
        xmin.firstChild.replaceWholeText(str(ymin_val))
        ymin.firstChild.replaceWholeText(str(w_val-xmax_val))
        xmax.firstChild.replaceWholeText(str(ymax_val))
        ymax.firstChild.replaceWholeText(str(w_val-xmin_val))    
    w.firstChild.replaceWholeText(str(h_val))
    h.firstChild.replaceWholeText(str(w_val))     
    with open(xml_name_new, 'w') as newfile:
        DOMTree.writexml(newfile)
        
    # rotate 180
    xml_name_new = os.path.splitext(xml_name)[0] + "_r180.xml"
    filename[0].firstChild.replaceWholeText(os.path.basename(xml_name_new))
    i = 0
    for object in objects:
        xmin_val, ymin_val, xmax_val, ymax_val = xmins[i], ymins[i], xmaxs[i], ymaxs[i]
        i += 1
        xmin = object.getElementsByTagName("xmin")[0]
        xmax = object.getElementsByTagName("xmax")[0]
        ymin = object.getElementsByTagName("ymin")[0]
        ymax = object.getElementsByTagName("ymax")[0]
        xmin.firstChild.replaceWholeText(str(w_val-xmax_val))
        ymin.firstChild.replaceWholeText(str(h_val-ymax_val))
        xmax.firstChild.replaceWholeText(str(w_val-xmin_val))
        ymax.firstChild.replaceWholeText(str(h_val-ymin_val))    
    w.firstChild.replaceWholeText(str(w_val))
    h.firstChild.replaceWholeText(str(h_val))     
    with open(xml_name_new, 'w') as newfile:
        DOMTree.writexml(newfile)
        
    # rotate 270
    xml_name_new = os.path.splitext(xml_name)[0] + "_r270.xml"
    filename[0].firstChild.replaceWholeText(os.path.basename(xml_name_new))
    i = 0
    for object in objects:
        xmin_val, ymin_val, xmax_val, ymax_val = xmins[i], ymins[i], xmaxs[i], ymaxs[i]
        i += 1
        xmin = object.getElementsByTagName("xmin")[0]
        xmax = object.getElementsByTagName("xmax")[0]
        ymin = object.getElementsByTagName("ymin")[0]
        ymax = object.getElementsByTagName("ymax")[0]
        xmin.firstChild.replaceWholeText(str(h_val-ymax_val))
        ymin.firstChild.replaceWholeText(str(xmin_val))
        xmax.firstChild.replaceWholeText(str(h_val-ymin_val))
        ymax.firstChild.replaceWholeText(str(xmax_val)) 
    w.firstChild.replaceWholeText(str(h_val))
    h.firstChild.replaceWholeText(str(w_val))        
    with open(xml_name_new, 'w') as newfile:
        DOMTree.writexml(newfile)

def brighten(xml_name):
    jpg_name_pre = os.path.splitext(xml_name)[0]
    jpg = Image.open(jpg_name_pre + ".jpg")
    factor = uniform(0.8, 1.2)
    jpg_name_new = jpg_name_pre + "_b" + str(factor)[:5] + ".jpg"
    ImageEnhance.Brightness(jpg).enhance(factor).save(jpg_name_new)
    jpg.close()
    xml_name_new = os.path.splitext(jpg_name_new)[0] + ".xml"
    copy2(xml_name, xml_name_new)        
        
def main(path):
    xml_names = scan_files(path, postfix=".xml")
    for xml_name in xml_names:
        rotate(xml_name)
        gen_xml(xml_name)
        brighten(xml_name)
    
if __name__ == "__main__":
    #path = os.getcwd()
    path = os.path.join(os.getcwd(), "train")
    main(path)