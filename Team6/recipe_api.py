import requests
from bs4 import BeautifulSoup
import re
import __future__
from generate_dicts import load
import pprint

PRIMARY_COOKING_METHODS = ["saute", "broil", "boil", "poach", "freeze", "bake"]
DESCRIPTORS = ["microwave safe","baking","prepared","dried","ground","seasoned","parmesan","grated","skim","Worchestershire","hot","crushed","small"]
PREPARATION = ["microwave safe","baking","prepared","dried","chopped","ground","grated","crushed"]
PREP_DESCRIPTORS = ["hot","prepared","dried"]
METHODS = ["grease","greasing","preheat","preheating","mix","mixing","melted","melting","arrange","arranging","microwave","microwaving","coat","coating","basting","broil","broiling","turning","sprinkle","sprinkling","preheat", "pour","place","coat","coating","squeeze","slice","melt","add","stir","cook","sprinkle","coated","stirring","reduce","adjusting","spoon","place", "season", "mix", "add", "blended", "form", "preheat", "preheated","preheat", "combine", "season", "place", "form", "mix"]

def get_methods():
    r = requests.get(str("https://en.wikipedia.org/wiki/Category:Cooking_techniques"))
    soup = BeautifulSoup(r.content, "html.parser")
    methods = []
    methods_div = soup.find("div", {"id": "mw-pages"})

    for method in methods_div.findAll("a"):
        try:
            mystring = str(method.text).lower()
        except:
            continue
        result = mystring
        start = mystring.find( '(' )
        end = mystring.find( ')' )
        if start != -1 and end != -1:
            result = mystring[start+1:end]
        if result:
            methods.append(result)
    return methods


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

    tools = []
    methods = []
    primary_methods = ""

    tools_list = load("tools")
    del tools_list[""]
    del tools_list["melt"]
    del tools_list["grease"]
    methods_list = []#METHODS#load("modifiers")
    for method in get_methods():
        methods_list.append(method)

    print methods_list
    #methods_list.remove("")
    measurement_list = load("measurements")
    measurement_list.append("to taste")
    measurement_list.append("dash")
    measurement_list.remove("")
    measurement_list.remove("chop")

    ingredients = soup.findAll("span", { "itemprop" : "ingredients" })
    number_reg = re.compile(r"[\d/]+[\d/ ]*")
    for ingredient_expression in ingredients:
    	ingredient_dict = {}
        quantity = ""
        for measurement in measurement_list:
            quantity_reg = re.compile(r"%s(?:s )?" % measurement)            
            if len(re.findall(quantity_reg, ingredient_expression.contents[0])) > 0 and len(quantity) < len(max(re.findall(quantity_reg, ingredient_expression.contents[0]), key=len)):
                quantity = max(re.findall(quantity_reg, ingredient_expression.contents[0]),key=len)
        number = re.findall(number_reg, ingredient_expression.contents[0])
        is_float = False
    	if len(number) > 0:
            number = max(number,key=len)
            original_number = number
            number = number.strip(" ")
            number_split = number.split(" ")
            split_num = False
            if len(number_split) > 1:
                split_num = True
                number = number_split[1]
            ingredient = ingredient_expression.contents[0]
            if "/" in number:
                formatted_number = str(float("%.2f" % eval(compile(number, "<string>", "eval", __future__.division.compiler_flag))))
                is_float = True
            else:
                formatted_number = number
            if split_num:
                formatted_number = float(number_split[0]) + float(formatted_number)
            if is_float:
                ingredient_dict["quantity"] = float(formatted_number)
            else:
                ingredient_dict["quantity"] = int(formatted_number)
    	else:
            number = "1"    		
            ingredient = ingredient_expression.contents[0]    		
            ingredient_dict["quantity"] = int(number)
        #if "chop" in quantity:
            #ingredient_dict["measurement"] = "unit"
        if quantity != "":
            ingredient_dict["measurement"] = quantity
        else:
            ingredient_dict["measurement"] = "unit"
        ingredient = ingredient.replace(original_number, "")
        ingredient = ingredient.replace(number, "")
        ingredient = ingredient.replace(quantity, "")
        ingredient = ingredient.strip(" ")
        split_ingredient = ingredient.split(",")
        ingredient_dict["descriptor"] = []
        ingredient_dict["preparation"] = []
        if len(split_ingredient) > 1:
            descriptor = split_ingredient[1].strip(" ")
            #ingredient_dict["descriptor"].append(descriptor)
            ingredient_dict["preparation"].append(descriptor)
        ingredient = split_ingredient[0]
        for d in DESCRIPTORS:
            if d in ingredient_expression.contents[0].lower() and d.lower() not in ingredient_dict["descriptor"] and str(d[0].upper() + d[1:]) not in ingredient_dict["descriptor"]:
                ingredient_dict["descriptor"].append(d)
                if d in ingredient:
                    ingredient = ingredient.replace(d, "")
        for word in ingredient_expression.contents[0].split(" "):
            if word[0].isupper() and word[0] not in ingredient_dict["descriptor"]:
                ingredient_dict["descriptor"].append(word)
                if word[0].lower() in ingredient_dict["descriptor"]:
                    print word[0]
                    print ingredient_dict
                    ingredient_dict["descriptor"].remove(word[0].lower())
                    print ingredient_dict
                if word in ingredient:
                    ingredient = ingredient.replace(word, "")
        for p in PREPARATION:
            if p in ingredient_expression.contents[0].lower() and p.lower() not in ingredient_dict["preparation"] and str(p[0].upper() + p[1:]) not in ingredient_dict["preparation"]:
                ingredient_dict["preparation"].append(p)
                if p in ingredient:
                    ingredient = ingredient.replace(p, "")
        ingredient = ingredient.strip(" ")
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
            if prim_method in step.contents[0].lower(): #and prim_method not in primary_methods:
                primary_methods = prim_method
        for method in methods_list:
            if method in step.contents[0].lower() and method not in methods:
                methods.append(method)
            elif method.strip("ed") in step.contents[0].lower() and method not in methods:
                methods.append(method)
            elif method.strip("ing") in step.contents[0].lower() and method not in methods:
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

    return results

def main():
	#pprint.pprint(autograder("http://allrecipes.com/Recipe/Easy-Garlic-Broiled-Chicken/"))
    #pprint.pprint(autograder("http://allrecipes.com/recipe/easy-meatloaf/"))
    pprint.pprint(autograder("http://allrecipes.com/Recipe/Meatball-Nirvana/"))
    #autograder("http://allrecipes.com/Recipe/Easy-Garlic-Broiled-Chicken/")

if __name__ == "__main__":
    main()