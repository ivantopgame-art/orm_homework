import json
import sqlalchemy
from sqlalchemy.orm import sessionmaker
from models import Base, Publisher, Shop, Book, Stock, Sale

# ===== НАСТРОЙКА ПОДКЛЮЧЕНИЯ =====
# Вместо password введи свой пароль от PostgreSQL
# Вместо your_db введи название своей базы данных
DSN = "postgresql://postgres:volhin21@localhost:5432/book_db"

# Создаём движок (подключение к БД)
engine = sqlalchemy.create_engine(DSN)

# Создаём таблицы (если их нет)
Base.metadata.create_all(engine)

# Создаём сессию для работы с БД
Session = sessionmaker(bind=engine)
session = Session()

# ===== ЗАГРУЗКА ДАННЫХ ИЗ JSON =====
with open('fixtures/tests_data.json', 'r', encoding='utf-8') as fd:
    data = json.load(fd)

for record in data:
    model = {
        'publisher': Publisher,
        'shop': Shop,
        'book': Book,
        'stock': Stock,
        'sale': Sale,
    }[record.get('model')]
    session.add(model(id=record.get('pk'), **record.get('fields')))

session.commit()
print("✅ Данные загружены в БД")


# ===== ФУНКЦИЯ ПОИСКА ПО ИЗДАТЕЛЮ =====
def get_sales_by_publisher(publisher_input):
    """
    Принимает имя или ID издателя
    Выводит: книга | магазин | цена | дата
    """
    # Определяем, ввели ID или имя
    if publisher_input.isdigit():
        publisher_id = int(publisher_input)
        publisher_name = None
    else:
        publisher_id = None
        publisher_name = publisher_input

    # Составляем запрос
    query = session.query(
        Book.title,
        Shop.name,
        Sale.price,
        Sale.date_sale
    ).join(Publisher, Book.id_publisher == Publisher.id
           ).join(Stock, Stock.id_book == Book.id
                  ).join(Shop, Shop.id == Stock.id_shop
                         ).join(Sale, Sale.id_stock == Stock.id)

    # Фильтруем по издателю
    if publisher_id:
        query = query.filter(Publisher.id == publisher_id)
    else:
        query = query.filter(Publisher.name == publisher_name)

    # Выполняем запрос
    results = query.all()

    if not results:
        print("❌ Ничего не найдено")
        return

    # Выводим результаты
    print("\n📚 Результаты:")
    for title, shop_name, price, date in results:
        print(f"{title} | {shop_name} | {price} | {date.strftime('%d-%m-%Y')}")


# ===== ОСНОВНАЯ ЧАСТЬ ПРОГРАММЫ =====
if __name__ == "__main__":
    # Ввод данных от пользователя
    publisher_input = input("Введите имя или ID издателя: ")
    get_sales_by_publisher(publisher_input)

    # Закрываем сессию
    session.close()