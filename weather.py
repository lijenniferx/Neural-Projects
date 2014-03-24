from urllib2 import urlopen
from bs4 import BeautifulSoup
from numpy import *
base_url='http://weather-warehouse.com/WeatherHistory/PastWeatherData_BostonLoganIntLArpt_Boston_MA_January.html'
html=urlopen(base_url).read()
soup=BeautifulSoup(html,'lxml')
all_urls=soup.findAll('a',{'class':'links'})  #### get urls to all of the months

month_id=1
final_table=[]
for months in all_urls:
    if len(months.text)>15:
        break
    else:
        month_soup=BeautifulSoup(urlopen(base_url[:44]+months['href']).read())
        
        #### getting table headers
        categories=[x.find('span').text for x in month_soup.findAll('tr')[1]]

        ##### some months don't have data for 2014!
        if month_soup.findAll('tr')[2].td.text=='2013':
            allrows=month_soup.findAll('tr')[2:]
        else:
            allrows=month_soup.findAll('tr')[3:]
                    
         
        #### getting numerical data
        stripped_rows=[x.findAll('td') for x in allrows[1:]]
        table=[]
        for x in stripped_rows:
            if len(x[0].text)>10:
                break
            else:
                temp=[]
                for y in x:
                    if not y.text:
                        temp.append(NaN) ### missing data for some of the months
                    else:
                        temp.append(float(y.text))
                    
                table.append(temp)
          
        #### getting the average temperature by year
        year_index=[x for (x,y) in enumerate(categories) if y=='Year'][0]
        mean_temp_index=[x for (x,y) in enumerate(categories) if y=='MeanTemperature(F)'][0]
        
        final_table.append([[x[year_index] for x in table]]+[[x[mean_temp_index] for x in table]])
        
        month_id+1
        

#### plotting
from pylab import plot,xlabel,ylabel,savefig,figure,close
import scipy
avg_temps=[x[1] for x in final_table]
plot(final_table[0][0],scipy.nanmean(avg_temps,0)) ### average annual temperature
close(1)
figure()
plot(arange(1,13),scipy.nanmean(avg_temps,1),'k') ### temperature by month (across all years)
recent_monthly_temps=[x[0:10] for x in avg_temps]
past_monthly_temps=[x[-10:] for x in avg_temps]
plot(arange(1,13),scipy.nanmean(recent_monthly_temps,1),'r',linewidth=1) ### temperature by month (across recent 10 years)
plot(arange(1,13),scipy.nanmean(past_monthly_temps,1),'b',linewidth=1) ### temperature by month (across most distant 10 years)
