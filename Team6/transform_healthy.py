#------------------------------------------------------------------------------
# Functions for Health Transformations
#------------------------------------------------------------------------------
# Requirements: py-bing-search
# pip install py-bing-search
#------------------------------------------------------------------------------
# TODO:
# Safety check modifiers
# Update unsalted/sodium stripped
# https://en.wikipedia.org/wiki/Glycemic_index
# http://www.nhlbi.nih.gov/health/educational/lose_wt/eat/shop_lcal_fat.htm
# http://greatist.com/health/83-healthy-recipe-substitutions
#------------------------------------------------------------------------------

from py_bing_search import PyBingSearch
import pickle
import os.path

## -- Temp (Testing)
from recipe_api import autograder
tR =  autograder("http://allrecipes.com/Recipe/Easy-Garlic-Broiled-Chicken/")
SaltedIngredients = {'ingredients': [{'measurement': u'cup', 'name': u'unsalted butter', 'quantity': 0.5}, {'measurement': u'tablespoon', 'name': u'unsalted minced garlic', 'quantity': 3}, {'measurement': u'tablespoon', 'name': u'oy sauce', 'quantity': 3}, {'measurement': u'teaspoon', 'name': u'unsalted black pepper', 'quantity': 0.25}, {'measurement': u'tablespoon', 'name': u'low sodium dried parsley', 'quantity': 1}, {'preparation': u'with skin', 'descriptor': u'with skin', 'measurement': 'unit', 'name': u'boneless chicken thighs', 'quantity': 6}, {'preparation': u'to taste', 'descriptor': u'to taste', 'measurement': 'unit', 'name': u'low sodium dried parsley', 'quantity': 1}], 'url': 'http://allrecipes.com/Recipe/Easy-Garlic-Broiled-Chicken/', 'cooking methods': ['lightly', '', 'melted'], 'primary cooking method': ['broil'], 'max': {'cooking tools': 7, 'cooking methods': 3, 'primary cooking method': 1}, 'cooking tools': ['knife', 'oven', 'broiler', 'baking pan', 'microwave', 'microwave safe bowl', 'baster']}
## -- End Temp (Testing) 

## -- Parameters --
NUM_SEARCH_RESULTS = 10
BING_SEARCH_KEY = 'mZWe3rWOjWMxHpyq4b6SNCRktZWeIql+zWcD0gcrm80'

## -- Provides --
## -- External facing functins

def t_low_sodium (recipe, is_to):
    '-> _Recipe_ Transforms a recipe to a low sodium variat'
    return transform(recipe,
                     't_sodium',
                     ['unsalted', 'low sodium'],
                     is_to)

def t_low_fat (recipe, is_to):
    '-> _Recipe_ Transforms a recipe to a low fat variant'
    return transform(recipe,
                     't_lowfat',
                     ['lowfat, skim, reduced fat'],
                     is_to)


## -- Internal --
def transform(recipe, fname, search_alias, is_to):
    '-> _Recipe_ transforms a recipe using dict fname and list-of search_alias'
    if (is_to):
        dict_transforms = load_t(fname)
                        
        for ingredient in recipe['ingredients']:
            found = False
            transform = ''

            # First check our dictionary of transforms
            try: transform = dict_transforms[ingredient['name']]
            except Exception:
                pass
  #          print ingredient['name'], transform
            if not (transform == '' or  transform == 'none'):
                ingredient['name'] = transform
                found = True
            if transform == 'none':
                found = True
            # Else search bing if not in transforms
            if not found:
                for alias in search_alias:
                    #safety check
                    for inner in search_alias:
                        index = ingredient['name'].find(inner)  ##! -- TODO: check modifiers ##!
                        if index != -1:
                            found = True
                            break
                    if not found:
                        if(found_pair(alias, ingredient['name'])):
                            dict_transforms[ingredient['name']] = alias + ' ' + ingredient['name'] #append
                            ingredient['name'] = alias + ' ' + ingredient['name'] #update recipe
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
                index = ingredient['name'].find(alias)
                if index != -1:
                    #cut out 
                    ingredient['name'] = ingredient['name'][:0] + ingredient['name'][(len(alias)+1):]
        return recipe

    
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


