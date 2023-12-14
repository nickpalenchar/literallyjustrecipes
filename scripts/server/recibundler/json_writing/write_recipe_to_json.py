"""
ASSUMES YOUR WORKING DIRECTORY IS scripts/

builds new recipes from the submitted google sheet.

Each new recipe should be its own separate PR. Therefore, it should be ran with
a script that can do said checkout and PR.

**Required**: a text file, `add_new_recipes_since`, containing one line--the iso
date of the last recipe to be added. This script will 
"""
import sys
import os
import csv
import json
import typing as t
from collections import namedtuple
from recibundler.schema.hugodata import Recipe, Ingredient
from datetime import datetime
from recibundler import reciparcer
from recibundler.schema.reciperow import reciperow
from .util import get_recipe_filename
import logging
from os import path

T = t.TypeVar("T")

logging.basicConfig(level=os.environ.get("LOGLEVEL", "WARN"))


def add_new_recipes(filepath):
    logging.debug(f"filepath is {filepath}")

    with open(filepath, newline="") as fh:
        reader = csv.reader(fh)

        with open("add_new_recipes_since") as datefh:
            try:
                last_date = datetime.fromisoformat(datefh.read().strip())
            except ValueError:
                logging.warn("starting from beginning of time")
                last_date = datetime(year=2022, month=1, day=28)

        # skip the header
        next(reader)

        for recipe in reader:
            recipe = reciperow(*recipe)
            if is_recipe_old(recipe, last_date):
                continue
            logging.info(f"the next recipe is {recipe.name}")
            write_recipe_to_json(recipe)

            with open("add_new_recipes_since", mode="w") as datefh:
                datefh.write(str(isodate_from_recipe(recipe)))
            return

        logging.error("no new recipes")
        sys.exit(1)


def isodate_from_recipe(recipe: reciperow) -> datetime:
    return datetime.strptime(recipe.timestamp, "%m/%d/%Y %H:%M:%S")


def is_recipe_old(recipe: reciperow, since) -> bool:
    """
    Parses the date from the "google" submission date and
    simply compares the date delta with `since`. If True, this is
    the next recipe to use
    """
    recipe_date = datetime.strptime(recipe.timestamp, "%m/%d/%Y %H:%M:%S")
    return recipe_date <= since

def ai_write_recipe_to_json(recipe: reciperow):
    ai_write_recipe_to_json

def write_recipe_to_json(recipe: reciperow, additional_keys=None):
    if additional_keys is None:
        additional_keys = {}
    attrs = {
        "version": "1",
        "name": recipe.name,
        "summary": recipe.summary,
        "steps": reciparcer.parse_steps(recipe.steps),
        "ingredients": reciparcer.parse_ingredients(recipe.ingredients),
        "timestamp": recipe.timestamp,
        "categories": [c.strip() for c in recipe.categories.split(",") if c.strip()],
        "difficulty": (int(recipe.difficulty) or 0) if recipe.difficulty else 0,
    }
    if recipe.author_name or recipe.social_links:
        attrs["attribution"] = {
            "name": recipe.author_name,
            "links": [
                {"type": "TODO", "link": link}
                for link in (
                    recipe.social_links.split("\n") if recipe.social_links else []
                )
            ],
        }
    optional_attrs = {
        "yields": None,  # TODO
        "yieldsUnit": None,  # TODO
        "prepTimeMinutes": int(recipe.prep_time) if recipe.prep_time else None,
        "cookTimeMinutes": int(recipe.cook_time) if recipe.cook_time else None,
        "cuisine": recipe.cuisine.split(", ") if recipe.cuisine else None,
        "diet": recipe.diet.split(", ") if recipe.diet else None,
    }

    for key, value in optional_attrs.items():
        if value:
            attrs[key] = value

    logging.debug("parsing")
    logging.debug(f"csv row: {recipe}")
    logging.info("Successfully imported recipe")
    recipe = Recipe(**attrs)

    filename = get_recipe_filename(recipe)
    logging.debug(f"Recipe will be named {filename}")
    with open(path.join("..", "..", "data", "recipes", filename), "w") as fh:
        fh.write(json.dumps({**recipe, **additional_keys}, indent=2))  # type: ignore


def optional(value) -> t.Optional[t.Any]:
    return value if value else None


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("please pass the path to the file to build recipes from.")
        sys.exit(1)
    add_new_recipes(sys.argv[1])
