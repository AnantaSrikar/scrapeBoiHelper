import pandas as pd
from datetime import timedelta, date
import requests
import lxml.html
from lxml import etree
import wget
import pprint
import re
import os
#for generating dates within a start and an end date

def writeForWorldo(data):
	fileManager = open('Worldometer.txt', 'w')
	fileManager.write(data)
	fileManager.close()

START_DATE = 22
START_MONTH = 2
END_DATE = 17
END_MONTH = 3
dates_list=[]
start_date = date(2020, START_MONTH, START_DATE)
end_date = date(2020, END_MONTH, END_DATE)
states = ["Andhra Pradesh","Arunachal Pradesh ","Assam","Bihar","Chhattisgarh","Goa","Gujarat","Haryana","Himachal Pradesh","Jammu and Kashmir","Jharkhand","Karnataka","Kerala","Madhya Pradesh","Maharashtra","Manipur","Meghalaya","Mizoram","Nagaland","Odisha","Punjab","Rajasthan","Sikkim","Tamil Nadu","Telangana","Tripura","Uttar Pradesh","Uttarakhand","West Bengal","Andaman and Nicobar Islands","Chandigarh","Dadra and Nagar Haveli","Daman and Diu","Lakshadweep","Delhi","Puducherry"]
def generate_dates(start_date, end_date):
	for n in range(int ((end_date - start_date).days)):
		yield start_date + timedelta(n)
	for single_date in daterange(start_date, end_date):
		dates_list.append(single_date.strftime("%m-%d-%Y"))
#define all urls
moh_url = 'https://www.mohfw.gov.in/'
worldo_url = 'https://www.worldometers.info/coronavirus/'
dh_url = 'https://www.deccanherald.com/national/coronavirus-india-update-state-wise-total-number-of-confirmed-cases-deaths-812987.html'
#pharma_url = 'https://docs.google.com/spreadsheets/d/1IPJW33Z9ADRBvZlqfkulEayUnYif6TrBz9GRjDfciTQ/export?format=csv&id=1IPJW33Z9ADRBvZlqfkulEayUnYif6TrBz9GRjDfciTQ&gid=0'
jhu_daily_url = 'https://github.com/CSSEGISandData/COVID-19/tree/master/csse_covid_19_data/csse_covid_19_daily_reports'
header=["Sno","State","Cases"]
#generate_dates()
#DECCAN HERALD
web_response = requests.get(dh_url)
txt_to_parse = web_response.text
x = txt_to_parse.split("articleBody")
y = x[1].split("https://www.arcgis.com/a")[0]
final_string = y.split("(the list will be regularly updated)")[1]  #pdated
tot_cases_dh_str = re.findall(r"Total number of positive cases in India: \d+",final_string)
tot_death_dh_str = re.findall(r"Total deaths in India: \d+",final_string)
header=["Sno","State","Cases"]
dh_table=pd.DataFrame(header)
for idx, word in enumerate(states):
	temp=re.findall(r"{0}: \d+".format(word),final_string)
	if(len(temp)==0):
		df_t=[str(idx+1),word,"0"]
		dh_table=dh_table.append(pd.DataFrame(df_t))
	else:
		temp2=temp[0].split(":")
		df_t=[str(idx+1),temp2[0],temp2[1]]
		dh_table=dh_table.append(pd.DataFrame(df_t))
dh_tot_cases = [int(i) for i in tot_cases_dh_str[0].split() if i.isdigit()]
dh_tot_death = [int(i) for i in tot_death_dh_str[0].split() if i.isdigit()]
#Worldometer
worldo_table = pd.read_html(worldo_url)
worldo_df = worldo_table[0]
worldo_india_row = worldo_df.loc[worldo_df['Country,Other'] == 'India']
worldo_tot_cases = int(worldo_india_row.TotalCases)
worldo_tot_death = int(worldo_india_row.TotalDeaths) 
worldometer_data = 'infected : ' + str(worldo_tot_cases) + '\ndeaths : ' + str(worldo_tot_death)

#MOH
web_response = requests.get(moh_url)
element_tree = lxml.html.fromstring(web_response.text)
moh_table=element_tree.xpath('//tr/td//text()')
moh_tot_cases=0
moh_tot_deaths=0
#updated:
index = moh_table.index('SOP for Mock Drill on 22nd March 2020 for Hospital Preparedness ')
index = index+1
end = len(moh_table)
moh_table=moh_table[index:end]
#moh_table=moh_table[10:]  #added (also updated 2nd time)
tmp_moh_table=moh_table
moh_table=pd.DataFrame(header)
conf_case=0
idx=1
for i in range(0,len(tmp_moh_table)):
	if(i%6==0):
		 sno=tmp_moh_table[i]
	elif (i%6==1):
		state_name=tmp_moh_table[i]
		if(state_name=="Total number of confirmed cases in India"):
			continue
	elif (i%6==2):
		if(state_name=="Total number of confirmed cases in India"):
			continue
		if(tmp_moh_table[i]=='\n        '):
			tmp_moh_table[i]='0'
		data_item = [str(p) for p in tmp_moh_table[i]]
		conf_case = conf_case + int(data_item[0])
	elif(i%6==3):
		if(state_name=="Total number of confirmed cases in India"):
			continue
		if(tmp_moh_table[i]=='\n        '):
			tmp_moh_table[i]='0'
		data_item = [str(p) for p in tmp_moh_table[i]]
		conf_case = conf_case + int(data_item[0])
	elif(i%6==4):
		if(state_name=="Total number of confirmed cases in India"):
			continue
		reco_case = tmp_moh_table[i]
	elif(i%6==5):
		if(state_name=="Union Territory of Ladakh"):
			state_name="Ladakh"
		if(state_name=="Union Territory of Chandigarh"):
			state_name="Chandigarh"
		if(state_name=="Union Territory of Jammu and Kashmir"):
			state_name="Jammu and Kashmir"
		if(state_name=="Total number of confirmed cases in India"):
			continue
		#append entry
		df_t=[str(idx),state_name,str(conf_case)]
		conf_case=0
		moh_table=moh_table.append(pd.DataFrame(df_t))
		idx = idx + 1
try:
	os.remove("MOHFW.csv")
	os.remove("DeccanHerald.csv")
	os.remove("Worldometer.txt")
except:
	pass

writeForWorldo(worldometer_data)

#PHARMA TECH
#wget.download(pharma_url, "pharma_tech.csv")
# tmp_pharma_table = pd.read_csv('pharma_tech.csv')
# pharma_table=pd.DataFrame(header)
# for ind in range(1,len(tmp_pharma_table)):
#     pharma_table = pharma_table.append(pd.DataFrame([str(ind),tmp_pharma_table['State/Union Territory'][ind], (tmp_pharma_table['Confirmed (Indian Nationals)'][ind] + tmp_pharma_table['Confirmed (Foreigners)'][ind])]))
#print(moh_table)
#print(dh_table)
#print(pharma_table)
moh_table.to_csv("MOHFW.csv")
dh_table.to_csv("DeccanHerald.csv")
#in pharma remove total get total (Total)
#jammu dh
#cleanup
#os.remove("pharma_tech.csv")
