import requests
from bs4 import BeautifulSoup
import re
import __future__
from generate_dicts import load
from transform_healthy import t_low_sodium, t_low_fat 
import pprint
import unicodedata
import os 

GLUTEN_FREE = {'bread crumbs':'corn meal', 'bread':'gluten-free bread', 'pasta':'rice', 'noodles':'rice' ,
                    'wheat flour': 'corn flour', 'matzo':'gluten-free matzo', 'flour tortilla': 'corn tortilla',
                    'rye flour': 'corn flour', 'barley flour': 'corn flour', 'oat flour': 'corn flour',
                    'panko': 'corn meal', 'farina': 'rice cereal', 'granola': 'rice cereal',
                    'pita bread': 'gluten-free flatbread', 'lasagna': 'gluten-free lasagna', 'macaroni':
                    'gluten-free macaroni', 'orzo': 'gluten-free orzo', 'couscous': 'gluten-free couscous', 'spaghetti':
                    'gluten free spaghetti', 'seitan': 'soy-based vegetable protein'}
LACTOSE_FREE = {'milk':'lactose-free milk', 'yogurt':'lactose-free yogurt', 'butter':'lactose-free margarine',
                     'sour cream': 'soy sour cream', 'buttermilk': 'soymilk', 'light cream': 'whole coconut milk',
                     'heavy cream': 'cream of coconut', 'ghee': 'soy margarine', 'evaporated milk': 'soy yogurt',
                     'low-fat milk': 'almond milk', 'whole milk': 'light coconut milk', 'cheese': 'soy cheese',
                     'ice cream': 'sorbet', 'milk chocolate': 'rice milk chocolate', 'powdered milk': 'soy milk powder',
                     'cream cheese': 'tofu spread', 'whey protein powder': 'soy protein powder', 'gelato':
                     'coconut milk ice cream', 'sherbet': 'sorbet', 'chocolate chips': 'carob chips'
                     }
GLUTEN = {'corn meal': 'bread crumbs', 'gluten-free bread': 'bread', 'rice': 'pasta', 'gluten-free matzo': 'matzo',
          'corn tortilla': 'flour tortilla', 'corn flour': 'rye flour', 'rice cereal': 'farina',
          'gluten-free flatbread': 'pita bread', 'gluten-free lasagna': 'lasagna', 'gluten-free macaroni': 'macaroni',
          'gluten-free orzo': 'orzo', 'gluten-free couscous': 'couscous', 'gluten free spaghetti': 'spaghetti',
          'soy-based vegetable protein': 'seitan'}
LACTOSE = {'lactose-free milk': 'milk', 'lactose-free yogurt': 'yogurt', 'lactose-free margarine': 'butter',
           'soy sour cream': 'sour cream', 'soymilk': 'buttermilk', 'whole coconut milk': 'light cream',
           'cream of coconut': 'heavy cream', 'soy margarine': 'ghee', 'soy yogurt': 'evaporated milk',
           'almond milk': 'low-fat milk', 'light coconut milk': 'whole milk', 'soy cheese': 'cheese',
           'sorbet': 'ice cream', 'rice milk chocolate': 'milk chocolate', 'soy milk powder': 'powdered milk',
           'tofu spread': 'cream cheese', 'soy protein powder': 'whey protein powder',
           'coconut milk ice cream': 'gelato', 'carob chips': 'chocolate chips'}
PRIMARY_COOKING_METHODS = ["sautee", "broil", "boil", "poach", "freeze", "bake", "grill", "fried", "roasted", "smoked"]
DESCRIPTORS = ["microwave safe","baking","prepared","dried","ground","seasoned","parmesan","grated","skim","Worchestershire","hot","crushed","small","skinless","boneless"]
PREPARATION = ["microwave safe","baking","prepared","dried","chopped","ground","grated","crushed","sliced","skinless","boneless"]
PREP_DESCRIPTORS = ["hot","prepared","dried"]
METHODS = ["sautee","grease","greasing","preheat","preheating","mix","mixing","melted","melting","arrange","arranging","microwave","microwaving","coat","coating","basting","broil","broiling","turning","sprinkle","sprinkling","preheat", "pour","place","coat","coating","squeeze","slice","melt","add","stir","cook","sprinkle","coated","stirring","reduce","adjusting","spoon","place", "season", "mix", "add", "blended", "form", "preheat", "preheated","preheat", "combine", "season", "place", "form", "mix"]
COLORS = ["red", "brown", "black", "blue", "green", "orange", "purple", "white", "pink", "yellow", "gold", "silver"]

def get_methods():
    r = requests.get(str("http://www.enchantedlearning.com/wordlist/cooking.shtml"))
    soup = BeautifulSoup(r.content)
    methods = []
    methods_div = soup.findAll("table")

    for div in methods_div:
        if "macerate" in str(div.contents):
            for method in div.findAll("br"):
                try:
                    mystring = remove_parentheses(str(method.previous_sibling)).lower().lstrip()
                except:
                    continue
                methods.append(mystring)
    return methods

def get_foods():
    r = requests.get("http://eatingatoz.com/food-list/")
    soup = BeautifulSoup(r.content)
    foods = []
    for food in soup.find("div",{"class:","entry"}).findAll("li"):
        try:
            mystring = remove_parentheses(str(food.text)).lower().lstrip()
        except:
            continue        
        foods.append(mystring)
 #COMMENT   print foods
    return foods

def get_tools():
    r = requests.get(str("http://www.enchantedlearning.com/wordlist/cookingtools.shtml"))
    soup = BeautifulSoup(r.content)
    tools = {}
    tools_div = soup.findAll("table")

    for div in tools_div:
        if "Dutch oven" in str(div.contents):
            for tool in div.findAll("br"):
                try:
                    mystring = remove_parentheses(str(tool.previous_sibling)).lower().lstrip()
                except:
                    continue
                tools[mystring] = mystring
    return tools

def remove_parentheses(mystring):
    result = mystring
    start = mystring.find( '(' )
    end = mystring.find( ')' )
    if start != -1 and end != -1:
        result = mystring[:start] + mystring[end+1:]
    return result

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

    steps = []

    tools = []
    methods = []
    primary_methods = ""

    food_list = get_foods()
    food_list.append("breast")
    food_list.append("olive")
    food_list.append("onion")
    while "" in food_list:
        food_list.remove("")

    tools_list = load("tools")
    tools_list.update(get_tools())
    while "" in tools_list:
        del tools_list[""]        
    del tools_list["melt"]
    del tools_list["grease"]
    methods_list = METHODS
    for method in get_methods():
        if method[-3:] != "ing":
            methods_list.append(method)

    while "" in methods:
        methods_list.remove("")
    measurement_list = load("measurements")
    measurement_list.append("to taste")
    measurement_list.append("dash")
    measurement_list.remove("")
    measurement_list.remove("chop")

    ingredients = soup.findAll("span", { "itemprop" : "ingredients" })
    number_reg = re.compile(r"[\d/]+[\d/ ]*")
    for ingredient_expression in ingredients:
    #COMMENT    print ingredient_expression.contents[0]
        ingredient_expression.contents[0] = remove_parentheses(ingredient_expression.contents[0]).replace(u"\u00E9", "e")
    	ingredient_dict = {}
        quantity = ""
        for measurement in measurement_list:
            quantity_reg = re.compile(r"%s(?:s )?" % measurement)            
            if len(re.findall(quantity_reg, ingredient_expression.contents[0])) > 0 and len(quantity) < len(max(re.findall(quantity_reg, ingredient_expression.contents[0]), key=len)) and quantity != "dash":
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
        if quantity != "":
            ingredient_dict["measurement"] = quantity.strip(" ")
        else:
            ingredient_dict["measurement"] = "unit"
        ingredient_dict["descriptor"] = ""
        ingredient_dict["preparation"] = ""
        ingredient = ingredient.replace(original_number, "")
        ingredient = ingredient.replace(number, "")
        ingredient = ingredient.replace(quantity, "")
        ingredient = ingredient.strip(" ")
        split_ingredient = ingredient.split(",") 
        no_split = False       
        if len(split_ingredient) > 1:
            if " or " not in split_ingredient[1] and len(split_ingredient[0].strip(" ").split(" ")) > 1:
                descriptor = split_ingredient[1].strip(" ")
                ingredient_dict["preparation"] = descriptor.strip(" ")                
            for food in food_list:
                if food in split_ingredient[1]:
       #COMMENT             print food
                    no_split = True
                    break
        if no_split:
            ingredient = ingredient.replace(",", "")
        else:            
            ingredient = split_ingredient[0]
  #COMMENT      print ingredient
        split_ingredient = ingredient.split(" ")
        if len(split_ingredient) > 1 and "and" not in ingredient:
            while "" in split_ingredient:
                split_ingredient.remove("")
            split_ingredient.remove(split_ingredient[len(split_ingredient)-1])
            concatenate = False
            for word in split_ingredient:
                if word not in food_list:
                    if concatenate:
                        new_word = color.strip(" ") + " " + word.strip(" ")
                        ingredient_dict["descriptor"] = new_word.strip(" ")
                        concatenate = False
                        ingredient = ingredient.replace(new_word, "")
                        continue
                    concatenate = False
                    if word in COLORS:
                        color = word
                        concatenate = True
                        continue
                    ingredient_dict["descriptor"] = word.strip(" ")
                    if word.strip(" ")[-2:] == "ly":
                        ingredient_dict["prep-description"] = word.strip(" ")
                    ingredient = ingredient.replace(word, "")
                elif word in food_list:
                    ingredient_dict["descriptor"] = word.strip(" ")
        for d in DESCRIPTORS:
            if d in ingredient_expression.contents[0].lower(): 
                ingredient_dict["descriptor"] = d.strip(" ")
                if d.strip(" ")[-2:] == "ly":
                    ingredient_dict["prep-description"] = d.strip(" ")
        for word in ingredient_expression.contents[0].split(" "):
            try:
                if word[0].isupper() and word[0] not in ingredient_dict["descriptor"]:
                    ingredient_dict["descriptor"] = word.strip(" ")
            except Exception:
                ingredient_dict["descriptor"] = ""
        for p in PREPARATION:
            if p in ingredient_expression.contents[0].lower():
                ingredient_dict["preparation"] = p.strip(" ")
                if p.strip(" ")[-2:] == "ly":
                    ingredient_dict["prep-description"] = p.strip(" ")
                if p in ingredient:
                    ingredient = ingredient.replace(p, "")        
        ingredient = ingredient.strip(" ").replace("  ", " ")
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
   #COMMENT     print str(step_number) + ". " + step.contents[0]
        steps.append(step.contents[0])
        step_number = step_number + 1
        for prim_method in PRIMARY_COOKING_METHODS:
            if prim_method in step.contents[0].lower(): 
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
    results["steps"] = steps

    return results

def change_method(results):
        primary_method =  results["primary cooking method"]
        ingredient = results["ingredients"]
        primary_ingredient = None
        valid_input = False
        for k in ingredient:
            if re.search("(?i)chicken|turkey|duck|goose|poultry", k['name']):
                primary_ingredient = k['name']
                internal_temp = 165
                baking_temp = 400
                baking_time = 35
            if re.search("(?i)steak|veal|lamb|beef", k['name']):
                primary_ingredient = k['name']
                baking_temp = 325
                internal_temp = 145
                baking_time = 90
            if re.search("(?i)ham|pork", k['name']):
                primary_ingredient = k['name']
                internal_temp = 145
                baking_temp = 325
                baking_time = 20
            if re.search("(?i)salmon|tuna|tilapia|trout|halibut|mackerel|sablefish|catfish|yellowtail|bass|cod|snapper|flounder|perch", k['name']):
                primary_ingredient = k['name']
                internal_temp = 145
                baking_temp = 350
                baking_time = 20
                    
        print "\n\nthe current method is", primary_method
        while valid_input == False:
            choice =  input("\nSelect a new method\n\n1. saute\n\n2. broil\n\n3. boil\n\n4. poach\n\n5. freeze\n\n6. bake\n\n7. grilled\n\n8. fried\n\n9. roasted\n\n10. smoked\n\n")
            
            
            ##saute
            if choice == 1:
                if primary_method == ['saute']:
                    print "You have selected the same method. Please select a different method"
                else:
                    results["cooking tools"] = ['stove', 'sauce pan', 'wooden spoon', 'cooking thermometer']
                    results["primary cooking method"] = ['saute']
                    print "\n\n1.) Using the ingredients listed below prepare the food\n\n"
                    for k in ingredient:
                        name = k['name']
                        quantity = k['quantity']
                        measurement = k['measurement']
                        print quantity, measurement.encode('utf-8'), name.encode('utf-8')
                    print "\n\n2.) Select a pan and preheat over medium-high heat until hot"
                    print "\n\n3.) Carefully add the food to the pan and reduce the heat to medium. Stir the food."
                    if primary_ingredient != None:
                        print "\n\n4.) Cook the", primary_ingredient.encode('utf-8'), "to an internal temperature of", internal_temp, "degrees fahrenheit"
                    else:
                        print "\n\n4.) Cook the food fully."
                    valid_input = True
            
            
            ##broiled
            elif choice == 2:
                if primary_method == ['broil']:
                    print "You have selected the same method. Please select a different method"
                else:
                    results["primary cooking method"] = ['broil']
                    results["cooking tools"] = ['oven', 'baking pan', 'broiler', 'oven mit', 'cooking thermometer']
                    if primary_ingredient != None:
                        print "\n\n1.) prepare the", primary_ingredient.encode('utf-8'), "with the following ingredients\n\n"
                        for k in ingredient:
                            name = k['name']
                            quantity = k['quantity']
                            measurement = k['measurement']
                            print quantity, measurement.encode('utf-8'), name.encode('utf-8')
                        print "\n\n2.) Turn the oven on to the broil setting"
                        print "\n\n3.) Place the", primary_ingredient.encode('utf-8'), "on a pan and then place in the oven"
                        print "\n\n4.) Cook the", primary_ingredient.encode('utf-8'), "until it reaches an internal temperature of", internal_temp, "degrees fahrenheit"
                        print "\n\n5.) Carefully remove the pan with an oven mit."
                    else:
                        print "\n\n1.) prepare the food with the following ingredients\n\n"
                        for k in ingredient:
                            name = k['name']
                            quantity = k['quantity']
                            measurement = k['measurement']
                            print quantity, measurement.encode('utf-8'), name.encode('utf-8')               
                        print "\n\n2.) Turn the oven on to the broil setting"
                        print "\n\n3.) Place the food in the oven and cook fully."
                        print "\n\n4.) Carefully remove the pan with an oven mit."
                    valid_input = True
            
            ## boiled
            elif choice == 3:
                if primary_method == ['boil']:
                    print "You have selected the same method. Please select a different method"
                else: 
                    results["primary cooking method"] = ['boil']
                    results["cooking tools"] = ['stove', 'pot', 'slotted spoon', 'cooking thermometer']
                    if primary_ingredient != None:
                        print "\n\n1.) Prepare the", primary_ingredient.encode('utf-8'), "with the following ingredients\n\n"
                        for k in ingredient:
                            name = k['name']
                            quantity = k['quantity']
                            measurement = k['measurement']
                            print quantity, measurement.encode('utf-8'), name.encode('utf-8')
                        print "\n\n2.) Bring a pot with water to a boil"
                        print "\n\n3.) Place the", primary_ingredient.encode('utf-8'), "in the water and cook until it reaches an internal temperature of", internal_temp, "degrees fahrenheit"
                        print "\n\n4.) Carefully remove the food with a slotted spoon."
                    else: 
                        print "\n\n1.) Prepare the food with the following ingredients\n\n"
                        for k in ingredient:
                            name = k['name']
                            quantity = k['quantity']
                            measurement = k['measurement']
                            print quantity, measurement.encode('utf-8'), name.encode('utf-8')
                        print "\n\n2.) Bring a pot with water to a boil."
                        print "\n\n3.) Place the food in the pot and cook fully."
                        print "\n\n4.) Carefully remove the food from the por with a slotted spoon."
                    valid_input = True
            ## poached
            elif choice == 4:
                if primary_method == ['poach']:
                    print "You have selected the same method. Please select a different method"
                else:
                    results["primary cooking method"] = ['poach']
                    results["cooking tools"] = ['saucepan', 'stove top', 'saucepan cover', 'cooking thermometer']
                    print "\n\n1.) Fill a saucepan with water and place over medium-high heat. Bring to boil."
                    print "\n\n 2.) Add the ingredients listed below to the pan\n\n"
                    for k in ingredient:
                        name = k['name']
                        quantity = k['quantity']
                        measurement = k['measurement']
                        print quantity, measurement.encode('utf-8'), name.encode('utf-8')
                    if primary_ingredient != None:
                        print "\n\n3.) Simmer the sauce pan until the", primary_ingredient.encode('utf-8'), "reaches an internal temperature of", internal_temp, "degrees fahrenheit."
                    else:
                        print "\n\n3.) Simmer the sauce pan until the food is fully cooked."
                    valid_input = True
                    
            ##freeze
            elif choice == 5:
                if primary_method == ['freeze']:
                    print "You have selected the same method. Please select a different method"
                if primary_ingredient != None:
                    print "You can't cook freeze food. You should really select a different method."
            
            ## bake
            elif choice == 6:   
                if primary_method == ['bake']:
                    print "You have selected the same method. Please select a different method"
                else:
                    results["primary cooking method"] = ['bake']
                    results["cooking tools"] = ['oven', 'baking pan', 'oven mit', 'cooking thermometer']
                    if primary_ingredient != None:
                        print "\n\n1.) preheat the oven to", baking_temp
                        print "\n\n2.) prepare the", primary_ingredient.encode('utf-8'), "with the ingredients listed below\n\n"
                        for k in ingredient:
                            name = k['name']
                            quantity = k['quantity']
                            measurement = k['measurement']
                            print quantity, measurement.encode('utf-8'), name.encode('utf-8')   
                        print "\n\n3.) Place the", primary_ingredient.encode('utf-8'), "in the oven and cook for", baking_time, "minutes or until the", primary_ingredient.encode('utf-8'), "reaches an internal temperature of", internal_temp, "degrees fahrenheit."
                    else:
                        print "\n\n1.) preheat the oven to 350 degrees fahrenheit."
                        print "\n\n2.) prepare the food with the ingredients listed below\n\n"
                        for k in ingredient:
                            name = k['name']
                            quantity = k['quantity']
                            measurement = k['measurement']
                            print quantity, measurement.encode('utf-8'), name.encode('utf-8')   
                        print "\n\n3.) place the food in the oven and cook fully."
                    valid_input = True
            
            
            ## grill
            elif choice == 7:
                if primary_method == ['grill']:
                    print "You have selected the same method. Please select a different method"
                else:
                    results["primary cooking method"] = ['grill']
                    results["cooking tools"] = ['grill', 'tongs', 'cooking thermometer']
                    print "\n\n1.) turn on grill."
                    if primary_ingredient != None:
                        print "\n\n2.) prepare the", primary_ingredient.encode('utf-8'), "with the following ingredients"
                        for k in ingredient:
                            name = k['name']
                            quantity = k['quantity']
                            measurement = k['measurement']
                            print quantity, measurement.encode('utf-8'), name.encode('utf-8')
                        print "\n\n3.) place the", primary_ingredient.encode('utf-8'), "on the grill."
                        print "\n\n4.) Cook fully turning the", primary_ingredient.encode('utf-8'), "until it reaches an internal temperature of", internal_temp, "degrees fahrenheit."
                    else:
                        print "\n\n2.) Prepare the food with the following ingredients"
                        for k in ingredient:
                            name = k['name']
                            quantity = k['quantity']
                            measurement = k['measurement']
                            print quantity, measurement.encode('utf-8'), name.encode('utf-8')
                        print "\n\n3.) Place the food on the grill."
                        print "\n\n4.) Cook fully turning the food every couple minutes."
                    valid_input = True
            
            ##fried
            elif choice == 8:
                if primary_method == ['fried']:
                    print "You have selected the same method. Please select a different method"
                else:
                    results["primary cooking method"] = ['fried']   
                    results["cooking tools"] = ['stove', 'sauce pan', 'slotted spoon', 'cooking thermometer']
                    print "\n\n1.) Fill a heavy bottom pot, deep sauce pan, or wok with an oil of your choice."
                    print "\n\n2.) Bring the oil to a temperature of between 325 - 375 degrees fahrenheit. "
                    if primary_ingredient != None:
                        print "\n\n3.) Prepare the", primary_ingredient.encode('utf-8'), "with the ingredients listed below."
                        for k in ingredient:
                            name = k['name']
                            quantity = k['quantity']
                            measurement = k['measurement']
                            print quantity, measurement.encode('utf-8'), name.encode('utf-8')   
                        print "\n\n4.) Carefully add the", primary_ingredient.encode('utf-8'), "to the oil making sure to maintain the temperature of the oil."
                        print "\n\n5.) Continue to fry the", primary_ingredient.encode('utf-8'), "until it reaches an internal temperature of", internal_temp, "degrees fahrenheit."
                        print "\n\n6.) Carefully remove the", primary_ingredient.encode('utf-8'), "from the oil with a slotted spoon."
                    else:
                        print "\n\n3.) Prepare the food with the ingredients listed below."
                        for k in ingredient:
                            name = k['name']
                            quantity = k['quantity']
                            measurement = k['measurement']
                            print quantity, measurement.encode('utf-8'), name.encode('utf-8')   
                        print "\n\n4.) Carefully add the food to the oil making sure to maintain the temperature of the oil."
                        print "\n\n5.) Continue to fry the food until it is cooked fully."
                        print "\n\n6.) Carefully remove the food from the oil with a slotted spoon."
                    valid_input = True
            
            ## roasted
            elif choice == 9:
                if primary_method == ['roasted']:
                    print "You have selected the same method. Please select a different method"
                else:
                    results["primary cooking method"] = ['roasted']
                    results["cooking tools"] = ['oven', 'baking pan', 'oven mit', 'cooking thermometer']
                    if primary_ingredient != None:
                        print "\n\n1.) preheat the oven to", baking_temp
                        print "\n\n2.) prepare the", primary_ingredient.encode('utf-8'), "with the ingredients listed below\n\n"
                        for k in ingredient:
                            name = k['name']
                            quantity = k['quantity']
                            measurement = k['measurement']
                            print quantity, measurement.encode('utf-8'), name.encode('utf-8')   
                        print "\n\n3.) Place the", primary_ingredient.encode('utf-8'), "in the oven and cook for", baking_time, "minutes or until the", primary_ingredient.encode('utf-8'), "reaches an internal temperature of", internal_temp, "degrees fahrenheit."
                    else:
                        print "\n\n1.) preheat the oven to 350 degrees fahrenheit."
                        print "\n\n2.) prepare the food with the ingredients listed below\n\n"
                        for k in ingredient:
                            name = k['name']
                            quantity = k['quantity']
                            measurement = k['measurement']
                            print quantity, measurement.encode('utf-8'), name.encode('utf-8')
                        print "\n\n3.) place the food in the oven and cook fully."
                    valid_input = True
            
            
            ##smoked NEED TO IMPLEMENT
            elif choice == 10:
                if primary_method == ['smoked']:
                    print "You have selected the same method. Please select a different method"
                else:
                    results["primary cooking method"] = ['smoked']
                    results["cooking tools"] = ['smoker', 'wood chunks', 'wood pieces', 'sauce pan', 'cooking thermometer']
                    print "\n\n1.) Prepare the smoker."
                    print "\n\n2.) Select the type of wood you would like to use. (Different woods have different flavors)"
                    print "\n\n3.) If using a wet smoking method place a pan of water inside the smoker."
                    print "\n\n4.) Soak smaller chips in water, but leave the larger pieces dry."
                    print "\n\n5.) Prepare the smoker by using the wood as fuel. Try to keep the temperature around 200 degrees fahrenheit."
                    if primary_ingredient != None:
                        print "\n\n6.) Prepare the", primary_ingredient.encode('utf-8'), "with the following ingredients"
                        for k in ingredient:
                            name = k['name']
                            quantity = k['quantity']
                            measurement = k['measurement']
                            print quantity, measurement.encode('utf-8'), name.encode('utf-8')
                        print "\n\n7.) Allow yourself 6-8 hours of smoking time and place the", primary_ingredient.encode('utf-8'), "into the smoker."
                        print "\n\n8.) While maintaing a temperature of 200 degrees fahrenheit monitor the temperature of the", primary_ingredient.encode('utf-8'), "until it cooks fully and reaches and internal temperature of", internal_temp, "degrees fahrenheit."
                        print "\n\n9.) Remove the", primary_ingredient.encode('utf-8'), "and enjoy."
                    else:
                        print "\n\n6.) Prepare the food with the following ingredients"
                        for k in ingredient:
                            name = k['name']
                            quantity = k['quantity']
                            measurement = k['measurement']
                            print quantity, measurement.encode('utf-8'), name.encode('utf-8')
                        print "\n\n7.) Allow yourself 6-8 hours of smoking time and place the food into the smoker."
                        print "\n\n8.) While maintaing a temperature of 200 degrees fahrenheit monitor the temperature of the food until it cooks fully."
                        print "\n\n9.) Remove the food and enjoy."
                    valid_input = True
            else:
                print "Please select a number in the range presented."
        
    #    print results   

def to_gluten_free(recipe):
    ingredients = recipe["ingredients"]
    i = 0
    for ingredient in ingredients:
        if ingredient["name"] in GLUTEN_FREE:
            recipe["ingredients"][i]["name"] = GLUTEN_FREE[ingredient["name"]]
        i = i + 1
    for ingredient in GLUTEN_FREE:
        for step in recipe["steps"]:
            j = 0
            if ingredient in step:
                recipe["steps"][j] = recipe["steps"][j].replace(ingredient,GLUTEN_FREE[ingredient])
            j = j + 1
    print recipe
    return recipe

def to_lactose_free(recipe):
    ingredients = recipe["ingredients"]
    i = 0
    for ingredient in ingredients:
        if ingredient["name"] in LACTOSE_FREE:
            recipe["ingredients"][i]["name"] = LACTOSE_FREE[ingredient["name"]]
        i = i + 1

    for ingredient in LACTOSE_FREE:
        j = 0
        for step in recipe["steps"]:
            if ingredient in step:
                recipe["steps"][j] = recipe["steps"][j].replace(ingredient,LACTOSE_FREE[ingredient])
            j = j + 1
    print recipe
    return recipe

def to_gluten(recipe):
    ingredients = recipe["ingredients"]
    i = 0
    for ingredient in ingredients:
        if ingredient["name"] in GLUTEN:
            recipe["ingredients"][i]["name"] = GLUTEN[ingredient["name"]]
        i = i + 1
    for ingredient in GLUTEN:
        j = 0
        for step in recipe["steps"]:
            if ingredient in step:
                recipe["steps"][j] = recipe["steps"][j].replace(ingredient,GLUTEN[ingredient])
            j = j + 1
    print recipe
    return recipe

def to_lactose(recipe):
    ingredients = recipe["ingredients"]
    i = 0
    for ingredient in ingredients:
        if ingredient["name"] in LACTOSE_FREE:
            recipe["ingredients"][i]["name"] = LACTOSE_FREE[ingredient["name"]]
        i = i + 1
    for ingredient in LACTOSE:
        j = 0
        for step in recipe["steps"]:
            if ingredient in step:
                recipe["steps"][j] = recipe["steps"][j].replace(ingredient,LACTOSE[ingredient])
            j = j + 1
    print recipe
    return recipe


def flush():
    os.system('clear')
    os.system('cls')
    


def display(recipe):
    num = 0
    flush()
    print "Ingredients: "
    print "-------------"
    for ingredient in recipe['ingredients']:
        if ingredient['name'] != 'none':
            print ingredient['quantity'], ingredient['measurement'], ingredient['descriptor'], ingredient['name']
    print "Steps: "
    print "-------------"
    for step in recipe['steps']:
        num+=1
        stepnum = str(num) + "."
        print stepnum, step

def start_interface():
    def pr_help():
        flush()
        print "List of commands:"
        print "lowsodium [mode] \t Transform to/from low-sodium"
        print "lowfat [mode] \t Transform to/from lowfat"
        print "glutenf [mode] \t Transform to/from gluten-free"
        print "lactosef [mode] \t Transform to/from lactose-free"
        print "method  \t Enter to the recipe cooking method"
        print "dispay \t Displays the current recipe"
        print "load [URL] \t Changes recipe to the selected URL"
        print "help \t Display all available of commands"
        print "exit \t Quits the program"
    print "Welcome to ARP (AllRecipes Parser)!"
    print "=========================================="
    print "Begin by entering in a URL"
    print "========================================="
    s_input = raw_input()
   # s_input = sys.stdin.readline()
    print "Parsing recipe"
    recipe = autograder(s_input);
    flush()
    display(recipe)
    print "========================================="
    print "Done! Please enter a transformation with"
    print "[transformation] [mode] with to/for values for [mode]"
    print "Example: lowsodium to /t transforms recipe to a low sodium version"
    print "Enter help for a full list of transformations and commands"
    
    while True:
        s_input = raw_input()
        tokens = s_input.split()
        if len(tokens) > 2:
            print "Unknown command. Type help for commands list or exit to quit"
        elif len(tokens) < 2:
            if tokens[0] == "help":
                pr_help()
            elif tokens[0] == "method":
                change_method(recipe);
            elif tokens[0] == "display":
                display(recipe);
            elif tokens[0] == "exit":
                return
            else:
                print "Unknown command. Type help for commands list or exit to quit"
        else:
            if tokens[0] == "lowsodium":
                if tokens[1] == "to":
                    flush()
                    print "Transforming to low-sodium..."
                    t_low_sodium(recipe, True)
                    flush()
                    display(recipe)
                elif tokens[1] == "from":
                    print "Transforming from low-sodium..."
                    t_low_sodium(recipe, False)
                    flush()
                    display(recipe)
                else:
                    print "Please select to/for for [mode]"
            elif tokens[0] == "lowfat":
                if tokens[1] == "to":
                    print "Transforming to lowfat..."
                    t_low_fat(recipe, True)
                    flush()
                    display(recipe)
                elif tokens[1] == "from":
                    print "Transforming from lowfat..."
                    t_low_fat(recipe, False)
                    flush()
                    display(recipe)
                else:
                    print "Please select to/for for [mode]"
            elif tokens[0] == "lactosef":
                if tokens[1] == "to":
                    print "Transforming to lactose-free..."
                    to_lactose_free(recipe)
                    flush()
                    display(recipe)
                elif tokens[1] == "from":
                    print "Transforming from lactose-free..."
                    to_lactose(recipe)
                    flush()
                    display(recipe)
                else:
                    print "Please select to/for for [mode]"
            elif tokens[0] == "glutenf":
                if tokens[1] == "to":
                    print "Transforming to gluten-free..."
                    to_gluten(recipe)
                    flush()
                    display(recipe)
                elif tokens[1] == "from":
                    print "Transforming from gluten-free..."
                    to_gluten_free(recipe)
                    flush()
                    display(recipe)
                else:
                    print "Please select to/for for [mode]"
            elif tokens[0] == "load":
                print "Loading recipe at URL"
                recipe = autograder(tokens[1])
                flush()
                display(recipe)
            else:
                print "Unknown command. Type help for commands list or exit to quit"

#tR= autograder("http://allrecipes.com/recipe/236391/cilantro-garlic-lime-sauteed-shrimp")
def main():
    start_interface();
    return
    
if __name__ == "__main__":
    main()
