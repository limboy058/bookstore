from flask import Blueprint
from flask import request
from flask import jsonify
from be.model import seller
import json

bp_seller = Blueprint("seller", __name__, url_prefix="/seller")


@bp_seller.route("/create_store", methods=["POST"])
def seller_create_store():
    user_id: str = request.json.get("user_id")
    store_id: str = request.json.get("store_id")
    s = seller.Seller()
    code, message = s.create_store(user_id, store_id)
    return jsonify({"message": message}), code


@bp_seller.route("/add_book", methods=["POST"])
def seller_add_book():
    user_id: str = request.json.get("user_id")
    store_id: str = request.json.get("store_id")
    book_info: str = request.json.get("book_info")
    # book_id: str = request.json.get("book_id")

    # title: str = request.json.get("title")
    # author: str = request.json.get("author")
    # publisher: str = request.json.get("publisher")
    # original_title: str = request.json.get("original_title")
    # translator: str = request.json.get("translator")
    # pub_year: str = request.json.get("pub_year")
    # pages: int = request.json.get("pages")
    # price: int = request.json.get("price")
    # currency_unit: str = request.json.get("currency_unit")
    # binding: str = request.json.get("binding")
    # isbn: str = request.json.get("isbn")
    # author_intro: str = request.json.get("author_intro")
    # book_intro: str = request.json.get("book_intro")
    # content: str = request.json.get("content")
    # tags:list[str]=request.json.get("tags")
    # picture:list[bytes]=request.json.get("picture")
    stock_level: str = request.json.get("stock_level", 0)

    s = seller.Seller()
    code, message = s.add_book(
        user_id,
        store_id,
        book_info.get("id"),
        json.dumps(book_info),
        # book_id,
        # title,
        # author,
        # publisher,
        # original_title,
        # translator,
        # pub_year,
        # pages,
        # price,
        # currency_unit,
        # binding,
        # isbn,
        # author_intro,
        # book_info,
        # content,
        # tags,
        # picture,
        stock_level)

    return jsonify({"message": message}), code


@bp_seller.route("/del_book", methods=["POST"])
def del_book():
    user_id: str = request.json.get("user_id")
    store_id: str = request.json.get("store_id")
    book_id: str = request.json.get("book_id")
    s = seller.Seller()
    code, message = s.del_book(
        user_id,
        store_id,
        book_id,
        )
    return jsonify({"message": message}), code


@bp_seller.route("/add_stock_level", methods=["POST"])
def add_stock_level():
    user_id: str = request.json.get("user_id")
    store_id: str = request.json.get("store_id")
    book_id: str = request.json.get("book_id")
    add_num: str = request.json.get("add_stock_level", 0)
    s = seller.Seller()
    code, message = s.add_stock_level(user_id, store_id, book_id, add_num)

    return jsonify({"message": message}), code


@bp_seller.route("/send_books", methods=["POST"])
def send_books():
    store_id = request.json.get("store_id")
    order_id = request.json.get("order_id")
    s = seller.Seller()
    code, message = s.send_books(store_id, order_id)
    return jsonify({"message": message}), code


@bp_seller.route("/search_order", methods=["POST"])
def search_order():
    seller_id = request.json.get("seller_id")
    store_id = request.json.get("store_id")
    s = seller.Seller()
    code, message, order_id_list = s.search_order(seller_id, store_id)
    return jsonify({"message": message, "order_id_list": order_id_list}), code

@bp_seller.route("/cancel", methods=["POST"])
def cancel():
    store_id = request.json.get("store_id")
    order_id = request.json.get("order_id")
    b = seller.Seller()
    code, message = b.cancel(store_id, order_id)
    return jsonify({"message": message}), code