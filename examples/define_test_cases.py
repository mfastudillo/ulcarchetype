import bw2data as bd
import bw2io as bi

from ulcarchetype import ulcarchetype

def main():

    # define elementary flows
    bd.projects.set_current('ulcarchetype')

    if bd.config.biosphere not in bd.databases:
        raise ValueError("biosphere database missing, install first")

    biosphere_db = bd.Database(bd.config.biosphere)

    pm_lowpop = biosphere_db.get(name='Particulate Matter, < 2.5 um',
                    categories=('air', 'low population density, long-term'))

    pm_lower_stratosphere = biosphere_db.get(name='Particulate Matter, < 2.5 um',
                    categories=('air', 'lower stratosphere + upper troposphere'))

    pm_non_urban = biosphere_db.get(name='Particulate Matter, < 2.5 um',
                    categories=('air', 'non-urban air or from high stacks'))

    pm_undefined= biosphere_db.get(name='Particulate Matter, < 2.5 um',
                    categories=('air',))

    pm_urban = biosphere_db.get(name='Particulate Matter, < 2.5 um',
                    categories=('air','urban air close to ground'))

 
    ### test database

    # activity 1
    act1_key=('test_db2','activity_1')
    # a unique emission of PM in an uncertain archetype
    biosphere_exchange_1={'amount':1,
                        'input':pm_undefined,
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
                        'input':pm_undefined,
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
    db=bd.Database('test_db2')
    db.write(database_dict)

 
    # create a test methods
    cfs=[(pm_non_urban,1),
     (pm_lower_stratosphere,1),
     (pm_lowpop,1),
     (pm_undefined,10),#unspecified
     (pm_urban,10)]

    test_method_name_1=('test method','1 unspecified')

    test_method_1=bd.Method(test_method_name_1)

    metadata_test_method={
    'description':'method to test uncertainty on archetype',
    'unit':'DALY'}
    test_method_1.register(**metadata_test_method)
    test_method_1.write(cfs)


    ## 0 unnespecified

    cfs=[
    (pm_non_urban,1),
    (pm_lower_stratosphere,1),
    (pm_lowpop,1),
    # (pm_undefined,10),#unspecified
    (pm_urban,10)]

    test_method_name_2=('test method','0 unspecified')

    test_method_2=bd.Method(test_method_name_2)

    metadata_test_method_2={'description':'method to test uncertainty on archetype',
    'unit':'DALY'}

    test_method_2.register(**metadata_test_method_2)
    test_method_2.write(cfs)


if __name__ == "__main__":
    main()