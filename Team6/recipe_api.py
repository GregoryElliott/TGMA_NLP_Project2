import requests
from bs4 import BeautifulSoup
import re

def autograder(url):
    '''Accepts the URL for a recipe, and returns a dictionary of the
    parsed results in the correct format. See project sheet for
    details on correct format.'''
    # your code here
    results = {}
    results['url'] = url
    results['ingredients'] = []
    r = requests.get(url)
    soup = BeautifulSoup(r.text)
    ingredients = soup.findAll("span", { "itemprop" : "ingredients" })
    quantity_reg = re.compile(r'[\d/]+ (?:teaspoon|tablespoon|cup)?s?')
    for ingregient_expression in ingredients:
    	ingredient_dict = {}
    	#print ingregient_expression
    	quantity = re.findall(quantity_reg, ingregient_expression.contents[0])
        print quantity
    	if len(quantity) > 0:
    		ingredient = ingregient_expression.contents[0].replace(quantity[0], "")
    		ingredient_dict['quantity'] = quantity[0]
    	else:
    		ingredient = ingregient_expression.contents[0]
    		ingredient_dict['quantity'] = 1
    	ingredient_dict['ingredient'] = ingredient
    	#print ingredient_dict
    	results['ingredients'].append(ingredient_dict)

    return results

def main():
	print autograder('http://allrecipes.com/recipe/80827/easy-garlic-broiled-chicken/')

if __name__ == '__main__':
    main()