import pickle
import os.path

def load(data):
    '''Loads the selected object'''
    f = data + '.data'
    with open(os.path.join("dicts", f)) as inFile:
        return pickle.load(inFile)

def generate_dicts():
    def dump(obj, fname):
        subdir = 'dicts'
        fname = fname + '.data'
        print 'Creating', fname 
        try: os.mkdir(subdir)
        except Exception:
            pass
        with open(os.path.join(subdir, fname), 'w') as outFile:
            pickle.dump(obj, outFile)
    def create_dict():
        d = {}
        with open("dicts.txt") as dictionary:
            for line in dictionary:
                if line.find("[modifiers]") != -1: break
                line = line.rstrip('\n')
                line = line.split(',')
                value = line[0]
                for token in line:
                    d[token] = value
        return d
    def create_list(start, end):
        l_modifiers = []
        foundModifier = False
        with open("dicts.txt") as dictionary:
            for line in dictionary:
                if line.find(end) != -1: break
                if(foundModifier):
                    line = line.rstrip('\n')
                    l_modifiers.append(line)
                elif line.find(start) != -1:
                    foundModifier = True
        return l_modifiers
    dump(create_dict(), 'tools')
    dump(create_list('[modifiers]','[measurements]'), 'modifiers')
    dump(create_list('[measurements]','[sizes]'), 'measurements')
    dump(create_list('[sizes]','[temperatures]'), 'sizes')
    dump(create_list('[temperatures]','[duration]'), 'temperatures')
    dump(create_list('[duration]','[health]'), 'duration')
    dump(create_list('[health]','[health-fat]'), 'health')
    dump(create_list('[descriptor]','[preparation]'), 'descriptor')
    dump(create_list('[preparation]','[prep-description]'), 'preparation')
    dump(create_list('[prep-description]','[End]'), 'prep-description')

        

    


