from tkinter import *
import os
from dotenv import load_dotenv
import requests
from PIL import Image, ImageTk
import io

root = Tk()
root.geometry('1200x900')

load_dotenv()
api_key = os.getenv("API_KEY")
base_url = os.getenv("BASE_URL")

add_button = None

def lookup_word():
    global add_button
    query = SearchString.get()
    endpoint =  base_url + "/food/ingredients/search?"
    params = {
        'query': query,
        'number': 1,
        'apiKey': api_key
    }

    response = requests.get(endpoint, params=params)

    if response.status_code == 200:
        data = response.json()
        if data["results"]:
            result = data["results"][0]["name"]
            if not add_button:
                add_button = Button(result_frame, text = "Add", command = add_ingredient)
                add_button.pack(side = LEFT, padx = 5)
        else:
            result = "No results found."
    else:
        result = "ERROR: " + str(response.status_code)

    print(result)
    SearchResultBar.config(text=result)

def show_main_screen():
    main_frame.pack(pady = 10)
    result_frame.pack(pady = 10)
    lookup_label.pack(pady = 5)
    Searchbar.pack(side = LEFT, padx = 5)
    lookup_button.pack(side = LEFT, padx = 5)
    ingredients_frame.pack(pady = 10)
    find_button.pack(pady = 10)
    recipe_frame.pack_forget()
    recipe_card_frame.pack_forget()

def show_recipe_screen():
    find_recipes()
    main_frame.pack_forget()
    lookup_label.pack_forget()
    Searchbar.pack_forget()
    lookup_button.pack_forget()
    result_frame.pack_forget()
    ingredients_frame.pack_forget()
    find_button.pack_forget()
    recipe_frame.pack()
    recipe_card_frame.pack_forget()

def show_card_screen(recipe_id):
    main_frame.pack_forget()
    lookup_label.pack_forget()
    Searchbar.pack_forget()
    lookup_button.pack_forget()
    result_frame.pack_forget()
    ingredients_frame.pack_forget()
    find_button.pack_forget()
    recipe_card_frame.pack()
    recipe_frame.pack_forget()

    show_recipe_cards(recipe_id)

def clear_frame(frame):
    for widget in frame.winfo_children():
        widget.destroy()

def show_recipe_cards(recipe_id):
    endpoint =  base_url + "/recipes/" + str(recipe_id) + "/card"
    params = {
        'apiKey': api_key
    }

    response = requests.get(endpoint, params = params)

    if response.status_code == 200:
        data = response.json()
        image_url = data["url"]

        image_response = requests.get(image_url)
        if image_response.status_code == 200:
            image_data = image_response.content
            image = Image.open(io.BytesIO(image_data))

            original_width, original_height = image.size
            aspect_ratio = 0.65

            resized_image = image.resize((int(original_width * aspect_ratio), int(original_height * aspect_ratio)), Image.LANCZOS)
            recipe_card_image = ImageTk.PhotoImage(resized_image)

            clear_frame(recipe_card_frame)

            top_frame = Frame(recipe_card_frame, bg = "white")
            top_frame.pack(fill = "x", pady = 5)

            back_button = Button(top_frame, text = "Back", command = show_recipe_screen)
            back_button.pack(side = LEFT, padx = 5, pady = 5)

            recipe_card_label = Label(recipe_card_frame, image = recipe_card_image)
            recipe_card_label.image = recipe_card_image
            recipe_card_label.pack(side = LEFT, padx = 10, pady = 5)

            nutrition_endpoint =  base_url + "/recipes/" + str(recipe_id) + "/nutritionLabel.png"
            nutrition_response = requests.get(nutrition_endpoint, params = params)
            if nutrition_response.status_code == 200:
                nutrition_data = nutrition_response.content
                nutritional_label_image = ImageTk.PhotoImage(Image.open(io.BytesIO(nutrition_data)))
                
                nutritional_label_label = Label(recipe_card_frame, image = nutritional_label_image)
                nutritional_label_label.image = nutritional_label_image
                nutritional_label_label.pack(side = LEFT, padx = 10, pady = 5)
            else:
                print("ERROR: " + str(nutrition_response.status_code))

            recipe_card_frame.pack()
        else:
            result = "ERROR: " + str(response.status_code)
            print(result)
    else: 
        result = "ERROR: " + str(response.status_code)
        print(result)

def show_recipes(recipes):
    clear_frame(recipe_frame)

    top_frame = Frame(recipe_frame)
    top_frame.pack(fill = "x", pady = 5)

    back_button = Button(top_frame, text = "Back", command = show_main_screen)
    back_button.pack(side = LEFT, padx = 5, pady = 5)

    recipes_label = Label(recipe_frame, text = "Recipes", font = ("Arial", 14, "bold"))
    recipes_label.pack(pady = 5)

    for recipe in recipes:
        recipe_button = Button(recipe_frame, text = recipe["title"], command = lambda recipe_id=recipe["id"]: show_card_screen(recipe_id))
        recipe_button.pack(pady = 5)

def find_recipes():
    ingredients = ",".join(added_ingredients)
    query = SearchString.get()
    endpoint =  base_url + "/recipes/findByIngredients?"
    params = {
        'ingredients': ingredients,
        'number': 10,
        'apiKey': api_key
    }

    response = requests.get(endpoint, params = params)

    if response.status_code == 200:
        data = response.json()
        show_recipes(data)
    else:
        result = "ERROR: " + str(response.status_code)

def update_ingredients():
    for widget in ingredients_frame.winfo_children():
        widget.destroy()

    ingredients_label = Label(ingredients_frame, text = "Ingredients", font = ("Arial", 14, "bold"))
    ingredients_label.pack(pady = 5)

    for ingredient in added_ingredients:
        ingredient_frame = Frame(ingredients_frame)
        ingredient_frame.pack(fill = "x", pady = 5)
        ingredient_label = Label(ingredient_frame, text = ingredient)
        ingredient_label.pack(side = LEFT, padx = 5)
        remove_button = Button(ingredient_frame, text = "Remove", command = lambda ingredient=ingredient: remove_ingredient(ingredient))
        remove_button.pack(side = LEFT, padx = 5)

def add_ingredient():
    ingredient = SearchResultBar.cget("text")
    if ingredient and ingredient != "No results found." and not ingredient.startswith("ERROR:"):
        added_ingredients.append(ingredient)
        update_ingredients()
        print(added_ingredients)

def remove_ingredient(ingredient):
    added_ingredients.remove(ingredient)
    update_ingredients()

frame = Frame(root)
frame.pack(pady = 10)

main_frame = Frame(root)
main_frame.pack()

logo = Image.open("bento_buddy_logo.png")
tk_logo = ImageTk.PhotoImage(logo)
logo_label = Label(main_frame, image = tk_logo)
logo_label.image = tk_logo
logo_label.pack(pady = (50, 30))

app_label = Label(main_frame, text = "Bento Buddy", font = ("Arial", 24, "bold"))
app_label.pack(pady = (10, 30))

lookup_label = Label(main_frame, text="Please select the ingredients: ", font = ("Arial", 14, "bold"))
lookup_label.pack(pady = 5)

Searchbar = Entry(main_frame)
Searchbar.pack(side = LEFT, padx = 5)
SearchString = StringVar(Searchbar, "")
Searchbar.config(textvariable = SearchString)

lookup_button = Button(main_frame, text = "Look Up", command = lookup_word)
lookup_button.pack(side = RIGHT, padx = 5)

result_frame = Frame(root)
result_frame.pack(pady = 10)

SearchResultBar = Label(result_frame)
SearchResultBar.pack(side = LEFT, padx = 5)

ingredients_frame = Frame(root)
ingredients_frame.pack(pady = 10)

find_button = Button(root, text = "Find Recipes", bg = "#321B41", fg = "#ffffff", command = show_recipe_screen)
find_button.pack(padx = 5)

added_ingredients = []

recipe_frame = Frame(root)

recipe_card_frame = Frame(root, bg = "white")
recipe_card_frame.pack_forget()

root.mainloop()
