import os
import shutil
from zipfile import ZipFile
from xml.etree import ElementTree
from xml.etree.ElementTree import Element as XElement  # shortened "XML Element"

from ..geo.construction import Construction
from ..geo.lib_commands import Command
from ..geo.lib_vars import *

temp_path = os.path.join(os.getcwd(), "temp")

#--------------------------------------------------------------------------

def rgb_to_hex(r, g, b):
    return '#{:02x}{:02x}{:02x}'.format(r, g, b)

def get_constr_xelem(ggb_path: str): # -> XElement:
    try:    
        os.mkdir(temp_path)
    except FileExistsError:
        pass
    shutil.copyfile(ggb_path, os.path.join(temp_path, "temp.ggb"))
    
    ggb = ZipFile(os.path.join(temp_path, "temp.ggb"))
    ggb.extractall(temp_path)
    ggb.close()
    os.remove(os.path.join(temp_path, "temp.ggb"))
    
    tree = ElementTree.parse(os.path.join(temp_path, "geogebra.xml"))
    root = tree.getroot()
    
    shutil.rmtree(temp_path)
    
    return root.find("construction")

def parse(constr_xelem: XElement, debug = False): # -> Construction:
    constr = Construction()
    xelems_left_to_pass = 0

    style = {}
    
    for xelem in constr_xelem:
        if xelem.tag == "element":
            name = xelem.attrib['label']
            #print(f'ELEMENT {name}')
            if xelem.attrib["type"] != "numeric":
                style[name] = {}

                elem = xelem.find("decoration")
                if elem is not None: 
                    style[name]['lines'] = int(elem.attrib['type'])
                    if xelem.attrib['type'] == 'angle':
                        style[name]['lines'] += 1
                       
                elem = xelem.find("show")
                if elem is not None: 
                    style[name]['show_element'] = (elem.attrib['object'] == 'true')
                    style[name]['show_label'] = (elem.attrib['label'] == 'true')
                
                elem = xelem.find("labelMode")
                if elem is not None:
                    caption = xelem.find("caption")
                    if (elem.attrib['val'] == '3') & (caption is not None):
                        style[name]['label'] = caption.attrib['val']
                        
                elem = xelem.find("labelOffset")
                if elem is not None: 
                    style[name]['offset'] = [float(elem.attrib['x']) / 100, -float(elem.attrib['y']) / 100]
 
                elem = xelem.find("arcSize")
                if elem is not None: 
                    if xelem.attrib['type'] == 'angle':
                        style[name]['r_offset'] = (float(elem.attrib['val']) - 30) / 30
                        
                elem = xelem.find("objColor")
                if elem is not None:
                    r, g, b, a = int(elem.attrib['r']), int(elem.attrib['g']), int(elem.attrib['b']), float(elem.attrib['alpha'])
                    if xelem.attrib['type'] in ['angle', 'polygon', 'arc', 'circle']:
                        style[name]['fill'] = rgb_to_hex(r, g, b)
                        style[name]['fill_opacity'] = a
                    lineStyle = xelem.find("lineStyle")
                    if lineStyle is not None:
                        thick, tt, op = lineStyle.attrib['thickness'], lineStyle.attrib['type'], float(lineStyle.attrib['opacity'])
                        if xelem.attrib['type'] in ['angle', 'segment', 'arc', 'circle']:
                            style[name]['stroke'] = rgb_to_hex(r, g, b)
                            #style[name]['stroke_opacity'] = op / 255
                            #style[name]['stroke_width'] = thick
                            if int(tt) > 0: style[name]['stroke_dash'] = 0.65
                        
        if xelems_left_to_pass:
            xelems_left_to_pass -= 1
            continue

        if xelem.tag == "expression":
            #xelems_left_to_pass = 1
            continue
        if xelem.tag == "command":
            comm_name = xelem.attrib["name"]
            if comm_name == "PointIn":
                xelems_left_to_pass = 1
                continue
            
            input_xelem = xelem.find("input")
            output_xelem = xelem.find("output")
            
            constr.add(Command(comm_name, list(input_xelem.attrib.values()), list(output_xelem.attrib.values())))
            xelems_left_to_pass = len(output_xelem.attrib)
            continue
        
        # Here xelem has to be a commandless point or numeric (Var)
        
        if xelem.tag == "element":
            if xelem.attrib["type"] == "point":
                coords = list(xelem.find("coords").attrib.values())
                coords.pop(-1) #  removing z coordinate
                constr.add(Command("Point", coords, xelem.attrib["label"]))
                continue
            if xelem.attrib["type"] == "numeric":
                value_xelem = xelem.find("value")
                constr.add(Var(xelem.attrib["label"], float(value_xelem.attrib["val"])))
                continue
            if xelem.attrib["type"] == "angle":
                value_xelem = xelem.find("value")
                constr.add(Var(xelem.attrib["label"], AngleSize(float(value_xelem.attrib["val"]))))
                continue
        
        raise ElementTree.ParseError(f"Unexpected XElement met:\n\t<{xelem.tag}>, {xelem.attrib}")

    constr.rebuild(debug = debug)

    #styling elements
    for name in style:
        for key in style[name]:
            #print(f'STYLE >> {name} >> {key} = {style[name][key]}')
            if key == 'show_element':
                constr.element(name).visible = style[name][key]
                continue
            constr.element(name).style[key] = style[name][key]

    return constr

def load(ggb_path: str, debug = False): # -> Construction:
    constr_xelem = get_constr_xelem(ggb_path)
    constr = parse(constr_xelem, debug = debug)
    
    return constr
