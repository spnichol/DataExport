#! python 3, coded in iPython Notebook 

get_ipython().magic('matplotlib inline')
import pandas as pd
from IPython.core.display import HTML
css = open('style-table.css').read() + open('style-notebook.css').read()
HTML('<style>{}</style>'.format(css))


get_ipython().run_cell_magic('time', '', "regs = pd.DataFrame.from_csv('regs.csv', index_col=None)")


get_ipython().run_cell_magic('time', '', "regcontact = pd.DataFrame.from_csv('regcontact.csv', index_col=None)")


get_ipython().run_cell_magic('time', '', "builddata = pd.DataFrame.from_csv('MockImportFile.csv', index_col=None)")


######## ------ CREATION OF regcombo DATAFRAME ----------  #########


regcombo = pd.merge(regs, regcontact, on='RegistrationID', how='inner')


regcombo.drop_duplicates(subset=None, keep='first', inplace=True)


regcombo.sort(columns=['RegistrationID'], axis=0, ascending=True, inplace=True)

regcombo['bizadd'] = regcombo.BusinessHouseNumber.map(str) + " " + regcombo.BusinessStreetName


#format address in regcombo 
regcombo.bizadd.replace(to_replace=' ST$', value=' STREET', regex=True, inplace=True)
regcombo.bizadd.replace(to_replace=' AVE$', value=' AVENUE', regex=True, inplace=True)
regcombo.bizadd.replace(to_replace=' BLVD.', value=' BOULEVARD', regex=True, inplace=True)
regcombo.bizadd.replace(to_replace=' BLVD$', value=' BOULEVARD', regex=True, inplace=True)
regcombo.bizadd.replace(to_replace=' PKY', value=' PARKWAY', regex=True, inplace=True)
regcombo.bizadd.replace(to_replace=' AVE ', value=' AVENUE ', regex=True, inplace=True)
regcombo.bizadd.replace(to_replace=' RD', value=' ROAD', regex=True, inplace=True)
regcombo.bizadd.replace(to_replace=' RD.', value=' ROAD', regex=True, inplace=True)
regcombo['MiddleInitial'].fillna('missing', inplace=True)

#list comprehension to create owner name column
regcombo['FullName'] = [
   "{0}, {1}, {2}"
   .format(last, first, middle if middle != 'missing' else "").strip(' , ') 
   for last, first, middle 
   in regcombo[['LastName', 'FirstName', 'MiddleInitial']].values]


#removes NaN from names and adds n/a
regcombo['FullName'] = ["{0}".format(full if full != 'nan, nan' else "n/a").strip()
                        for full in regcombo['FullName'].values]
#formats text to title case 
regcombo['FullName'] = regcombo['FullName'].str.title()

#adds apartment unit to business address ***CODE EXECUTED VIA LIST COMPREHENSION BELOW***

#uses list comprehension to add apartment unit to business address
regcombo['bizadd'] = [
   "{0}, {1}"
   .format(address, suite if suite != 'NaN' else "").strip(', nan') 
   for address, suite 
   in regcombo[['bizadd', 'BusinessApartment']].values]

#strips whitespace from owner address
regcombo['bizadd'] = regcombo['bizadd'].str.strip()

#adds n/a to empty cells in BizAdd
regcombo['bizadd'] = [
   "{0}"
   .format(address if address != '' else "n/a").strip() 
   for address 
   in regcombo['bizadd'].values]

#formats other columns into title case
regcombo['address'] = regcombo['address'].str.title()
regcombo['ContactDescription'] = regcombo['ContactDescription'].str.title()




######## ------ CREATION OF ownercombo DATAFRAME ----------  #########


ownercombo = regcombo[['BuildingID', 'RegistrationID', 'RegistrationContactID', 'address', 'Type', 'ContactDescription', 'CorporationName', 'FullName', 'bizadd']]


### fills blank cells with n/a
ownercombo.loc[0, 'CorporationName'] = ownercombo.CorporationName.fillna('n/a', inplace=True)


######## ------ CREATION OF yescorp DATAFRAME ----------  #########


yescorp = ownercombo[ownercombo.CorporationName != 'n/a']


######## ------ CREATION OF nocorp DATAFRAME ----------  #########


#finds unique buildings that have n/a for corporation name

nocorp = ownercombo.groupby('BuildingID').filter(lambda x: (x['CorporationName'] == 'n/a').all()) 


## formats bizadd and owner name 
nocorp['bizadd'] = nocorp['bizadd'].str.title()
nocorp['FullName'] = nocorp['FullName'].str.title()


nocorp['BizNameAdd'] = ["{0}, {1}".format(name, address if address != 'n/a' else "").strip() for name, address in nocorp[['FullName', 'bizadd']].values]


############ --------  CREATES LOT for BBL in REGCOMBO ----------- ##########


regcombo['LotStr'] = regcombo.Lot.astype(pd.np.float)



regcombo['LotStr'] = regcombo.LotStr.astype(pd.np.int64)


regcombo['LotStr'] = regcombo.LotStr.astype(pd.np.str)



def Lotskies(x):
    if len(x) == 1:
        return '000' + x
    elif len(x) == 2:
        return '00' + x
    elif len(x) == 3:
        return '0' + x
    else:
        return x


regcombo['LotCorrect'] = regcombo.LotStr.apply(Lotskies)


############ --------  CREATES block for BBL in REGCOMBO ----------- ##########



regcombo['BlockStr'] = regcombo.Block.astype(pd.np.float)


regcombo['BlockStr'] = regcombo.BlockStr.astype(pd.np.int64)


regcombo['BlockStr'] = regcombo.BlockStr.astype(pd.np.str)


def Blockster(x):
    if len(x) == 1:
        return '000' + x
    if len(x) == 2: 
        return '00' + x
    if len(x) == 3:
        return '0' + x 
    else: 
        return x 


regcombo['BlockCorrect'] = regcombo.BlockStr.apply(Blockster)

############ --------  MERGES bock and lot for BBL in REGCOMBO ----------- ##########


regcombo['LotCorrect'] = regcombo.LotCorrect.astype(pd.np.str)


regcombo['BlockCorrect'] = regcombo.BlockCorrect.astype(pd.np.str)


regcombo['NewBBL'] = ('30' + regcombo.BlockCorrect.astype(str) + regcombo.LotCorrect.astype(str))


regcombo['BBL'] = regcombo['NewBBL']



############ --------  CREATES BBLGUIDE AND ADDS BBL TO NOCORP AND YESCORP ----------- ##########



BBLGuide = regcombo[['BuildingID', 'BBL']]



nocorp = pd.merge(nocorp[list('BBL')], BBLGuide, on='BuildingID', how='inner')


df1.merge(df2[list('xab')])



nocorp = nocorp.drop_duplicates()



yescorp = yescorp.merge(BBLGuide, on='BuildingID', how='inner')



yescorp = yescorp.drop_duplicates()



yescorp


del yescorp['Type']


del yescorp['FullName']


del yescorp['ContactDescription']


del yescorp['RegistrationContactID']



yescorp = yescorp.drop_duplicates()


############ --------  CREATES NAMELIST AND DISPLAY NAME for no corp ----------- ##########


NameList = regcombo[['BuildingID', 'RegistrationID', 'RegistrationContactID', 'FirstName', 'MiddleInitial', 'LastName']]


NameList['DisplayName'] = NameList.FirstName + " " + NameList.MiddleInitial + " " + NameList.LastName



NameList['DisplayName'] = NameList.DisplayName.str.replace('missing', '')



NameList['DisplayName'] = NameList.DisplayName.str.title()


NameList = NameList.drop_duplicates()


NameList = NameList.drop_duplicates()

nocorp = nocorp.merge(NameList, on='RegistrationContactID', how='inner')


############ --------  CREATES build_data  ----------- ##########


builddata = builddata[['BBL', 'Address', 'ZipCode', 'YearBuilt', 'NumBldgs', 'NumFloors', 'UnitsRes']]


def yearchanger(x):
    if x == 0:
        return 'Unknown'
    else:
        return x

builddata['YearBuilt'] = builddata.YearBuilt.apply(yearchanger)



builddata['Address'] = builddata.Address.str.title()


############ --------  MAKES CASE FORMATTING CHANGES TO yescorp ----------- ##########


yescorp['CorporationName'] = yescorp.CorporationName.str.title()


yescorp['address'] = yescorp.address.str.title()


############ --------  DONE FORMATTING DATA ----------- ##########


############ -------- USES LIST COMPREHENSION TO CREATE COMBINE COLUMNS ----------- ##########


nocorp['at1'] = 'at'


nocorp['DisplayBizAdd'] = ["{0} {1} {2}".format(name, at if address != 'N/A' else "", address if address != 'N/A' else "").strip(',') for name, at, address in nocorp[['DisplayName', 
'at1', 'bizadd']].values]


nocorp['RegistrationID'] = nocorp.RegistrationID_x


nocorp['BuildingAddress'] = nocorp.address


nocorp['BusinessAddress'] = nocorp.bizadd

############ --------  CREATES A REFERENCE DF FOR CONTACT ID AND BUILDINGID MATCHING ----------- ##########



nocorp = nocorp.merge(NameList, on='RegistrationContactID', how='inner')


nocorp = nocorp.merge(BBLGuide, on='BuildingID', how='inner')


yescorp['BusinessAddress'] = yescorp.bizadd.str.title()


yescorp['BuildingAddress'] = yescorp.address


builddata['ZipCode'] = builddata.ZipCode.fillna('Unknown', inplace=False)



############ --------  DATA EXPORT PREPS ----------- ##########



nocorp_export = nocorp[['BBL', 'BuildingID', 'RegistrationID', 'BuildingAddress', 'DisplayName', 'BusinessAddress', 'DisplayBizAdd']]



nocorp_export.drop_duplicates()



yescorp_export = yescorp[['BBL', 'BuildingID', 'RegistrationID', 'BuildingAddress', 'CorporationName', 'BusinessAddress']]



nocorp_export.drop_duplicates()



builddata_export = builddata


nocorp_export = nocorp_export.drop_duplicates()



nocorp_export.to_csv('nocorp_export.csv')



yescorp_export.to_csv('yescorp_export.csv')



builddata_export.to_csv('builddata_export.csv')



nocorp_export



yescorp_export










..

