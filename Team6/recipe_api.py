import requests
from bs4 import BeautifulSoup
import re
import __future__

PRIMARY_COOKING_METHODS = ['saute', 'broil', 'boil', 'poach', 'freeze']

def autograder(url):
    '''Accepts the URL for a recipe, and returns a dictionary of the
    parsed results in the correct format. See project sheet for
    details on correct format.'''
    # your code here

    results = {}
    results['url'] = url
    results['ingredients'] = []
    r = requests.get(url)
    primary_methods = []
    soup = BeautifulSoup(r.text)
    ingredients = soup.findAll("span", { "itemprop" : "ingredients" })
    quantity_reg = re.compile(r'[\d/]+ (?:teaspoon|tablespoon|cup)?s?')
    number_reg = re.compile(r'[\d/]+')
    for ingredient_expression in ingredients:
    	ingredient_dict = {}
    	quantity = re.findall(quantity_reg, ingredient_expression.contents[0])
        number = re.findall(number_reg, ingredient_expression.contents[0])
    	if len(quantity) > 0:
            ingredient = ingredient_expression.contents[0]
            if number[0] in quantity[0] and '/' in number[0]:
                formatted_quantity = quantity[0].replace(number[0], "%.2f" % eval(compile(number[0], '<string>', 'eval', __future__.division.compiler_flag)))
                ingredient = ingredient.replace(number[0], "%.2f" % eval(compile(number[0], '<string>', 'eval', __future__.division.compiler_flag)))
            else:
                formatted_quantity = quantity[0]
    		ingredient_dict['quantity'] = formatted_quantity
    	else:
    		ingredient = ingredient_expression.contents[0]
    		ingredient_dict['quantity'] = 1
    	ingredient_dict['ingredient'] = ingredient
    	results['ingredients'].append(ingredient_dict)
    method = soup.findAll("span", { "class" : "recipe-directions__list--item" })
    step_number = 1
    for step in method:
        if step.contents == []:
            method.remove(step)
            break
        print str(step_number) + '. ' + step.contents[0]
        step_number = step_number + 1
        for prim_method in PRIMARY_COOKING_METHODS:
            if prim_method in step.contents[0].lower() and prim_method not in primary_methods:
                primary_methods.append(prim_method)
    results['primary cooking method'] = primary_methods

    return results

def main():
	print autograder('http://allrecipes.com/Recipe/Easy-Garlic-Broiled-Chicken/')

if __name__ == '__main__':
    main()