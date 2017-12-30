import xml.etree.cElementTree as et
import pandas as pd
import re
from urllib.request import urlopen

depth=0
record = {}
allrecords=[]
namespaces=[]

df = pd.DataFrame()

def is_not_empty(any_structure):
    if any_structure:
        #print('Structure is not empty.')
        return True
    else:
        #print('Structure is empty.')
        return False
 
#convert XML to pandas.DataFrame by iterating through XML tree

# Test sources:
# http://online.effbot.org/rss.xml
# http://api.worldbank.org/v2/indicators
    
for event, node in et.iterparse(urlopen("http://api.worldbank.org/v2/indicators"), ['start', 'end', 'start-ns', 'end-ns']):

    if event == "start-ns":
        namespaces.insert(0, node)
        print(namespaces)

    elif event == "end-ns":
        namespaces.pop(0)

    elif event == 'end':
        depth -= 1        #come back up a level in the tree
        #print('end - ', node.tag)
        if depth is 1:    # 1 = root level, means we have exited reading the row
            allrecords.append(record)
            #print('Row: ')
            #print(record)
            record = {}   #reset row record

    elif event == 'start':
        depth += 1        # 1 = root (whole table), 2 = row, 3+ = cols
        #print('start - ', node.tag)
        #print ('DATA:: depth: ', depth, 'tag: ', node.tag, 'attrib: ', node.attrib, 'text: ', node.text)

        if is_not_empty(namespaces):
            string = '{'+namespaces[0][1]+'}'
            node.tag = node.tag.replace(string, '')

        if depth>1:     # levels 2+ means we are inside a row
            #if there are attriutes set, then we need to decode into further rows:
            d = node.attrib
                
            if is_not_empty(d):
                for k, v in d.items():
                    record[node.tag + '-' + k] = v

                    if node.text is not None:        # skip if text is None (empty)
                        match_obj = re.search('\w', node.text)
                        # we want .text to have alphanumeric characters
                        # for some reason XML records with no text content were coming back as '/n' + random no of spaces
                        if is_not_empty(match_obj):
                            record[node.tag + '-' + k + '-' + 'desc'] = node.text
                            
            else:
                if node.text is not None:        # skip if text is None (empty)
                    match_obj = re.search('\w', node.text)
                    # we want .text to have alphanumeric characters
                    # for some reason XML records with no text content were coming back as '/n' + random no of spaces
                    if is_not_empty(match_obj):
                        record[node.tag] = node.text

df = pd.DataFrame(allrecords)
df.head(10)
