from ulcarchetype import ulcarchetype
import bw2data
import bw2io

bw2data.projects.set_current('test_ulcarchetype')


# configuration 

if 'biosphere3' not in bw2data.databases:
    bw2io.bw2setup()

 
### test database

# activity 1
e1 = ('biosphere3', '051aaf7a-6c1a-4e86-999f-85d5f0830df6')
act1_key=('test_db2','activity_1')
# a unique emission of PM in an uncertain archetype
biosphere_exchange_1={'amount':1,
                     'input':e1,
                     'output':act1_key,
                     'type':'biosphere',
                     'uncertainty type': 4, # uniform
                     'minimum':1,
                     'maximum':3}
production_exchange_1={'amount':1,
                     'input':act1_key,
                     'output':act1_key,
                     'type':'production',
                     'uncertainty type':0}
act_1_dict={'name':'test_activity_1',
 'unit':'megajoule',
 'exchanges':[production_exchange_1,biosphere_exchange_1]}

# activity 2
act2_key=('test_db2','activity_2')

production_exchange_2={'amount':1,
                     'input':act2_key,
                     'output':act2_key,
                     'type':'production',
                     'uncertainty type':0}

technosphere_exchange_1={
    'amount':10, # or negative?
    'input':act1_key,
    'output':act2_key,
    'type':'technosphere',
    'uncertainty type':3,
    'loc':10,
    'scale':1,
}
# a unique emission of PM in an uncertain archetype
biosphere_exchange_2={'amount':1,
                     'input':e1,
                     'output':act2_key,
                     'type':'biosphere',
                     'uncertainty type': 4, # uniform
                     'minimum':1,
                     'maximum':1.1}

act_2_dict={'name':'test_activity_2','unit':'megajoule',
            'exchanges':[production_exchange_2,
            technosphere_exchange_1,
            biosphere_exchange_2]}

database_dict={act1_key:act_1_dict,
               act2_key:act_2_dict}
db=bw2data.Database('test_db2')
db.write(database_dict)

 
# create a test methods

e1 = ('biosphere3', '051aaf7a-6c1a-4e86-999f-85d5f0830df6')
e2 = ('biosphere3', 'ddd99a3a-be86-423d-b36a-a9dc8af1b1f8')
e3 = ('biosphere3', '66f50b33-fd62-4fdd-a373-c5b0de7de00d')
e4 = ('biosphere3', '21e46cb8-6233-4c99-bac3-c41d2ab99498')
e5 = ('biosphere3', '230d8a0a-517c-43fe-8357-1818dd12997a')

for e in [e1,e2,e3,e4,e5]:
    emission = bw2data.get_activity(e)
    print(emission['name'],emission['categories'])
    
cfs=[(e1,1),
     (e2,1),
     (e3,1),
     (e4,10),#unspecified
     (e5,10)]

test_method_name_1=('test method','1 unspecified')

test_method_1=bw2data.Method(test_method_name_1)

metadata_test_method={
'description':'method to test uncertainty on archetype',
'unit':'DALY'}
test_method_1.register(**metadata_test_method)
test_method_1.write(cfs)


## 0 unnespecified

cfs=[(e1,1),
 (e2,1),
 (e3,1),
 #(e4,10),#unspecified
 (e5,10)]

test_method_name_2=('test method','0 unspecified')

test_method_2=bw2data.Method(test_method_name_2)

metadata_test_method_2={'description':'method to test uncertainty on archetype',
 'unit':'DALY'}

test_method_2.register(**metadata_test_method_2)
test_method_2.write(cfs)
