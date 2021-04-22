import pathlib as pl
import time
import warnings
from collections import OrderedDict
import re
import pandas as pd
from bs4 import BeautifulSoup as BS
from selenium import webdriver

from Utilities import Read_Excel
from Main import CTO_Extraction_Removal
# from html_table_parser import HTMLTableParser
from Utilities.Environment_Selection import Portal_Selection

warnings.filterwarnings('ignore')
from selenium.webdriver.chrome.options import Options

chrome_options = Options()
# chrome_options.add_argument("--headless")
chrome_options.add_argument("--test-type")
chrome_options.add_argument("--disable-extensions")
chrome_options.add_argument("start-maximized")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("user_agent=Course5I_Automation_Enablement_QC_NA")

abspath = pl.Path(__file__).parent.absolute()
abs = str(abspath)
Chrome_Driver_Path = str(abspath) + '\\ChromeDriver\\chromedriver.exe'

opts = Options()
opts.add_argument("userAgent = Course5I_Automation_MTM_Removal")
driver = webdriver.Chrome(executable_path=Chrome_Driver_Path, chrome_options=opts)
driver.maximize_window()

Input_template, final_path = Read_Excel.Read_Excel()
global Spec_List
Spec_List = []

web_url, main_url = Portal_Selection()


def MTM_Specs_Extraction():
    global soup
    global r
    global MTM_Specs
    global All_models_link
    global Part_Number_set
    global Specification_name_list
    All_models_link = ""
    if Input_template.loc[r, 'Action to perform'] == "MTM Addition":
        All_models_link = soup.find('h2', {'class': 'tabbedBrowse-title'})
        if (All_models_link.find('a')):
            All_models_link = All_models_link.find('a').get('href')
            All_models_link = web_url + "/us/en/p/" + All_models_link
            print(All_models_link)
            driver.get(All_models_link)
            time.sleep(6)
            soup = BS(driver.page_source, 'lxml')
        else:
            driver.get(url)
            time.sleep(5)
            soup = BS(driver.page_source, 'lxml')
    if Input_template.loc[r, 'Action to perform'] == "MTM Removal":
        All_models_link = url
        driver.get(url)
        time.sleep(6)
        soup = BS(driver.page_source, 'lxml')

    No_of_Products = len(soup.find_all('div', {
        'class': 'tabbedBrowse-productListing-featureList featureList-bulleted featureList-linedRows'}))
    # print(No_of_Products)

    Material_list = []
    MTM_Specs = pd.DataFrame()
    # MTM_Specs

    if No_of_Products == 0:
        # print("Series page has only one material")
        Title_set = []
        Description_set = []
        if (soup.find('div', {'class': 'partNumber'})):
            Part_Number = soup.find('div', {'class': 'partNumber'})
            if Part_Number:
                Part_Number_set = Part_Number.text.strip().split(':')[1]
            elif soup.find('button', {
                'class': 'product_detail_pages_models_form_submit button-called-out tabbedBrowse-productListing-footer-button-first button-full'}):
                CTO_PN = soup.find('button', {
                    'class': 'product_detail_pages_models_form_submit button-called-out tabbedBrowse-productListing-footer-button-first button-full'})
                Part_Number_set = CTO_PN.get('data-productcode')
            elif driver.find_elements_by_xpath("//div[@id='singlesku-configure-summary']/div[2]/div[1]//input"):
                Part_Number_set = []
                CTO_PN = driver.find_elements_by_xpath("//div[@id='singlesku-configure-summary']/div[2]/div[1]//input")
                # print(CTO_PN)
                for c in CTO_PN:
                    var = c.get_attribute('productcode')
                    # print(var)
                    Part_Number_set.append(var)

                Part_Number_set = [ele for ele in Part_Number_set if ele]
                print(Part_Number_set)

            # print("Part Number-----------------------------",Part_Number)
            Tech_Specs = soup.find_all('ul', {'class': 'configuratorItem-mtmTable'})
            Length_of_Specs = len(soup.find_all('li', {'class': 'configuratorItem-mtmTable-row cf'}))
            print(Length_of_Specs)
            for i in Tech_Specs:
                Title = i.find_all('h4', {'class': 'configuratorItem-mtmTable-title'})
                Description = i.find_all('p', {'class': 'configuratorItem-mtmTable-description'})
                for rx in range(Length_of_Specs):
                    print(Title[rx].text.split()[0])
                    Title_set.append(Title[rx].text.split()[0])
                    print(Description[rx].text.strip())
                    Description_set.append(Description[rx].text.strip())
            MTM_Specs = pd.DataFrame(Description_set, index=Title_set)
            MTM_Specs = MTM_Specs.transpose()
            MTM_Specs['Part Number'] = Part_Number_set
            MTM_Specs.set_index("Part Number", inplace=True)



    else:
        count_ct0 = 0
        # driver.get(All_models_link)
        CTO_series = ""
        # print("Series page has more than one Material")
        Products_List = soup.find_all('div', {
            'class': 'tabbedBrowse-productListing-featureList featureList-bulleted featureList-linedRows'})
        CTO_series = soup.find_all('div', {'class': 'claim-wrapper'})
        CTO_series_footer = soup.find_all('form', {'class': 'tabbedBrowse-productListing-footer-form'})
        Total_features = len(Products_List[0].find_all('dd'))
        print("Total number of features-------------------------------------", Total_features)
        Specification_name_list = []
        Part_Number_set = []
        for i in range(No_of_Products):
            Part_Number_list = \
                soup.find_all('li', {'class': 'tabbedBrowse-productListing-container only-allow-small-pricingSummary'})[
                    i]
            Part_Number = Part_Number_list.find('div', {'class': 'partNumber'})
            if Part_Number:
                Part_Number = Part_Number.text.strip().split(':')[1].replace(' \xa0', "")
                print("PartNumber---------------------------------------", Part_Number)
                Part_Number_set.append(Part_Number)
            else:
                for cto in CTO_series_footer:
                    # print(i.get('id'))
                    # CTO_len = len(cto.get('id'))
                    if cto.get('id') == None:
                        pass
                    else:
                        CTO_len = len(cto.get('id'))
                        # print(CTO_len)
                        # print(len(i.get('id')))
                        if CTO_len == 31:
                            CTO = cto.get('id')
                            CTO_no = CTO[-15:]
                            print("Part Number----------------------------------", CTO_no)
                            if CTO_no not in Part_Number_set:
                                Part_Number_set.append(CTO_no)

            # driver.get(url)
            if Input_template.loc[r, 'Region/Country'] == 'US':
                for j in range(Total_features):
                    print("feature----------------------------", j)
                    if (Products_List[i].find('dt').get('data-term')):
                        Specification_1 = Products_List[i].find_all('dt')[j].get('data-term')
                        print("Feature Name----------------------------------------", Specification_1)
                        Specification = Products_List[i].find_all('dd')[j].text
                        # Specification_name_list.add(Specification_1)
                    else:
                        Specification_1 = Products_List[i].find_all('dt')[j].text
                        print("Feature Name-----------------------", Specification_1)
                        Specification = Products_List[i].find_all('dd')[j].text
                        # Specification_name_list.add(Specification_1)
                    if Specification_1 in Specification_name_list:
                        pass
                    else:
                        Specification_name_list.append(Specification_1)

                    print(Specification)
                    MTM_Specs.loc[i, j] = Specification

            if Input_template.loc[r, 'Region/Country'] == 'CA':
                for j in range(Total_features):
                    print("feature----------------------------", j)
                    if (Products_List[i].find('dt').get('data-term')):
                        Specification_1 = Products_List[i].find_all('dt')[j].get('data-term')
                        print("Feature Name-----------------------", Specification_1)
                        Specification = Products_List[i].find_all('dd')[j].text
                        # Specification_name_list.add(Specification_1)
                    else:
                        Specification_1 = Products_List[i].find_all('dt')[j].text
                        print("Feature Name-----------------------", Specification_1)
                        Specification = Products_List[i].find_all('dd')[j].text
                        # Specification_name_list.add(Specification_1)
                    if Specification_1 in Specification_name_list:
                        pass
                    else:
                        Specification_name_list.append(Specification_1)

                    print(Specification)
                    MTM_Specs.loc[i, j] = Specification

        # Specification_name_list.append('Operating Language')
        MTM_Specs.columns = Specification_name_list
        MTM_Specs['Part Number'] = Part_Number_set
        MTM_Specs.set_index("Part Number", inplace=True)

        MTM_Specs.rename(columns={"Hard": "Storage", "Hard Drive": "Storage", "WiFi": "Connectivity",
                                  "Wireless": "Connectivity", "Hard Drive": "Storage",
                                  "WiFi Wireless LAN Adapters": "Connectivity",
                                  "Display Type": "Display"}, inplace=True)

        if 'Operating System Language' in MTM_Specs.columns:
            MTM_Specs = MTM_Specs.drop(['Operating System Language'], axis=1)


CTO_DF, Final_Storage_CTO, memory_qty = CTO_Extraction_Removal.CTO_Extraction_Removal(web_url)
rows_index_MTM = Input_template['Part Number'].index

# print(rows_index_MTM)
for r in rows_index_MTM:
    # print(r)
    Input_material = str(Input_template.loc[r, 'Part Number'])
    # print("Material from Input File ---------------------------",Input_material)

    if Input_template.loc[r, 'Region/Country'] == 'US' or Input_template.loc[r, 'Region/Country'] == 'North America':
        url = web_url + '/us/en/p/' + str(Input_template.loc[r, 'Article Number']).strip()
    elif Input_template.loc[r, 'Region/Country'] == 'CA' or Input_template.loc[r, 'Region/Country'] == 'North America':
        url = web_url + '/ca/en/p/' + str(Input_template.loc[r, 'Part Number']).strip()

    #  print("URL-----------------------------", url)
    driver.switch_to.window(driver.window_handles[0])
    driver.get(url)
    time.sleep(6)
    soup = BS(driver.page_source, 'lxml')
    time.sleep(4)
    MTM_Specs_Extraction()
    print('MTM Specs looks like ', MTM_Specs)

    # print(MTM_Specs.columns)
    print(MTM_Specs['Processor'])
    print(CTO_DF['Processor'])
    # print(MTM_Specs['Processor'])
    # print(MTM_Specs['Connectivity'])
    print("All Columns names :", MTM_Specs.columns)

    Row_count = MTM_Specs.shape
    Row_count = Row_count[0]

# Processor Validation
if 'Processor' in MTM_Specs.columns or 'Processor' in CTO_DF.columns :
    if 'Processor' in MTM_Specs.columns:
        MTM_Processors = list(MTM_Specs['Processor'])
    else:
        MTM_Processors = []

    if 'Processor' in CTO_DF.columns:
        CTO_Processors = list(CTO_DF['Processor'])
    else:
        CTO_Processors = []

    All_Processors = MTM_Processors + CTO_Processors
    Unique_processors = list(OrderedDict.fromkeys(All_Processors))
    # global processor_values
    processor_values = []
    core_flag = 0
    max_processor_intel_core = 0
    max_processor_intel_core_value = 0
    print(Unique_processors)
    pattern = "i\d{1,2}\-"

    for itr in range(0, len(Unique_processors)):
        # 10 th generation
        if (str(Unique_processors[itr]).find('10th Generation') != -1) and str(Unique_processors[itr]).find(
                'i9') != -1 and core_flag != 1:
            found = re.search(pattern, str(Unique_processors[itr]))
            core_value = int(str(Unique_processors[itr])[found.span(0)[0] + 1:found.span(0)[1] - 1])
            core_value = 100 + core_value
            if core_value > max_processor_intel_core_value:
                max_processor_intel_core_value = core_value
                max_processor_intel_core = itr
        elif (str(Unique_processors[itr]).find('10th Generation') != -1) and str(
                Unique_processors[itr]).find('i7') != -1 and core_flag != 1:
            found = re.search(pattern, str(Unique_processors[itr]))
            core_value = int(str(Unique_processors[itr])[found.span(0)[0] + 1:found.span(0)[1] - 1])
            core_value = 100 + core_value
            if core_value > max_processor_intel_core_value:
                max_processor_intel_core_value = core_value
                max_processor_intel_core = itr

        elif (str(Unique_processors[itr]).find('10th Generation') != -1) and str(
                Unique_processors[itr]).find('i5') != -1 and core_flag != 1:
            found = re.search(pattern, str(Unique_processors[itr]))
            core_value = int(str(Unique_processors[itr])[found.span(0)[0] + 1:found.span(0)[1] - 1])
            core_value = 100 + core_value
            if core_value > max_processor_intel_core_value:
                max_processor_intel_core_value = core_value
                max_processor_intel_core = itr

        # 9 th Generation
        elif (str(Unique_processors[itr]).find('9th Generation') != -1) and str(Unique_processors[itr]).find(
                'i9') != -1 and core_flag != 1:
            found = re.search(pattern, str(Unique_processors[itr]))
            core_value = int(str(Unique_processors[itr])[found.span(0)[0] + 1:found.span(0)[1] - 1])
            core_value = 90 + core_value
            if core_value > max_processor_intel_core_value:
                max_processor_intel_core_value = core_value
                max_processor_intel_core = itr

        elif (str(Unique_processors[itr]).find('9th Generation') != -1) and str(
                Unique_processors[itr]).find('i7') != -1 and core_flag != 1:
            found = re.search(pattern, str(Unique_processors[itr]))
            core_value = int(str(Unique_processors[itr])[found.span(0)[0] + 1:found.span(0)[1] - 1])
            core_value = 90 + core_value
            if core_value > max_processor_intel_core_value:
                max_processor_intel_core_value = core_value
                max_processor_intel_core = itr

        elif (str(Unique_processors[itr]).find('9th Generation') != -1) and str(
                Unique_processors[itr]).find('i5') != -1 and core_flag != 1:
            found = re.search(pattern, str(Unique_processors[itr]))
            core_value = int(str(Unique_processors[itr])[found.span(0)[0] + 1:found.span(0)[1] - 1])
            core_value = 90 + core_value
            if core_value > max_processor_intel_core_value:
                max_processor_intel_core_value = core_value
                max_processor_intel_core = itr


        # 8th generation
        elif (str(Unique_processors[itr]).find('8th Generation') != -1) and str(Unique_processors[itr]).find(
                'i9') != -1 and core_flag != 1:
            found = re.search(pattern, str(Unique_processors[itr]))
            core_value = int(str(Unique_processors[itr])[found.span(0)[0] + 1:found.span(0)[1] - 1])
            core_value = 80 + core_value
            if core_value > max_processor_intel_core_value:
                max_processor_intel_core_value = core_value
                max_processor_intel_core = itr

        elif (str(Unique_processors[itr]).find('8th Generation') != -1) and str(
                Unique_processors[itr]).find('i7') != -1 and core_flag != 1:
            found = re.search(pattern, str(Unique_processors[itr]))
            core_value = int(str(Unique_processors[itr])[found.span(0)[0] + 1:found.span(0)[1] - 1])
            core_value = 80 + core_value
            if core_value > max_processor_intel_core_value:
                max_processor_intel_core_value = core_value
                max_processor_intel_core = itr

        elif (str(Unique_processors[itr]).find('8th Generation') != -1) and str(
                Unique_processors[itr]).find('i5') != -1 and core_flag != 1:
            found = re.search(pattern, str(Unique_processors[itr]))
            core_value = int(str(Unique_processors[itr])[found.span(0)[0] + 1:found.span(0)[1] - 1])
            core_value = 80 + core_value
            if core_value > max_processor_intel_core_value:
                max_processor_intel_core_value = core_value
                max_processor_intel_core = itr



        # Xeon
        elif str(Unique_processors[itr]).find('Intel® Xeon® W-10855M Processor with vPro™') != -1:
            processor_values.append(str(Unique_processors[itr]))


        elif str(Unique_processors[itr]).find('Intel® Xeon® W-10855M Processor') != -1:
            processor_values.append('Up to ' + str(Unique_processors[itr]))

        th = re.findall('\d{1,3}th|\d{1,3} th', str(Unique_processors[max_processor_intel_core]).lower())[0]
        super_th = th.replace('th', 'ᵗʰ')

        processor_values.append('Up to ' + str(Unique_processors[max_processor_intel_core]).replace(th, super_th))

    print('Processors: ', All_Processors)
    processor_values = (list(set(processor_values)))
    Spec_List.append(processor_values)

# Operating system validation
if 'Operating System' in MTM_Specs.columns or 'Operating System' in CTO_DF.columns:
    if 'Operating System' in MTM_Specs.columns:
        MTM_OS = list(MTM_Specs['Operating System'])
    else:
        MTM_OS = []

    if 'Operating System' in CTO_DF.columns:
        CTO_OS = list(CTO_DF['Operating System'])
    else:
        CTO_OS = []

    All_OS = MTM_OS + CTO_OS
    Unique_OS = list(OrderedDict.fromkeys(All_OS))
    global OS_values
    OS_values = []

    os_home_pro = []
    os_others = []
    for ele in Unique_OS:
        if 'home' in ele.lower() or 'pro' in ele.lower():
            os_home_pro.append(ele)
        else:
            os_others.append(ele)
    done = 0
    for i in range(len(os_home_pro)):
        if 'Pro' in os_home_pro[i]:
            if 'recommends' in os_home_pro[i]:
                done = 1

            elif 'recommends' in os_home_pro[i] and done == 0:
                print(os_home_pro[i])
                os_home_pro[i] = os_home_pro[i] + '- Lenovo recommends Windows 10 Pro for Business'

    OS_values = os_home_pro + os_others
    OS_values = [ele for ele in OS_values if ele != 'No Operating System']
    OS_values = [ele.replace("\xa0",'') for ele in OS_values if ele]
    print('Operating System: ', OS_values)
    Spec_List.append(OS_values)

# Display validation
if 'Display' in MTM_Specs.columns or 'Display Type' in CTO_DF.columns:
    if 'Display' in MTM_Specs.columns:
        MTM_Dis = list(MTM_Specs['Display'])
    else:
        MTM_Dis = []

    if 'Display Type' in CTO_DF.columns:
        CTO_Dis = list(CTO_DF['Display Type'])
    else:
        CTO_Dis = []

    All_Display = MTM_Dis + CTO_Dis
    Unique_Display = list(OrderedDict.fromkeys(All_Display))
    Unique_Display = [ele for ele in Unique_Display if ele]
    print(len(Unique_Display))
    print(Unique_Display)
    global Display_values
    Display_values = []
    Display_values = Unique_Display
    Display_flag = 0
    Spec_List.append(Display_values)

print("**************Display*************")
print('Display: ', Display_values)
# Memory validation
if 'Memory' in MTM_Specs.columns or 'Memory' in CTO_DF.columns:
    if 'Memory' in MTM_Specs.columns:
        MTM_Mem = list(MTM_Specs['Memory'])
        print('MTM Memory: ', MTM_Mem)
    else:
        MTM_Mem = []

    if 'Memory' in CTO_DF.columns:
        CTO_Mem = list(CTO_DF['Memory'])
        print('CTO Memory', CTO_Mem)
    else:
        CTO_Mem = []

    All_Memory = MTM_Mem + CTO_Mem
    All_Memory = [ele for ele in All_Memory if ele]
    Unique_Memory = list(OrderedDict.fromkeys(All_Memory))
    Unique_Memory = [ele for ele in Unique_Memory if ele != 'Not available']
    print(len(Unique_Memory))
    print('Combined memory: ', Unique_Memory)

    regex = re.compile(".*?\((.*?)\)")
    memory_ecc = []
    memory_other = []
    memory_ecc_speed = []
    memory_other_speed = []

    # ECC memory ----------------------------------------------------------------------------------------------------------

    for ele in Unique_Memory:
        if 'ECC' in ele:
            memory_ecc.append(ele)
            memory_ecc_speed.append(
                int(re.findall('\d{1,5}', re.findall('\d{1,5}MHz|\d{1,5} MHz', ele)[0].strip())[0].strip()))

        else:
            memory_other.append(ele)
            memory_other_speed.append(
                int(re.findall('\d{1,5}', re.findall('\d{1,5}MHz|\d{1,5} MHz', ele)[0].strip())[0].strip()))

    print('ECC Memory: ', memory_ecc)
    print('Other Memory: ', memory_other)

    memory_ecc_ddr4 = []
    memory_ecc_ddr3 = []

    for a in memory_ecc:

        if 'LPDDR4' in a and ('(' in a and ')' in a):
            ddr4_ecc = 'LPDDR4'
            if 'soldered' in a.lower():
                soldered_ecc_ddr4 = ' (Soldered)'
                memory_ecc_ddr4.append(a)
            else:
                soldered_ecc_ddr4 = ''
                memory_ecc_ddr4.append(a.replace(re.findall(regex, a)[0], '').replace('()', '').strip())
        elif 'LPDDR4' in a and ('(' not in a and ')' not in a):
            ddr4_ecc = 'LPDDR4'
            memory_ecc_ddr4.append(a)
        elif 'DDR4' in a and ('(' in a and ')' in a):
            ddr4_ecc = 'DDR4'
            if 'soldered' in a.lower():
                soldered_ecc_ddr4 = ' (Soldered)'
                memory_ecc_ddr4.append(a)
            else:
                soldered_ecc_ddr4 = ''
                memory_ecc_ddr4.append(a.replace(re.findall(regex, a)[0], '').replace('()', '').strip())
        elif 'DDR4' in a and ('(' not in a and ')' not in a):
            ddr4_ecc = 'DDR4'
            memory_ecc_ddr4.append(a)
        else:
            ecc_other = ' ECC'

        if 'LPDDR3' in a and ('(' in a and ')' in a):
            ddr3_ecc = 'LPDDR3'
            if 'soldered' in a:
                soldered_ecc_ddr3 = ' (Soldered)'
                memory_ecc_ddr3.append(a)
            else:
                soldered_ecc_ddr3 = ''
                memory_ecc_ddr3.append(a.replace(re.findall(regex, a)[0], '').replace('()', '').strip())
        elif 'LPDDR3' in a and ('(' not in a and ')' not in a):
            ddr3_ecc = 'LPDDR3'
            memory_ecc_ddr3.append(a)
        elif 'DDR3' in a and ('(' in a and ')' in a):
            ddr3_ecc = 'DDR3'
            if 'soldered' in a:
                soldered_ecc_ddr3 = ' (Soldered)'
                memory_ecc_ddr3.append(a)
            else:
                soldered_ecc_ddr3 = ''
                memory_ecc_ddr3.append(a.replace(re.findall(regex, a)[0], '').replace('()', '').strip())
        elif 'DDR3' in a and ('(' not in a and ')' not in a):
            ddr3_ecc = 'DDR3'
            memory_ecc_ddr3.append(a)
        else:
            ecc_other = ' ECC'
    print('ECC Memory with DDR3: ', memory_ecc_ddr3)
    print('ECC Memory with DDR4: ', memory_ecc_ddr4)

    memory_other_ddr4 = []
    memory_other_ddr3 = []

    for a in memory_other:
        if 'LPDDR4' in a and ('(' in a and ')' in a):
            ddr4_other = 'LPDDR4'
            if 'soldered' in a.lower():
                soldered_other_ddr4 = ' (Soldered)'
                memory_other_ddr4.append(a)
            else:
                soldered_other_ddr4 = ''
                memory_other_ddr4.append(a.replace(re.findall(regex, a)[0], '').replace('()', '').strip())
        elif 'LPDDR4' in a and ('(' not in a and ')' not in a):
            ddr4_other = 'LPDDR4'
            memory_other_ddr4.append(a)
        elif 'DDR4' in a and ('(' in a and ')' in a):
            ddr4_other = 'DDR4'
            if 'soldered' in a.lower():
                soldered_other_ddr4 = ' (Soldered)'
                memory_other_ddr4.append(a)
            else:
                soldered_other_ddr4 = ''
                memory_other_ddr4.append(a.replace(re.findall(regex, a)[0], '').replace('()', '').strip())
        elif 'DDR4' in a and ('(' not in a and ')' not in a):
            ddr4_other = 'DDR4'
            memory_other_ddr4.append(a)
        else:
            ecc_other = ''

        if 'LPDDR3' in a and ('(' in a and ')' in a):
            ddr3_other = 'LPDDR3'
            if 'soldered' in a.lower():
                soldered_other_ddr3 = ' (Soldered)'
                memory_other_ddr3.append(a)
            else:
                soldered_other_ddr3 = ''
                memory_other_ddr3.append(a.replace(re.findall(regex, a)[0], '').replace('()', '').strip())
        elif 'LPDDR3' in a and ('(' in a and ')' in a):
            ddr3_other = 'LPDDR3'
            memory_other_ddr3.append(a)
        elif 'DDR3' in a and ('(' in a and ')' in a):
            ddr3_other = 'DDR3'
            if 'soldered' in a.lower():
                soldered_other_ddr3 = ' (Soldered)'
                memory_other_ddr3.append(a)
            else:
                soldered_other_ddr3 = ''
                memory_other_ddr3.append(a.replace(re.findall(regex, a)[0], '').replace('()', '').strip())
        elif 'DDR3' in a and ('(' in a and ')' in a):
            ddr3_other = 'DDR3'
            memory_other_ddr3.append(a)
        else:
            ecc_other = ''

    print('Other Memory with DDR3: ', memory_other_ddr3)
    print('Other Memory with DDR4: ', memory_other_ddr4)


    def memory_validation(speed_val, memory_val, ddr_val, ecc_other, soldered):
        """
        Validates extracted memory with actual quantity.
        Takes 3 arguments:
        1) speed_list - List of MHz values
        2) memory_list_gb - List of memory values
        3) DDR - Double data rate value
        """

        global max_memory
        global speed
        global counter
        global final_value

        max_memory = []
        speed = []
        counter = []

        for i in list(set(speed_val)):
            print(i)
            speed.append(i)
            memory_split_gb = []

            for j in memory_val:
                if i in j:
                    memory_split_gb.append(int(j.split("GB")[0].strip()))
            counter.append(len(memory_split_gb))
            max_memory.append(max(memory_split_gb))
            print(max_memory)
            print(counter)

            final_value = []

            for ele in zip(speed, max_memory, counter):
                print(ele)
                if ele[2] > 1:
                    final_value.append('Upto ' + str(ele[1] * memory_qty) + ' GB ' + str(ddr_val) + ' ' + ele[0] + str(
                        ecc_other) + soldered)


    speed_other_ddr4 = []
    speed_other_ddr3 = []

    speed_ecc_ddr4 = []
    speed_ecc_ddr3 = []

    for oth_ddr4 in memory_other_ddr4:
        print("========================", oth_ddr4)
        print(oth_ddr4)
        speed_other_ddr4_prev = re.findall(r"\d{1,5}\s?MHz", oth_ddr4)
        speed_other_ddr4.append(speed_other_ddr4_prev[0].strip())
        print('Memory speed of previous element : ', speed_other_ddr4_prev)

    for oth_ddr3 in memory_other_ddr3:
        print("========================", oth_ddr3)
        print(oth_ddr3)
        speed_other_ddr3_prev = re.findall(r"\d{1,5}\s?MHz", oth_ddr3)
        speed_other_ddr3.append(speed_other_ddr3_prev[0].strip())
        print('Memory speed of previous element : ', speed_other_ddr3_prev)

    for ecc_ddr3 in memory_ecc_ddr3:
        print("========================", ecc_ddr3)
        print(ecc_ddr3)
        speed_ecc_ddr3_prev = re.findall(r"\d{1,5}\s?MHz", ecc_ddr3)
        speed_ecc_ddr3.append(speed_ecc_ddr3_prev[0].strip())
        print('Memory speed of previous element : ', speed_ecc_ddr3_prev)

    for ecc_ddr4 in memory_ecc_ddr4:
        print("========================", ecc_ddr4)
        print(ecc_ddr4)
        speed_ecc_ddr4_prev = re.findall(r"\d{1,5}\s?MHz", ecc_ddr4)
        speed_ecc_ddr4.append(speed_ecc_ddr4_prev[0].strip())
        print('Memory speed of previous element : ', speed_ecc_ddr4_prev)

    if len(memory_other_ddr3) > 0:
        memory_validation(speed_other_ddr3, memory_other_ddr3, ddr3_other, ecc_other, soldered_other_ddr3)
        final_other_ddr3 = final_value
    else:
        final_other_ddr3 = []

    if len(memory_other_ddr4) > 0:
        memory_validation(speed_other_ddr4, memory_other_ddr4, ddr4_other, ecc_other, soldered_other_ddr4)
        final_other_ddr4 = final_value
    else:
        final_other_ddr4 = []

    if len(memory_ecc_ddr3) > 0:
        memory_validation(speed_ecc_ddr3, memory_ecc_ddr3, ddr3_ecc, ecc_other, soldered_ecc_ddr3)
        final_ecc_ddr3 = final_value
    else:
        final_ecc_ddr3 = []

    if len(memory_ecc_ddr4) > 0:
        memory_validation(speed_ecc_ddr4, memory_ecc_ddr4, ddr4_ecc, ecc_other, soldered_ecc_ddr4)
        final_ecc_ddr4 = final_value
    else:
        final_ecc_ddr4 = []

    validated_max_memory_all = final_other_ddr3 + final_other_ddr4 + final_ecc_ddr3 + final_ecc_ddr4
    print(validated_max_memory_all)
    Memory_values = validated_max_memory_all
    Memory_values = [ele for ele in Memory_values if ele]

    print('Memory: ', Memory_values)
Spec_List.append(Memory_values)

# ================================================================================================================
print(MTM_Specs['Storage'])

if 'Storage' in MTM_Specs.columns or len(Final_Storage_CTO) > 0:
    if 'Storage' in MTM_Specs.columns:
        MTM_Str = list(MTM_Specs['Storage'])
    else:
        MTM_Str = []
    if len(Final_Storage_CTO) > 0:
        CTO_str = Final_Storage_CTO
    else:
        CTO_str = []

    All_Storage = MTM_Str + CTO_str
    Unique_Storage = list(OrderedDict.fromkeys(All_Storage))
    print(len(Unique_Storage))
    print('Combined Storage: ', Unique_Storage)
    global Storage_values
    Storage_values = []
    Max_Storage = 0
    Unique_Storage = [ele for ele in Unique_Storage if ele]

    if len(Unique_Storage) > 0:

        print('Storage: ', Unique_Storage)

        ssd = []
        hdd = []

        for ele in Unique_Storage:
            if 'SSD' in ele or 'OPAL' in ele:
                ssd.append(ele.replace('OPAL', '').replace('PCIe', '').replace(',', '').strip())
            elif 'HDD' in ele:
                hdd.append(ele)

        print(ssd)
        print(hdd)

        ssd_converted = []
        for ele in ssd:
            if 'TB' in ele:
                aa = int(re.findall('\d{1,2}\s[TB]', ele)[0][:-1].strip()) * 1000
                ssd_converted.append(
                    ele.replace(re.findall('\d{1,2}\s[TB]', ele)[0][:-1].strip(), str(aa)).replace('TB', 'GB'))
            elif 'GB' in ele:
                ssd_converted.append(ele)

        hdd_converted = []
        for ele1 in hdd:
            if 'TB' in ele1:
                aa1 = int(re.findall('\d{1,2}\s[TB]', ele1)[0][:-1].strip()) * 1000
                hdd_converted.append(
                    ele1.replace(re.findall('\d{1,2}\s[TB]', ele1)[0][:-1].strip(), str(aa1)).replace('TB', 'GB'))
            elif 'GB' in ele1:
                hdd_converted.append(ele1)

        print(ssd_converted)
        print(hdd_converted)

        max_storage_ssd = []
        max_storage_hdd = []

        for ele in ssd_converted:
            max_storage_ssd.append(int(ele.split('GB')[0].strip()))

        for ele in hdd_converted:
            max_storage_hdd.append(int(ele.split('GB')[0].strip()))

        if max_storage_ssd:
            max_storage_ssd = max(max_storage_ssd)
            print(max_storage_ssd)
        else:
            max_storage_ssd = 0

        if max_storage_hdd:
            max_storage_hdd = max(max_storage_hdd)
            print(max_storage_hdd)
        else:
            max_storage_hdd = 0



    else:
        max_storage_ssd = 0
        max_storage_hdd = 0
        print('No Hard drive')
        pass


    if len(str(max_storage_ssd)) == 3:
        total_ssd = str(max_storage_ssd) + ' GB SSD'
    elif len(str(max_storage_ssd)) >= 4:
        if max_storage_ssd % 1000 == 0:
            total_ssd = str(round(max_storage_ssd / 1000)) + ' TB SSD'
        else:
            total_ssd = str(max_storage_ssd / 1000) + ' TB SSD'
    else:
        total_ssd = []

    if len(str(max_storage_hdd)) == 3:
        total_hdd = str(max_storage_hdd) + ' GB SSD'
    elif len(str(max_storage_hdd)) >= 4:
        if max_storage_hdd % 1000 == 0:
            total_hdd = str(round(max_storage_hdd/1000)) + ' TB SSD'
        else:
            total_hdd = str(max_storage_hdd/1000) + ' TB SSD'
    else:
        total_hdd = []


    Storage_values = [total_ssd, total_hdd]
    Storage_values = ['Upto ' + str(ele) for ele in Storage_values if ele]
    Storage_values = list(set(Storage_values))
    print('Storage: ', Storage_values)
    Spec_List.append(Storage_values)

# Warranty validation
if 'Warranty' in MTM_Specs.columns or 'Warranty' in CTO_DF.columns:
    if 'Warranty' in MTM_Specs.columns:
        MTM_War = list(MTM_Specs['Warranty'])
    else:
        MTM_War = []

    if 'Warranty' in CTO_DF.columns:
        CTO_War = list(MTM_Specs['Warranty'])
    else:
        CTO_War = []


    All_Warranty = MTM_War + CTO_War
    Unique_Warranty = list(OrderedDict.fromkeys(All_Warranty))
    Unique_Warranty = [ele for ele in Unique_Warranty if ele]
    print(len(Unique_Warranty))
    print('Warranty: ', Unique_Warranty)
    global warranty_values
    warranty_values = []
    warranty_values = Unique_Warranty
    warranty_values = [warr.lower() for warr in warranty_values if warr]
    warranty_values = list(set(warranty_values))
    warranty_values = [warr.capitalize() for warr in warranty_values if warr]
    print(warranty_values)
    print('Warranty: ', warranty_values)
    Spec_List.append(warranty_values)

# Graphics validation
if 'Graphics' in MTM_Specs.columns or 'Graphic Card' in CTO_DF.columns:
    if 'Graphics' in MTM_Specs.columns:
        MTM_Graphics = list(MTM_Specs['Graphics'])
    else:
        MTM_Graphics =[]

    if 'Graphic Card' in CTO_DF.columns:
        CTO_Graphics = list(CTO_DF['Graphic Card'])
    else:
        CTO_Graphics = []

    All_Graphics = MTM_Graphics + CTO_Graphics
    Unique_Graphics = list(OrderedDict.fromkeys(All_Graphics))
    print(len(Unique_Graphics))
    print(Unique_Graphics)
    Graphics_values = []
    Graphics_values = Unique_Graphics

    # UHD validation

    Graphics_values = [ele for ele in Graphics_values if ele]
    print('Graphics: ', Graphics_values)

    graphic_uhd = []
    graphic_others = []

    for ele in Graphics_values:
        if 'Intel' in ele and 'UHD' in ele:
            graphic_uhd.append(ele)
        else:
            graphic_others.append(ele)

    print(graphic_uhd)
    print(graphic_others)

    max_uhd = []

    if graphic_uhd:
        for ele in graphic_uhd:
            if re.findall('\d{1,3}', ele):
                max_uhd.append(int(re.findall('\d{1,4}', re.findall('UHD \d{1,4}|UHD\d{1,4}', ele)[0])[0].strip()))
            else:
                print('No number')

        if len(max_uhd) > 0:
            max_uhd = max(max_uhd)
            final_graphics_uhd = ['Integrated Intel® UHD ' + str(max_uhd) + ' Graphics']
            print(final_graphics_uhd)
        else:
            final_graphics_uhd = ['Integrated Intel® UHD Graphics']
            print(final_graphics_uhd)
    else:
        final_graphics_uhd = []

    graphic_all = final_graphics_uhd + list(set(graphic_others))
    graphic_all = [graph.lower() for graph in graphic_all if graph]
    graphic_all = list(set(graphic_all))
    graphic_all = [graph.capitalize() for graph in graphic_all if graph]
    print(graphic_all)
    Spec_List.append(graphic_all)

# Camera validation
# if 'Camera' in MTM_Specs.columns:
#     All_Cameras = list(MTM_Specs['Camera'])+list(CTO_DF['Camera'])
#     Unique_Camera = list(OrderedDict.fromkeys(All_Cameras))
#     print(len(Unique_Camera))
#     print(Unique_Camera)
#     Camera_values = []
#     Camera_values = Unique_Camera
#     Spec_List.append(Camera_values)

# Fingerprint Validation
Fingerprint_values = []
if 'Fingerprint Reader' in MTM_Specs.columns or 'Fingerprint Reader' in CTO_DF.columns:
    if 'Fingerprint Reader' in MTM_Specs.columns :
        MTM_Fin = list(MTM_Specs['Fingerprint Reader'])
    else:
        MTM_Fin = []

    if 'Fingerprint Reader' in CTO_DF.columns :
        CTO_Fin = list(CTO_DF['Fingerprint Reader'])
    else:
        CTO_Fin = []

    All_Fingerprints = MTM_Fin + CTO_Fin
    Unique_Fingerprints = list(OrderedDict.fromkeys(All_Fingerprints))
    print(len(Unique_Fingerprints))
    print(Unique_Fingerprints)
    Fingerprint_values = []
    Fingerprint_values = Unique_Fingerprints
    Fingerprint_values = [ele for ele in Fingerprint_values if ele]
    print('Fingerprint Values: ', Fingerprint_values)
    Spec_List.append(Fingerprint_values)

# Keyboard Validation
if 'Keyboard' in MTM_Specs.columns or 'Keyboard' in CTO_DF.columns:
    if 'Keyboard' in MTM_Specs.columns:
        MTM_Key = list(MTM_Specs['Keyboard'])
    else:
        MTM_Key = []

    if 'Keyboard' in CTO_DF.columns:
        CTO_Key = list(CTO_DF['Keyboard'])
    else:
        CTO_Key = []


    All_Keyboards = MTM_Key + CTO_Key
    Unique_Keyboards = list(OrderedDict.fromkeys(All_Keyboards))
    print(len(Unique_Keyboards))
    print(Unique_Keyboards)
    Keyboard_values = []
    Keyboard_values = Unique_Keyboards
    Keyboard_values = [ele for ele in Keyboard_values if ele]
    print('Keyboard: ', Keyboard_values)
    Spec_List.append(Keyboard_values)

# Connectivity validation
if 'Connectivity' in MTM_Specs.columns or 'Connectivity' in CTO_DF.columns:
    if 'Connectivity' in MTM_Specs.columns:
        MTM_Conn = list(MTM_Specs['Connectivity'])
    else:
        MTM_Conn = []
    if 'Connectivity' in CTO_DF.columns:
        CTO_Conn = list(CTO_DF['Connectivity'])
    else:
        CTO_Conn = []

    All_Connectivity = MTM_Conn + CTO_Conn
    Unique_Connectivity = list(OrderedDict.fromkeys(All_Connectivity))
    print(len(Unique_Connectivity))
    print(Unique_Connectivity)
    Connectivity_values = []
    Connectivity_values = Unique_Connectivity
    Connectivity_values = [ele for ele in Connectivity_values if ele]
    print('Connectivity: ', Connectivity_values)
    Spec_List.append(Connectivity_values)

# Spec_List = [processor_values, OS_values, Display_values, Memory_values, Storage_values, warranty_values,
#             Graphics_values, Camera_values, Fingerprint_values, Keyboard_values, Connectivity_values]

print(Spec_List)
print(Spec_List[Spec_List.index(processor_values)])

driver.quit()
