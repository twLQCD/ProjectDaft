import sys
import os
import re
import time
from daftlistings import Daft, SearchType
import xml.etree.ElementTree as et
from search_sender import Search_Sender

def check_new(key, my_dict):
    new_props = False
    locations = list(my_dict[key].keys())
    for locs in locations:
        if (len(my_dict[keys][locs]) != 0 and new_props == False):
            new_props = True
                
    return new_props

def write_props_to_files(my_dict):
    
    keys = list(my_dict.keys())
    for users in keys:
        tmp = users.split('@')
        filename_out = tmp[0] + '_property_lists.txt'
        fileout = open(filename_out, 'w')
        locations = list(my_dict[users].keys())
        for elems in locations:
            fileout.write(elems + ':\n')
            fileout.write('\n')
            for props in my_dict[users][elems]:
                fileout.write(props.title + '\n')
                fileout.write(props.price + '\n')
                fileout.write(props.daft_link + '\n')
                fileout.write('\n')
        fileout.close()

class Property_Io:
    
    saved_properties = {}
    new_property_list = True
    
    
    def __init__(self, xml_in):
        self.xml_in = xml_in
        self.saved_properties_file = xml_in
        filein = open(xml_in,'a')
        if (os.stat(xml_in).st_size != 0):
            self.new_property_list = False
            print('Found saved properties')
        filein.close()
            
    def read(self):
        if not self.new_property_list:
            self.tree = et.parse(self.saved_properties_file)
            self.root = self.tree.getroot()
            for child in self.root:
                property_list = []
                for elem in child.findall("prop"):
                    property_list.append(elem.text)
            
                self.saved_properties[child.attrib["name"]] = property_list
        
    def write(self):
        keys = list(self.saved_properties.keys())
        tree_out = et.Element("Save_List")
        for users in keys:
            root = et.SubElement(tree_out, "User")
            root.set("name", users)
            for props in self.saved_properties[users]:
                    child = et.SubElement(root, "prop")
                    child.text = props
        out_xml = et.tostring(tree_out)
        with open(self.xml_in, "wb") as f:
            f.write(out_xml)
                
        f.close()
    
    def add_to_saved_properties(self, property_list):
        #check against the saved property list
        #and remove the repeated ones
        if not self.new_property_list:
            users = list(self.saved_properties.keys())
            for keys in users:
                for elems in self.saved_properties[keys]:
                    for keys in users:
                        locations = list(property_list[keys])
                        for locs in locations:
                            for elem in property_list[keys][locs]:
                                if (elem.daft_link == elems):
                                    property_list[keys][locs].remove(elem)
                                
        #add the survivors to the saved property list
            for keys in users:
                locations = list(property_list[keys])
                for locs in locations:
                    for elem in property_list[keys][locs]:
                        self.saved_properties[keys].append(elem.daft_link)
        else:
            users = list(property_list.keys())
            for keys in users:
                self.saved_properties[keys] = []
                locations = list(property_list[keys])
                for locs in locations:
                    for elems in property_list[keys][locs]:
                        self.saved_properties[keys].append(elems.daft_link)
                    
               
    def return_saved_properties(self):
        return self.saved_properties

class Params_Reader:
    
    params = {}
    
    def __init__(self, xml_in):
        self.xml = xml_in
        

    def read(self):
        tree = et.parse(self.xml)
        root = tree.getroot()
        for child in root:
            location_dict = {}
            for elem in child.findall("Location"):
                params_dict = {}
                for elems in elem:
                    params_dict[elems.tag] = elems.text
                
                location_dict[elem.attrib["name"]] = params_dict
                
            self.params[child.attrib["name"]] = location_dict
            
    def print_params(self):
        print(self.params)
        
    def keys(self):
        return self.params.keys()
    
    def return_params(self):
        return self.params
    
class Property_Searcher:
    
    property_list = {}
    
    def __init__(self, xml_in):
        self.reader = Params_Reader(xml_in)
        self.reader.read()
        self.search_params = (self.reader).return_params()
        self.users = list((self.search_params).keys())
        
    def print_params(self):
        print(self.search_params)
        
    
    def search(self):
        for users in self.users:
            locations = list(self.search_params[users].keys())
            location_dict = {}
            for keys in locations:
                self.daft = Daft()
                self.daft.set_search_type(SearchType.RESIDENTIAL_RENT)
                self.daft.set_location(keys)
                print(keys)
                self.daft.set_min_price(int(self.search_params[users][keys]["rent_min"]))
                self.daft.set_max_price(int(self.search_params[users][keys]["rent_max"]))
                location_dict[keys] = self.daft.search()
                for elems in location_dict[keys]:
                    price = re.sub('[^0-9]','',elems.price)
                    if (int(price) > int(self.search_params[users][keys]["rent_max"]) ):
                        location_dict[keys].remove(elems)
                        
            self.property_list[users] = location_dict
            
    def return_users(self):
        return list(self.property_list.keys())
    
    def return_user_search_locations(self, key):
        return list(self.property_list[key])
    
    def return_property_list(self):
        return self.property_list
    
    def print_property_list(self):
        print(self.property_list)

if __name__ == '__main__':

    if (len(sys.argv) != 4):
        print("usage: main.py ini.xml sending_email sending_email_password")
        quit(1)

    searching = True
    while searching:
        my_search = Property_Searcher(sys.argv[1])
        my_search.search()
        my_dict = my_search.return_property_list()
        my_saved = Property_Io('../user_saved/saved_props.xml')
        my_saved.read()

        my_saved.add_to_saved_properties(my_dict)
        my_saved.write()
        users = list(my_dict.keys())
        for keys in users:
            if check_new(keys, my_dict):
                print('Found new properties')
                write_props_to_files(my_dict)        
                send_off = Search_Sender(keys, sys.argv[2], sys.argv[3])
            else:
                print('Did not find new properties')
                
        time.sleep(600)
        print('Restarting Search...')
 