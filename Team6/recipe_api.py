import requests
from bs4 import BeautifulSoup
import re
import __future__
from generate_dicts import load

PRIMARY_COOKING_METHODS = ["saute", "broil", "boil", "poach", "freeze"]
DESCRIPTORS = ["microwave safe ", "baking "]

def autograder(url):
    """Accepts the URL for a recipe, and returns a dictionary of the
    parsed results in the correct format. See project sheet for
    details on correct format."""
    # your code here

    results = {}
    results["url"] = url
    results["ingredients"] = []
    r = requests.get(url)
    soup = BeautifulSoup(r.text)

    primary_methods = []
    tools = []
    methods = []

    tools_list = load("tools")
    methods_list = load("modifiers")
    del tools_list[""]
    del tools_list["melt"]
    del tools_list["grease"]
    tools_list["knife"] = "knife"
    measurement_list = load("measurements")

    ingredients = soup.findAll("span", { "itemprop" : "ingredients" })
    number_reg = re.compile(r"[\d/]+")
    for ingredient_expression in ingredients:
    	ingredient_dict = {}
        quantity = ""
        for measurement in measurement_list:
            #quantity_reg = re.compile(r"[\d/]+ (?:teaspoon|tablespoon|cup)?s?")
            quantity_reg = re.compile(r"(?:%s)?" % measurement)            
            if len(re.findall(quantity_reg, ingredient_expression.contents[0])) > 0 and len(quantity) < len(max(re.findall(quantity_reg, ingredient_expression.contents[0]), key=len)):
                quantity = max(re.findall(quantity_reg, ingredient_expression.contents[0]),key=len)
        number = re.findall(number_reg, ingredient_expression.contents[0])
        is_float = False
    	if len(number) > 0:
            number = max(number,key=len)
            ingredient = ingredient_expression.contents[0]
            if "/" in number:
                formatted_number = str(float("%.2f" % eval(compile(number, "<string>", "eval", __future__.division.compiler_flag))))
                is_float = True
            else:
                formatted_number = number
            if is_float:
                ingredient_dict["quantity"] = float(formatted_number)
            else:
                ingredient_dict["quantity"] = int(formatted_number)
    	else:
            number = "1"    		
            ingredient = ingredient_expression.contents[0]    		
            ingredient_dict["quantity"] = int(number)
        if quantity != "":
            ingredient_dict["measurement"] = quantity
        else:
            ingredient_dict["measurement"] = "unit"
        ingredient = ingredient.replace(number, "")
        ingredient = ingredient.replace(quantity, "")
        ingredient = ingredient.strip(" ")
        ingredient = ingredient.strip("s ")
        split_ingredient = ingredient.split(",")
        if len(split_ingredient) > 1:
            descriptor = split_ingredient[1].strip(" ")
            ingredient_dict["descriptor"] = descriptor
            ingredient_dict["preparation"] = descriptor
        ingredient = split_ingredient[0]
    	ingredient_dict["name"] = ingredient
    	results["ingredients"].append(ingredient_dict)
        for tool in tools_list:
            if tool in ingredient and tools_list[tool] not in tools:
                tools.append(tools_list[tool])

    method_html = soup.findAll("span", { "class" : "recipe-directions__list--item" })
    step_number = 1
    for step in method_html:
        if step.contents == []:
            method_html.remove(step)
            break
        print str(step_number) + ". " + step.contents[0]
        step_number = step_number + 1
        for prim_method in PRIMARY_COOKING_METHODS:
            if prim_method in step.contents[0].lower() and prim_method not in primary_methods:
                primary_methods.append(prim_method)
        for method in methods_list:
            if method in step.contents[0].lower() and method not in methods:
                methods.append(method)
        for tool in tools_list:
            skip = False
            for descriptor in DESCRIPTORS:
                if descriptor + tool in step.contents[0].lower() and descriptor + tools_list[tool] not in tools:
                    tools.append(descriptor + tools_list[tool])
                    skip = True            
            redundant = False
            for descriptor in DESCRIPTORS:
                if descriptor + tools_list[tool] in tools:
                        redundant = True
            if tool in step.contents[0].lower() and tools_list[tool] not in tools and not skip:
                if not redundant:
                    tools.append(tools_list[tool])
    results["primary cooking method"] = primary_methods
    results["cooking methods"] = methods
    results["cooking tools"] = tools
    max_list = {}
    max_list["cooking tools"] = (len(tools))
    max_list["primary cooking method"] = len(primary_methods)
    max_list["cooking methods"] = len(methods)
    results["max"] = max_list

    return results

def main():
	print autograder("http://allrecipes.com/Recipe/Easy-Garlic-Broiled-Chicken/")

if __name__ == "__main__":
    main()