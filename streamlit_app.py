# Importálás
import streamlit as st
from snowflake.snowpark import Session
from snowflake.snowpark.functions import col

# Cím és leírás
st.title(":cup_with_straw: Customize Your Smoothie :cup_with_straw:")
st.write("Choose the fruits you want in your custom Smoothie.")

# Felhasználónév megadása
name_on_order = st.text_input('Name on Smoothie:')
st.write("The name on your Smoothie will be:", name_on_order)

# Snowflake kapcsolódás - .streamlit/secrets.toml alapján
connection_parameters = {
    "account": st.secrets["account"],
    "user": st.secrets["user"],
    "password": st.secrets["password"],
    "role": st.secrets["role"],
    "warehouse": st.secrets["warehouse"],
    "database": st.secrets["database"],
    "schema": st.secrets["schema"]
}

# Session létrehozása
session = Session.builder.configs(connection_parameters).create()

# Gyümölcslista betöltése
try:
    fruit_df = session.table("smoothies.public.fruit_options").select(col('Fruit_name'))
    fruit_list = [row['FRUIT_NAME'] for row in fruit_df.collect()]
except Exception as e:
    st.error(f"Hiba történt a gyümölcslista betöltésekor: {e}")
    fruit_list = []

# Kiválasztás
ingredients_list = st.multiselect(
    "Choose up to 5 ingredients:",
    options=fruit_list,
    max_selections=5
)

# Ha van kiválasztva valami
if ingredients_list:
    ingredients_string = ', '.join(ingredients_list)
    insert_stmt = f"""
        INSERT INTO smoothies.public.orders (ingredients, name_on_order)
        VALUES ('{ingredients_string}', '{name_on_order}')
    """

    st.code(insert_stmt, language='sql')

    # Megrendelés gomb
    if st.button("Submit Order"):
        try:
            session.sql(insert_stmt).collect()
            st.success(f"Your Smoothie is ordered, {name_on_order}!", icon="✅")
        except Exception as e:
            st.error(f"Hiba a rendelés mentése közben: {e}")
