from pathlib import Path
import bw2data as bd
import bw2io

def main():

    bd.projects.set_current('bw25')

    b3_codes = [a.key[1] for a in bd.Database('biosphere3')]

    path = Path(__file__).parent/'impact_world_expert_version.bw2package'
    assert path.exists(),path

    methods = bw2io.package.BW2Package.load_file(path)

    
    for m in methods:
        # remove ones with 0 cf, convert tuple to list
        m['data'] = [[ef,cf] for (ef,cf) in m['data'] if cf!=0]

        # remove the cfs related to ef that are no longer present in biosphere3
        m['data'] = [[ef,cf] for ef,cf in m['data'] if ef[1] in b3_codes]
    
        not_duplicated = len(m['data']) == len({ef for (ef,cf) in m['data']})
        assert not_duplicated,'the same substance has more than 1 characterisation factor'

    for m in methods:
        method = bd.Method(m['name'])
        assert method.validate(m['data'])
        method.register(unit=m['metadata']['unit'])
        method.write(m['data'])


if __name__ == '__main__':

    main()