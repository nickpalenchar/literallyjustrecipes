from openai import OpenAI
import json
import os

script_dir = os.path.dirname(os.path.abspath(__file__))


with open(os.path.join(script_dir, "../../../../secrets.json")) as fh:
    secrets = json.loads(fh.read())


def main():
    client = OpenAI(api_key=secrets["OPENAPI_SECRET_KEY"])

    with open(os.path.join(script_dir, "../../../../data/schemas/recipes.json")) as fh:
        recipe_schema = fh.read()

    response = client.chat.completions.create(
        model="gpt-3.5-turbo-1106",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {
                "role": "user",
                "content": f"This is a JSON Schema that expresses a cooking recipe. Do you understand it?\n{recipe_schema}",
            },
            {
                "role": "system",
                "content": "Yes, I understand the JSON schema. It defines the structure and constraints for a cooking recipe. It includes properties for the recipe name, summary, cuisine, diet, difficulty level, cooking time, ingredients, steps, and more.The schema also defines the required properties for a valid recipe. If you have any specific questions or need help with anything related to this JSON schema, feel free to ask!",
            },
            {
                "role": "user",
                "content": "Do you think you can translate a written english recipe into this json schema?"
            }
        ],
    )
    print(response.choices[0].message.content)


if __name__ == "__main__":
    main()
