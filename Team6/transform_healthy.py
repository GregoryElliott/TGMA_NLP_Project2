#------------------------------------------------------------------------------
# Functions for Health Transformations
#------------------------------------------------------------------------------
# Requirements: py-bing-search
# pip install py-bing-search
#------------------------------------------------------------------------------

from py_bing_search import PyBingSearch
import pickle
import os.path

## -- Parameters --
NUM_SEARCH_RESULTS = 10
BING_SEARCH_KEY = 'mZWe3rWOjWMxHpyq4b6SNCRktZWeIql+zWcD0gcrm80'

## -- Provides --
## -- External facing functins

def t_low_sodium (recipe, is_to):
    '-> _Recipe_ Transforms a recipe to a low sodium variat'
    return transform(recipe,
                     't_sodium',
                     ['low sodium', 'unsalted', 'low-sodium', 'sodium-free'],
                     {'marinade': 'cirtus juice',
                      'baking soda': 'eggs'},
                     ['salt', 'salted'],
                     is_to)

def t_low_fat (recipe, is_to):
    '-> _Recipe_ Transforms a recipe to a low fat variant'
    return transform(recipe,
                     't_lowfat',
                     ['skim', 'lowfat', 'reduced fat'],
                     {'ice cream' : 'sorbet', 
                      'cream' : 'milk',
                      'cocoa' : 'cacao',
                      'chocolate' : 'cacao',
                      'bacon' :  'prosciutto',
                      'egg' : 'egg white',
                      'eggs' : 'egg whites',
                      'bison' : 'beef',
                      'sour cream' : 'cottage cheese',
                      'ramen noodles' : 'rice noodles',
                      'granola': 'bran flakes',
                      'alfredo': 'marinara',
                      'donut' : 'english muffin',
                      'guacamole' : 'salsa',
                      'refried beans' : 'salsa'
                     },
                     [],
                     is_to)


## -- Internal --
def transform(recipe, fname, search_alias, replacements, discards, is_to):
    '-> _Recipe_ transforms a recipe using dict fname and list-of search_alias'
    if (is_to):
        dict_transforms = load_t(fname)

        # Discards
        for ingredient in recipe['ingredients']:
            for discard in discards:
                if ingredient['name'].find(discard) != -1:
                    print 'removing', ingredient
                    del ingredient

                    
        for ingredient in recipe['ingredients']:
            found = False
            transform = ''

            # Replacements
            for replacement in replacements.keys():
                if ingredient['name'].find(replacement) != -1:
                    ingredient['name'] = replacements[replacement]
                    continue #move on to next
          
            # First check our dictionary of transforms
            try: transform = dict_transforms[ingredient['name']]
            except Exception:
                pass
            if not (transform == '' or  transform == 'none'):
                if not check_descriptor(ingredient['descriptor'], transform)[0]: 
                    ingredient['descriptor'].append(transform)
                found = True
            if transform == 'none':
                found = True
            # Else search bing if not in transforms
            if not found:
                for alias in search_alias:
                    #safety check
                    for inner in search_alias:
                        found = check_descriptor(ingredient['descriptor'], inner)[0]
                        if found:
                            break
                    if not found:
                        if(found_pair(alias, ingredient['name'])):
                            dict_transforms[ingredient['name']] = alias #append
                            ingredient['descriptor'].append(alias)  #update recipe
                            found = True
                            break # only need one alias
            # Not in dictionary & Not in bing -> append none to dict
            if not found:
                dict_transforms[ingredient['name']] = 'none'

        # Store new transforms in dictionary
        dump_transform(dict_transforms, fname)
        return recipe
    else:
        for ingredient in recipe['ingredients']:
            for alias in search_alias:
                try:
                    ingredient['descriptor'].remove(alias)
                except Exception:
                    pass
        return recipe


def check_descriptor (lst, alias):
    index = -1
    ittr = 0 
    for descriptor in lst:
        ittr+=1
        index = descriptor.find(alias)
        if (index != -1):
            return [True, ittr]
    return [False, 0]

## -- File Management
def load_t(fname):
    '-> _Dict_ of transform fname'
    f = fname + '.data'
    f = os.path.join("transforms", f)
    if not os.path.exists(f):
        emptyDict = {}
        return emptyDict
    with open(f) as inFile:
        return pickle.load(inFile)

def dump_transform(object, fname):
    '-> _null_, dump object at transform\fname '
    f = fname + '.data'
    subdir = 'transforms'
    fname = fname + '.data'
    print 'Creating', fname 
    try: os.mkdir(subdir)
    except Exception:
        pass
    with open(os.path.join(subdir, fname), 'w') as outFile:
        pickle.dump(object, outFile)
        
## -- Misc Helpers
def norm (s):
    '-> _String_ set lowercase, striped of nonalpha'
    ns = ""
    for i in range(0, len(s)):
        if(s[i].isalpha() or s[i].isspace() ):
            ns += s[i].lower(); 

    return ns 

def get_results(search):
    '-> _List_ of dictionaries of results'
    bing = PyBingSearch(BING_SEARCH_KEY)
    results, next_uri = bing.search(search, limit =NUM_SEARCH_RESULTS, format ='json')
    return results

def found_pair (term, ingredient):
    '-> _Bool_ of whether term + ingredient pair was found'
    print term, ingredient
    try: results = get_results(term + ingredient);
    except Exception:
        return False
    for result in results:
        norm_string = norm(result.description)
        if (norm_string.find(term + ' ' + ingredient) != -1):
            print norm_string
            return True
    return False


