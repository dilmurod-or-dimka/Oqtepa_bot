import psycopg2
from config import DB_USER, DB_HOST, DB_NAME, DB_PASSWORD
import random
from utils.helpers import read_json, format_price


class DataBase:
    def __init__(self):
        self.database = psycopg2.connect(
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST
        )

    def manager(self, sql, *args,
                fetchone: bool = False,
                fetchall: bool = False,
                fetchmany: bool = False,
                commit: bool = False):
        with self.database as db:
            with db.cursor() as cursor:
                cursor.execute(sql, args)
                if commit:
                    result = db.commit()
                elif fetchone:
                    result = cursor.fetchone()
                elif fetchall:
                    result = cursor.fetchall()
                elif fetchmany:
                    result = cursor.fetchmany()
            return result


class TableCreator(DataBase):
    def create_users_table(self):
        sql = """
            DROP TABLE IF EXISTS users;
            CREATE TABLE IF NOT EXISTS users(
                user_id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
                name TEXT,
                phone_number TEXT,
                chat_id BIGINT NOT NULL UNIQUE
            );
        """
        self.manager(sql, commit=True)

    def create_categories_table(self):
        sql = """
            DROP TABLE IF EXISTS categories;
            CREATE TABLE IF NOT EXISTS categories(
                category_id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
                category_title TEXT
            );
        """
        self.manager(sql, commit=True)

    def create_products_table(self):
        sql = """
            DROP TABLE IF EXISTS products;
            CREATE TABLE IF NOT EXISTS products(
                product_id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
                name TEXT,
                img_url TEXT,
                price TEXT,
                quantity INTEGER,
                description TEXT,
                category_id INTEGER REFERENCES categories(category_id)
            );
        """
        self.manager(sql, commit=True)

    def create_cart_table(self):
        sql = """
            DROP TABLE IF EXISTS cart CASCADE;
            CREATE TABLE IF NOT EXISTS cart(
                cart_id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
                user_id INTEGER NOT NULL UNIQUE,
                total_quantity INTEGER DEFAULT 0,
                total_price INTEGER DEFAULT 0,

                FOREIGN KEY (user_id) REFERENCES users(user_id)
            );
        """
        self.manager(sql, commit=True)

    def create_cart_products_table(self):
        sql = """
            DROP TABLE IF EXISTS cart_products;
            CREATE TABLE IF NOT EXISTS cart_products(
                cart_product_id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
                cart_id INTEGER NOT NULL,
                product_id INTEGER NOT NULL,

                quantity INTEGER DEFAULT 0,
                price INTEGER,

                FOREIGN KEY (cart_id) REFERENCES cart(cart_id),
                FOREIGN KEY (product_id) REFERENCES products(product_id),

                UNIQUE(cart_id, product_id)
            );
        """
        self.manager(sql, commit=True)


class UserManager(DataBase):
    def get_user_id(self, chat_id):
        sql = "SELECT user_id FROM users WHERE chat_id = %s;"
        return self.manager(sql, chat_id, fetchone=True)

    def add_user(self, name, phone_number, chat_id):
        sql = "INSERT INTO users(name, phone_number, chat_id) VALUES (%s, %s, %s);"
        self.manager(sql, name, phone_number, chat_id, commit=True)


class CategoryManager(DataBase):
    def get_categories(self):
        sql = "SELECT category_title FROM categories;"
        categories = self.manager(sql, fetchall=True)
        return [category[0] for category in categories]

    def get_category_id(self, category):
        sql = "SELECT category_id FROM categories WHERE category_title = %s;"
        return self.manager(sql, category, fetchone=True)[0]


class ProductManager(DataBase):
    def get_products_by_category(self, category_id):
        sql = "SELECT name FROM products WHERE category_id = %s;"
        titles = self.manager(sql, category_id, fetchall=True)
        return [title[0] for title in titles]

    def get_product_info(self, product_name):
        sql = """
            SELECT product_id, img_url, price, quantity, description
            FROM products WHERE name = %s;
        """
        return self.manager(sql, product_name, fetchone=True)

    def get_product_quantity(self, product_id):
        sql = "SELECT quantity FROM products WHERE product_id = %s;"
        return self.manager(sql, product_id, fetchone=True)[0]

    def get_product_price(self, product_id):
        sql = "SELECT price FROM products WHERE product_id = %s;"
        return self.manager(sql, product_id, fetchone=True)[0]


class CartManager(DataBase):
    def get_cart_info(self, user_id):
        sql = """
               SELECT total_price, total_quantity FROM cart
               WHERE user_id = %s
           """
        return self.manager(sql, user_id, fetchone=True)

    def add_user_id(self, user_id):
        sql = """INSERT INTO cart (user_id) VALUES (%s) ON CONFLICT (user_id) DO NOTHING;"""
        self.manager(sql, user_id, commit=True)

    def get_cart_id(self, user_id):
        sql = "SELECT cart_id FROM cart WHERE user_id = %s;"
        return self.manager(sql, user_id, fetchone=True)[0]

    def clear_cart(self, cart_id):
        sql = """
            DELETE FROM cart_products
            WHERE cart_id = %s;

            UPDATE cart 
            SET total_price = 0,
                total_quantity = 0;
        """
        self.manager(sql, cart_id, commit=True)


class CartProductManager(DataBase):
    def show_cart_items(self, cart_id):
        sql = """
            SELECT name, cart_products.quantity, cart_products.price FROM cart_products
            JOIN products USING(product_id) WHERE cart_id = %s;
        """
        return self.manager(sql, cart_id, fetchall=True)

    def update(self, cart_id, product_id, price, quantity):
        cursor = self.database.cursor()
        cursor.execute("""
        INSERT INTO cart_products(cart_id, product_id, price, quantity)
        VALUES(%(cart_id)s, %(product_id)s, %(price)s, %(quantity)s )
        ON CONFLICT (cart_id, product_id) DO UPDATE
        SET price = cart_products.price + %(price)s,
        quantity = %(quantity)s
        WHERE cart_products.cart_id = %(cart_id)s
        AND cart_products.product_id = %(product_id)s;

        UPDATE cart
        SET total_price = info.total_price,
        total_quantity = info.total_quantity

        FROM (
            SELECT SUM(quantity) AS total_quantity,
            SUM(price) AS total_price
            FROM cart_products
            WHERE cart_id = %(cart_id)s
        ) AS info;
        """, {
            "cart_id": cart_id,
            "product_id": product_id,
            "price": price,
            "quantity": quantity
        })
        self.database.commit()


class MainManager:
    def __init__(self):
        self.user: UserManager = UserManager()
        self.category: CategoryManager = CategoryManager()
        self.product: ProductManager = ProductManager()
        self.cart: CartManager = CartManager()
        self.cart_product: CartProductManager = CartProductManager()


creator = TableCreator()
# creator.create_cart_products_table()
# creator.create_cart_table()
# creator.create_products_table()
# creator.create_categories_table()
# creator.create_users_table()


def fill_categories_table(file_path, db: DataBase):
    categories = read_json(file_path)
    sql = "INSERT INTO categories(category_title) VALUES (%s);"
    for category in categories:
        db.manager(sql, category, commit=True)
        print(f"Добавили категорию: {category}")


def fill_products_table(file_path, db: DataBase):
    products_json = read_json(file_path)
    sql = """
        INSERT INTO products(name, img_url, price, quantity, description, category_id)
        VALUES(%s,%s,%s,%s,%s,%s);
    """
    for item in products_json:
        categories_sql = "SELECT category_id FROM categories WHERE category_title = %s;"
        category_id = db.manager(categories_sql, item["category"], fetchone=True)[0]  # ('a',)
        for product in item["products"]:
            quantity = random.randrange(1, 51)
            price = format_price(product["price"])
            db.manager(
                sql,
                product["name"],
                product["img"],
                price,
                quantity,
                product["description"],
                category_id,
                commit=True
            )
            print(f"Добавили продукт: {product['name']}")

# fill_products_table("../foods.json", DataBase())
# fill_categories_table("../categories.json", DataBase())
