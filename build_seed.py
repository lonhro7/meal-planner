#!/usr/bin/env python3
"""Author the curated recipe library and emit frontend seed.js.
Energy authored in kcal for sanity, converted to kJ on output. Prices AUD.
Meat types: beef, chicken, lamb, pork, sausage, smallgoods, fish, salmon
(veal / kangaroo / duck removed)."""
import json

def ing(name, qty, unit, category="pantry", price=0.0, step=0, optional=False,
        is_meat=False, meat_type="", meat_cut=""):
    return {"name": name, "quantity": qty, "unit": unit, "category": category,
            "is_meat": is_meat, "meat_type": meat_type, "meat_cut": meat_cut,
            "optional": optional, "price_per_unit": price, "step_index": step}

def meat(name, qty, unit, mtype, cut, price, step=0):
    return ing(name, qty, unit, "meat", price, step, is_meat=True, meat_type=mtype, meat_cut=cut)

R = []
def add(title, kcal, protein, carbs, fat, prep, cook, leftover, wl, dairy, tags,
        steps, ings, servings=4, kid=True, source="House recipe"):
    cat = "fresh" if leftover <= 1 else ("ok" if leftover == 2 else "excellent")
    R.append({"title": title, "source_name": source, "servings": servings,
        "prep_min": prep, "cook_min": cook, "leftover": cat, "weight_loss_rating": wl,
        "kid_friendly": kid, "kj": round(kcal * 4.184), "protein_g": protein,
        "carbs_g": carbs, "fat_g": fat, "dairy": dairy, "tags": tags,
        "method_steps": steps, "ingredients": ings})

# shorthand ingredient builders for very common items
def onion(n=1, s=0): return ing("Onion",n,"whole","veg",0.45,s)
def garlic(n=2,s=0): return ing("Garlic",n,"clove","veg",0.08,s)
def oil(n=1,s=0): return ing("Olive oil",n,"tbsp","pantry",0.12,s)
def voil(n=1,s=0): return ing("Vegetable oil",n,"tbsp","pantry",0.10,s)
def rice(g=300,s=0): return ing("Basmati rice",g,"g","pantry",0.003,s)
def passata(ml=500,s=0): return ing("Tomato passata",ml,"ml","pantry",0.004,s)
def dicedtom(s=0): return ing("Tinned diced tomatoes",1,"can","pantry",1.20,s)
def coconut(s=0): return ing("Coconut milk",1,"can","pantry",1.80,s)
def carrot(n=1,s=0): return ing("Carrot",n,"whole","veg",0.30,s)
def broccoli(s=0): return ing("Broccoli",1,"whole","veg",2.50,s)
def capsicum(s=0): return ing("Red capsicum",1,"whole","veg",1.20,s)
def cheese(g=100,s=0): return ing("Cheese, grated",g,"g","dairy",0.014,s)

# =================================================================== BEEF
add("Spaghetti Bolognese",620,32,78,20,10,35,3,3,"replaceable",
    ["pasta","beef","one-pot","freezer-friendly","kid-favourite"],
    ["Cook the diced onion, carrot and garlic in the oil for 5 minutes.",
     "Add the beef mince and brown for 8 minutes.",
     "Stir in the passata, tinned tomatoes and oregano; simmer 20 minutes.",
     "Cook the spaghetti, drain, and serve topped with the sauce and parmesan."],
    [meat("Beef mince",500,"g","beef","mince",0.016,1),onion(),carrot(1,0),garlic(2,0),
     passata(500,2),dicedtom(2),ing("Dried oregano",1,"tsp","spice",0.02,2),
     ing("Spaghetti",400,"g","pantry",0.004,3),ing("Parmesan, grated",40,"g","dairy",0.03,3,optional=True),oil(1,0)])
add("Beef Tacos",560,30,48,26,10,15,1,3,"replaceable",["mexican","beef","quick","kid-favourite"],
    ["Cook the onion in oil 3 minutes, add the mince and brown 6 minutes.",
     "Stir in the taco spice and 100 ml water; simmer 5 minutes.",
     "Warm the tortillas and fill with beef, cheese, lettuce and tomato."],
    [meat("Beef mince",500,"g","beef","mince",0.016,0),onion(),ing("Taco spice mix",2,"tbsp","spice",0.20,1),
     ing("Tortillas",8,"whole","bakery",0.25,2),cheese(100,2),ing("Lettuce",0.5,"whole","veg",2.00,2),
     ing("Tomato",2,"whole","veg",0.60,2)])
add("Beef Chilli con Carne",610,34,72,18,10,40,3,3,"free",["mexican","beef","one-pot","freezer-friendly","budget"],
    ["Cook the onion and garlic 4 minutes, add the mince and brown.",
     "Add chilli spice, tinned tomatoes, kidney beans and stock; simmer 25 minutes.",
     "Serve over rice."],
    [meat("Beef mince",500,"g","beef","mince",0.016,0),onion(),garlic(2,0),ing("Mild chilli spice",1,"tbsp","spice",0.15,1),
     dicedtom(1),ing("Tinned kidney beans",1,"can","pantry",1.10,1),ing("Beef stock",200,"ml","pantry",0.002,1),rice(300,2)])
add("Slow-Cooked Beef Ragu",650,40,66,22,15,180,3,3,"replaceable",["pasta","beef","slow-cook","long-cook","freezer-friendly"],
    ["Brown the beef in oil, remove. Cook onion, carrot, celery and garlic 6 minutes.",
     "Return beef with passata, stock and bay; simmer gently 2.5–3 hours until it shreds.",
     "Shred through the sauce and toss with pappardelle."],
    [meat("Beef chuck",700,"g","beef","chuck",0.015,0),onion(1,1),carrot(1,1),ing("Celery",1,"whole","veg",0.40,1),
     garlic(3,1),passata(700,2),ing("Beef stock",300,"ml","pantry",0.002,2),ing("Bay leaf",1,"whole","spice",0.05,2),
     ing("Pappardelle",400,"g","pantry",0.005,2),oil(1,0)])
add("Beef & Broccoli Stir Fry",520,33,54,16,10,15,1,4,"free",["stir-fry","beef","quick","dairy-free"],
    ["Cook the rice. Stir-fry the beef strips in hot oil 3 minutes, remove.",
     "Stir-fry broccoli and carrot 4 minutes.",
     "Return beef, add soy and oyster sauce, toss and serve over rice."],
    [meat("Beef strips",400,"g","beef","stir-fry strips",0.022,1),broccoli(2),carrot(1,2),
     ing("Soy sauce",3,"tbsp","sauce",0.06,2),ing("Oyster sauce",2,"tbsp","sauce",0.10,2),rice(300,0),voil(1,1)])
add("Beef & Vegetable Stir Fry with Noodles",560,34,58,18,15,15,1,4,"free",["stir-fry","beef","quick","noodles","dairy-free"],
    ["Cook the noodles. Stir-fry the beef strips in hot oil 3 minutes, remove.",
     "Stir-fry capsicum, broccoli and carrot 4 minutes.",
     "Return beef, add noodles, oyster and soy sauce, toss 2 minutes."],
    [meat("Beef strips",400,"g","beef","stir-fry strips",0.022,1),ing("Hokkien noodles",400,"g","pantry",0.006,0),
     capsicum(2),broccoli(2),carrot(1,2),ing("Oyster sauce",2,"tbsp","sauce",0.10,2),ing("Soy sauce",1,"tbsp","sauce",0.06,2),voil(1,1)])
add("Beef Meatballs in Tomato Sauce",590,33,52,26,20,30,3,3,"replaceable",["beef","kid-favourite","freezer-friendly"],
    ["Mix mince, breadcrumbs and egg; roll into balls and brown.",
     "Cook onion and garlic 4 minutes, add passata and oregano.",
     "Return meatballs, simmer 15 minutes; serve with pasta."],
    [meat("Beef mince",500,"g","beef","mince",0.016,0),ing("Breadcrumbs",60,"g","pantry",0.005,0),
     ing("Egg",1,"whole","dairy",0.40,0),onion(1,1),garlic(3,0),passata(500,1),
     ing("Dried oregano",1,"tsp","spice",0.02,1),ing("Spaghetti",350,"g","pantry",0.004,2)])
add("Beef Nachos",680,30,58,34,10,20,1,2,"required",["mexican","beef","kid-favourite"],
    ["Brown the mince with onion, add taco spice, tomatoes and beans; simmer 8 minutes.",
     "Spread corn chips on a tray, top with beef and cheese, bake 8 minutes."],
    [meat("Beef mince",500,"g","beef","mince",0.016,0),onion(),ing("Taco spice mix",2,"tbsp","spice",0.20,0),
     dicedtom(0),ing("Tinned kidney beans",1,"can","pantry",1.10,0),ing("Corn chips",250,"g","pantry",0.012,1),cheese(150,1)])
add("Cottage Pie",640,31,56,32,20,45,3,3,"replaceable",["oven","beef","comfort","freezer-friendly","kid-favourite"],
    ["Boil and mash the potatoes with milk and butter.",
     "Brown the mince with onion and carrot, add peas, stock and tomato paste; simmer 10 minutes.",
     "Top with mash and bake at 200°C for 25 minutes."],
    [meat("Beef mince",500,"g","beef","mince",0.016,1),ing("Potato",6,"whole","veg",0.40,0),
     ing("Milk",60,"ml","dairy",0.0015,0),ing("Butter",30,"g","dairy",0.010,0),onion(1,1),carrot(1,1),
     ing("Frozen peas",150,"g","veg",0.004,1),ing("Beef stock",200,"ml","pantry",0.002,1),ing("Tomato paste",2,"tbsp","pantry",0.10,1)])
add("Beef Stroganoff",620,34,48,30,10,25,2,3,"required",["beef","pasta","comfort"],
    ["Brown the beef strips in butter, remove. Cook onion and mushrooms 5 minutes.",
     "Add stock and mustard, simmer 5 minutes, stir in sour cream.",
     "Return beef and serve over pasta or rice."],
    [meat("Beef strips",500,"g","beef","stir-fry strips",0.022,0),ing("Button mushrooms",200,"g","veg",0.012,1),
     onion(1,1),ing("Beef stock",250,"ml","pantry",0.002,2),ing("Dijon mustard",1,"tbsp","sauce",0.10,2),
     ing("Sour cream",150,"g","dairy",0.010,2),ing("Butter",20,"g","dairy",0.010,0),ing("Fettuccine",350,"g","pantry",0.005,3)])
add("Beef Rissoles with Gravy",560,30,34,32,15,20,2,3,"replaceable",["beef","kid-favourite","budget"],
    ["Mix mince, grated onion, breadcrumbs and egg; shape into patties.",
     "Fry 4 minutes each side. Make gravy from the pan with stock.",
     "Serve with mash and peas."],
    [meat("Beef mince",600,"g","beef","mince",0.016,0),onion(1,0),ing("Breadcrumbs",60,"g","pantry",0.005,0),
     ing("Egg",1,"whole","dairy",0.40,0),ing("Beef stock",250,"ml","pantry",0.002,1),
     ing("Potato",5,"whole","veg",0.40,2),ing("Frozen peas",150,"g","veg",0.004,2)])
add("Massaman Beef Curry",640,32,58,28,15,120,3,3,"free",["curry","beef","slow-cook","long-cook","dairy-free","freezer-friendly"],
    ["Brown the beef, add massaman paste and cook 1 minute.",
     "Add coconut milk, potato and stock; simmer 1.5–2 hours until tender.",
     "Serve over rice with peanuts."],
    [meat("Beef chuck",700,"g","beef","chuck",0.015,0),ing("Massaman curry paste",3,"tbsp","sauce",0.30,0),
     coconut(1),ing("Potato",3,"whole","veg",0.40,1),ing("Beef stock",200,"ml","pantry",0.002,1),
     rice(300,2),ing("Peanuts",40,"g","pantry",0.02,2,optional=True)])
add("Beef Burgers with Chips",720,36,58,38,15,20,1,2,"replaceable",["beef","kid-favourite"],
    ["Bake the oven chips. Shape the mince into patties and season.",
     "Fry the patties 4 minutes each side.",
     "Build burgers with buns, cheese, lettuce and tomato."],
    [meat("Beef mince",600,"g","beef","mince",0.016,1),ing("Burger buns",4,"whole","bakery",0.80,2),
     cheese(80,2),ing("Lettuce",0.5,"whole","veg",2.00,2),ing("Tomato",1,"whole","veg",0.60,2),
     ing("Oven chips",600,"g","veg",0.005,0)])
add("Mongolian Beef",560,32,52,22,10,15,1,3,"free",["stir-fry","beef","quick","dairy-free"],
    ["Toss beef strips in cornflour. Fry in hot oil until crisp, remove.",
     "Make sauce with soy, brown sugar, garlic and ginger; simmer 2 minutes.",
     "Return beef, toss, and serve over rice with spring onion."],
    [meat("Beef strips",500,"g","beef","stir-fry strips",0.022,0),ing("Cornflour",2,"tbsp","pantry",0.02,0),
     ing("Soy sauce",4,"tbsp","sauce",0.06,1),ing("Brown sugar",2,"tbsp","pantry",0.05,1),garlic(2,1),
     ing("Ginger",1,"tbsp","veg",0.10,1),rice(300,2),ing("Spring onion",2,"whole","veg",0.30,2)])
add("Corned Beef with White Sauce",540,34,30,30,15,150,3,3,"required",["beef","slow-cook","long-cook","comfort"],
    ["Simmer the corned silverside with bay and peppercorns 2.5 hours.",
     "Boil potatoes and carrots. Make a white sauce with butter, flour and milk.",
     "Slice the beef and serve with vegetables and sauce."],
    [meat("Corned silverside",1000,"g","beef","corned silverside",0.014,0),ing("Bay leaf",2,"whole","spice",0.05,0),
     ing("Potato",5,"whole","veg",0.40,1),carrot(3,1),ing("Butter",40,"g","dairy",0.010,2),
     ing("Plain flour",40,"g","pantry",0.002,2),ing("Milk",500,"ml","dairy",0.0015,2)])
add("Beef Fried Rice",540,26,70,16,15,15,2,3,"free",["stir-fry","beef","rice","quick","uses-leftovers","dairy-free"],
    ["Scramble the eggs in oil, set aside. Brown the diced beef.",
     "Add peas, corn and carrot, stir-fry 3 minutes.",
     "Add cold rice and soy, toss, fold egg back through."],
    [meat("Beef mince",400,"g","beef","mince",0.016,0),ing("Egg",2,"whole","dairy",0.40,0),
     ing("Frozen peas and corn",250,"g","veg",0.005,1),carrot(1,1),rice(300,2),ing("Soy sauce",2,"tbsp","sauce",0.06,2),voil(1,0)])
add("Steak with Roast Vegetables",560,40,30,30,10,30,1,4,"free",["beef","low-carb","dairy-free"],
    ["Roast the pumpkin, potato and beans at 200°C for 25 minutes.",
     "Pan-sear the steaks 3 minutes each side, rest 5 minutes.",
     "Slice and serve with the vegetables."],
    [meat("Beef porterhouse steaks",600,"g","beef","porterhouse steak",0.030,1),ing("Pumpkin",400,"g","veg",0.004,0),
     ing("Potato",3,"whole","veg",0.40,0),ing("Green beans",200,"g","veg",0.012,0),oil(2,0)])
add("Beef Enchiladas",650,33,58,30,20,30,2,2,"required",["mexican","beef","oven","freezer-friendly"],
    ["Brown mince with onion and taco spice, add half the tomatoes.",
     "Roll the beef in tortillas, place in a dish, top with the rest of the tomatoes and cheese.",
     "Bake at 200°C for 20 minutes."],
    [meat("Beef mince",500,"g","beef","mince",0.016,0),onion(),ing("Taco spice mix",2,"tbsp","spice",0.20,0),
     dicedtom(1),ing("Tortillas",8,"whole","bakery",0.25,1),cheese(150,1)])

# =================================================================== CHICKEN
add("Butter Chicken",710,38,72,28,15,25,3,2,"replaceable",["curry","chicken","rice","kid-favourite"],
    ["Brown the chicken in butter. Add the curry paste and cook 1 minute.",
     "Add passata and coconut milk; simmer 15 minutes.",
     "Serve over rice with coriander."],
    [meat("Chicken thigh fillet",600,"g","chicken","thigh fillet",0.013,0),ing("Butter",40,"g","dairy",0.010,0),
     ing("Butter chicken paste",2,"tbsp","sauce",0.30,1),passata(300,2),coconut(2),rice(300,2),
     ing("Fresh coriander",1,"bunch","veg",2.00,2,optional=True)])
add("Chicken & Vegetable Fried Rice",540,30,68,16,15,15,2,3,"free",["stir-fry","chicken","rice","quick","uses-leftovers","dairy-free","kid-favourite"],
    ["Scramble the eggs in oil, set aside. Cook the diced chicken 5 minutes.",
     "Add peas, corn and carrot 3 minutes.",
     "Add cold rice and soy, toss, fold egg through."],
    [meat("Chicken breast",400,"g","chicken","breast",0.012,1),ing("Egg",2,"whole","dairy",0.40,0),
     ing("Frozen peas and corn",250,"g","veg",0.005,2),carrot(1,2),rice(300,0),ing("Soy sauce",2,"tbsp","sauce",0.06,3),voil(1,0)])
add("Honey Soy Chicken Drumsticks",600,34,64,20,10,35,2,3,"free",["chicken","oven","budget","dairy-free","kid-favourite"],
    ["Mix honey, soy and garlic; toss with drumsticks.",
     "Bake at 200°C for 35 minutes, basting once.",
     "Serve with rice and steamed broccoli."],
    [meat("Chicken drumsticks",8,"whole","chicken","drumstick",0.90,0),ing("Honey",2,"tbsp","pantry",0.20,0),
     ing("Soy sauce",3,"tbsp","sauce",0.06,0),garlic(2,0),rice(300,2),broccoli(2)])
add("Chicken Schnitzel with Chips & Salad",720,40,62,32,20,25,1,2,"free",["chicken","oven","kid-favourite"],
    ["Bake the oven chips. Crumb the chicken in flour, egg and breadcrumbs.",
     "Shallow-fry 3 minutes each side until golden.",
     "Serve with chips and salad."],
    [meat("Chicken breast",600,"g","chicken","breast",0.012,1),ing("Plain flour",60,"g","pantry",0.002,1),
     ing("Egg",2,"whole","dairy",0.40,1),ing("Breadcrumbs",150,"g","pantry",0.005,1),
     ing("Oven chips",750,"g","veg",0.005,0),ing("Mixed salad leaves",150,"g","veg",0.02,2)])
add("Chicken Parmigiana",690,44,48,32,20,30,2,2,"required",["chicken","oven","kid-favourite"],
    ["Crumb and shallow-fry the chicken, place in a dish.",
     "Top with passata, ham and cheese; bake at 200°C for 20 minutes.",
     "Serve with steamed vegetables."],
    [meat("Chicken breast",600,"g","chicken","breast",0.012,0),meat("Sliced ham",100,"g","smallgoods","sliced ham",0.024,1),
     ing("Plain flour",50,"g","pantry",0.002,0),ing("Egg",2,"whole","dairy",0.40,0),ing("Breadcrumbs",150,"g","pantry",0.005,0),
     passata(200,1),cheese(120,1),ing("Green beans",250,"g","veg",0.012,2)])
add("Thai Green Chicken Curry",620,34,58,26,15,20,3,3,"free",["curry","chicken","rice","dairy-free","freezer-friendly"],
    ["Fry the curry paste in oil, add chicken and brown.",
     "Add coconut milk and fish sauce, simmer 10 minutes.",
     "Add capsicum and beans, simmer 5 minutes; serve over rice."],
    [meat("Chicken thigh fillet",600,"g","chicken","thigh fillet",0.013,0),ing("Green curry paste",2,"tbsp","sauce",0.30,0),
     coconut(1),ing("Fish sauce",1,"tbsp","sauce",0.08,1),capsicum(2),ing("Green beans",150,"g","veg",0.012,2),rice(300,0),voil(1,0)])
add("Chicken Fajitas",590,36,56,22,15,15,1,3,"replaceable",["mexican","chicken","quick","kid-favourite"],
    ["Toss the sliced chicken with fajita spice; stir-fry 5 minutes, remove.",
     "Stir-fry capsicum and onion 4 minutes, return chicken.",
     "Serve in warm tortillas with lime."],
    [meat("Chicken breast",500,"g","chicken","breast",0.012,0),capsicum(0),onion(),ing("Fajita spice mix",2,"tbsp","spice",0.20,0),
     ing("Tortillas",8,"whole","bakery",0.25,2),ing("Lime",1,"whole","fruit",0.60,2),voil(1,1)])
add("Roast Chicken with Vegetables",640,42,40,34,15,80,3,3,"free",["chicken","roast","long-cook","dairy-free","freezer-friendly"],
    ["Rub the chicken with oil and seasoning. Scatter potato, carrot and pumpkin around it.",
     "Roast at 200°C for 75–80 minutes until juices run clear. Rest 10 minutes and carve."],
    [meat("Whole chicken",1600,"g","chicken","whole",0.006,0),ing("Potato",4,"whole","veg",0.40,0),
     carrot(2,0),ing("Pumpkin",400,"g","veg",0.004,0),oil(2,0)])
add("Chicken & Vegetable Soup",360,28,34,10,15,30,3,5,"free",["soup","chicken","light","weight-loss","dairy-free","freezer-friendly"],
    ["Cook onion, carrot and celery in oil 5 minutes; add chicken and brown.",
     "Add stock, simmer 20 minutes, add pasta and cook until tender."],
    [meat("Chicken thigh fillet",400,"g","chicken","thigh fillet",0.013,0),onion(1,0),carrot(2,0),ing("Celery",2,"whole","veg",0.40,0),
     ing("Chicken stock",1500,"ml","pantry",0.002,1),ing("Small soup pasta",150,"g","pantry",0.004,1),oil(1,0)])
add("Chicken & Chorizo Rice",640,34,66,24,15,30,3,3,"free",["one-pot","chicken","smallgoods","rice","dairy-free"],
    ["Brown the chorizo, then the chicken. Add onion, capsicum and garlic.",
     "Stir in rice, paprika, tomatoes and stock; cover and simmer 20 minutes."],
    [meat("Chicken thigh fillet",400,"g","chicken","thigh fillet",0.013,0),meat("Chorizo",150,"g","smallgoods","chorizo",0.022,0),
     onion(1,1),capsicum(1),garlic(2,1),rice(300,2),ing("Smoked paprika",1,"tsp","spice",0.03,2),dicedtom(2),ing("Chicken stock",400,"ml","pantry",0.002,2)])
add("Chicken Satay Skewers",560,38,28,32,20,15,1,3,"free",["chicken","bbq","dairy-free"],
    ["Thread chicken onto skewers and grill 10 minutes.",
     "Make satay sauce with peanut butter, coconut milk and soy.",
     "Serve with rice and cucumber."],
    [meat("Chicken thigh fillet",600,"g","chicken","thigh fillet",0.013,0),ing("Peanut butter",4,"tbsp","pantry",0.04,1),
     coconut(1),ing("Soy sauce",2,"tbsp","sauce",0.06,1),rice(300,2),ing("Cucumber",1,"whole","veg",1.00,2)])
add("Teriyaki Chicken with Rice",580,36,64,18,10,20,2,3,"free",["chicken","rice","quick","dairy-free","kid-favourite"],
    ["Cook the rice. Pan-fry the sliced chicken until golden.",
     "Add teriyaki sauce and glaze 2 minutes; serve over rice with broccoli."],
    [meat("Chicken thigh fillet",600,"g","chicken","thigh fillet",0.013,1),ing("Teriyaki sauce",4,"tbsp","sauce",0.10,1),
     rice(300,0),broccoli(1)])
add("Chicken Cacciatore",560,38,34,26,15,40,3,3,"free",["chicken","one-pot","dairy-free","freezer-friendly"],
    ["Brown the chicken thighs, remove. Cook onion, garlic and capsicum.",
     "Add tomatoes, olives and stock; return chicken and simmer 30 minutes.",
     "Serve with crusty bread or polenta."],
    [meat("Chicken thigh cutlets",8,"whole","chicken","thigh cutlet",1.00,0),onion(1,1),garlic(2,1),capsicum(1),
     dicedtom(2),ing("Kalamata olives",60,"g","pantry",0.02,2),ing("Chicken stock",200,"ml","pantry",0.002,2)])
add("Chicken Korma",640,36,54,30,15,30,3,2,"required",["curry","chicken","rice","freezer-friendly"],
    ["Brown the chicken, add korma paste and cook 1 minute.",
     "Add cream and stock; simmer 20 minutes.",
     "Serve over rice."],
    [meat("Chicken thigh fillet",600,"g","chicken","thigh fillet",0.013,0),ing("Korma paste",2,"tbsp","sauce",0.30,0),
     ing("Thickened cream",200,"ml","dairy",0.008,1),ing("Chicken stock",150,"ml","pantry",0.002,1),rice(300,2)])
add("Sweet & Sour Chicken",600,32,72,18,15,20,1,3,"free",["chicken","rice","dairy-free","kid-favourite"],
    ["Cook the rice. Toss the chicken in cornflour and fry until golden.",
     "Add capsicum and pineapple, then the sweet & sour sauce; toss 3 minutes."],
    [meat("Chicken breast",500,"g","chicken","breast",0.012,0),ing("Cornflour",2,"tbsp","pantry",0.02,0),
     capsicum(1),ing("Tinned pineapple",1,"can","pantry",1.50,1),ing("Sweet & sour sauce",150,"ml","sauce",0.01,1),rice(300,0)])
add("Chicken Burrito Bowls",620,38,66,22,15,20,2,3,"replaceable",["mexican","chicken","rice"],
    ["Cook the rice. Toss chicken with taco spice and pan-fry.",
     "Warm the black beans and corn.",
     "Build bowls with rice, chicken, beans, corn, cheese and salsa."],
    [meat("Chicken thigh fillet",500,"g","chicken","thigh fillet",0.013,0),ing("Taco spice mix",2,"tbsp","spice",0.20,0),
     rice(300,0),ing("Tinned black beans",1,"can","pantry",1.10,1),ing("Tinned corn",1,"can","pantry",1.20,1),cheese(80,2),ing("Salsa",150,"g","sauce",0.01,2)])
add("Lemon & Herb Roast Chicken Pieces",520,40,20,30,10,45,2,4,"free",["chicken","oven","low-carb","dairy-free"],
    ["Toss chicken pieces with lemon, garlic, oregano and oil.",
     "Roast at 200°C for 40 minutes with zucchini and capsicum."],
    [meat("Chicken thigh cutlets",8,"whole","chicken","thigh cutlet",1.00,0),ing("Lemon",1,"whole","fruit",0.70,0),
     garlic(3,0),ing("Dried oregano",1,"tsp","spice",0.02,0),ing("Zucchini",2,"whole","veg",0.80,1),capsicum(1),oil(2,0)])
add("Chicken Noodle Stir Fry",540,32,60,16,15,15,1,3,"free",["stir-fry","chicken","noodles","quick","dairy-free"],
    ["Cook the noodles. Stir-fry the chicken until golden, remove.",
     "Stir-fry the mixed vegetables 4 minutes.",
     "Return chicken, add noodles and hoisin, toss."],
    [meat("Chicken breast",400,"g","chicken","breast",0.012,1),ing("Hokkien noodles",400,"g","pantry",0.006,0),
     ing("Mixed stir-fry vegetables",400,"g","veg",0.008,2),ing("Hoisin sauce",2,"tbsp","sauce",0.12,2),voil(1,1)])
add("Chicken Tikka with Rice",600,38,58,22,20,25,2,3,"replaceable",["curry","chicken","rice"],
    ["Marinate chicken in yoghurt and tikka spice; grill or pan-fry.",
     "Make a quick tomato sauce, fold the chicken through; serve with rice."],
    [meat("Chicken thigh fillet",600,"g","chicken","thigh fillet",0.013,0),ing("Natural yoghurt",100,"g","dairy",0.008,0),
     ing("Tikka spice",2,"tbsp","spice",0.20,0),passata(300,1),rice(300,1)])
add("Chicken Pad Thai",590,32,66,20,20,15,1,3,"free",["chicken","noodles","dairy-free"],
    ["Soak the rice noodles. Stir-fry the chicken, push aside and scramble the egg.",
     "Add noodles and pad thai sauce, toss.",
     "Top with peanuts, bean sprouts and lime."],
    [meat("Chicken breast",400,"g","chicken","breast",0.012,0),ing("Rice noodles",300,"g","pantry",0.006,1),
     ing("Egg",2,"whole","dairy",0.40,0),ing("Pad thai sauce",100,"ml","sauce",0.02,1),
     ing("Peanuts",40,"g","pantry",0.02,2),ing("Bean sprouts",100,"g","veg",0.01,2),ing("Lime",1,"whole","fruit",0.60,2)])
add("Chicken & Leek Pie",680,32,52,38,20,45,3,2,"required",["chicken","oven","comfort","freezer-friendly"],
    ["Cook the diced chicken and leek in butter. Stir in flour, then stock and cream.",
     "Pour into a dish, top with puff pastry, bake at 200°C for 25 minutes."],
    [meat("Chicken thigh fillet",600,"g","chicken","thigh fillet",0.013,0),ing("Leek",1,"whole","veg",1.50,0),
     ing("Butter",30,"g","dairy",0.010,0),ing("Plain flour",30,"g","pantry",0.002,0),ing("Chicken stock",200,"ml","pantry",0.002,0),
     ing("Thickened cream",100,"ml","dairy",0.008,0),ing("Puff pastry",2,"whole","bakery",1.00,1)])
add("Tandoori Chicken with Rice",560,40,52,18,20,30,2,3,"replaceable",["chicken","oven","rice"],
    ["Marinate chicken in yoghurt and tandoori spice 15 minutes.",
     "Bake at 220°C for 25 minutes.",
     "Serve with rice and cucumber salad."],
    [meat("Chicken thigh cutlets",8,"whole","chicken","thigh cutlet",1.00,0),ing("Natural yoghurt",150,"g","dairy",0.008,0),
     ing("Tandoori spice",2,"tbsp","spice",0.20,0),rice(300,2),ing("Cucumber",1,"whole","veg",1.00,2)])
add("Chicken Laksa",620,34,58,26,15,25,2,3,"free",["soup","chicken","noodles","dairy-free"],
    ["Fry the laksa paste, add coconut milk and stock; simmer.",
     "Add the sliced chicken and cook through.",
     "Add noodles and bean sprouts; serve with lime."],
    [meat("Chicken thigh fillet",500,"g","chicken","thigh fillet",0.013,1),ing("Laksa paste",3,"tbsp","sauce",0.30,0),
     coconut(0),ing("Chicken stock",500,"ml","pantry",0.002,0),ing("Rice noodles",300,"g","pantry",0.006,2),
     ing("Bean sprouts",100,"g","veg",0.01,2),ing("Lime",1,"whole","fruit",0.60,2)])
add("Chicken Caesar Salad",480,36,22,28,15,15,1,4,"required",["chicken","salad","low-carb"],
    ["Grill the chicken and slice. Toast the bread for croutons.",
     "Toss cos lettuce with caesar dressing, top with chicken, croutons and parmesan."],
    [meat("Chicken breast",500,"g","chicken","breast",0.012,0),ing("Cos lettuce",1,"whole","veg",2.50,1),
     ing("Caesar dressing",100,"ml","sauce",0.02,1),ing("Bread",2,"slice","bakery",0.30,0),ing("Parmesan, grated",40,"g","dairy",0.03,1)])
add("Honey Mustard Chicken Traybake",560,38,40,26,15,40,2,3,"free",["chicken","tray-bake","one-pan","dairy-free"],
    ["Toss chicken and chopped vegetables with honey, mustard and oil.",
     "Roast at 200°C for 40 minutes, turning once."],
    [meat("Chicken thigh cutlets",8,"whole","chicken","thigh cutlet",1.00,0),ing("Honey",2,"tbsp","pantry",0.20,0),
     ing("Wholegrain mustard",2,"tbsp","sauce",0.10,0),ing("Potato",4,"whole","veg",0.40,0),carrot(2,0),oil(2,0)])

print("after part 1:", len(R))

# =================================================================== PORK
add("Sausage & Vegetable Tray Bake",580,24,52,30,10,40,2,3,"free",["tray-bake","sausage","easy","one-pan","dairy-free","kid-favourite"],
    ["Chop potatoes, capsicum, red onion and zucchini; spread on a tray with oil.",
     "Nestle the sausages among the vegetables and bake at 200°C for 40 minutes."],
    [meat("Thick pork sausages",8,"whole","sausage","pork sausage",0.55,1),ing("Potato",4,"whole","veg",0.40,0),
     capsicum(0),ing("Red onion",1,"whole","veg",0.55,0),ing("Zucchini",1,"whole","veg",0.80,0),oil(2,0)])
add("Sausages with Mash & Peas",620,26,54,32,10,25,2,2,"replaceable",["sausage","kid-favourite","comfort"],
    ["Mash the boiled potatoes with milk and butter.",
     "Pan-fry the sausages 12–15 minutes. Make gravy from the pan.",
     "Serve sausages over mash with peas and gravy."],
    [meat("Thick beef sausages",8,"whole","sausage","beef sausage",0.50,1),ing("Potato",6,"whole","veg",0.40,0),
     ing("Milk",60,"ml","dairy",0.0015,0),ing("Butter",30,"g","dairy",0.010,0),ing("Frozen peas",200,"g","veg",0.004,2),ing("Beef stock",200,"ml","pantry",0.002,1)])
add("Spaghetti Carbonara",660,30,72,28,10,20,1,2,"replaceable",["pasta","smallgoods","quick"],
    ["Cook the spaghetti. Fry the diced bacon until crisp.",
     "Whisk eggs with parmesan and pepper.",
     "Off the heat, toss pasta with bacon then the egg mix, loosening with pasta water."],
    [meat("Bacon",200,"g","smallgoods","bacon",0.020,1),ing("Spaghetti",400,"g","pantry",0.004,0),
     ing("Egg",3,"whole","dairy",0.40,2),ing("Parmesan, grated",60,"g","dairy",0.03,2),ing("Black pepper",1,"tsp","spice",0.02,2)])
add("Pork San Choy Bau",420,30,18,24,15,15,1,4,"free",["quick","pork","low-carb","dairy-free"],
    ["Stir-fry the pork mince 6 minutes. Add garlic, carrot and water chestnuts 3 minutes.",
     "Stir in hoisin and soy; spoon into lettuce cups."],
    [meat("Pork mince",500,"g","pork","mince",0.014,0),garlic(2,0),carrot(1,0),
     ing("Tinned water chestnuts",1,"can","pantry",1.50,0),ing("Hoisin sauce",2,"tbsp","sauce",0.12,1),
     ing("Soy sauce",1,"tbsp","sauce",0.06,1),ing("Iceberg lettuce",1,"whole","veg",2.50,1)])
add("Pork Chops with Apple & Greens",480,34,22,26,10,20,1,4,"free",["pork","low-carb","dairy-free"],
    ["Pan-fry the pork chops 4 minutes each side, rest.",
     "Cook the sliced apple 3 minutes. Steam the greens.",
     "Serve the chops with apple and greens."],
    [meat("Pork loin chops",4,"whole","pork","loin chop",1.80,0),ing("Apple",2,"whole","fruit",0.60,1),
     ing("Green beans",200,"g","veg",0.012,1),ing("Broccolini",1,"bunch","veg",2.80,1),oil(1,0)])
add("Slow-Cooker Pulled Pork",620,38,48,28,15,300,3,3,"free",["pork","slow-cook","long-cook","freezer-friendly","dairy-free"],
    ["Rub the pork with paprika, sugar and salt; slow-cook with barbecue sauce 8 hours.",
     "Shred, toss slaw, and pile into rolls."],
    [meat("Pork shoulder",1000,"g","pork","shoulder (boneless)",0.011,0),ing("Smoked paprika",1,"tbsp","spice",0.03,0),
     ing("Brown sugar",1,"tbsp","pantry",0.05,0),ing("Barbecue sauce",125,"ml","sauce",0.01,0),
     ing("Cabbage",0.25,"whole","veg",1.50,1),carrot(1,1),ing("Bread rolls",6,"whole","bakery",0.60,1)])
add("Sweet & Sour Pork",620,32,74,20,15,20,1,3,"free",["pork","rice","dairy-free","kid-favourite"],
    ["Toss the pork in cornflour and fry until golden.",
     "Add capsicum and pineapple, then sweet & sour sauce; toss.",
     "Serve over rice."],
    [meat("Pork loin",500,"g","pork","loin",0.016,0),ing("Cornflour",2,"tbsp","pantry",0.02,0),
     capsicum(1),ing("Tinned pineapple",1,"can","pantry",1.50,1),ing("Sweet & sour sauce",150,"ml","sauce",0.01,1),rice(300,2)])
add("Pork & Vegetable Stir Fry",500,32,46,18,15,15,1,4,"free",["stir-fry","pork","quick","dairy-free"],
    ["Stir-fry the pork strips in hot oil, remove.",
     "Stir-fry broccoli, capsicum and carrot 4 minutes.",
     "Return pork, add soy and oyster sauce; serve over rice."],
    [meat("Pork stir-fry strips",400,"g","pork","stir-fry strips",0.018,0),broccoli(1),capsicum(1),carrot(1,1),
     ing("Soy sauce",2,"tbsp","sauce",0.06,2),ing("Oyster sauce",1,"tbsp","sauce",0.10,2),rice(300,0),voil(1,0)])
add("Pork Schnitzel with Vegetables",700,40,52,34,20,20,1,2,"free",["pork","oven","kid-favourite"],
    ["Crumb the pork steaks and shallow-fry 3 minutes each side.",
     "Steam peas and carrots; serve with lemon."],
    [meat("Pork schnitzel steaks",500,"g","pork","schnitzel steak",0.020,0),ing("Plain flour",50,"g","pantry",0.002,0),
     ing("Egg",2,"whole","dairy",0.40,0),ing("Breadcrumbs",150,"g","pantry",0.005,0),ing("Frozen peas",150,"g","veg",0.004,1),carrot(2,1)])
add("Sausage Pasta",620,26,72,26,10,25,3,3,"replaceable",["pasta","sausage","one-pot","kid-favourite","freezer-friendly"],
    ["Squeeze the sausage meat from the skins and brown, breaking it up.",
     "Add onion, garlic and passata; simmer 15 minutes.",
     "Toss with cooked pasta and parmesan."],
    [meat("Italian pork sausages",6,"whole","sausage","pork sausage",0.55,0),onion(1,1),garlic(2,1),
     passata(500,1),ing("Penne",400,"g","pantry",0.004,2),ing("Parmesan, grated",40,"g","dairy",0.03,2,optional=True)])
add("Honey Soy Pork Meatballs",560,30,52,26,20,25,2,3,"free",["pork","dairy-free","kid-favourite"],
    ["Mix pork mince, breadcrumbs and garlic; roll and brown.",
     "Add honey, soy and a splash of water; glaze 5 minutes.",
     "Serve over rice with greens."],
    [meat("Pork mince",500,"g","pork","mince",0.014,0),ing("Breadcrumbs",50,"g","pantry",0.005,0),garlic(2,0),
     ing("Honey",2,"tbsp","pantry",0.20,1),ing("Soy sauce",3,"tbsp","sauce",0.06,1),rice(300,2),broccoli(2)])
add("BLT-Style Bacon & Egg Pasta",600,26,66,26,10,20,1,2,"replaceable",["pasta","smallgoods","quick"],
    ["Cook the pasta. Fry the bacon and cherry tomatoes.",
     "Toss with spinach, then a beaten egg off the heat until glossy."],
    [meat("Bacon",200,"g","smallgoods","bacon",0.020,0),ing("Spaghetti",400,"g","pantry",0.004,0),
     ing("Cherry tomatoes",200,"g","veg",0.012,1),ing("Baby spinach",80,"g","veg",0.02,1),ing("Egg",2,"whole","dairy",0.40,1)])

# =================================================================== LAMB
add("Shepherd's Pie",650,32,58,32,20,40,3,3,"replaceable",["oven","lamb","comfort","freezer-friendly","kid-favourite"],
    ["Mash the boiled potatoes with milk and butter.",
     "Brown the lamb mince with onion and carrot; add peas, stock and tomato paste, simmer 10 minutes.",
     "Top with mash and bake at 200°C for 25 minutes."],
    [meat("Lamb mince",500,"g","lamb","mince",0.018,1),ing("Potato",6,"whole","veg",0.40,0),
     ing("Milk",60,"ml","dairy",0.0015,0),ing("Butter",30,"g","dairy",0.010,0),onion(1,1),carrot(1,1),
     ing("Frozen peas",150,"g","veg",0.004,1),ing("Beef stock",200,"ml","pantry",0.002,1),ing("Tomato paste",2,"tbsp","pantry",0.10,1)])
add("Lamb Roast with Vegetables",700,44,42,38,15,90,3,3,"free",["lamb","roast","long-cook","dairy-free","freezer-friendly"],
    ["Rub the lamb leg with oil, garlic and rosemary. Surround with potato, pumpkin and carrot.",
     "Roast at 200°C for 80–90 minutes; rest 15 minutes and carve."],
    [meat("Lamb leg",1200,"g","lamb","leg (bone in)",0.016,0),garlic(3,0),ing("Rosemary",2,"sprig","spice",0.20,0),
     ing("Potato",4,"whole","veg",0.40,1),ing("Pumpkin",400,"g","veg",0.004,1),carrot(2,1),oil(2,0)])
add("Lamb Kofta with Flatbread",600,34,44,30,20,15,2,3,"replaceable",["lamb","bbq","kid-favourite"],
    ["Mix lamb mince with cumin, coriander and garlic; shape onto skewers and grill.",
     "Toss a tomato-cucumber salad; serve in flatbread with yoghurt."],
    [meat("Lamb mince",500,"g","lamb","mince",0.018,0),ing("Ground cumin",1,"tsp","spice",0.03,0),
     ing("Ground coriander",1,"tsp","spice",0.03,0),garlic(2,0),ing("Tomato",2,"whole","veg",0.60,1),
     ing("Cucumber",1,"whole","veg",1.00,1),ing("Flatbread",4,"whole","bakery",0.80,1),ing("Natural yoghurt",100,"g","dairy",0.008,1,optional=True)])
add("Lamb Curry",640,36,52,30,15,90,3,3,"free",["curry","lamb","slow-cook","long-cook","dairy-free","freezer-friendly"],
    ["Brown the lamb, add curry paste and cook 1 minute.",
     "Add tomatoes and stock; simmer 1.5 hours until tender.",
     "Serve over rice."],
    [meat("Lamb shoulder",700,"g","lamb","shoulder (boneless)",0.017,0),ing("Rogan josh paste",3,"tbsp","sauce",0.30,0),
     dicedtom(1),ing("Beef stock",200,"ml","pantry",0.002,1),rice(300,2)])
add("Lamb Chops with Mash",620,36,34,38,10,20,1,3,"replaceable",["lamb","low-carb"],
    ["Mash the boiled potatoes with butter.",
     "Pan-fry the lamb chops 3 minutes each side, rest.",
     "Serve with mash and steamed beans."],
    [meat("Lamb loin chops",8,"whole","lamb","loin chop",1.40,1),ing("Potato",5,"whole","veg",0.40,0),
     ing("Butter",30,"g","dairy",0.010,0),ing("Green beans",250,"g","veg",0.012,2)])
add("Moussaka",620,30,44,34,25,50,3,2,"required",["lamb","oven","comfort","freezer-friendly"],
    ["Fry the eggplant slices. Brown the lamb with onion, garlic and cinnamon; add tomatoes.",
     "Layer eggplant and mince, top with a cheese sauce, bake at 190°C for 35 minutes."],
    [meat("Lamb mince",500,"g","lamb","mince",0.018,0),ing("Eggplant",2,"whole","veg",1.80,0),onion(1,0),garlic(2,0),
     ing("Ground cinnamon",0.5,"tsp","spice",0.02,0),dicedtom(0),ing("Milk",300,"ml","dairy",0.0015,1),
     ing("Plain flour",30,"g","pantry",0.002,1),cheese(80,1)])
add("Lamb Souvlaki Wraps",580,34,46,28,20,15,1,3,"replaceable",["lamb","bbq","kid-favourite"],
    ["Toss diced lamb with oregano, lemon and garlic; grill 8 minutes.",
     "Warm the pita, add lamb, salad and tzatziki."],
    [meat("Lamb leg steaks",500,"g","lamb","leg steak",0.022,0),ing("Dried oregano",1,"tsp","spice",0.02,0),
     ing("Lemon",1,"whole","fruit",0.70,0),garlic(2,0),ing("Pita bread",4,"whole","bakery",0.70,1),
     ing("Tzatziki",150,"g","dairy",0.012,1),ing("Mixed salad leaves",100,"g","veg",0.02,1)])

# =================================================================== FISH & SEAFOOD
add("Baked Salmon with Roast Vegetables",520,38,32,26,10,30,1,5,"free",["fish","salmon","healthy","oven","weight-loss","dairy-free","low-carb"],
    ["Roast pumpkin, potato and broccoli 20 minutes.",
     "Add the salmon and roast 12 minutes; squeeze over lemon."],
    [meat("Salmon fillets",4,"whole","salmon","fillet",4.50,1),ing("Pumpkin",400,"g","veg",0.004,0),
     ing("Potato",3,"whole","veg",0.40,0),broccoli(0),oil(2,0),ing("Lemon",1,"whole","fruit",0.70,1)])
add("Teriyaki Salmon with Rice",610,38,62,22,10,20,1,4,"free",["fish","salmon","healthy","dairy-free","high-protein"],
    ["Cook the rice. Sear the salmon skin-side down 4 minutes, flip 2 minutes.",
     "Glaze with teriyaki; serve over rice with broccolini."],
    [meat("Salmon fillets",4,"whole","salmon","fillet",4.50,1),ing("Teriyaki sauce",4,"tbsp","sauce",0.10,1),
     rice(300,0),ing("Broccolini",1,"bunch","veg",2.80,1)])
add("Oven-Baked Fish & Chips",560,34,58,20,10,30,1,3,"free",["fish","oven","dairy-free","kid-favourite"],
    ["Bake the chips 15 minutes. Crumb the fish and bake with the chips 15 minutes.",
     "Serve with peas and lemon."],
    [meat("White fish fillets",500,"g","fish","white fillet",0.028,1),ing("Oven chips",750,"g","veg",0.005,0),
     ing("Plain flour",50,"g","pantry",0.002,1),ing("Egg",2,"whole","dairy",0.40,1),ing("Breadcrumbs",150,"g","pantry",0.005,1),
     ing("Frozen peas",200,"g","veg",0.004,2),ing("Lemon",1,"whole","fruit",0.70,2)])
add("Baked Barramundi with Salad",420,36,18,22,10,18,1,5,"free",["fish","healthy","weight-loss","low-carb","dairy-free"],
    ["Bake the barramundi with oil and lemon 15–18 minutes.",
     "Toss a salad of leaves, tomato, cucumber and avocado; serve the fish on top."],
    [meat("Barramundi fillets",500,"g","fish","barramundi fillet",0.034,0),ing("Mixed salad leaves",150,"g","veg",0.02,1),
     ing("Tomato",2,"whole","veg",0.60,1),ing("Cucumber",1,"whole","veg",1.00,1),ing("Avocado",1,"whole","fruit",1.50,1),
     ing("Lemon",1,"whole","fruit",0.70,0),oil(1,0)])
add("Tuna Mornay Pasta Bake",590,32,66,22,15,25,3,3,"required",["pasta","fish","budget","no-fresh-meat","kid-favourite"],
    ["Cook the pasta. Make a white sauce with butter, flour and milk; stir in most of the cheese.",
     "Fold through tuna, corn, peas and pasta; top with cheese and bake 20 minutes."],
    [ing("Tinned tuna",2,"can","pantry",1.50,1),ing("Pasta (macaroni)",350,"g","pantry",0.004,0),
     ing("Butter",40,"g","dairy",0.010,0),ing("Plain flour",40,"g","pantry",0.002,0),ing("Milk",500,"ml","dairy",0.0015,0),
     cheese(120,0),ing("Tinned corn",1,"can","pantry",1.20,1),ing("Frozen peas",100,"g","veg",0.004,1)])
add("Fish Tacos",520,30,52,20,15,15,1,3,"replaceable",["fish","mexican","quick"],
    ["Toss the fish with spice and pan-fry 3 minutes each side.",
     "Warm tortillas; fill with fish, slaw and a squeeze of lime."],
    [meat("White fish fillets",500,"g","fish","white fillet",0.028,0),ing("Taco spice mix",1,"tbsp","spice",0.20,0),
     ing("Tortillas",8,"whole","bakery",0.25,1),ing("Cabbage",0.25,"whole","veg",1.50,1),ing("Lime",1,"whole","fruit",0.60,1)])
add("Prawn Stir Fry with Noodles",520,30,58,16,15,12,1,4,"free",["stir-fry","fish","noodles","quick","dairy-free"],
    ["Cook the noodles. Stir-fry the prawns 2 minutes, remove.",
     "Stir-fry the vegetables 4 minutes, return prawns, add noodles and soy."],
    [meat("Green prawns",400,"g","fish","prawn",0.030,1),ing("Hokkien noodles",400,"g","pantry",0.006,0),
     ing("Mixed stir-fry vegetables",400,"g","veg",0.008,2),ing("Soy sauce",2,"tbsp","sauce",0.06,2),voil(1,1)])
add("Garlic Prawn Pasta",600,28,66,24,10,15,1,2,"replaceable",["pasta","fish","quick"],
    ["Cook the pasta. Fry the prawns in garlic butter 3 minutes.",
     "Toss with pasta, chilli, lemon and parsley."],
    [meat("Green prawns",400,"g","fish","prawn",0.030,1),ing("Spaghetti",400,"g","pantry",0.004,0),
     ing("Butter",40,"g","dairy",0.010,1),garlic(4,1),ing("Lemon",1,"whole","fruit",0.70,2),ing("Parsley",0.5,"bunch","veg",1.00,2)])
add("Fish Curry",520,32,44,24,15,25,3,4,"free",["curry","fish","dairy-free","freezer-friendly"],
    ["Fry the curry paste, add coconut milk and simmer.",
     "Add the fish pieces and cook gently 8 minutes; serve over rice."],
    [meat("White fish fillets",500,"g","fish","white fillet",0.028,1),ing("Mild curry paste",2,"tbsp","sauce",0.30,0),
     coconut(0),rice(300,2),ing("Baby spinach",80,"g","veg",0.02,1)])
add("Salmon & Pea Pasta",620,34,64,26,10,20,1,3,"required",["pasta","fish","salmon","quick"],
    ["Cook the pasta with the peas in the last 2 minutes.",
     "Flake the cooked salmon, toss with pasta, cream, lemon and dill."],
    [meat("Salmon fillets",400,"g","salmon","fillet",4.50,1),ing("Penne",400,"g","pantry",0.004,0),
     ing("Frozen peas",150,"g","veg",0.004,0),ing("Thickened cream",150,"ml","dairy",0.008,1),
     ing("Lemon",1,"whole","fruit",0.70,1),ing("Dill",0.5,"bunch","veg",1.00,1,optional=True)])
add("Prawn Fried Rice",520,26,68,14,15,15,2,3,"free",["stir-fry","fish","rice","uses-leftovers","dairy-free"],
    ["Scramble the eggs, set aside. Stir-fry the prawns 2 minutes.",
     "Add peas, corn and carrot, then cold rice and soy; fold egg through."],
    [meat("Green prawns",300,"g","fish","prawn",0.030,0),ing("Egg",2,"whole","dairy",0.40,0),
     ing("Frozen peas and corn",250,"g","veg",0.005,1),carrot(1,1),rice(300,2),ing("Soy sauce",2,"tbsp","sauce",0.06,2)])
add("Fish Pie",600,34,48,28,20,40,3,2,"required",["fish","oven","comfort","freezer-friendly"],
    ["Poach the fish in milk, then make a sauce with the milk, butter and flour.",
     "Fold fish and peas through; top with mash and bake at 200°C for 25 minutes."],
    [meat("White fish fillets",500,"g","fish","white fillet",0.028,0),ing("Milk",400,"ml","dairy",0.0015,0),
     ing("Butter",40,"g","dairy",0.010,0),ing("Plain flour",30,"g","pantry",0.002,0),ing("Frozen peas",150,"g","veg",0.004,0),
     ing("Potato",6,"whole","veg",0.40,1)])

print("after part 2:", len(R))

# =================================================================== VEGETARIAN
add("Vegetable & Lentil Curry",430,16,68,12,15,25,3,5,"free",["curry","vegetarian","budget","healthy","weight-loss","freezer-friendly","no-fresh-meat","dairy-free"],
    ["Cook onion, garlic and carrot in oil 5 minutes; stir in curry paste.",
     "Add lentils, tomatoes, coconut milk and water; simmer 20 minutes.",
     "Stir through spinach; serve with rice."],
    [ing("Tinned brown lentils",2,"can","pantry",1.00,1),onion(1,0),garlic(2,0),carrot(2,0),
     ing("Mild curry paste",2,"tbsp","sauce",0.30,0),dicedtom(1),coconut(1),ing("Baby spinach",100,"g","veg",0.02,2),rice(300,2)])
add("Pumpkin & Chickpea Curry",410,15,62,12,15,25,3,5,"free",["curry","vegetarian","healthy","weight-loss","dairy-free","freezer-friendly","no-fresh-meat"],
    ["Cook onion and garlic; add curry paste and pumpkin.",
     "Add chickpeas, coconut milk and water; simmer 20 minutes.",
     "Stir through spinach; serve with rice."],
    [ing("Pumpkin",700,"g","veg",0.004,1),ing("Tinned chickpeas",2,"can","pantry",1.00,1),onion(1,0),garlic(2,0),
     ing("Mild curry paste",2,"tbsp","sauce",0.30,0),coconut(1),ing("Baby spinach",100,"g","veg",0.02,2),rice(300,2)])
add("Vegetable Stir-Fry with Tofu",440,22,46,18,15,15,1,4,"free",["stir-fry","vegetarian","quick","dairy-free","no-fresh-meat"],
    ["Fry the cubed tofu until golden, remove.",
     "Stir-fry capsicum, broccoli and carrot 4 minutes.",
     "Return tofu, add soy and hoisin; serve over rice."],
    [ing("Firm tofu",400,"g","pantry",0.010,0),capsicum(1),broccoli(1),carrot(1,1),
     ing("Soy sauce",2,"tbsp","sauce",0.06,2),ing("Hoisin sauce",1,"tbsp","sauce",0.12,2),rice(300,0),voil(1,0)])
add("Minestrone Soup",340,14,54,8,15,30,3,5,"free",["soup","vegetarian","light","weight-loss","budget","dairy-free","freezer-friendly","no-fresh-meat"],
    ["Cook onion, carrot, celery and garlic 6 minutes.",
     "Add tomatoes, stock and cannellini beans; simmer 15 minutes, add pasta.",
     "Stir through spinach; serve with bread."],
    [onion(1,0),carrot(2,0),ing("Celery",2,"whole","veg",0.40,0),garlic(2,0),dicedtom(1),
     ing("Vegetable stock",1200,"ml","pantry",0.002,1),ing("Tinned cannellini beans",1,"can","pantry",1.00,1),
     ing("Small soup pasta",150,"g","pantry",0.004,1),ing("Baby spinach",80,"g","veg",0.02,2),ing("Crusty bread",1,"whole","bakery",3.50,2)])
add("Vegetable Fried Rice",420,12,72,10,15,15,2,3,"free",["stir-fry","vegetarian","rice","quick","uses-leftovers","dairy-free","no-fresh-meat"],
    ["Scramble the eggs, set aside. Stir-fry mixed vegetables 4 minutes.",
     "Add cold rice and soy; fold egg through."],
    [ing("Egg",3,"whole","dairy",0.40,0),ing("Frozen mixed vegetables",300,"g","veg",0.005,1),rice(300,2),ing("Soy sauce",2,"tbsp","sauce",0.06,2),voil(1,0)])
add("Red Lentil Dahl",380,18,58,8,10,30,3,5,"free",["curry","vegetarian","budget","healthy","weight-loss","dairy-free","freezer-friendly","no-fresh-meat"],
    ["Cook onion, garlic and ginger; add spices.",
     "Add red lentils, tomatoes and water; simmer 25 minutes until soft.",
     "Serve with rice or naan."],
    [ing("Red lentils",300,"g","pantry",0.004,1),onion(1,0),garlic(2,0),ing("Ginger",1,"tbsp","veg",0.10,0),
     ing("Garam masala",1,"tbsp","spice",0.03,0),dicedtom(1),rice(300,2)])
add("Vegetable Lasagne",560,22,58,26,25,45,3,2,"required",["pasta","vegetarian","oven","comfort","freezer-friendly","no-fresh-meat"],
    ["Make a tomato-vegetable sauce with onion, zucchini, mushroom and passata.",
     "Layer with lasagne sheets and a cheese sauce; bake at 190°C for 35 minutes."],
    [onion(1,0),ing("Zucchini",1,"whole","veg",0.80,0),ing("Button mushrooms",150,"g","veg",0.012,0),passata(700,0),
     ing("Lasagne sheets",250,"g","pantry",0.006,1),ing("Milk",500,"ml","dairy",0.0015,1),ing("Plain flour",40,"g","pantry",0.002,1),cheese(150,1)])
add("Macaroni Cheese",620,24,68,28,10,25,2,2,"required",["pasta","vegetarian","comfort","kid-favourite","no-fresh-meat"],
    ["Cook the macaroni. Make a cheese sauce with butter, flour, milk and cheese.",
     "Combine, top with extra cheese and grill until golden."],
    [ing("Macaroni",400,"g","pantry",0.004,0),ing("Butter",50,"g","dairy",0.010,1),ing("Plain flour",50,"g","pantry",0.002,1),
     ing("Milk",600,"ml","dairy",0.0015,1),cheese(200,1)])
add("Shakshuka",360,18,26,20,10,25,1,4,"replaceable",["vegetarian","one-pan","low-carb","no-fresh-meat"],
    ["Cook onion, capsicum and garlic; add tomatoes and paprika, simmer 10 minutes.",
     "Make wells and crack in the eggs; cover and cook until set.",
     "Serve with crusty bread."],
    [ing("Egg",6,"whole","dairy",0.40,1),onion(1,0),capsicum(0),garlic(2,0),dicedtom(0),
     ing("Smoked paprika",1,"tsp","spice",0.03,0),ing("Crusty bread",1,"whole","bakery",3.50,2)])
add("Vegetable Frittata",380,20,18,26,10,25,2,4,"required",["vegetarian","low-carb","one-pan","no-fresh-meat"],
    ["Cook the potato, zucchini and onion until soft.",
     "Pour over beaten eggs with cheese; cook, then finish under the grill."],
    [ing("Egg",8,"whole","dairy",0.40,1),ing("Potato",2,"whole","veg",0.40,0),ing("Zucchini",1,"whole","veg",0.80,0),onion(1,0),cheese(80,1)])
add("Halloumi & Vegetable Traybake",480,22,40,26,10,35,1,3,"required",["vegetarian","tray-bake","one-pan","no-fresh-meat"],
    ["Roast chopped capsicum, zucchini, red onion and chickpeas 25 minutes.",
     "Add the halloumi slices and roast 8 minutes."],
    [ing("Halloumi",250,"g","dairy",0.030,1),capsicum(0),ing("Zucchini",1,"whole","veg",0.80,0),
     ing("Red onion",1,"whole","veg",0.55,0),ing("Tinned chickpeas",1,"can","pantry",1.00,0),oil(2,0)])
add("Vegetarian Burritos",560,20,80,18,15,20,2,3,"replaceable",["mexican","vegetarian","freezer-friendly","no-fresh-meat"],
    ["Cook rice. Warm black beans with taco spice and corn.",
     "Fill tortillas with rice, beans, cheese and salsa; roll and toast."],
    [rice(300,0),ing("Tinned black beans",2,"can","pantry",1.10,1),ing("Taco spice mix",1,"tbsp","spice",0.20,1),
     ing("Tinned corn",1,"can","pantry",1.20,1),ing("Tortillas",8,"whole","bakery",0.25,2),cheese(100,2),ing("Salsa",150,"g","sauce",0.01,2)])
add("Pumpkin Risotto",520,16,72,18,10,30,1,3,"required",["vegetarian","rice","no-fresh-meat"],
    ["Roast the diced pumpkin. Toast the rice with onion, then add stock a ladle at a time.",
     "Stir in pumpkin and parmesan until creamy."],
    [ing("Pumpkin",500,"g","veg",0.004,0),ing("Arborio rice",300,"g","pantry",0.005,1),onion(1,1),
     ing("Vegetable stock",1000,"ml","pantry",0.002,1),ing("Parmesan, grated",50,"g","dairy",0.03,1)])
add("Bean & Vegetable Chilli",400,18,64,8,10,30,3,5,"free",["mexican","vegetarian","budget","healthy","weight-loss","freezer-friendly","no-fresh-meat","dairy-free"],
    ["Cook onion, garlic and capsicum; add chilli spice.",
     "Add tomatoes, kidney and black beans; simmer 20 minutes.",
     "Serve over rice."],
    [onion(1,0),garlic(2,0),capsicum(0),ing("Mild chilli spice",1,"tbsp","spice",0.15,0),dicedtom(1),
     ing("Tinned kidney beans",1,"can","pantry",1.10,1),ing("Tinned black beans",1,"can","pantry",1.10,1),rice(300,2)])
add("Gnocchi with Tomato & Basil",520,16,84,14,10,20,1,3,"replaceable",["pasta","vegetarian","quick","kid-favourite","no-fresh-meat"],
    ["Simmer a quick sauce of passata, garlic and basil.",
     "Boil the gnocchi until they float; toss through the sauce with parmesan."],
    [ing("Gnocchi",500,"g","pantry",0.006,1),passata(500,0),garlic(2,0),ing("Basil",0.5,"bunch","veg",1.50,0),
     ing("Parmesan, grated",40,"g","dairy",0.03,1,optional=True)])
add("Falafel Wraps",520,18,68,20,15,20,1,3,"replaceable",["vegetarian","kid-favourite","no-fresh-meat"],
    ["Bake or pan-fry the falafel until golden.",
     "Warm the pita; fill with falafel, salad and hummus."],
    [ing("Falafel",12,"whole","pantry",0.30,0),ing("Pita bread",4,"whole","bakery",0.70,1),
     ing("Mixed salad leaves",100,"g","veg",0.02,1),ing("Hummus",150,"g","sauce",0.012,1),ing("Tomato",1,"whole","veg",0.60,1)])
add("Stuffed Capsicums",420,18,48,16,15,40,2,3,"required",["vegetarian","oven","no-fresh-meat"],
    ["Cook rice with onion, garlic and tomatoes.",
     "Fill halved capsicums, top with cheese, bake at 190°C for 30 minutes."],
    [capsicum(0),rice(250,0),onion(1,0),garlic(2,0),dicedtom(0),cheese(100,1)])
add("Pea & Mint Pasta",480,18,74,12,10,15,1,3,"replaceable",["pasta","vegetarian","quick","no-fresh-meat"],
    ["Cook the pasta with the peas in the last 2 minutes.",
     "Toss with mint, lemon, olive oil and parmesan."],
    [ing("Orecchiette",400,"g","pantry",0.004,0),ing("Frozen peas",250,"g","veg",0.004,0),ing("Mint",0.5,"bunch","veg",1.00,1),
     ing("Lemon",1,"whole","fruit",0.70,1),oil(2,1),ing("Parmesan, grated",40,"g","dairy",0.03,1,optional=True)])

# =================================================================== MIXED / PASTA / OTHER
add("Homemade Pizza Night",680,28,78,26,15,15,1,2,"required",["pizza","smallgoods","fun","kid-favourite"],
    ["Spread the bases with passata; top with mozzarella and ham.",
     "Bake at 220°C for 12–15 minutes; serve with salad."],
    [meat("Sliced ham",150,"g","smallgoods","sliced ham",0.024,0),ing("Pizza bases",2,"whole","bakery",2.50,0),
     passata(150,0),ing("Mozzarella, grated",200,"g","dairy",0.016,0),ing("Mixed salad leaves",100,"g","veg",0.02,1)])
add("Beef & Bacon Pasta Bake",680,34,64,32,15,35,3,2,"required",["pasta","beef","smallgoods","oven","freezer-friendly","kid-favourite"],
    ["Brown the mince and bacon with onion; add passata and simmer.",
     "Fold through cooked pasta, top with cheese, bake at 200°C for 20 minutes."],
    [meat("Beef mince",400,"g","beef","mince",0.016,0),meat("Bacon",100,"g","smallgoods","bacon",0.020,0),onion(1,0),
     passata(500,0),ing("Penne",400,"g","pantry",0.004,1),cheese(150,1)])
add("Chicken & Bacon Alfredo",700,40,62,34,10,25,2,2,"required",["pasta","chicken","smallgoods","comfort"],
    ["Cook the pasta. Fry the chicken and bacon.",
     "Add cream and parmesan; toss through the pasta."],
    [meat("Chicken breast",400,"g","chicken","breast",0.012,0),meat("Bacon",100,"g","smallgoods","bacon",0.020,0),
     ing("Fettuccine",400,"g","pantry",0.005,0),ing("Thickened cream",250,"ml","dairy",0.008,1),ing("Parmesan, grated",60,"g","dairy",0.03,1)])
add("Nasi Goreng",560,26,68,20,15,15,2,3,"free",["stir-fry","rice","smallgoods","uses-leftovers","dairy-free"],
    ["Fry the diced bacon, then add vegetables.",
     "Add cold rice and kecap manis; top with a fried egg."],
    [meat("Bacon",150,"g","smallgoods","bacon",0.020,0),rice(300,1),ing("Frozen mixed vegetables",250,"g","veg",0.005,0),
     ing("Kecap manis",3,"tbsp","sauce",0.02,1),ing("Egg",4,"whole","dairy",0.40,1)])
add("Chicken Quesadillas",600,34,52,28,10,15,1,3,"required",["mexican","chicken","quick","kid-favourite"],
    ["Cook and shred the chicken with taco spice.",
     "Fill tortillas with chicken and cheese; toast until golden."],
    [meat("Chicken breast",400,"g","chicken","breast",0.012,0),ing("Taco spice mix",1,"tbsp","spice",0.20,0),
     ing("Tortillas",8,"whole","bakery",0.25,1),cheese(200,1)])
add("Fried Rice with Egg & Peas",400,14,70,8,10,15,2,3,"free",["rice","vegetarian","quick","uses-leftovers","budget","dairy-free","no-fresh-meat"],
    ["Scramble the eggs, set aside. Stir-fry peas, corn and carrot.",
     "Add cold rice and soy; fold egg through."],
    [ing("Egg",3,"whole","dairy",0.40,0),ing("Frozen peas and corn",300,"g","veg",0.005,1),carrot(1,1),rice(350,2),ing("Soy sauce",2,"tbsp","sauce",0.06,2)])
add("Beef Ramen Bowls",560,30,64,18,10,20,1,3,"free",["soup","beef","noodles","dairy-free"],
    ["Simmer the stock with soy, ginger and garlic.",
     "Cook the ramen; sear the beef strips.",
     "Assemble bowls with noodles, broth, beef, egg and greens."],
    [meat("Beef strips",300,"g","beef","stir-fry strips",0.022,1),ing("Ramen noodles",300,"g","pantry",0.006,1),
     ing("Beef stock",1000,"ml","pantry",0.002,0),ing("Soy sauce",3,"tbsp","sauce",0.06,0),ing("Ginger",1,"tbsp","veg",0.10,0),
     ing("Egg",2,"whole","dairy",0.40,2),ing("Bok choy",2,"whole","veg",0.80,2)])
add("Pesto Chicken Pasta",640,38,62,26,10,20,1,2,"required",["pasta","chicken","quick"],
    ["Cook the pasta. Pan-fry the chicken.",
     "Toss pasta and chicken with pesto, cherry tomatoes and parmesan."],
    [meat("Chicken breast",400,"g","chicken","breast",0.012,0),ing("Penne",400,"g","pantry",0.004,0),
     ing("Basil pesto",100,"g","sauce",0.02,1),ing("Cherry tomatoes",200,"g","veg",0.012,1),ing("Parmesan, grated",40,"g","dairy",0.03,1)])
add("Chicken Congee",320,24,44,6,10,40,3,5,"free",["soup","chicken","rice","light","weight-loss","dairy-free"],
    ["Simmer the rice in plenty of stock with ginger 35 minutes until porridge-like.",
     "Add the shredded chicken; top with spring onion and soy."],
    [meat("Chicken thigh fillet",300,"g","chicken","thigh fillet",0.013,1),rice(200,0),
     ing("Chicken stock",1500,"ml","pantry",0.002,0),ing("Ginger",1,"tbsp","veg",0.10,0),ing("Spring onion",2,"whole","veg",0.30,1)])
add("Tomato Soup with Grilled Cheese",420,14,52,18,10,25,2,3,"required",["soup","vegetarian","comfort","kid-favourite","no-fresh-meat"],
    ["Simmer tomatoes, onion, garlic and stock 20 minutes; blend.",
     "Make grilled cheese sandwiches and serve alongside."],
    [dicedtom(0),onion(1,0),garlic(2,0),ing("Vegetable stock",500,"ml","pantry",0.002,0),
     ing("Bread",8,"slice","bakery",0.30,1),cheese(150,1)])

# =================================================================== BATCH A
add("Beef Goulash",560,36,44,26,15,120,3,3,"replaceable",["beef","slow-cook","long-cook","freezer-friendly","comfort"],
    ["Brown the beef, remove. Cook onion and capsicum, stir in paprika.",
     "Return beef with tomatoes and stock; simmer 1.5–2 hours.",
     "Serve with pasta or potatoes and a dollop of sour cream."],
    [meat("Beef chuck",700,"g","beef","chuck",0.015,0),onion(1,1),capsicum(1),ing("Sweet paprika",2,"tbsp","spice",0.03,1),
     dicedtom(2),ing("Beef stock",300,"ml","pantry",0.002,2),ing("Sour cream",100,"g","dairy",0.010,2,optional=True),ing("Pasta",350,"g","pantry",0.004,2)])
add("Beef & Mushroom Pie",680,32,54,38,20,45,3,2,"required",["beef","oven","comfort","freezer-friendly"],
    ["Brown the beef and onion, add mushrooms. Stir in flour, stock and Worcestershire; simmer.",
     "Pour into a dish, top with puff pastry, bake at 200°C for 25 minutes."],
    [meat("Beef chuck",600,"g","beef","chuck",0.015,0),ing("Button mushrooms",200,"g","veg",0.012,0),onion(1,0),
     ing("Plain flour",30,"g","pantry",0.002,0),ing("Beef stock",300,"ml","pantry",0.002,0),ing("Worcestershire sauce",1,"tbsp","sauce",0.05,0),ing("Puff pastry",2,"whole","bakery",1.00,1)])
add("Beef Kebabs with Rice",520,34,44,22,20,15,1,4,"free",["beef","bbq","dairy-free"],
    ["Thread beef and vegetables onto skewers; brush with oil and spice.",
     "Grill 10 minutes, turning. Serve over rice."],
    [meat("Beef rump",500,"g","beef","rump",0.026,0),capsicum(0),ing("Red onion",1,"whole","veg",0.55,0),
     ing("Zucchini",1,"whole","veg",0.80,0),ing("Mixed spice",1,"tbsp","spice",0.10,0),rice(300,1),oil(2,0)])
add("Beef Pho",480,30,58,10,15,40,2,4,"free",["soup","beef","noodles","dairy-free"],
    ["Simmer the stock with star anise, ginger and cinnamon 30 minutes.",
     "Cook the rice noodles; slice the beef thinly.",
     "Assemble bowls with noodles, raw beef and hot broth; top with herbs and lime."],
    [meat("Beef rump",300,"g","beef","rump",0.026,2),ing("Rice noodles",300,"g","pantry",0.006,1),
     ing("Beef stock",1500,"ml","pantry",0.002,0),ing("Star anise",2,"whole","spice",0.10,0),ing("Ginger",1,"tbsp","veg",0.10,0),
     ing("Bean sprouts",100,"g","veg",0.01,2),ing("Lime",1,"whole","fruit",0.60,2),ing("Fresh coriander",1,"bunch","veg",2.00,2)])
add("Beef Rendang",620,36,32,40,15,150,3,3,"free",["curry","beef","slow-cook","long-cook","dairy-free","freezer-friendly"],
    ["Brown the beef with rendang paste.",
     "Add coconut milk; simmer very gently 2–2.5 hours until dark and thick.",
     "Serve with rice."],
    [meat("Beef chuck",700,"g","beef","chuck",0.015,0),ing("Rendang paste",3,"tbsp","sauce",0.30,0),coconut(1),rice(300,2)])
add("Meatloaf with Vegetables",560,32,32,32,15,55,3,3,"replaceable",["beef","oven","comfort","freezer-friendly","kid-favourite"],
    ["Mix mince, breadcrumbs, egg and grated onion; press into a loaf tin.",
     "Glaze with tomato sauce, bake at 190°C for 50 minutes.",
     "Serve with mash and greens."],
    [meat("Beef mince",700,"g","beef","mince",0.016,0),ing("Breadcrumbs",80,"g","pantry",0.005,0),ing("Egg",2,"whole","dairy",0.40,0),
     onion(1,0),ing("Tomato sauce",3,"tbsp","sauce",0.02,1),ing("Potato",5,"whole","veg",0.40,2),ing("Green beans",200,"g","veg",0.012,2)])
add("Beef Bourguignon",620,38,30,36,20,150,3,3,"free",["beef","slow-cook","long-cook","freezer-friendly","comfort"],
    ["Brown the beef and bacon, remove. Cook onion, carrot and mushrooms.",
     "Return with stock and herbs; simmer 2–2.5 hours.",
     "Serve with mash or crusty bread."],
    [meat("Beef chuck",700,"g","beef","chuck",0.015,0),meat("Bacon",100,"g","smallgoods","bacon",0.020,0),
     onion(1,1),carrot(2,1),ing("Button mushrooms",200,"g","veg",0.012,1),ing("Beef stock",500,"ml","pantry",0.002,2),ing("Thyme",2,"sprig","spice",0.10,2)])
add("Salisbury Steak with Gravy",560,32,28,34,15,25,2,3,"replaceable",["beef","comfort","kid-favourite"],
    ["Shape seasoned mince into oval patties and brown.",
     "Make an onion-mushroom gravy in the pan; simmer the patties in it 10 minutes.",
     "Serve with mash."],
    [meat("Beef mince",600,"g","beef","mince",0.016,0),onion(1,1),ing("Button mushrooms",150,"g","veg",0.012,1),
     ing("Beef stock",300,"ml","pantry",0.002,1),ing("Plain flour",1,"tbsp","pantry",0.02,1),ing("Potato",5,"whole","veg",0.40,2)])
add("Beef Vindaloo",560,34,40,26,15,60,3,3,"free",["curry","beef","dairy-free","freezer-friendly"],
    ["Brown the beef, add vindaloo paste and cook 1 minute.",
     "Add tomatoes and stock; simmer 45 minutes until tender.",
     "Serve with rice."],
    [meat("Beef chuck",600,"g","beef","chuck",0.015,0),ing("Vindaloo paste",3,"tbsp","sauce",0.30,0),dicedtom(1),
     ing("Beef stock",200,"ml","pantry",0.002,1),rice(300,2)])
add("Steak Sandwiches",640,34,52,32,15,15,1,2,"replaceable",["beef","quick"],
    ["Fry the minute steaks and caramelise the onions.",
     "Build sandwiches with rocket, tomato, cheese and relish on toasted bread."],
    [meat("Beef minute steaks",500,"g","beef","minute steak",0.028,0),onion(2,0),ing("Turkish bread",1,"whole","bakery",4.00,1),
     ing("Rocket",60,"g","veg",0.03,1),ing("Tomato",1,"whole","veg",0.60,1),cheese(80,1),ing("Tomato relish",2,"tbsp","sauce",0.03,1)])
add("Beef Lasagne",700,36,60,34,30,50,3,2,"required",["pasta","beef","oven","comfort","freezer-friendly","kid-favourite"],
    ["Make a bolognese sauce. Make a cheese sauce.",
     "Layer with lasagne sheets; bake at 190°C for 40 minutes."],
    [meat("Beef mince",600,"g","beef","mince",0.016,0),onion(1,0),passata(700,0),ing("Lasagne sheets",250,"g","pantry",0.006,1),
     ing("Milk",600,"ml","dairy",0.0015,1),ing("Plain flour",50,"g","pantry",0.002,1),cheese(200,1)])
add("Beef & Barley Soup",380,26,44,10,15,60,3,4,"free",["soup","beef","budget","dairy-free","freezer-friendly","weight-loss"],
    ["Brown the beef, add onion, carrot and celery.",
     "Add barley, stock and tomatoes; simmer 45 minutes."],
    [meat("Beef chuck",400,"g","beef","chuck",0.015,0),ing("Pearl barley",150,"g","pantry",0.004,1),onion(1,0),carrot(2,0),
     ing("Celery",2,"whole","veg",0.40,0),ing("Beef stock",1500,"ml","pantry",0.002,1),dicedtom(1)])
add("Chilli Beef Noodles",560,30,64,18,10,15,1,3,"free",["stir-fry","beef","noodles","quick","dairy-free"],
    ["Cook the noodles. Stir-fry the mince until crisp.",
     "Add chilli-garlic sauce and soy; toss with noodles and greens."],
    [meat("Beef mince",400,"g","beef","mince",0.016,1),ing("Egg noodles",400,"g","pantry",0.006,0),
     ing("Chilli garlic sauce",2,"tbsp","sauce",0.10,1),ing("Soy sauce",2,"tbsp","sauce",0.06,1),ing("Bok choy",2,"whole","veg",0.80,1)])

# ---- CHICKEN A ----
add("Chicken Chow Mein",540,32,60,16,15,15,1,3,"free",["stir-fry","chicken","noodles","quick","dairy-free"],
    ["Cook the noodles. Stir-fry the chicken, then the cabbage and carrot.",
     "Add noodles, soy and oyster sauce; toss."],
    [meat("Chicken breast",400,"g","chicken","breast",0.012,1),ing("Egg noodles",400,"g","pantry",0.006,0),
     ing("Cabbage",0.25,"whole","veg",1.50,1),carrot(1,1),ing("Soy sauce",2,"tbsp","sauce",0.06,2),ing("Oyster sauce",1,"tbsp","sauce",0.10,2)])
add("Chicken Biryani",640,34,72,22,20,40,3,3,"replaceable",["curry","chicken","rice","freezer-friendly"],
    ["Brown the chicken with biryani spice and onion.",
     "Layer with par-cooked rice and yoghurt; steam 20 minutes.",
     "Fluff and serve with coriander."],
    [meat("Chicken thigh fillet",600,"g","chicken","thigh fillet",0.013,0),ing("Biryani spice",2,"tbsp","spice",0.20,0),onion(2,0),
     ing("Basmati rice",350,"g","pantry",0.003,1),ing("Natural yoghurt",150,"g","dairy",0.008,1),ing("Fresh coriander",1,"bunch","veg",2.00,2)])
add("Chicken Katsu Curry",680,36,74,26,20,25,2,3,"replaceable",["chicken","rice","kid-favourite"],
    ["Crumb and fry the chicken; slice.",
     "Make a katsu curry sauce with onion, carrot, curry powder and stock.",
     "Serve chicken over rice with the sauce."],
    [meat("Chicken breast",500,"g","chicken","breast",0.012,0),ing("Plain flour",50,"g","pantry",0.002,0),ing("Egg",2,"whole","dairy",0.40,0),
     ing("Panko breadcrumbs",150,"g","pantry",0.006,0),onion(1,1),carrot(1,1),ing("Curry powder",1,"tbsp","spice",0.05,1),rice(300,2)])
add("Chicken Marsala",560,38,24,30,10,25,2,2,"required",["chicken","comfort"],
    ["Fry the chicken, remove. Cook mushrooms, add marsala (or stock) and cream.",
     "Return chicken; simmer 10 minutes. Serve with mash or pasta."],
    [meat("Chicken breast",600,"g","chicken","breast",0.012,0),ing("Button mushrooms",200,"g","veg",0.012,1),
     ing("Chicken stock",200,"ml","pantry",0.002,1),ing("Thickened cream",150,"ml","dairy",0.008,1),ing("Fettuccine",350,"g","pantry",0.005,2)])
add("Chicken & Mushroom Risotto",560,30,68,18,10,30,1,3,"required",["chicken","rice","comfort"],
    ["Cook the chicken and mushrooms. Toast the rice with onion.",
     "Add stock a ladle at a time until creamy; stir in parmesan."],
    [meat("Chicken thigh fillet",400,"g","chicken","thigh fillet",0.013,0),ing("Button mushrooms",200,"g","veg",0.012,0),
     ing("Arborio rice",300,"g","pantry",0.005,1),onion(1,1),ing("Chicken stock",1000,"ml","pantry",0.002,1),ing("Parmesan, grated",50,"g","dairy",0.03,1)])
add("Chicken Kiev with Vegetables",680,38,44,38,20,30,1,2,"required",["chicken","oven","kid-favourite"],
    ["Stuff the chicken with garlic butter, crumb, and bake at 200°C for 25 minutes.",
     "Serve with mash and peas."],
    [meat("Chicken breast",600,"g","chicken","breast",0.012,0),ing("Butter",60,"g","dairy",0.010,0),garlic(3,0),
     ing("Breadcrumbs",150,"g","pantry",0.005,0),ing("Egg",2,"whole","dairy",0.40,0),ing("Potato",4,"whole","veg",0.40,1),ing("Frozen peas",150,"g","veg",0.004,1)])
add("Chicken Shawarma Wraps",580,36,50,26,20,20,1,3,"replaceable",["chicken","middle-eastern","kid-favourite"],
    ["Toss chicken with shawarma spice and grill.",
     "Warm flatbread; fill with chicken, salad, pickles and garlic sauce."],
    [meat("Chicken thigh fillet",600,"g","chicken","thigh fillet",0.013,0),ing("Shawarma spice",2,"tbsp","spice",0.20,0),
     ing("Flatbread",4,"whole","bakery",0.80,1),ing("Mixed salad leaves",100,"g","veg",0.02,1),ing("Garlic sauce",80,"g","sauce",0.02,1)])
add("Chicken Souvlaki Plate",560,40,36,28,20,15,1,4,"replaceable",["chicken","bbq","low-carb"],
    ["Marinate chicken in lemon, oregano and garlic; grill on skewers.",
     "Serve with Greek salad and tzatziki."],
    [meat("Chicken thigh fillet",600,"g","chicken","thigh fillet",0.013,0),ing("Lemon",1,"whole","fruit",0.70,0),
     ing("Dried oregano",1,"tsp","spice",0.02,0),garlic(2,0),ing("Tomato",2,"whole","veg",0.60,1),ing("Cucumber",1,"whole","veg",1.00,1),ing("Tzatziki",150,"g","dairy",0.012,1)])
add("Chicken Pot Pie",680,32,54,38,20,45,3,2,"required",["chicken","oven","comfort","freezer-friendly"],
    ["Cook chicken with onion, carrot and peas; thicken with flour, stock and cream.",
     "Top with pastry; bake at 200°C for 25 minutes."],
    [meat("Chicken thigh fillet",600,"g","chicken","thigh fillet",0.013,0),onion(1,0),carrot(1,0),ing("Frozen peas",150,"g","veg",0.004,0),
     ing("Plain flour",30,"g","pantry",0.002,0),ing("Chicken stock",250,"ml","pantry",0.002,0),ing("Thickened cream",100,"ml","dairy",0.008,0),ing("Puff pastry",2,"whole","bakery",1.00,1)])
add("Sticky Chicken Wings with Rice",620,32,58,28,10,40,2,2,"free",["chicken","oven","dairy-free","kid-favourite"],
    ["Toss the wings in soy, honey and garlic; bake at 200°C for 35 minutes.",
     "Serve with rice and steamed greens."],
    [meat("Chicken wings",1000,"g","chicken","wings",0.009,0),ing("Soy sauce",3,"tbsp","sauce",0.06,0),ing("Honey",3,"tbsp","pantry",0.20,0),
     garlic(3,0),rice(300,1),ing("Bok choy",2,"whole","veg",0.80,1)])
add("Chicken Adobo",520,36,42,22,10,45,3,3,"free",["chicken","one-pot","dairy-free","freezer-friendly"],
    ["Simmer the chicken in soy, vinegar, garlic and bay 40 minutes.",
     "Reduce the sauce and serve over rice."],
    [meat("Chicken thigh cutlets",8,"whole","chicken","thigh cutlet",1.00,0),ing("Soy sauce",4,"tbsp","sauce",0.06,0),
     ing("White vinegar",4,"tbsp","pantry",0.02,0),garlic(4,0),ing("Bay leaf",2,"whole","spice",0.05,0),rice(300,1)])
add("Chicken Tortilla Soup",420,30,40,14,15,30,3,4,"free",["soup","chicken","mexican","dairy-free","freezer-friendly"],
    ["Simmer chicken with onion, garlic, tomatoes, corn and stock.",
     "Shred the chicken back in; top with crushed corn chips and lime."],
    [meat("Chicken breast",400,"g","chicken","breast",0.012,0),onion(1,0),garlic(2,0),dicedtom(0),
     ing("Tinned corn",1,"can","pantry",1.20,0),ing("Chicken stock",1000,"ml","pantry",0.002,0),ing("Corn chips",100,"g","pantry",0.012,1),ing("Lime",1,"whole","fruit",0.60,1)])
add("Chicken & Sweetcorn Soup",320,24,34,8,10,20,2,5,"free",["soup","chicken","light","weight-loss","dairy-free","quick"],
    ["Simmer chicken in stock with creamed corn.",
     "Thicken with cornflour; stir in beaten egg in ribbons."],
    [meat("Chicken breast",300,"g","chicken","breast",0.012,0),ing("Creamed corn",1,"can","pantry",1.50,0),
     ing("Chicken stock",1200,"ml","pantry",0.002,0),ing("Cornflour",2,"tbsp","pantry",0.02,1),ing("Egg",2,"whole","dairy",0.40,1)])
add("Coq au Vin",600,38,26,34,20,90,3,3,"free",["chicken","slow-cook","long-cook","freezer-friendly","comfort"],
    ["Brown the chicken and bacon. Cook onion and mushrooms.",
     "Add stock and herbs; simmer 1–1.5 hours. Serve with mash."],
    [meat("Chicken thigh cutlets",8,"whole","chicken","thigh cutlet",1.00,0),meat("Bacon",100,"g","smallgoods","bacon",0.020,0),
     onion(1,1),ing("Button mushrooms",200,"g","veg",0.012,1),ing("Chicken stock",500,"ml","pantry",0.002,2),ing("Thyme",2,"sprig","spice",0.10,2)])
add("Chicken Burgers",640,38,54,30,15,20,1,2,"replaceable",["chicken","kid-favourite"],
    ["Crumb and fry the chicken patties.",
     "Build burgers with buns, lettuce, tomato and mayo; serve with chips."],
    [meat("Chicken breast",600,"g","chicken","breast",0.012,0),ing("Breadcrumbs",100,"g","pantry",0.005,0),ing("Egg",1,"whole","dairy",0.40,0),
     ing("Burger buns",4,"whole","bakery",0.80,1),ing("Lettuce",0.5,"whole","veg",2.00,1),ing("Oven chips",500,"g","veg",0.005,1)])
add("Chicken Meatball Subs",640,34,58,28,20,25,2,2,"required",["chicken","kid-favourite"],
    ["Roll and bake chicken meatballs; simmer in tomato sauce.",
     "Fill sub rolls with meatballs and cheese; grill until melted."],
    [meat("Chicken mince",500,"g","chicken","mince",0.014,0),ing("Breadcrumbs",50,"g","pantry",0.005,0),passata(400,1),
     ing("Sub rolls",4,"whole","bakery",0.90,2),cheese(100,2)])
add("Chicken Fajita Bowls",560,36,58,18,15,20,2,3,"replaceable",["mexican","chicken","rice"],
    ["Cook rice. Sear spiced chicken with capsicum and onion.",
     "Build bowls with rice, chicken, beans, corn and salsa."],
    [meat("Chicken breast",500,"g","chicken","breast",0.012,0),ing("Fajita spice mix",2,"tbsp","spice",0.20,0),capsicum(0),onion(1,0),
     rice(300,0),ing("Tinned black beans",1,"can","pantry",1.10,1),ing("Salsa",150,"g","sauce",0.01,1)])
add("Lemon Chicken (Chinese-Style)",600,34,66,20,15,20,1,3,"free",["chicken","rice","dairy-free","kid-favourite"],
    ["Fry the battered chicken until crisp.",
     "Make a lemon sauce; toss the chicken through. Serve over rice."],
    [meat("Chicken breast",500,"g","chicken","breast",0.012,0),ing("Cornflour",3,"tbsp","pantry",0.02,0),ing("Egg",1,"whole","dairy",0.40,0),
     ing("Lemon",2,"whole","fruit",0.70,1),ing("Sugar",2,"tbsp","pantry",0.03,1),rice(300,1)])

# ---- PORK A ----
add("Pork Ramen",580,30,66,20,15,30,2,3,"free",["soup","pork","noodles","dairy-free"],
    ["Simmer stock with soy, miso, ginger and garlic.",
     "Cook ramen; slice the pork.",
     "Assemble bowls with noodles, broth, pork, egg and greens."],
    [meat("Pork loin",300,"g","pork","loin",0.016,1),ing("Ramen noodles",300,"g","pantry",0.006,1),ing("Chicken stock",1200,"ml","pantry",0.002,0),
     ing("Miso paste",2,"tbsp","sauce",0.10,0),ing("Ginger",1,"tbsp","veg",0.10,0),ing("Egg",2,"whole","dairy",0.40,2),ing("Bok choy",2,"whole","veg",0.80,2)])
add("Char Siu Pork with Rice",600,34,64,22,15,40,2,3,"free",["pork","oven","rice","dairy-free"],
    ["Marinate pork in char siu sauce; roast at 200°C for 35 minutes, glazing.",
     "Slice and serve over rice with greens."],
    [meat("Pork scotch fillet",600,"g","pork","scotch fillet",0.018,0),ing("Char siu sauce",100,"ml","sauce",0.02,0),
     rice(300,1),ing("Bok choy",2,"whole","veg",0.80,1)])
add("Pork Katsu with Rice",680,36,72,28,20,20,1,2,"replaceable",["pork","rice","kid-favourite"],
    ["Crumb and fry the pork; slice.",
     "Serve over rice with katsu sauce and shredded cabbage."],
    [meat("Pork loin steaks",500,"g","pork","loin steak",0.018,0),ing("Panko breadcrumbs",150,"g","pantry",0.006,0),ing("Egg",2,"whole","dairy",0.40,0),
     ing("Plain flour",50,"g","pantry",0.002,0),rice(300,1),ing("Cabbage",0.25,"whole","veg",1.50,1),ing("Tonkatsu sauce",60,"ml","sauce",0.02,1)])
add("Sweet Chilli Pork Stir Fry",520,32,52,18,15,15,1,3,"free",["stir-fry","pork","quick","dairy-free"],
    ["Stir-fry the pork, remove. Stir-fry the vegetables.",
     "Return pork, add sweet chilli and soy; serve over rice."],
    [meat("Pork stir-fry strips",400,"g","pork","stir-fry strips",0.018,0),capsicum(1),ing("Snow peas",150,"g","veg",0.02,1),
     ing("Sweet chilli sauce",3,"tbsp","sauce",0.02,2),ing("Soy sauce",1,"tbsp","sauce",0.06,2),rice(300,0)])
add("Pork Larb with Rice",440,30,32,20,15,15,1,4,"free",["pork","thai","low-carb","dairy-free","quick"],
    ["Fry the pork mince until browned.",
     "Toss with lime, fish sauce, chilli, herbs and shallots. Serve in lettuce or with rice."],
    [meat("Pork mince",500,"g","pork","mince",0.014,0),ing("Lime",1,"whole","fruit",0.60,1),ing("Fish sauce",2,"tbsp","sauce",0.08,1),
     ing("Fresh mint",0.5,"bunch","veg",1.00,1),ing("Iceberg lettuce",1,"whole","veg",2.50,1),rice(200,1)])
add("Pork & Fennel Sausage Pasta",640,28,70,28,10,25,3,3,"replaceable",["pasta","sausage","one-pot","freezer-friendly"],
    ["Brown the sausage meat with fennel seeds.",
     "Add passata and simmer; toss with pasta and parmesan."],
    [meat("Pork & fennel sausages",6,"whole","sausage","pork sausage",0.60,0),ing("Fennel seeds",1,"tsp","spice",0.03,0),
     passata(500,1),ing("Rigatoni",400,"g","pantry",0.004,1),ing("Parmesan, grated",40,"g","dairy",0.03,1,optional=True)])
add("Bacon & Egg Pie",620,26,44,38,20,45,3,2,"required",["smallgoods","oven","comfort","freezer-friendly"],
    ["Line a dish with pastry; fill with bacon and crack in the eggs.",
     "Top with pastry; bake at 200°C for 35 minutes."],
    [meat("Bacon",250,"g","smallgoods","bacon",0.020,0),ing("Egg",6,"whole","dairy",0.40,1),ing("Shortcrust pastry",2,"whole","bakery",1.00,0),ing("Puff pastry",1,"whole","bakery",1.00,1)])
add("Pork Carnitas Tacos",560,32,46,26,15,120,3,3,"free",["mexican","pork","slow-cook","long-cook","dairy-free","freezer-friendly"],
    ["Slow-cook the pork with orange, cumin and garlic until it shreds.",
     "Crisp the pork; serve in tortillas with salsa and lime."],
    [meat("Pork shoulder",1000,"g","pork","shoulder (boneless)",0.011,0),ing("Orange",1,"whole","fruit",0.80,0),ing("Ground cumin",1,"tbsp","spice",0.03,0),
     garlic(3,0),ing("Tortillas",8,"whole","bakery",0.25,1),ing("Salsa",150,"g","sauce",0.01,1),ing("Lime",1,"whole","fruit",0.60,1)])
add("Bangers & Colcannon",620,26,52,34,15,30,2,2,"replaceable",["sausage","comfort","kid-favourite"],
    ["Fry the sausages. Mash the potatoes with cabbage, butter and milk.",
     "Serve sausages over colcannon with gravy."],
    [meat("Thick pork sausages",8,"whole","sausage","pork sausage",0.55,0),ing("Potato",6,"whole","veg",0.40,1),
     ing("Cabbage",0.25,"whole","veg",1.50,1),ing("Butter",30,"g","dairy",0.010,1),ing("Milk",60,"ml","dairy",0.0015,1)])

print("after batch A:", len(R))

# =================================================================== BATCH B
# ---- LAMB B ----
add("Lamb Rogan Josh",620,36,44,30,15,90,3,3,"replaceable",["curry","lamb","slow-cook","long-cook","freezer-friendly"],
    ["Brown the lamb, add rogan josh paste.",
     "Add tomatoes, yoghurt and stock; simmer 1.5 hours. Serve with rice."],
    [meat("Lamb shoulder",700,"g","lamb","shoulder (boneless)",0.017,0),ing("Rogan josh paste",3,"tbsp","sauce",0.30,0),dicedtom(1),
     ing("Natural yoghurt",100,"g","dairy",0.008,1),ing("Beef stock",200,"ml","pantry",0.002,1),rice(300,1)])
add("Lamb Tagine",560,34,48,24,20,90,3,3,"free",["lamb","slow-cook","long-cook","middle-eastern","dairy-free","freezer-friendly"],
    ["Brown the lamb with onion and Moroccan spice.",
     "Add apricots, chickpeas and stock; simmer 1.5 hours. Serve with couscous."],
    [meat("Lamb shoulder",700,"g","lamb","shoulder (boneless)",0.017,0),onion(1,0),ing("Moroccan spice",2,"tbsp","spice",0.20,0),
     ing("Dried apricots",80,"g","pantry",0.02,1),ing("Tinned chickpeas",1,"can","pantry",1.00,1),ing("Couscous",250,"g","pantry",0.006,1)])
add("Slow-Braised Lamb Shanks",620,44,30,36,15,180,3,3,"free",["lamb","slow-cook","long-cook","comfort","freezer-friendly"],
    ["Brown the shanks; cook onion, carrot and garlic.",
     "Add red wine or stock, tomatoes and rosemary; braise 2.5–3 hours. Serve with mash."],
    [meat("Lamb shanks",4,"whole","lamb","shank",3.50,0),onion(1,1),carrot(2,1),garlic(3,1),
     ing("Beef stock",500,"ml","pantry",0.002,2),dicedtom(2),ing("Rosemary",2,"sprig","spice",0.20,2)])
add("Lamb Cutlets with Couscous",560,34,38,28,15,15,1,3,"free",["lamb","quick","dairy-free"],
    ["Grill the lamb cutlets 3 minutes each side.",
     "Prepare couscous; toss with roast vegetables and herbs. Serve with the cutlets."],
    [meat("Lamb cutlets",8,"whole","lamb","cutlet",2.20,0),ing("Couscous",250,"g","pantry",0.006,1),
     ing("Zucchini",1,"whole","veg",0.80,1),capsicum(1),oil(2,1)])
add("Greek Lamb Traybake",620,38,36,36,15,50,2,3,"replaceable",["lamb","tray-bake","one-pan","greek","freezer-friendly"],
    ["Toss lamb, potato, capsicum and onion with lemon, oregano and oil.",
     "Roast at 200°C for 45 minutes. Serve with tzatziki."],
    [meat("Lamb leg",700,"g","lamb","leg (boneless)",0.016,0),ing("Potato",4,"whole","veg",0.40,0),capsicum(0),onion(1,0),
     ing("Lemon",1,"whole","fruit",0.70,0),ing("Dried oregano",1,"tsp","spice",0.02,0),ing("Tzatziki",150,"g","dairy",0.012,1)])
add("Lamb Meatballs in Tomato Sauce",580,32,44,30,20,30,3,3,"replaceable",["lamb","kid-favourite","freezer-friendly"],
    ["Roll spiced lamb meatballs and brown.",
     "Simmer in tomato sauce 15 minutes; serve with couscous or pasta."],
    [meat("Lamb mince",500,"g","lamb","mince",0.018,0),ing("Breadcrumbs",50,"g","pantry",0.005,0),ing("Ground cumin",1,"tsp","spice",0.03,0),
     passata(500,1),ing("Couscous",250,"g","pantry",0.006,2)])
add("Lamb Burgers",620,34,46,32,15,15,1,2,"replaceable",["lamb","bbq","kid-favourite"],
    ["Shape spiced lamb patties and grill.",
     "Build burgers with buns, salad and tzatziki."],
    [meat("Lamb mince",600,"g","lamb","mince",0.018,0),ing("Burger buns",4,"whole","bakery",0.80,1),
     ing("Mixed salad leaves",80,"g","veg",0.02,1),ing("Tzatziki",100,"g","dairy",0.012,1)])
add("Lamb Saag",540,34,30,30,15,60,3,3,"required",["curry","lamb","freezer-friendly"],
    ["Brown the lamb with onion and spice.",
     "Add spinach and a little cream; simmer 45 minutes. Serve with rice."],
    [meat("Lamb shoulder",600,"g","lamb","shoulder (boneless)",0.017,0),onion(1,0),ing("Garam masala",1,"tbsp","spice",0.03,0),
     ing("Frozen spinach",250,"g","veg",0.006,1),ing("Thickened cream",100,"ml","dairy",0.008,1),rice(300,1)])

# ---- FISH & SEAFOOD B ----
add("Salmon Fishcakes",480,28,44,20,20,20,2,3,"replaceable",["fish","salmon","kid-favourite"],
    ["Mix flaked salmon with mashed potato, herbs and egg; shape into cakes.",
     "Crumb and pan-fry until golden. Serve with salad and lemon."],
    [meat("Salmon fillets",400,"g","salmon","fillet",4.50,0),ing("Potato",4,"whole","veg",0.40,0),ing("Egg",1,"whole","dairy",0.40,0),
     ing("Breadcrumbs",100,"g","pantry",0.005,0),ing("Mixed salad leaves",100,"g","veg",0.02,1),ing("Lemon",1,"whole","fruit",0.70,1)])
add("Prawn Laksa",620,30,58,28,15,25,2,3,"free",["soup","fish","noodles","dairy-free"],
    ["Fry laksa paste, add coconut milk and stock.",
     "Add prawns and cook 3 minutes; add noodles and bean sprouts. Serve with lime."],
    [meat("Green prawns",400,"g","fish","prawn",0.030,1),ing("Laksa paste",3,"tbsp","sauce",0.30,0),coconut(0),
     ing("Chicken stock",500,"ml","pantry",0.002,0),ing("Rice noodles",300,"g","pantry",0.006,2),ing("Bean sprouts",100,"g","veg",0.01,2),ing("Lime",1,"whole","fruit",0.60,2)])
add("Prawn Curry",480,28,42,22,15,25,3,4,"free",["curry","fish","dairy-free","freezer-friendly"],
    ["Fry curry paste, add coconut milk and tomatoes.",
     "Add prawns and cook 4 minutes. Serve over rice."],
    [meat("Green prawns",500,"g","fish","prawn",0.030,1),ing("Mild curry paste",2,"tbsp","sauce",0.30,0),coconut(0),dicedtom(0),rice(300,1)])
add("Beer-Battered Fish with Chips",640,32,64,28,15,25,1,2,"replaceable",["fish","kid-favourite"],
    ["Bake the chips. Dip fish in batter and shallow-fry until golden.",
     "Serve with chips, peas and lemon."],
    [meat("White fish fillets",500,"g","fish","white fillet",0.028,0),ing("Self-raising flour",150,"g","pantry",0.002,0),
     ing("Oven chips",750,"g","veg",0.005,1),ing("Frozen peas",200,"g","veg",0.004,1),ing("Lemon",1,"whole","fruit",0.70,1)])
add("Prawn Tacos",500,28,46,22,15,12,1,3,"replaceable",["fish","mexican","quick"],
    ["Pan-fry the prawns with spice.",
     "Fill tortillas with prawns, slaw, avocado and lime."],
    [meat("Green prawns",400,"g","fish","prawn",0.030,0),ing("Taco spice mix",1,"tbsp","spice",0.20,0),
     ing("Tortillas",8,"whole","bakery",0.25,1),ing("Cabbage",0.25,"whole","veg",1.50,1),ing("Avocado",1,"whole","fruit",1.50,1),ing("Lime",1,"whole","fruit",0.60,1)])
add("Seafood Marinara Pasta",600,32,66,20,10,20,1,2,"replaceable",["pasta","fish","quick"],
    ["Cook the pasta. Fry garlic, add marinara mix and cook through.",
     "Add passata and toss with pasta and parsley."],
    [meat("Marinara seafood mix",400,"g","fish","marinara mix",0.026,1),ing("Spaghetti",400,"g","pantry",0.004,0),
     garlic(3,1),passata(400,2),ing("Parsley",0.5,"bunch","veg",1.00,2)])
add("Kedgeree",520,28,60,18,10,25,2,3,"replaceable",["fish","rice","comfort"],
    ["Cook rice with curry powder. Flake the smoked fish.",
     "Fold fish, peas and boiled egg through the rice."],
    [meat("Smoked fish fillets",400,"g","fish","smoked fillet",0.030,1),rice(300,0),ing("Curry powder",1,"tbsp","spice",0.05,0),
     ing("Frozen peas",150,"g","veg",0.004,2),ing("Egg",3,"whole","dairy",0.40,2)])
add("Baked Whole Snapper",420,38,10,26,15,30,1,5,"free",["fish","healthy","low-carb","dairy-free","weight-loss"],
    ["Stuff the snapper with lemon and herbs; bake at 200°C for 25 minutes.",
     "Serve with steamed greens and salad."],
    [meat("Whole snapper",1200,"g","fish","whole snapper",0.020,0),ing("Lemon",2,"whole","fruit",0.70,0),
     ing("Parsley",0.5,"bunch","veg",1.00,0),ing("Broccolini",1,"bunch","veg",2.80,1),oil(2,0)])
add("Prawn Pad Thai",580,30,66,20,20,15,1,3,"free",["fish","noodles","dairy-free"],
    ["Soak the noodles. Stir-fry prawns, push aside and scramble egg.",
     "Add noodles and pad thai sauce; top with peanuts, sprouts and lime."],
    [meat("Green prawns",400,"g","fish","prawn",0.030,0),ing("Rice noodles",300,"g","pantry",0.006,1),ing("Egg",2,"whole","dairy",0.40,0),
     ing("Pad thai sauce",100,"ml","sauce",0.02,1),ing("Peanuts",40,"g","pantry",0.02,2),ing("Bean sprouts",100,"g","veg",0.01,2),ing("Lime",1,"whole","fruit",0.60,2)])
add("Thai Fish Cakes with Rice",500,28,48,20,20,20,2,3,"free",["fish","thai","dairy-free"],
    ["Blend fish with red curry paste and beans; shape and fry.",
     "Serve with rice and sweet chilli sauce."],
    [meat("White fish fillets",500,"g","fish","white fillet",0.028,0),ing("Red curry paste",2,"tbsp","sauce",0.30,0),
     ing("Green beans",100,"g","veg",0.012,0),rice(300,1),ing("Sweet chilli sauce",4,"tbsp","sauce",0.02,1)])
add("Smoked Salmon Pasta",600,30,64,24,10,15,1,2,"required",["pasta","fish","salmon","quick"],
    ["Cook the pasta. Warm cream with lemon and peas.",
     "Fold through smoked salmon and dill; toss with pasta."],
    [meat("Smoked salmon",200,"g","salmon","smoked",0.050,1),ing("Fettuccine",400,"g","pantry",0.005,0),
     ing("Thickened cream",200,"ml","dairy",0.008,1),ing("Frozen peas",100,"g","veg",0.004,1),ing("Lemon",1,"whole","fruit",0.70,1),ing("Dill",0.5,"bunch","veg",1.00,1,optional=True)])
add("Garlic Butter Prawns with Rice",520,28,54,20,10,15,1,3,"required",["fish","rice","quick"],
    ["Cook the rice. Fry prawns in garlic butter with chilli and lemon.",
     "Serve over rice with parsley."],
    [meat("Green prawns",500,"g","fish","prawn",0.030,1),ing("Butter",50,"g","dairy",0.010,1),garlic(4,1),
     ing("Lemon",1,"whole","fruit",0.70,1),rice(300,0),ing("Parsley",0.5,"bunch","veg",1.00,1)])
add("Tuna Pasta Salad",480,24,60,14,15,12,2,3,"replaceable",["pasta","fish","budget","no-fresh-meat","light"],
    ["Cook and cool the pasta.",
     "Toss with tuna, corn, cherry tomatoes, mayo and herbs."],
    [ing("Tinned tuna",2,"can","pantry",1.50,1),ing("Pasta spirals",350,"g","pantry",0.004,0),ing("Tinned corn",1,"can","pantry",1.20,1),
     ing("Cherry tomatoes",200,"g","veg",0.012,1),ing("Whole-egg mayonnaise",4,"tbsp","sauce",0.02,1)])

# ---- VEGETARIAN B ----
add("Chana Masala",400,16,64,10,10,30,3,5,"free",["curry","vegetarian","budget","healthy","weight-loss","dairy-free","freezer-friendly","no-fresh-meat"],
    ["Cook onion, garlic and ginger; add spices.",
     "Add chickpeas and tomatoes; simmer 20 minutes. Serve with rice."],
    [ing("Tinned chickpeas",2,"can","pantry",1.00,1),onion(1,0),garlic(2,0),ing("Ginger",1,"tbsp","veg",0.10,0),
     ing("Garam masala",1,"tbsp","spice",0.03,0),dicedtom(1),rice(300,1)])
add("Palak Paneer",440,20,32,26,15,25,3,4,"required",["curry","vegetarian","freezer-friendly","no-fresh-meat"],
    ["Wilt and blend the spinach. Fry the paneer.",
     "Simmer spinach with spices and cream; fold in paneer. Serve with rice."],
    [ing("Paneer",250,"g","dairy",0.020,0),ing("Frozen spinach",400,"g","veg",0.006,0),onion(1,0),ing("Garam masala",1,"tbsp","spice",0.03,0),
     ing("Thickened cream",100,"ml","dairy",0.008,1),rice(300,1)])
add("Vegetable Biryani",480,12,84,10,20,35,3,4,"replaceable",["rice","vegetarian","freezer-friendly","no-fresh-meat"],
    ["Fry onion and biryani spice; add mixed vegetables.",
     "Layer with par-cooked rice and yoghurt; steam 20 minutes."],
    [ing("Frozen mixed vegetables",400,"g","veg",0.005,0),onion(2,0),ing("Biryani spice",2,"tbsp","spice",0.20,0),
     ing("Basmati rice",350,"g","pantry",0.003,1),ing("Natural yoghurt",100,"g","dairy",0.008,1)])
add("Tofu Pad Thai",520,20,68,18,20,15,1,3,"free",["noodles","vegetarian","dairy-free","no-fresh-meat"],
    ["Soak the noodles. Fry tofu, push aside and scramble egg.",
     "Add noodles and sauce; top with peanuts, sprouts and lime."],
    [ing("Firm tofu",400,"g","pantry",0.010,0),ing("Rice noodles",300,"g","pantry",0.006,1),ing("Egg",2,"whole","dairy",0.40,0),
     ing("Pad thai sauce",100,"ml","sauce",0.02,1),ing("Peanuts",40,"g","pantry",0.02,2),ing("Bean sprouts",100,"g","veg",0.01,2)])
add("Eggplant Parmigiana",480,18,44,26,20,45,3,2,"required",["vegetarian","oven","comfort","freezer-friendly","no-fresh-meat"],
    ["Fry the eggplant slices. Layer with passata and cheese.",
     "Bake at 190°C for 30 minutes. Serve with salad or bread."],
    [ing("Eggplant",2,"whole","veg",1.80,0),passata(500,1),ing("Mozzarella, grated",200,"g","dairy",0.016,1),ing("Parmesan, grated",40,"g","dairy",0.03,1)])
add("Aloo Gobi",360,10,52,12,15,30,3,5,"free",["curry","vegetarian","budget","healthy","weight-loss","dairy-free","no-fresh-meat"],
    ["Fry onion and spices; add potato and cauliflower.",
     "Add a little water; cover and cook 20 minutes. Serve with rice or naan."],
    [ing("Potato",4,"whole","veg",0.40,1),ing("Cauliflower",0.5,"whole","veg",3.00,1),onion(1,0),ing("Curry powder",1,"tbsp","spice",0.05,0),rice(300,1)])
add("Spinach & Ricotta Cannelloni",560,24,54,26,25,40,3,2,"required",["pasta","vegetarian","oven","comfort","freezer-friendly","no-fresh-meat"],
    ["Mix ricotta and spinach; pipe into cannelloni tubes.",
     "Top with passata and cheese; bake at 190°C for 35 minutes."],
    [ing("Cannelloni tubes",250,"g","pantry",0.006,0),ing("Ricotta",500,"g","dairy",0.012,0),ing("Frozen spinach",250,"g","veg",0.006,0),
     passata(500,1),cheese(100,1)])
add("Vegetable Pad See Ew",520,16,74,16,15,15,1,3,"free",["noodles","vegetarian","dairy-free","no-fresh-meat"],
    ["Stir-fry the vegetables in a hot wok.",
     "Add wide noodles, soy and oyster-style sauce; char slightly and serve."],
    [ing("Fresh rice noodles",400,"g","pantry",0.006,1),ing("Broccoli",1,"whole","veg",2.50,0),carrot(1,0),
     ing("Soy sauce",3,"tbsp","sauce",0.06,1),ing("Egg",2,"whole","dairy",0.40,1)])
add("Sweet Potato & Black Bean Tacos",480,16,74,14,15,25,2,4,"free",["mexican","vegetarian","healthy","dairy-free","no-fresh-meat"],
    ["Roast the diced sweet potato with spice.",
     "Warm the black beans; fill tortillas with both, avocado and lime."],
    [ing("Sweet potato",600,"g","veg",0.004,0),ing("Taco spice mix",1,"tbsp","spice",0.20,0),ing("Tinned black beans",2,"can","pantry",1.10,1),
     ing("Tortillas",8,"whole","bakery",0.25,1),ing("Avocado",1,"whole","fruit",1.50,1),ing("Lime",1,"whole","fruit",0.60,1)])
add("Vegetable Korma",480,14,58,22,15,30,3,3,"required",["curry","vegetarian","freezer-friendly","no-fresh-meat"],
    ["Fry onion and korma paste; add mixed vegetables.",
     "Add cream and simmer 20 minutes. Serve with rice."],
    [ing("Frozen mixed vegetables",400,"g","veg",0.005,0),onion(1,0),ing("Korma paste",2,"tbsp","sauce",0.30,0),
     ing("Thickened cream",150,"ml","dairy",0.008,1),rice(300,1)])
add("Butter Bean & Tomato Stew",360,16,52,10,10,25,3,5,"free",["vegetarian","budget","healthy","weight-loss","dairy-free","freezer-friendly","no-fresh-meat"],
    ["Cook onion, garlic and capsicum; add smoked paprika.",
     "Add butter beans and tomatoes; simmer 20 minutes. Serve with bread."],
    [ing("Tinned butter beans",2,"can","pantry",1.00,1),onion(1,0),garlic(2,0),capsicum(0),
     ing("Smoked paprika",1,"tsp","spice",0.03,0),dicedtom(1),ing("Crusty bread",1,"whole","bakery",3.50,1)])
add("Pumpkin Soup with Bread",300,8,44,10,10,30,3,5,"replaceable",["soup","vegetarian","light","weight-loss","budget","freezer-friendly","no-fresh-meat"],
    ["Cook onion and garlic; add pumpkin, potato and stock.",
     "Simmer 25 minutes and blend; stir in a little cream. Serve with bread."],
    [ing("Pumpkin",800,"g","veg",0.004,0),ing("Potato",2,"whole","veg",0.40,0),onion(1,0),garlic(2,0),
     ing("Vegetable stock",1000,"ml","pantry",0.002,1),ing("Thickened cream",100,"ml","dairy",0.008,1,optional=True),ing("Crusty bread",1,"whole","bakery",3.50,1)])
add("Caprese Pasta",520,18,74,16,10,15,1,3,"required",["pasta","vegetarian","quick","no-fresh-meat"],
    ["Cook the pasta. Toss with cherry tomatoes, torn mozzarella and basil.",
     "Finish with olive oil and a splash of balsamic."],
    [ing("Penne",400,"g","pantry",0.004,0),ing("Cherry tomatoes",250,"g","veg",0.012,1),ing("Fresh mozzarella",200,"g","dairy",0.020,1),
     ing("Basil",0.5,"bunch","veg",1.50,1),oil(2,1)])
add("Roasted Vegetable Pasta",480,14,74,14,15,30,2,4,"replaceable",["pasta","vegetarian","healthy","no-fresh-meat"],
    ["Roast capsicum, zucchini, eggplant and onion.",
     "Toss with pasta, passata and basil."],
    [ing("Penne",400,"g","pantry",0.004,0),capsicum(0),ing("Zucchini",1,"whole","veg",0.80,0),ing("Eggplant",1,"whole","veg",1.80,0),
     onion(1,0),passata(400,1),ing("Basil",0.5,"bunch","veg",1.50,1)])
add("Tofu Katsu Curry",560,20,78,18,20,25,2,3,"free",["vegetarian","rice","dairy-free","no-fresh-meat"],
    ["Crumb and fry the tofu. Make a katsu curry sauce.",
     "Serve tofu over rice with the sauce."],
    [ing("Firm tofu",400,"g","pantry",0.010,0),ing("Panko breadcrumbs",150,"g","pantry",0.006,0),ing("Plain flour",50,"g","pantry",0.002,0),
     onion(1,1),carrot(1,1),ing("Curry powder",1,"tbsp","spice",0.05,1),rice(300,2)])
add("Zucchini & Cheese Slice",380,18,24,24,15,40,3,3,"required",["vegetarian","oven","kid-favourite","no-fresh-meat"],
    ["Mix grated zucchini, eggs, flour, cheese and onion.",
     "Bake at 180°C for 35 minutes. Serve with salad."],
    [ing("Zucchini",3,"whole","veg",0.80,0),ing("Egg",5,"whole","dairy",0.40,0),ing("Self-raising flour",150,"g","pantry",0.002,0),
     cheese(150,0),onion(1,0),ing("Mixed salad leaves",100,"g","veg",0.02,1)])
add("Spanish Omelette",420,18,36,24,15,30,2,4,"required",["vegetarian","low-carb","one-pan","no-fresh-meat"],
    ["Slowly cook sliced potato and onion in oil until soft.",
     "Add beaten eggs; cook, then flip and finish. Serve with salad."],
    [ing("Potato",4,"whole","veg",0.40,0),onion(1,0),ing("Egg",8,"whole","dairy",0.40,1),oil(3,0),ing("Mixed salad leaves",100,"g","veg",0.02,1)])
add("Baked Gnocchi with Vegetables",560,18,80,18,15,30,3,3,"required",["pasta","vegetarian","oven","comfort","no-fresh-meat"],
    ["Toss gnocchi with a tomato-vegetable sauce.",
     "Top with mozzarella; bake at 200°C for 20 minutes."],
    [ing("Gnocchi",500,"g","pantry",0.006,0),passata(500,0),ing("Zucchini",1,"whole","veg",0.80,0),capsicum(0),
     ing("Mozzarella, grated",150,"g","dairy",0.016,1)])
add("Dal Makhani",420,18,56,14,15,40,3,4,"required",["curry","vegetarian","freezer-friendly","no-fresh-meat"],
    ["Simmer lentils with tomato, ginger and garlic until soft.",
     "Stir in butter and a little cream. Serve with rice or naan."],
    [ing("Tinned brown lentils",2,"can","pantry",1.00,0),dicedtom(0),ing("Ginger",1,"tbsp","veg",0.10,0),garlic(2,0),
     ing("Butter",30,"g","dairy",0.010,1),ing("Thickened cream",80,"ml","dairy",0.008,1),rice(300,1)])

# ---- PIZZA / MISC B ----
add("Margherita Pizza",620,24,80,22,15,15,1,2,"required",["pizza","vegetarian","fun","kid-favourite","no-fresh-meat"],
    ["Spread bases with passata; top with mozzarella and basil.",
     "Bake at 220°C for 12–15 minutes."],
    [ing("Pizza bases",2,"whole","bakery",2.50,0),passata(150,0),ing("Fresh mozzarella",200,"g","dairy",0.020,0),ing("Basil",0.5,"bunch","veg",1.50,1)])
add("BBQ Chicken Pizza",700,34,78,26,15,15,1,2,"required",["pizza","chicken","fun","kid-favourite"],
    ["Spread bases with barbecue sauce; top with cooked chicken, onion and cheese.",
     "Bake at 220°C for 12–15 minutes."],
    [meat("Chicken breast",300,"g","chicken","breast",0.012,0),ing("Pizza bases",2,"whole","bakery",2.50,0),
     ing("Barbecue sauce",80,"ml","sauce",0.01,0),ing("Red onion",1,"whole","veg",0.55,0),ing("Mozzarella, grated",200,"g","dairy",0.016,1)])
add("Ham & Pineapple Pizza",680,28,80,24,10,15,1,2,"required",["pizza","smallgoods","fun","kid-favourite"],
    ["Spread bases with passata; top with ham, pineapple and cheese.",
     "Bake at 220°C for 12–15 minutes."],
    [meat("Sliced ham",150,"g","smallgoods","sliced ham",0.024,0),ing("Pizza bases",2,"whole","bakery",2.50,0),
     passata(150,0),ing("Tinned pineapple",1,"can","pantry",1.50,0),ing("Mozzarella, grated",200,"g","dairy",0.016,1)])
add("Vegetable Quesadillas",520,18,58,22,10,15,1,3,"required",["mexican","vegetarian","quick","kid-favourite","no-fresh-meat"],
    ["Cook capsicum, corn and beans with spice.",
     "Fill tortillas with the mix and cheese; toast until golden."],
    [ing("Tortillas",8,"whole","bakery",0.25,1),capsicum(0),ing("Tinned corn",1,"can","pantry",1.20,0),
     ing("Tinned black beans",1,"can","pantry",1.10,0),cheese(200,1)])
add("Loaded Vegetable Nachos",600,20,64,28,10,20,1,2,"required",["mexican","vegetarian","kid-favourite","no-fresh-meat"],
    ["Warm beans with spice. Spread corn chips on a tray.",
     "Top with beans and cheese; bake 8 minutes. Add tomato and avocado."],
    [ing("Corn chips",250,"g","pantry",0.012,0),ing("Tinned kidney beans",2,"can","pantry",1.10,0),ing("Taco spice mix",1,"tbsp","spice",0.20,0),
     cheese(150,1),ing("Tomato",2,"whole","veg",0.60,1),ing("Avocado",1,"whole","fruit",1.50,1)])
add("Sausage Rolls with Salad",620,22,52,36,15,30,2,2,"required",["sausage","oven","kid-favourite"],
    ["Roll seasoned sausage mince in puff pastry; slice and bake at 200°C for 25 minutes.",
     "Serve with a garden salad and sauce."],
    [meat("Sausage mince",500,"g","sausage","sausage mince",0.014,0),ing("Puff pastry",3,"whole","bakery",1.00,0),
     ing("Breadcrumbs",50,"g","pantry",0.005,0),ing("Mixed salad leaves",100,"g","veg",0.02,1),ing("Tomato sauce",3,"tbsp","sauce",0.02,1)])
add("Fried Egg Rice Bowl",380,14,62,8,5,15,1,4,"free",["rice","vegetarian","quick","budget","uses-leftovers","dairy-free","no-fresh-meat"],
    ["Reheat rice with soy and sesame.",
     "Top each bowl with a fried egg, spring onion and chilli sauce."],
    [rice(350,0),ing("Egg",4,"whole","dairy",0.40,1),ing("Soy sauce",2,"tbsp","sauce",0.06,0),
     ing("Spring onion",2,"whole","veg",0.30,1),ing("Chilli sauce",1,"tbsp","sauce",0.02,1)])
add("Minute Steak with Salad",420,38,12,26,5,10,1,5,"free",["beef","quick","low-carb","dairy-free","high-protein"],
    ["Sear the minute steaks 1–2 minutes each side.",
     "Serve with a big garden salad and mustard."],
    [meat("Beef minute steaks",600,"g","beef","minute steak",0.028,0),ing("Mixed salad leaves",200,"g","veg",0.02,1),
     ing("Tomato",2,"whole","veg",0.60,1),ing("Cucumber",1,"whole","veg",1.00,1),ing("Dijon mustard",1,"tbsp","sauce",0.10,1)])
add("Chicken Caesar Wraps",560,34,46,26,10,15,1,3,"required",["chicken","quick","kid-favourite"],
    ["Grill and slice the chicken.",
     "Fill wraps with cos, chicken, caesar dressing and parmesan."],
    [meat("Chicken breast",500,"g","chicken","breast",0.012,0),ing("Tortillas",4,"whole","bakery",0.25,1),
     ing("Cos lettuce",1,"whole","veg",2.50,1),ing("Caesar dressing",80,"ml","sauce",0.02,1),ing("Parmesan, grated",40,"g","dairy",0.03,1)])

# =================================================================== BATCH C
add("Beef Stir Fry with Black Bean Sauce",540,32,52,18,10,15,1,3,"free",["stir-fry","beef","quick","dairy-free"],
    ["Stir-fry the beef, remove. Stir-fry capsicum and onion.",
     "Return beef, add black bean sauce; toss and serve over rice."],
    [meat("Beef strips",400,"g","beef","stir-fry strips",0.022,0),capsicum(1),onion(1,1),
     ing("Black bean sauce",3,"tbsp","sauce",0.10,2),rice(300,0)])
add("Chicken Cordon Bleu",700,42,44,38,20,30,1,2,"required",["chicken","oven","kid-favourite"],
    ["Stuff chicken with ham and cheese; crumb and bake at 200°C for 25 minutes.",
     "Serve with mash and greens."],
    [meat("Chicken breast",600,"g","chicken","breast",0.012,0),meat("Sliced ham",80,"g","smallgoods","sliced ham",0.024,0),
     cheese(100,0),ing("Breadcrumbs",150,"g","pantry",0.005,0),ing("Egg",2,"whole","dairy",0.40,0),ing("Potato",4,"whole","veg",0.40,1)])
add("Chicken Enchiladas",650,34,58,30,20,30,2,2,"required",["mexican","chicken","oven","freezer-friendly"],
    ["Cook and shred chicken with spice; roll in tortillas.",
     "Top with tomato sauce and cheese; bake at 200°C for 20 minutes."],
    [meat("Chicken thigh fillet",500,"g","chicken","thigh fillet",0.013,0),ing("Taco spice mix",2,"tbsp","spice",0.20,0),
     ing("Tortillas",8,"whole","bakery",0.25,1),dicedtom(1),cheese(150,1)])
add("Butter Chicken Meatballs",680,34,60,32,20,30,3,2,"required",["chicken","curry","kid-favourite","freezer-friendly"],
    ["Roll and bake chicken meatballs.",
     "Simmer in butter chicken sauce; serve over rice."],
    [meat("Chicken mince",500,"g","chicken","mince",0.014,0),ing("Breadcrumbs",50,"g","pantry",0.005,0),
     ing("Butter chicken paste",2,"tbsp","sauce",0.30,1),passata(300,1),coconut(1),rice(300,1)])
add("Pork Belly with Greens",640,30,20,50,15,120,2,2,"free",["pork","slow-cook","long-cook","low-carb","dairy-free"],
    ["Slow-roast the scored pork belly until crisp.",
     "Rest and slice; serve with stir-fried Asian greens."],
    [meat("Pork belly",800,"g","pork","belly",0.016,0),ing("Bok choy",3,"whole","veg",0.80,1),
     ing("Soy sauce",2,"tbsp","sauce",0.06,1),garlic(2,1)])
add("Honey Mustard Pork Steaks",460,34,24,26,10,20,1,3,"free",["pork","quick","dairy-free"],
    ["Pan-fry the pork steaks; rest.",
     "Make a honey-mustard pan sauce; serve with roast vegetables."],
    [meat("Pork loin steaks",500,"g","pork","loin steak",0.018,0),ing("Honey",2,"tbsp","pantry",0.20,1),
     ing("Wholegrain mustard",2,"tbsp","sauce",0.10,1),ing("Potato",3,"whole","veg",0.40,0),carrot(2,0)])
add("Salmon Poke Bowl",560,34,58,20,15,15,1,4,"free",["fish","salmon","healthy","rice","dairy-free","high-protein"],
    ["Cook and cool the rice. Cube the salmon and toss with soy and sesame.",
     "Build bowls with rice, salmon, avocado, cucumber and edamame."],
    [meat("Salmon fillets",400,"g","salmon","fillet",4.50,1),rice(300,0),ing("Avocado",1,"whole","fruit",1.50,1),
     ing("Cucumber",1,"whole","veg",1.00,1),ing("Edamame",150,"g","veg",0.012,1),ing("Soy sauce",2,"tbsp","sauce",0.06,1)])
add("Fish Burritos",560,30,60,20,15,20,1,3,"replaceable",["fish","mexican"],
    ["Cook rice. Pan-fry spiced fish and flake.",
     "Fill tortillas with rice, fish, beans, salsa and cheese; roll and toast."],
    [meat("White fish fillets",500,"g","fish","white fillet",0.028,0),ing("Taco spice mix",1,"tbsp","spice",0.20,0),rice(250,0),
     ing("Tinned black beans",1,"can","pantry",1.10,1),ing("Tortillas",8,"whole","bakery",0.25,1),ing("Salsa",150,"g","sauce",0.01,1)])
add("Mushroom Stroganoff",460,14,58,18,10,25,2,3,"required",["vegetarian","pasta","comfort","no-fresh-meat"],
    ["Cook onion and mushrooms; add stock and mustard.",
     "Stir in sour cream; serve over pasta."],
    [ing("Button mushrooms",400,"g","veg",0.012,0),onion(1,0),ing("Vegetable stock",250,"ml","pantry",0.002,0),
     ing("Dijon mustard",1,"tbsp","sauce",0.10,0),ing("Sour cream",150,"g","dairy",0.010,1),ing("Fettuccine",350,"g","pantry",0.005,1)])
add("Vegetable Jalfrezi",380,12,58,10,15,25,3,5,"free",["curry","vegetarian","healthy","weight-loss","dairy-free","no-fresh-meat"],
    ["Fry onion, capsicum and spices.",
     "Add mixed vegetables and tomatoes; simmer 20 minutes. Serve with rice."],
    [ing("Frozen mixed vegetables",400,"g","veg",0.005,0),onion(1,0),capsicum(0),ing("Curry powder",1,"tbsp","spice",0.05,0),
     dicedtom(1),rice(300,1)])
add("Halloumi & Salad Wraps",480,20,52,22,10,10,1,3,"required",["vegetarian","quick","kid-favourite","no-fresh-meat"],
    ["Pan-fry the halloumi slices.",
     "Fill wraps with halloumi, salad and hummus."],
    [ing("Halloumi",250,"g","dairy",0.030,0),ing("Tortillas",4,"whole","bakery",0.25,1),
     ing("Mixed salad leaves",100,"g","veg",0.02,1),ing("Hummus",150,"g","sauce",0.012,1)])
add("Pea & Ham Soup",360,22,44,8,15,60,3,4,"free",["soup","smallgoods","budget","dairy-free","freezer-friendly"],
    ["Simmer split peas with a ham hock, onion and carrot 50 minutes.",
     "Shred the ham back in; season and serve with bread."],
    [meat("Ham hock",600,"g","smallgoods","ham hock",0.012,0),ing("Split peas",300,"g","pantry",0.004,0),onion(1,0),carrot(2,0),
     ing("Crusty bread",1,"whole","bakery",3.50,1)])
add("Beef Kofta Curry",600,34,42,32,20,35,3,3,"replaceable",["curry","beef","freezer-friendly"],
    ["Roll spiced beef koftas and brown.",
     "Simmer in a tomato-yoghurt curry sauce 20 minutes; serve with rice."],
    [meat("Beef mince",500,"g","beef","mince",0.016,0),ing("Garam masala",1,"tbsp","spice",0.03,0),onion(1,1),
     dicedtom(1),ing("Natural yoghurt",100,"g","dairy",0.008,1),rice(300,1)])
add("Teriyaki Tofu Bowl",480,20,64,14,15,20,1,4,"free",["vegetarian","rice","dairy-free","no-fresh-meat"],
    ["Fry the tofu until golden; glaze with teriyaki.",
     "Serve over rice with steamed broccoli and sesame."],
    [ing("Firm tofu",400,"g","pantry",0.010,0),ing("Teriyaki sauce",4,"tbsp","sauce",0.10,0),rice(300,1),broccoli(1)])

print("after batch C:", len(R))

# =================================================================== BATCH D — WEIGHT LOSS (25)
add("Grilled Chicken & Garden Salad",360,40,14,16,10,15,1,5,"free",["chicken","salad","weight-loss","low-carb","dairy-free","high-protein"],
    ["Grill the chicken breast and slice.","Toss leaves, cucumber, tomato and onion with lemon and oil; top with chicken."],
    [meat("Chicken breast",500,"g","chicken","breast",0.012,0),ing("Mixed salad leaves",150,"g","veg",0.02,1),ing("Cucumber",1,"whole","veg",1.00,1),ing("Tomato",2,"whole","veg",0.60,1),ing("Lemon",1,"whole","fruit",0.70,1),oil(1,1)])
add("Lemon Garlic Prawn Salad",320,32,12,16,10,10,1,5,"free",["fish","salad","weight-loss","low-carb","dairy-free","high-protein"],
    ["Pan-fry prawns with garlic and lemon.","Serve over leaves, avocado and cherry tomatoes."],
    [meat("Green prawns",400,"g","fish","prawn",0.030,0),garlic(2,0),ing("Lemon",1,"whole","fruit",0.70,0),ing("Mixed salad leaves",150,"g","veg",0.02,1),ing("Avocado",0.5,"whole","fruit",1.50,1),ing("Cherry tomatoes",150,"g","veg",0.012,1)])
add("Zucchini Noodle Chicken Stir Fry",340,34,18,14,15,15,1,5,"free",["chicken","stir-fry","weight-loss","low-carb","dairy-free","high-protein"],
    ["Stir-fry chicken strips, remove.","Stir-fry zucchini noodles and capsicum 3 minutes; return chicken with soy and garlic."],
    [meat("Chicken breast",450,"g","chicken","breast",0.012,0),ing("Zucchini",3,"whole","veg",0.80,1),capsicum(1),ing("Soy sauce",2,"tbsp","sauce",0.06,1),garlic(2,1),voil(1,0)])
add("Steamed Fish with Asian Greens",320,36,10,14,10,15,1,5,"free",["fish","healthy","weight-loss","low-carb","dairy-free","high-protein"],
    ["Steam the fish with ginger and soy.","Steam bok choy and gai lan; serve with the fish and a drizzle of sesame oil."],
    [meat("White fish fillets",500,"g","fish","white fillet",0.028,0),ing("Ginger",1,"tbsp","veg",0.10,0),ing("Soy sauce",2,"tbsp","sauce",0.06,0),ing("Bok choy",3,"whole","veg",0.80,1),ing("Sesame oil",1,"tsp","pantry",0.05,1)])
add("Chicken & Cabbage Stir Fry",340,32,20,14,10,15,1,4,"free",["chicken","stir-fry","weight-loss","budget","dairy-free","high-protein"],
    ["Stir-fry chicken, remove.","Stir-fry shredded cabbage and carrot; return chicken with soy and sesame."],
    [meat("Chicken breast",450,"g","chicken","breast",0.012,0),ing("Cabbage",0.5,"whole","veg",1.50,1),carrot(1,1),ing("Soy sauce",2,"tbsp","sauce",0.06,1),voil(1,0)])
add("Vegetable & White Bean Soup",300,14,44,6,10,25,3,5,"free",["soup","vegetarian","weight-loss","budget","dairy-free","freezer-friendly","no-fresh-meat"],
    ["Cook onion, carrot and celery.","Add stock, tomatoes and cannellini beans; simmer 20 minutes with spinach."],
    [onion(1,0),carrot(2,0),ing("Celery",2,"whole","veg",0.40,0),ing("Vegetable stock",1200,"ml","pantry",0.002,1),dicedtom(1),ing("Tinned cannellini beans",1,"can","pantry",1.00,1),ing("Baby spinach",80,"g","veg",0.02,1)])
add("Tuna Salad Lettuce Cups",300,28,14,14,10,10,1,5,"free",["fish","salad","weight-loss","low-carb","budget","dairy-free","no-fresh-meat","high-protein"],
    ["Mix tuna with corn, red onion and a little olive oil and lemon.","Spoon into baby cos lettuce cups."],
    [ing("Tinned tuna",2,"can","pantry",1.50,0),ing("Tinned corn",1,"can","pantry",1.20,0),ing("Red onion",0.5,"whole","veg",0.55,0),ing("Baby cos lettuce",1,"whole","veg",2.00,1),ing("Lemon",1,"whole","fruit",0.70,0)])
add("Cauliflower Rice Chicken Bowl",360,36,20,16,15,20,1,5,"free",["chicken","weight-loss","low-carb","dairy-free","high-protein"],
    ["Pan-fry chicken with spice. Pulse cauliflower and stir-fry as rice.",
     "Build bowls with cauli-rice, chicken, avocado and tomato."],
    [meat("Chicken thigh fillet",500,"g","chicken","thigh fillet",0.013,0),ing("Cauliflower",1,"whole","veg",3.00,1),ing("Avocado",0.5,"whole","fruit",1.50,2),ing("Tomato",1,"whole","veg",0.60,2),ing("Mixed spice",1,"tbsp","spice",0.10,0)])
add("Miso Grilled Salmon with Greens",420,34,16,24,10,15,1,4,"free",["fish","salmon","healthy","weight-loss","dairy-free","high-protein"],
    ["Brush salmon with miso and grill.","Steam broccolini and edamame; serve alongside."],
    [meat("Salmon fillets",4,"whole","salmon","fillet",4.50,0),ing("Miso paste",2,"tbsp","sauce",0.10,0),ing("Broccolini",1,"bunch","veg",2.80,1),ing("Edamame",150,"g","veg",0.012,1)])
add("Poached Chicken & Slaw",340,36,16,14,15,20,2,5,"free",["chicken","weight-loss","low-carb","dairy-free","high-protein"],
    ["Poach the chicken, then shred.","Toss cabbage, carrot and herbs with a light dressing; combine with chicken."],
    [meat("Chicken breast",500,"g","chicken","breast",0.012,0),ing("Cabbage",0.25,"whole","veg",1.50,1),carrot(1,1),ing("Fresh mint",0.5,"bunch","veg",1.00,1),ing("Lime",1,"whole","fruit",0.60,1)])
add("Prawn & Vegetable Skewers",300,28,14,14,20,12,1,5,"free",["fish","bbq","weight-loss","low-carb","dairy-free","high-protein"],
    ["Thread prawns, capsicum and zucchini onto skewers.","Grill 8 minutes, brushing with garlic and oil. Serve with salad."],
    [meat("Green prawns",400,"g","fish","prawn",0.030,0),capsicum(0),ing("Zucchini",1,"whole","veg",0.80,0),garlic(2,1),ing("Mixed salad leaves",100,"g","veg",0.02,1)])
add("Spiced Chickpea & Spinach Stew",340,14,50,8,10,25,3,5,"free",["vegetarian","weight-loss","budget","dairy-free","freezer-friendly","no-fresh-meat"],
    ["Cook onion, garlic and spices.","Add chickpeas and tomatoes; simmer 15 minutes with spinach."],
    [ing("Tinned chickpeas",2,"can","pantry",1.00,1),onion(1,0),garlic(2,0),ing("Ground cumin",1,"tsp","spice",0.03,0),dicedtom(1),ing("Baby spinach",100,"g","veg",0.02,1)])
add("Grilled Fish Lettuce Tacos",320,30,16,14,15,12,1,5,"free",["fish","mexican","weight-loss","low-carb","dairy-free","high-protein"],
    ["Pan-fry spiced fish and flake.","Serve in lettuce cups with slaw, avocado and lime."],
    [meat("White fish fillets",450,"g","fish","white fillet",0.028,0),ing("Taco spice mix",1,"tbsp","spice",0.20,0),ing("Iceberg lettuce",1,"whole","veg",2.50,1),ing("Cabbage",0.25,"whole","veg",1.50,1),ing("Lime",1,"whole","fruit",0.60,1)])
add("Chicken Zoodle Soup",320,30,20,12,15,30,3,5,"free",["soup","chicken","weight-loss","low-carb","dairy-free","freezer-friendly","high-protein"],
    ["Simmer chicken in stock with carrot and celery.","Add zucchini noodles at the end; season and serve."],
    [meat("Chicken breast",400,"g","chicken","breast",0.012,0),ing("Chicken stock",1500,"ml","pantry",0.002,0),carrot(2,0),ing("Celery",2,"whole","veg",0.40,0),ing("Zucchini",2,"whole","veg",0.80,1)])
add("Roasted Vegetable & Lentil Salad",380,16,54,10,15,30,3,5,"free",["vegetarian","salad","weight-loss","dairy-free","no-fresh-meat"],
    ["Roast pumpkin, capsicum and red onion.","Toss with lentils, rocket and a lemon dressing."],
    [ing("Pumpkin",400,"g","veg",0.004,0),capsicum(0),ing("Red onion",1,"whole","veg",0.55,0),ing("Tinned brown lentils",1,"can","pantry",1.00,1),ing("Rocket",60,"g","veg",0.03,1),ing("Lemon",1,"whole","fruit",0.70,1)])
add("Baked Cod with Ratatouille",340,34,18,14,15,35,2,5,"free",["fish","healthy","weight-loss","low-carb","dairy-free","freezer-friendly","high-protein"],
    ["Simmer eggplant, zucchini, capsicum and tomatoes into a ratatouille.","Bake the cod on top 15 minutes."],
    [meat("Cod fillets",500,"g","fish","cod fillet",0.030,1),ing("Eggplant",1,"whole","veg",1.80,0),ing("Zucchini",1,"whole","veg",0.80,0),capsicum(0),dicedtom(0)])
add("Vietnamese Chicken Salad",360,32,26,14,20,15,1,5,"free",["chicken","salad","weight-loss","dairy-free","high-protein"],
    ["Poach and shred chicken.","Toss with cabbage, carrot, herbs and a nuoc cham dressing; top with peanuts."],
    [meat("Chicken breast",450,"g","chicken","breast",0.012,0),ing("Cabbage",0.25,"whole","veg",1.50,1),carrot(1,1),ing("Fresh mint",0.5,"bunch","veg",1.00,1),ing("Fish sauce",1,"tbsp","sauce",0.08,1),ing("Peanuts",30,"g","pantry",0.02,1)])
add("Mushroom & Spinach Omelette",320,22,8,22,10,15,1,4,"free",["vegetarian","weight-loss","low-carb","dairy-free","no-fresh-meat","high-protein"],
    ["Cook mushrooms and spinach.","Pour over beaten eggs; fold and serve with salad."],
    [ing("Egg",6,"whole","dairy",0.40,1),ing("Button mushrooms",150,"g","veg",0.012,0),ing("Baby spinach",80,"g","veg",0.02,0),ing("Mixed salad leaves",100,"g","veg",0.02,1)])
add("Chicken San Choy Bau",360,34,16,18,15,15,1,4,"free",["chicken","quick","weight-loss","low-carb","dairy-free","high-protein"],
    ["Stir-fry chicken mince with garlic and water chestnuts.","Season with hoisin and soy; spoon into lettuce cups."],
    [meat("Chicken mince",500,"g","chicken","mince",0.014,0),garlic(2,0),ing("Tinned water chestnuts",1,"can","pantry",1.50,0),ing("Hoisin sauce",2,"tbsp","sauce",0.12,1),ing("Iceberg lettuce",1,"whole","veg",2.50,1)])
add("Cabbage & Chicken Rice-Paper Rolls",320,26,34,8,25,10,1,5,"free",["chicken","weight-loss","dairy-free","high-protein"],
    ["Poach and slice chicken.","Roll with rice paper, lettuce, carrot, cucumber and herbs; serve with dipping sauce."],
    [meat("Chicken breast",400,"g","chicken","breast",0.012,0),ing("Rice paper",12,"whole","pantry",0.10,1),ing("Carrot",1,"whole","veg",0.30,1),ing("Cucumber",1,"whole","veg",1.00,1),ing("Hoisin sauce",2,"tbsp","sauce",0.12,1)])
add("Grilled Chicken with Cauliflower Mash",360,38,18,16,15,25,2,5,"free",["chicken","weight-loss","low-carb","dairy-free","high-protein"],
    ["Steam and blend cauliflower with a splash of stock for mash.","Grill the chicken; serve with mash and greens."],
    [meat("Chicken breast",500,"g","chicken","breast",0.012,0),ing("Cauliflower",1,"whole","veg",3.00,0),ing("Vegetable stock",100,"ml","pantry",0.002,0),ing("Green beans",200,"g","veg",0.012,1)])
add("Prawn & Zucchini Stir Fry",320,30,16,14,10,12,1,5,"free",["fish","stir-fry","weight-loss","low-carb","dairy-free","high-protein"],
    ["Stir-fry prawns, remove.","Stir-fry zucchini and capsicum; return prawns with garlic and soy."],
    [meat("Green prawns",400,"g","fish","prawn",0.030,0),ing("Zucchini",2,"whole","veg",0.80,1),capsicum(1),garlic(2,1),ing("Soy sauce",2,"tbsp","sauce",0.06,1),voil(1,0)])
add("Chicken & Broccoli Soup",320,30,18,14,10,25,3,5,"free",["soup","chicken","weight-loss","low-carb","dairy-free","freezer-friendly","high-protein"],
    ["Simmer chicken in stock with onion and broccoli.","Blend half for body; return shredded chicken."],
    [meat("Chicken breast",400,"g","chicken","breast",0.012,0),ing("Chicken stock",1500,"ml","pantry",0.002,0),onion(1,0),broccoli(0)])
add("Baked Salmon with Asparagus",420,34,10,26,10,20,1,5,"free",["fish","salmon","healthy","weight-loss","low-carb","dairy-free","high-protein"],
    ["Roast salmon and asparagus with lemon and oil 15 minutes.","Serve with a green salad."],
    [meat("Salmon fillets",4,"whole","salmon","fillet",4.50,0),ing("Asparagus",2,"bunch","veg",3.50,0),ing("Lemon",1,"whole","fruit",0.70,0),ing("Mixed salad leaves",100,"g","veg",0.02,1),oil(1,0)])
add("Mixed Bean & Vegetable Chilli",360,16,58,6,10,25,3,5,"free",["vegetarian","mexican","weight-loss","budget","dairy-free","freezer-friendly","no-fresh-meat"],
    ["Cook onion, garlic and capsicum with chilli spice.","Add mixed beans and tomatoes; simmer 20 minutes. Serve with rice or lettuce."],
    [onion(1,0),garlic(2,0),capsicum(0),ing("Mild chilli spice",1,"tbsp","spice",0.15,0),ing("Tinned mixed beans",2,"can","pantry",1.10,1),dicedtom(1)])
print("after batch D:", len(R))

# =================================================================== BATCH E — HIGH PROTEIN (25)
add("Steak & Eggs",560,44,8,38,5,15,1,4,"free",["beef","high-protein","low-carb","dairy-free"],
    ["Sear the steaks to your liking; rest.","Fry the eggs; serve with grilled tomato and spinach."],
    [meat("Beef porterhouse steaks",600,"g","beef","porterhouse steak",0.030,0),ing("Egg",4,"whole","dairy",0.40,1),ing("Tomato",2,"whole","veg",0.60,1),ing("Baby spinach",80,"g","veg",0.02,1)])
add("Chicken & Quinoa Power Bowl",520,44,44,18,15,25,2,4,"free",["chicken","high-protein","healthy","dairy-free"],
    ["Cook quinoa. Grill and slice chicken.","Build bowls with quinoa, chicken, chickpeas, avocado and greens."],
    [meat("Chicken breast",500,"g","chicken","breast",0.012,0),ing("Quinoa",250,"g","pantry",0.008,0),ing("Tinned chickpeas",1,"can","pantry",1.00,1),ing("Avocado",1,"whole","fruit",1.50,1),ing("Baby spinach",80,"g","veg",0.02,1)])
add("Beef & Black Bean Bowl",560,40,52,20,15,20,2,3,"free",["beef","mexican","high-protein","rice","dairy-free"],
    ["Brown the mince with spice.","Serve over rice with black beans, corn and salsa."],
    [meat("Beef mince",500,"g","beef","mince",0.016,0),ing("Taco spice mix",2,"tbsp","spice",0.20,0),rice(300,1),ing("Tinned black beans",1,"can","pantry",1.10,1),ing("Salsa",150,"g","sauce",0.01,1)])
add("Salmon with Lentils",560,42,36,26,10,30,2,4,"free",["fish","salmon","high-protein","healthy","dairy-free"],
    ["Simmer lentils with onion and stock.","Pan-sear salmon; serve on the lentils with lemon."],
    [meat("Salmon fillets",4,"whole","salmon","fillet",4.50,1),ing("Tinned brown lentils",2,"can","pantry",1.00,0),onion(1,0),ing("Lemon",1,"whole","fruit",0.70,1)])
add("Chicken Souvlaki Bowl",560,46,40,22,20,20,2,4,"free",["chicken","high-protein","greek","dairy-free"],
    ["Grill marinated chicken skewers.","Serve over rice with chickpeas, tomato and cucumber."],
    [meat("Chicken thigh fillet",600,"g","chicken","thigh fillet",0.013,0),ing("Lemon",1,"whole","fruit",0.70,0),rice(250,1),ing("Tinned chickpeas",1,"can","pantry",1.00,1),ing("Cucumber",1,"whole","veg",1.00,1)])
add("Prawn & Egg Fried Rice",520,34,64,12,15,15,2,3,"free",["fish","stir-fry","rice","high-protein","dairy-free"],
    ["Scramble eggs, set aside. Stir-fry prawns.","Add peas, rice and soy; fold egg through."],
    [meat("Green prawns",400,"g","fish","prawn",0.030,0),ing("Egg",3,"whole","dairy",0.40,0),ing("Frozen peas",150,"g","veg",0.004,1),rice(300,1),ing("Soy sauce",2,"tbsp","sauce",0.06,1)])
add("Chicken Chilli (High-Protein)",480,42,44,12,10,35,3,4,"free",["chicken","mexican","high-protein","one-pot","dairy-free","freezer-friendly"],
    ["Brown chicken mince with onion and chilli spice.","Add beans and tomatoes; simmer 25 minutes. Serve with rice."],
    [meat("Chicken mince",500,"g","chicken","mince",0.014,0),onion(1,0),ing("Mild chilli spice",1,"tbsp","spice",0.15,0),ing("Tinned kidney beans",1,"can","pantry",1.10,1),dicedtom(1),rice(200,1)])
add("Beef Rump with Greens & Beans",520,44,30,24,10,20,1,4,"free",["beef","high-protein","low-carb","dairy-free"],
    ["Sear the rump; rest and slice.","Serve with white beans warmed with garlic and steamed greens."],
    [meat("Beef rump",600,"g","beef","rump",0.026,0),ing("Tinned cannellini beans",1,"can","pantry",1.00,1),garlic(2,1),ing("Broccolini",1,"bunch","veg",2.80,1)])
add("Lamb & Chickpea Bowl",560,40,42,24,15,25,3,3,"free",["lamb","high-protein","middle-eastern","dairy-free"],
    ["Brown spiced lamb mince.","Serve over couscous with chickpeas, tomato and mint."],
    [meat("Lamb mince",500,"g","lamb","mince",0.018,0),ing("Moroccan spice",1,"tbsp","spice",0.20,0),ing("Couscous",250,"g","pantry",0.006,1),ing("Tinned chickpeas",1,"can","pantry",1.00,1),ing("Fresh mint",0.5,"bunch","veg",1.00,1)])
add("Tofu & Edamame Stir Fry",460,30,42,18,15,15,1,4,"free",["vegetarian","stir-fry","high-protein","dairy-free","no-fresh-meat"],
    ["Fry tofu until golden.","Stir-fry edamame and vegetables; add tofu, soy and sesame. Serve over rice."],
    [ing("Firm tofu",500,"g","pantry",0.010,0),ing("Edamame",200,"g","veg",0.012,1),capsicum(1),ing("Soy sauce",3,"tbsp","sauce",0.06,1),rice(200,0)])
add("Chicken & Bean Burrito Bowl",560,44,54,16,15,20,2,3,"free",["chicken","mexican","high-protein","rice","dairy-free"],
    ["Cook spiced chicken.","Build bowls with rice, black beans, corn, salsa and coriander."],
    [meat("Chicken breast",500,"g","chicken","breast",0.012,0),ing("Taco spice mix",2,"tbsp","spice",0.20,0),rice(250,1),ing("Tinned black beans",1,"can","pantry",1.10,1),ing("Salsa",150,"g","sauce",0.01,1)])
add("Salmon Poke Bowl (Protein)",560,40,52,20,15,15,1,4,"free",["fish","salmon","high-protein","rice","dairy-free"],
    ["Cube salmon and toss with soy and sesame.","Serve over rice with edamame, avocado and cucumber."],
    [meat("Salmon fillets",450,"g","salmon","fillet",4.50,0),rice(250,1),ing("Edamame",150,"g","veg",0.012,1),ing("Avocado",1,"whole","fruit",1.50,1),ing("Soy sauce",2,"tbsp","sauce",0.06,0)])
add("Chicken Shawarma Bowl",540,44,44,20,20,25,2,3,"free",["chicken","high-protein","middle-eastern","dairy-free"],
    ["Roast shawarma-spiced chicken.","Serve over rice with chickpeas, tomato and pickles."],
    [meat("Chicken thigh fillet",600,"g","chicken","thigh fillet",0.013,0),ing("Shawarma spice",2,"tbsp","spice",0.20,0),rice(250,1),ing("Tinned chickpeas",1,"can","pantry",1.00,1),ing("Tomato",2,"whole","veg",0.60,1)])
add("Baked Chicken Thighs & Lentils",520,42,34,24,10,40,3,4,"free",["chicken","high-protein","one-pot","dairy-free","freezer-friendly"],
    ["Brown chicken thighs. Add lentils, tomato and stock.","Bake at 190°C for 30 minutes."],
    [meat("Chicken thigh cutlets",8,"whole","chicken","thigh cutlet",1.00,0),ing("Tinned brown lentils",2,"can","pantry",1.00,1),dicedtom(1),ing("Chicken stock",200,"ml","pantry",0.002,1)])
add("Steak Fajita Bowl",540,42,46,20,15,20,2,3,"free",["beef","mexican","high-protein","dairy-free"],
    ["Sear spiced beef strips with capsicum and onion.","Serve over rice with beans and salsa."],
    [meat("Beef strips",500,"g","beef","stir-fry strips",0.022,0),ing("Fajita spice mix",2,"tbsp","spice",0.20,0),capsicum(0),onion(1,0),rice(250,1),ing("Tinned black beans",1,"can","pantry",1.10,1)])
add("Prawn & Quinoa Salad",480,34,44,16,15,20,2,4,"free",["fish","salad","high-protein","healthy","dairy-free"],
    ["Cook quinoa. Pan-fry prawns.","Toss quinoa, prawns, chickpeas, tomato and herbs with lemon."],
    [meat("Green prawns",400,"g","fish","prawn",0.030,0),ing("Quinoa",250,"g","pantry",0.008,0),ing("Tinned chickpeas",1,"can","pantry",1.00,1),ing("Tomato",2,"whole","veg",0.60,1),ing("Lemon",1,"whole","fruit",0.70,1)])
add("Chicken & Chickpea Curry",520,40,48,18,15,30,3,4,"free",["chicken","curry","high-protein","dairy-free","freezer-friendly"],
    ["Brown chicken with curry paste.","Add chickpeas, tomatoes and coconut milk; simmer 20 minutes. Serve with rice."],
    [meat("Chicken thigh fillet",500,"g","chicken","thigh fillet",0.013,0),ing("Mild curry paste",2,"tbsp","sauce",0.30,0),ing("Tinned chickpeas",1,"can","pantry",1.00,1),dicedtom(1),coconut(1),rice(200,1)])
add("Beef Kofta & Salad",520,40,26,30,20,15,2,4,"free",["beef","high-protein","middle-eastern","low-carb","dairy-free"],
    ["Shape spiced beef koftas and grill.","Serve with a big chopped salad and hummus."],
    [meat("Beef mince",600,"g","beef","mince",0.016,0),ing("Ground cumin",1,"tsp","spice",0.03,0),ing("Tomato",2,"whole","veg",0.60,1),ing("Cucumber",1,"whole","veg",1.00,1),ing("Hummus",150,"g","sauce",0.012,1)])
add("Grilled Fish & White Beans",480,40,34,18,10,20,2,4,"free",["fish","high-protein","healthy","dairy-free"],
    ["Warm white beans with garlic, tomato and spinach.","Grill the fish; serve on top with lemon."],
    [meat("White fish fillets",500,"g","fish","white fillet",0.028,0),ing("Tinned cannellini beans",2,"can","pantry",1.00,0),garlic(2,0),ing("Baby spinach",80,"g","veg",0.02,0),ing("Lemon",1,"whole","fruit",0.70,1)])
add("Chicken Meatballs & Quinoa",520,42,44,18,20,30,3,4,"free",["chicken","high-protein","dairy-free","freezer-friendly"],
    ["Roll and bake chicken meatballs.","Simmer in tomato sauce; serve over quinoa."],
    [meat("Chicken mince",500,"g","chicken","mince",0.014,0),ing("Breadcrumbs",40,"g","pantry",0.005,0),passata(400,1),ing("Quinoa",250,"g","pantry",0.008,1)])
add("Turkey-Style Chicken Burgers (Protein)",520,44,40,20,15,20,1,4,"free",["chicken","high-protein","dairy-free"],
    ["Mix chicken mince with herbs; shape and grill patties.","Serve in wholemeal buns with salad."],
    [meat("Chicken mince",600,"g","chicken","mince",0.014,0),ing("Wholemeal burger buns",4,"whole","bakery",0.90,1),ing("Mixed salad leaves",100,"g","veg",0.02,1),ing("Tomato",1,"whole","veg",0.60,1)])
add("Egg & Bean Breakfast-for-Dinner",460,30,44,18,10,15,1,4,"free",["vegetarian","high-protein","budget","dairy-free","no-fresh-meat"],
    ["Warm baked beans with smoked paprika.","Fry or poach eggs; serve with toast and grilled tomato."],
    [ing("Egg",6,"whole","dairy",0.40,1),ing("Tinned baked beans",2,"can","pantry",1.20,0),ing("Smoked paprika",1,"tsp","spice",0.03,0),ing("Wholemeal bread",4,"slice","bakery",0.30,1)])
add("Pork & Bean Stew (Protein)",520,42,40,22,15,45,3,3,"free",["pork","high-protein","one-pot","dairy-free","freezer-friendly"],
    ["Brown diced pork with onion and garlic.","Add beans, tomatoes and stock; simmer 35 minutes."],
    [meat("Pork loin",500,"g","pork","loin",0.016,0),onion(1,0),garlic(2,0),ing("Tinned cannellini beans",2,"can","pantry",1.00,1),dicedtom(1),ing("Chicken stock",200,"ml","pantry",0.002,1)])
add("Chicken & Lentil Soup (Protein)",440,38,40,12,15,35,3,5,"free",["soup","chicken","high-protein","weight-loss","dairy-free","freezer-friendly"],
    ["Brown chicken with onion, carrot and celery.","Add lentils and stock; simmer 25 minutes."],
    [meat("Chicken thigh fillet",400,"g","chicken","thigh fillet",0.013,0),ing("Red lentils",200,"g","pantry",0.004,1),onion(1,0),carrot(2,0),ing("Chicken stock",1500,"ml","pantry",0.002,1)])
add("Tuna & White Bean Salad",460,38,38,14,10,10,1,4,"free",["fish","salad","high-protein","budget","dairy-free","no-fresh-meat"],
    ["Flake tuna over cannellini beans.","Toss with red onion, tomato, parsley, lemon and olive oil."],
    [ing("Tinned tuna",3,"can","pantry",1.50,0),ing("Tinned cannellini beans",2,"can","pantry",1.00,0),ing("Red onion",0.5,"whole","veg",0.55,0),ing("Tomato",2,"whole","veg",0.60,0),ing("Lemon",1,"whole","fruit",0.70,0)])
print("after batch E:", len(R))

# =================================================================== BATCH F — DAIRY FREE (50)
add("Chicken Teriyaki Donburi",560,34,74,14,10,20,2,3,"free",["chicken","rice","dairy-free","kid-favourite"],
    ["Cook rice. Pan-fry chicken and glaze with teriyaki.","Serve over rice with spring onion and sesame."],
    [meat("Chicken thigh fillet",600,"g","chicken","thigh fillet",0.013,0),ing("Teriyaki sauce",4,"tbsp","sauce",0.10,0),rice(300,1),ing("Spring onion",2,"whole","veg",0.30,1)])
add("Beef Bulgogi Bowl",580,38,58,20,20,15,2,3,"free",["beef","korean","rice","dairy-free"],
    ["Marinate beef in soy, sesame, garlic and pear; sear hot.","Serve over rice with cucumber and kimchi."],
    [meat("Beef strips",500,"g","beef","stir-fry strips",0.022,0),ing("Soy sauce",3,"tbsp","sauce",0.06,0),garlic(2,0),rice(300,1),ing("Cucumber",1,"whole","veg",1.00,1)])
add("Pork Bibimbap",560,34,66,18,20,20,2,3,"free",["pork","korean","rice","dairy-free"],
    ["Cook rice. Stir-fry pork with gochujang.","Top rice with pork, carrot, spinach and a fried egg."],
    [meat("Pork mince",400,"g","pork","mince",0.014,0),ing("Gochujang",2,"tbsp","sauce",0.10,0),rice(300,1),carrot(1,1),ing("Baby spinach",80,"g","veg",0.02,1),ing("Egg",4,"whole","dairy",0.40,1)])
add("Singapore Noodles",520,26,62,18,15,15,1,3,"free",["noodles","smallgoods","stir-fry","dairy-free"],
    ["Soak vermicelli. Stir-fry prawns and ham with curry powder.","Add noodles, egg and vegetables; toss."],
    [meat("Green prawns",250,"g","fish","prawn",0.030,0),meat("Sliced ham",100,"g","smallgoods","sliced ham",0.024,0),ing("Rice vermicelli",300,"g","pantry",0.006,1),ing("Curry powder",1,"tbsp","spice",0.05,0),ing("Egg",2,"whole","dairy",0.40,1),capsicum(1)])
add("Kung Pao Chicken",520,34,44,20,15,15,1,3,"free",["chicken","stir-fry","rice","dairy-free"],
    ["Stir-fry chicken with dried chilli and garlic.","Add sauce and peanuts; serve over rice."],
    [meat("Chicken thigh fillet",500,"g","chicken","thigh fillet",0.013,0),garlic(2,0),ing("Soy sauce",3,"tbsp","sauce",0.06,1),ing("Peanuts",50,"g","pantry",0.02,1),rice(300,1)])
add("Sweet Chilli Chicken Stir Fry",520,32,58,16,10,15,1,3,"free",["chicken","stir-fry","quick","dairy-free","kid-favourite"],
    ["Stir-fry chicken, remove.","Stir-fry vegetables; return chicken with sweet chilli and soy. Serve over rice."],
    [meat("Chicken breast",450,"g","chicken","breast",0.012,0),ing("Mixed stir-fry vegetables",400,"g","veg",0.008,1),ing("Sweet chilli sauce",3,"tbsp","sauce",0.02,1),rice(300,0)])
add("Ginger Beef Stir Fry",520,34,50,18,15,15,1,3,"free",["beef","stir-fry","quick","dairy-free"],
    ["Fry crisp beef strips.","Add ginger, garlic and soy sauce; toss and serve over rice."],
    [meat("Beef strips",450,"g","beef","stir-fry strips",0.022,0),ing("Ginger",1,"tbsp","veg",0.10,1),garlic(2,1),ing("Soy sauce",3,"tbsp","sauce",0.06,1),rice(300,0)])
add("Chicken Yakisoba",540,30,64,16,15,15,1,3,"free",["chicken","noodles","stir-fry","dairy-free","kid-favourite"],
    ["Stir-fry chicken and cabbage.","Add noodles and yakisoba sauce; toss."],
    [meat("Chicken thigh fillet",400,"g","chicken","thigh fillet",0.013,0),ing("Hokkien noodles",400,"g","pantry",0.006,1),ing("Cabbage",0.25,"whole","veg",1.50,0),ing("Barbecue sauce",3,"tbsp","sauce",0.01,1)])
add("Thai Basil Chicken (Pad Krapow)",480,32,44,18,10,12,1,4,"free",["chicken","thai","quick","dairy-free"],
    ["Stir-fry chicken mince with garlic and chilli.","Add fish sauce, soy and basil; serve over rice with a fried egg."],
    [meat("Chicken mince",500,"g","chicken","mince",0.014,0),garlic(3,0),ing("Fish sauce",1,"tbsp","sauce",0.08,1),ing("Basil",0.5,"bunch","veg",1.50,1),rice(250,1),ing("Egg",4,"whole","dairy",0.40,1)])
add("Vietnamese Caramel Chicken",520,34,50,18,10,25,2,3,"free",["chicken","dairy-free"],
    ["Caramelise sugar, add fish sauce and chicken.","Simmer until sticky; serve over rice with cucumber."],
    [meat("Chicken thigh fillet",600,"g","chicken","thigh fillet",0.013,0),ing("Brown sugar",2,"tbsp","pantry",0.05,0),ing("Fish sauce",2,"tbsp","sauce",0.08,0),rice(300,1),ing("Cucumber",1,"whole","veg",1.00,1)])
add("Japanese Chicken Curry",560,30,74,16,15,30,3,3,"free",["chicken","curry","rice","dairy-free","freezer-friendly"],
    ["Brown chicken with onion and carrot.","Add stock and curry roux; simmer until thick. Serve over rice."],
    [meat("Chicken thigh fillet",500,"g","chicken","thigh fillet",0.013,0),onion(1,0),carrot(2,0),ing("Japanese curry roux",100,"g","sauce",0.02,1),rice(300,1)])
add("Sticky Sesame Chicken",560,32,64,18,15,20,1,3,"free",["chicken","rice","dairy-free","kid-favourite"],
    ["Fry battered chicken until crisp.","Toss in a sticky sesame-soy sauce; serve over rice with broccoli."],
    [meat("Chicken breast",500,"g","chicken","breast",0.012,0),ing("Cornflour",3,"tbsp","pantry",0.02,0),ing("Soy sauce",3,"tbsp","sauce",0.06,1),ing("Honey",2,"tbsp","pantry",0.20,1),rice(300,1),broccoli(1)])
add("Beef Chow Fun",540,30,64,16,15,15,1,3,"free",["beef","noodles","stir-fry","dairy-free"],
    ["Sear beef, remove.","Stir-fry flat noodles with bean sprouts and spring onion; return beef with soy."],
    [meat("Beef strips",400,"g","beef","stir-fry strips",0.022,0),ing("Fresh rice noodles",400,"g","pantry",0.006,1),ing("Bean sprouts",100,"g","veg",0.01,1),ing("Soy sauce",3,"tbsp","sauce",0.06,1)])
add("Prawn Nasi Goreng",520,28,66,16,15,15,2,3,"free",["fish","rice","stir-fry","dairy-free","uses-leftovers"],
    ["Stir-fry prawns and vegetables.","Add cold rice and kecap manis; top with a fried egg."],
    [meat("Green prawns",300,"g","fish","prawn",0.030,0),rice(300,1),ing("Frozen mixed vegetables",250,"g","veg",0.005,0),ing("Kecap manis",3,"tbsp","sauce",0.02,1),ing("Egg",4,"whole","dairy",0.40,1)])
add("Chilli Garlic Noodles with Chicken",520,30,64,16,10,15,1,3,"free",["chicken","noodles","quick","dairy-free"],
    ["Cook noodles. Stir-fry chicken.","Toss with chilli-garlic oil, soy and greens."],
    [meat("Chicken breast",400,"g","chicken","breast",0.012,0),ing("Egg noodles",400,"g","pantry",0.006,1),garlic(3,1),ing("Chilli garlic sauce",2,"tbsp","sauce",0.10,1),ing("Bok choy",2,"whole","veg",0.80,1)])
add("Chicken Jalfrezi",480,34,40,18,15,30,3,4,"free",["chicken","curry","dairy-free","freezer-friendly"],
    ["Brown chicken with onion and capsicum.","Add jalfrezi spices and tomatoes; simmer 20 minutes. Serve with rice."],
    [meat("Chicken thigh fillet",500,"g","chicken","thigh fillet",0.013,0),onion(1,0),capsicum(0),ing("Curry powder",1,"tbsp","spice",0.05,0),dicedtom(1),rice(200,1)])
add("Lamb Keema with Peas",520,34,44,22,10,30,3,3,"free",["lamb","curry","dairy-free","freezer-friendly","budget"],
    ["Brown lamb mince with onion and spices.","Add tomatoes and peas; simmer 20 minutes. Serve with rice or roti."],
    [meat("Lamb mince",500,"g","lamb","mince",0.018,0),onion(1,0),ing("Garam masala",1,"tbsp","spice",0.03,0),dicedtom(1),ing("Frozen peas",150,"g","veg",0.004,1),rice(200,1)])
add("Chana Aloo (Chickpea & Potato Curry)",420,14,68,10,10,30,3,5,"free",["curry","vegetarian","budget","weight-loss","dairy-free","freezer-friendly","no-fresh-meat"],
    ["Fry onion, garlic and spices.","Add potato, chickpeas and tomatoes; simmer 25 minutes. Serve with rice."],
    [ing("Potato",3,"whole","veg",0.40,1),ing("Tinned chickpeas",2,"can","pantry",1.00,1),onion(1,0),garlic(2,0),ing("Curry powder",1,"tbsp","spice",0.05,0),dicedtom(1),rice(200,1)])
add("Beef Madras",520,36,40,24,15,50,3,3,"free",["curry","beef","slow-cook","dairy-free","freezer-friendly"],
    ["Brown beef with madras paste.","Add tomatoes and stock; simmer 40 minutes. Serve with rice."],
    [meat("Beef chuck",600,"g","beef","chuck",0.015,0),ing("Madras paste",3,"tbsp","sauce",0.30,0),dicedtom(1),ing("Beef stock",200,"ml","pantry",0.002,1),rice(200,1)])
add("Egg & Potato Curry",420,18,50,16,10,25,3,4,"free",["curry","vegetarian","budget","dairy-free","no-fresh-meat"],
    ["Boil eggs and potato.","Make a tomato-onion curry sauce; add eggs and potato. Serve with rice."],
    [ing("Egg",6,"whole","dairy",0.40,1),ing("Potato",3,"whole","veg",0.40,0),onion(1,0),ing("Curry powder",1,"tbsp","spice",0.05,0),dicedtom(0),rice(200,1)])
add("Prawn Masala",440,30,36,18,15,25,3,4,"free",["curry","fish","dairy-free"],
    ["Fry onion, garlic, ginger and spices.","Add tomatoes and prawns; simmer 8 minutes. Serve with rice."],
    [meat("Green prawns",500,"g","fish","prawn",0.030,1),onion(1,0),garlic(2,0),ing("Garam masala",1,"tbsp","spice",0.03,0),dicedtom(0),rice(200,1)])
add("Chicken Tinga Tacos",480,32,44,18,15,30,3,3,"free",["chicken","mexican","dairy-free"],
    ["Simmer chicken with chipotle and tomato, then shred.","Serve in tortillas with onion and coriander."],
    [meat("Chicken thigh fillet",500,"g","chicken","thigh fillet",0.013,0),ing("Chipotle sauce",2,"tbsp","sauce",0.10,0),dicedtom(0),ing("Tortillas",8,"whole","bakery",0.25,1),ing("Red onion",0.5,"whole","veg",0.55,1)])
add("Beef Barbacoa Bowl",540,38,52,20,15,120,3,3,"free",["beef","mexican","slow-cook","long-cook","dairy-free","freezer-friendly"],
    ["Slow-cook beef with chipotle, cumin and stock until it shreds.","Serve over rice with beans and salsa."],
    [meat("Beef chuck",700,"g","beef","chuck",0.015,0),ing("Chipotle sauce",2,"tbsp","sauce",0.10,0),ing("Ground cumin",1,"tbsp","spice",0.03,0),rice(250,1),ing("Tinned black beans",1,"can","pantry",1.10,1)])
add("Pork Verde",500,36,40,22,15,90,3,3,"free",["pork","mexican","slow-cook","dairy-free","freezer-friendly"],
    ["Slow-cook pork with salsa verde until tender.","Shred; serve in tortillas or over rice."],
    [meat("Pork shoulder",700,"g","pork","shoulder (boneless)",0.011,0),ing("Salsa verde",200,"g","sauce",0.02,0),ing("Tortillas",8,"whole","bakery",0.25,1),ing("Lime",1,"whole","fruit",0.60,1)])
add("Black Bean & Sweet Potato Bowl",440,14,72,10,15,30,3,5,"free",["vegetarian","mexican","weight-loss","dairy-free","no-fresh-meat"],
    ["Roast spiced sweet potato.","Serve over rice with black beans, corn, avocado and lime."],
    [ing("Sweet potato",600,"g","veg",0.004,0),ing("Taco spice mix",1,"tbsp","spice",0.20,0),rice(250,1),ing("Tinned black beans",1,"can","pantry",1.10,1),ing("Avocado",1,"whole","fruit",1.50,1)])
print("after batch F1:", len(R))

add("Chipotle Chicken Rice",520,34,60,16,15,25,3,3,"free",["chicken","mexican","rice","one-pot","dairy-free","freezer-friendly"],
    ["Brown chicken with chipotle and onion.","Add rice, tomatoes and stock; cover and simmer 20 minutes."],
    [meat("Chicken thigh fillet",500,"g","chicken","thigh fillet",0.013,0),ing("Chipotle sauce",2,"tbsp","sauce",0.10,0),onion(1,0),rice(300,1),dicedtom(1),ing("Chicken stock",300,"ml","pantry",0.002,1)])
add("Harissa Chicken Traybake",480,36,38,20,15,40,2,4,"free",["chicken","tray-bake","one-pan","dairy-free","freezer-friendly"],
    ["Toss chicken, chickpeas and vegetables with harissa and oil.","Roast at 200°C for 40 minutes."],
    [meat("Chicken thigh cutlets",8,"whole","chicken","thigh cutlet",1.00,0),ing("Harissa paste",2,"tbsp","sauce",0.10,0),ing("Tinned chickpeas",1,"can","pantry",1.00,0),capsicum(0),ing("Red onion",1,"whole","veg",0.55,0)])
add("Lemon Herb Fish Traybake",420,34,30,18,10,30,1,5,"free",["fish","tray-bake","one-pan","weight-loss","dairy-free","high-protein"],
    ["Arrange fish, cherry tomatoes and beans on a tray with lemon, garlic and oil.","Roast at 200°C for 20 minutes."],
    [meat("White fish fillets",500,"g","fish","white fillet",0.028,0),ing("Cherry tomatoes",200,"g","veg",0.012,0),ing("Green beans",200,"g","veg",0.012,0),ing("Lemon",1,"whole","fruit",0.70,0),garlic(2,0)])
add("Moroccan Chickpea Stew",380,14,60,8,10,30,3,5,"free",["vegetarian","middle-eastern","weight-loss","budget","dairy-free","freezer-friendly","no-fresh-meat"],
    ["Cook onion, garlic and Moroccan spice.","Add chickpeas, tomatoes and pumpkin; simmer 20 minutes. Serve with couscous."],
    [ing("Tinned chickpeas",2,"can","pantry",1.00,1),onion(1,0),garlic(2,0),ing("Moroccan spice",1,"tbsp","spice",0.20,0),dicedtom(1),ing("Pumpkin",300,"g","veg",0.004,1),ing("Couscous",200,"g","pantry",0.006,1)])
add("Spiced Lamb Flatbreads",560,32,48,28,15,20,1,3,"free",["lamb","middle-eastern","dairy-free"],
    ["Cook spiced lamb mince with onion.","Spread over flatbreads and grill; top with salad and lemon."],
    [meat("Lamb mince",500,"g","lamb","mince",0.018,0),onion(1,0),ing("Ground cumin",1,"tsp","spice",0.03,0),ing("Flatbread",4,"whole","bakery",0.80,1),ing("Mixed salad leaves",100,"g","veg",0.02,1)])
add("Greek Chicken Skewers with Rice",520,40,44,20,20,20,2,4,"free",["chicken","greek","rice","dairy-free","high-protein"],
    ["Marinate chicken in lemon, oregano and garlic; grill on skewers.","Serve over rice with tomato and cucumber."],
    [meat("Chicken thigh fillet",600,"g","chicken","thigh fillet",0.013,0),ing("Lemon",1,"whole","fruit",0.70,0),ing("Dried oregano",1,"tsp","spice",0.02,0),rice(250,1),ing("Cucumber",1,"whole","veg",1.00,1)])
add("Sausage & Bean Casserole",560,26,50,28,10,40,3,3,"free",["sausage","one-pot","dairy-free","freezer-friendly","budget"],
    ["Brown the sausages, then onion and garlic.","Add beans, tomatoes and stock; simmer 30 minutes."],
    [meat("Thick pork sausages",8,"whole","sausage","pork sausage",0.55,0),onion(1,1),garlic(2,1),ing("Tinned mixed beans",2,"can","pantry",1.10,1),dicedtom(1),ing("Chicken stock",200,"ml","pantry",0.002,1)])
add("Chicken & Vegetable Traybake",440,36,38,16,10,40,2,4,"free",["chicken","tray-bake","one-pan","dairy-free","freezer-friendly"],
    ["Toss chicken and chopped vegetables with oil and herbs.","Roast at 200°C for 40 minutes."],
    [meat("Chicken thigh cutlets",8,"whole","chicken","thigh cutlet",1.00,0),ing("Potato",4,"whole","veg",0.40,0),carrot(2,0),ing("Zucchini",1,"whole","veg",0.80,0),oil(2,0)])
add("Beef & Vegetable Stew",480,38,38,20,15,120,3,4,"free",["beef","slow-cook","long-cook","dairy-free","freezer-friendly","comfort"],
    ["Brown beef; add onion, carrot and celery.","Add stock and potato; simmer 1.5–2 hours."],
    [meat("Beef chuck",700,"g","beef","chuck",0.015,0),onion(1,1),carrot(2,1),ing("Celery",2,"whole","veg",0.40,1),ing("Potato",3,"whole","veg",0.40,1),ing("Beef stock",600,"ml","pantry",0.002,1)])
add("Pork & Apple Traybake",480,34,32,24,10,45,2,3,"free",["pork","tray-bake","one-pan","dairy-free"],
    ["Roast pork with apple, red onion and potato.","Season with sage and roast at 200°C for 40 minutes."],
    [meat("Pork loin steaks",600,"g","pork","loin steak",0.018,0),ing("Apple",2,"whole","fruit",0.60,0),ing("Red onion",1,"whole","veg",0.55,0),ing("Potato",4,"whole","veg",0.40,0)])
add("Lemon Herb Chicken Drumsticks",480,34,20,30,10,40,2,3,"free",["chicken","oven","dairy-free","budget"],
    ["Toss drumsticks with lemon, garlic, oregano and oil.","Roast at 200°C for 40 minutes; serve with salad."],
    [meat("Chicken drumsticks",8,"whole","chicken","drumstick",0.90,0),ing("Lemon",1,"whole","fruit",0.70,0),garlic(3,0),ing("Dried oregano",1,"tsp","spice",0.02,0),ing("Mixed salad leaves",100,"g","veg",0.02,1)])
add("Fish & Chickpea Traybake",440,34,36,16,10,30,2,4,"free",["fish","tray-bake","one-pan","dairy-free","high-protein"],
    ["Roast chickpeas, tomatoes and capsicum with spice.","Add fish and roast 15 minutes; finish with lemon."],
    [meat("White fish fillets",500,"g","fish","white fillet",0.028,1),ing("Tinned chickpeas",1,"can","pantry",1.00,0),ing("Cherry tomatoes",200,"g","veg",0.012,0),capsicum(0),ing("Lemon",1,"whole","fruit",0.70,1)])
add("Beef Mince & Vegetable Skillet",460,32,36,20,10,20,2,4,"free",["beef","one-pan","quick","dairy-free","budget"],
    ["Brown mince with onion and garlic.","Add mixed vegetables and tomato; simmer 10 minutes. Serve with rice."],
    [meat("Beef mince",500,"g","beef","mince",0.016,0),onion(1,0),garlic(2,0),ing("Frozen mixed vegetables",300,"g","veg",0.005,1),passata(300,1),rice(200,1)])
add("Chicken & Chorizo Traybake",520,34,36,26,10,40,2,3,"free",["chicken","smallgoods","tray-bake","one-pan","dairy-free"],
    ["Toss chicken, chorizo, potato and capsicum with paprika and oil.","Roast at 200°C for 40 minutes."],
    [meat("Chicken thigh cutlets",6,"whole","chicken","thigh cutlet",1.00,0),meat("Chorizo",150,"g","smallgoods","chorizo",0.022,0),ing("Potato",4,"whole","veg",0.40,0),capsicum(0),ing("Smoked paprika",1,"tsp","spice",0.03,0)])
add("Lentil Bolognese",420,18,66,8,10,30,3,5,"free",["pasta","vegetarian","weight-loss","budget","dairy-free","freezer-friendly","no-fresh-meat"],
    ["Cook onion, carrot and garlic.","Add lentils and passata; simmer 20 minutes. Toss with pasta."],
    [ing("Tinned brown lentils",2,"can","pantry",1.00,1),onion(1,0),carrot(1,0),garlic(2,0),passata(500,1),ing("Spaghetti",350,"g","pantry",0.004,1)])
add("Vegetable Paella",440,12,78,8,15,35,3,4,"free",["rice","vegetarian","dairy-free","no-fresh-meat"],
    ["Fry onion, capsicum and garlic with paprika and saffron.","Add rice, stock and vegetables; simmer 20 minutes."],
    [ing("Paella or arborio rice",300,"g","pantry",0.005,1),onion(1,0),capsicum(0),garlic(2,0),ing("Smoked paprika",1,"tsp","spice",0.03,0),ing("Vegetable stock",750,"ml","pantry",0.002,1),ing("Frozen peas",150,"g","veg",0.004,1)])
add("Prawn Paella",520,30,68,10,15,35,2,3,"free",["rice","fish","dairy-free"],
    ["Fry onion, capsicum and garlic with paprika.","Add rice and stock; simmer 15 minutes, then prawns and peas 5 minutes."],
    [meat("Green prawns",400,"g","fish","prawn",0.030,1),ing("Paella or arborio rice",300,"g","pantry",0.005,0),onion(1,0),capsicum(0),ing("Smoked paprika",1,"tsp","spice",0.03,0),ing("Chicken stock",750,"ml","pantry",0.002,0),ing("Frozen peas",150,"g","veg",0.004,1)])
add("Sausage & Lentil Stew",520,28,46,24,10,40,3,3,"free",["sausage","one-pot","dairy-free","freezer-friendly","budget"],
    ["Brown sausages, then onion and carrot.","Add lentils, tomatoes and stock; simmer 30 minutes."],
    [meat("Thick pork sausages",6,"whole","sausage","pork sausage",0.55,0),onion(1,1),carrot(1,1),ing("Tinned brown lentils",2,"can","pantry",1.00,1),dicedtom(1),ing("Chicken stock",300,"ml","pantry",0.002,1)])
add("Pumpkin & Lentil Dahl",400,16,60,8,10,30,3,5,"free",["curry","vegetarian","weight-loss","budget","dairy-free","freezer-friendly","no-fresh-meat"],
    ["Cook onion, garlic and spices.","Add red lentils, pumpkin and stock; simmer 25 minutes. Serve with rice."],
    [ing("Red lentils",250,"g","pantry",0.004,1),ing("Pumpkin",400,"g","veg",0.004,1),onion(1,0),garlic(2,0),ing("Garam masala",1,"tbsp","spice",0.03,0),rice(200,1)])
add("Teriyaki Beef Bowl",540,36,58,18,10,15,1,3,"free",["beef","rice","quick","dairy-free","kid-favourite"],
    ["Stir-fry beef strips.","Glaze with teriyaki; serve over rice with steamed broccoli."],
    [meat("Beef strips",500,"g","beef","stir-fry strips",0.022,0),ing("Teriyaki sauce",4,"tbsp","sauce",0.10,1),rice(300,1),broccoli(1)])
add("Moroccan Chicken Traybake",480,36,40,20,15,45,2,4,"free",["chicken","tray-bake","one-pan","middle-eastern","dairy-free"],
    ["Toss chicken, sweet potato and chickpeas with Moroccan spice.","Roast at 200°C for 40 minutes; scatter coriander."],
    [meat("Chicken thigh cutlets",8,"whole","chicken","thigh cutlet",1.00,0),ing("Sweet potato",400,"g","veg",0.004,0),ing("Tinned chickpeas",1,"can","pantry",1.00,0),ing("Moroccan spice",2,"tbsp","spice",0.20,0)])
add("Sweet & Sticky Pork Stir Fry",520,34,54,18,10,15,1,3,"free",["pork","stir-fry","quick","rice","dairy-free"],
    ["Stir-fry pork strips.","Add hoisin, soy and honey; toss with vegetables and serve over rice."],
    [meat("Pork stir-fry strips",450,"g","pork","stir-fry strips",0.018,0),ing("Hoisin sauce",2,"tbsp","sauce",0.12,1),ing("Soy sauce",1,"tbsp","sauce",0.06,1),ing("Mixed stir-fry vegetables",300,"g","veg",0.008,1),rice(300,0)])
add("Cajun Chicken & Rice",500,36,56,14,10,25,3,3,"free",["chicken","one-pot","rice","dairy-free","freezer-friendly"],
    ["Brown Cajun-spiced chicken with onion and capsicum.","Add rice and stock; simmer 20 minutes."],
    [meat("Chicken thigh fillet",500,"g","chicken","thigh fillet",0.013,0),ing("Cajun spice",2,"tbsp","spice",0.15,0),onion(1,0),capsicum(0),rice(300,1),ing("Chicken stock",400,"ml","pantry",0.002,1)])
add("Chickpea & Spinach Curry",400,15,58,10,10,25,3,5,"free",["curry","vegetarian","weight-loss","budget","dairy-free","freezer-friendly","no-fresh-meat"],
    ["Fry onion, garlic and curry paste.","Add chickpeas, tomatoes and coconut milk; simmer 15 minutes with spinach. Serve with rice."],
    [ing("Tinned chickpeas",2,"can","pantry",1.00,1),onion(1,0),garlic(2,0),ing("Mild curry paste",2,"tbsp","sauce",0.30,0),dicedtom(1),coconut(1),ing("Baby spinach",100,"g","veg",0.02,1),rice(200,1)])
add("Beef & Broccoli Noodle Bowl",540,34,58,16,10,15,1,3,"free",["beef","noodles","stir-fry","quick","dairy-free"],
    ["Cook noodles. Stir-fry beef, remove.","Stir-fry broccoli; return beef with soy and oyster sauce, toss with noodles."],
    [meat("Beef strips",400,"g","beef","stir-fry strips",0.022,0),ing("Egg noodles",400,"g","pantry",0.006,1),broccoli(1),ing("Soy sauce",2,"tbsp","sauce",0.06,1),ing("Oyster sauce",1,"tbsp","sauce",0.10,1)])
print("after batch F2:", len(R))

def store_of(i): return "meat" if i["is_meat"] else "pantry"

# ---- split compound method steps into clear single-action steps ----------
# Breaks a lumped step at sentence ends, semicolons, " then ", and at a comma
# that is followed by an imperative verb — but never inside an ingredient list
# (a comma before a noun like "carrot" is left alone). Ingredient step_index
# values are remapped so each ingredient stays attached to its original action.
import re as _re
_STEP_VERBS = ("add","stir","pour","return","season","simmer","bring","reduce","remove","serve","drain",
  "mix","fold","top","garnish","cover","transfer","heat","brown","fry","roast","bake","cook","scatter",
  "sprinkle","spoon","layer","whisk","combine","toss","coat","set","rest","leave","spread","arrange",
  "deglaze","melt","boil","steam","grill","divide","finish","taste","adjust","continue","meanwhile",
  "then","tip","press","shape","form","dust","rub","marinate","warm","reheat","assemble","fill","wrap",
  "roll","flip","turn","baste","glaze","thicken","mash","blend","puree","crush","squeeze","drizzle",
  "dot","microwave","preheat")
_VRE = "|".join(sorted(set(_STEP_VERBS), key=len, reverse=True))
def _split_step(text):
    raw = []
    for p in _re.split(r"(?:\.\s+|;\s+|\s+then\s+)", text.strip()):
        p = p.strip().rstrip(".")
        if not p: continue
        for s in _re.split(r",\s+(?=(?:%s)\b)" % _VRE, p, flags=_re.I):
            s = s.strip().rstrip(".").strip()
            if s: raw.append(s[0].upper() + s[1:])
    # a bare single-word fragment (e.g. "Remove") reads better joined to the step before it
    merged = []
    for s in raw:
        if merged and len(s.split()) == 1:
            merged[-1] = merged[-1] + ", then " + s[0].lower() + s[1:]
        else:
            merged.append(s)
    return [m + "." for m in merged] or [text]
def split_methods():
    for r in R:
        newsteps, mapping = [], {}
        for i, st in enumerate(r["method_steps"]):
            mapping[i] = len(newsteps)
            newsteps.extend(_split_step(st))
        r["method_steps"] = newsteps
        for ing in r["ingredients"]:
            ing["step_index"] = mapping.get(ing.get("step_index", 0), 0)
split_methods()

print("total recipes:", len(R))
js = ("// Curated recipe library (generated by build_seed.py).\n"
      "// Australian family dinners, metric, serve 4. Energy kJ, prices AUD.\n"
      "const SEED_RECIPES = " + json.dumps(R, ensure_ascii=False) + ";\n")
open("/home/claude/meal-planner-iphone/seed.js", "w").write(js)
print("wrote seed.js;", sum(len(r['ingredients']) for r in R), "ingredient lines")
