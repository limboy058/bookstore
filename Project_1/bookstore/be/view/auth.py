from flask import Blueprint
from flask import request
from flask import jsonify
from be.model import user
from be.model.book import searchBook

bp_auth = Blueprint("auth", __name__, url_prefix="/auth")


@bp_auth.route("/login", methods=["POST"])
def login():
    user_id = request.json.get("user_id", "")
    password = request.json.get("password", "")
    terminal = request.json.get("terminal", "")
    u = user.User()
    code, message, token = u.login(user_id=user_id,
                                   password=password,
                                   terminal=terminal)
    return jsonify({"message": message, "token": token}), code


@bp_auth.route("/logout", methods=["POST"])
def logout():
    user_id: str = request.json.get("user_id")
    token: str = request.headers.get("token")
    u = user.User()
    code, message = u.logout(user_id=user_id, token=token)
    return jsonify({"message": message}), code


@bp_auth.route("/register", methods=["POST"])
def register():
    user_id = request.json.get("user_id", "")
    password = request.json.get("password", "")
    u = user.User()
    code, message = u.register(user_id=user_id, password=password)
    return jsonify({"message": message}), code


@bp_auth.route("/unregister", methods=["POST"])
def unregister():
    user_id = request.json.get("user_id", "")
    password = request.json.get("password", "")
    u = user.User()
    code, message = u.unregister(user_id=user_id, password=password)
    return jsonify({"message": message}), code


@bp_auth.route("/password", methods=["POST"])
def change_password():
    user_id = request.json.get("user_id", "")
    old_password = request.json.get("oldPassword", "")
    new_password = request.json.get("newPassword", "")
    u = user.User()
    code, message = u.change_password(user_id=user_id,
                                      old_password=old_password,
                                      new_password=new_password)
    return jsonify({"message": message}), code


@bp_auth.route("/search_book", methods=["POST"])
def search_book():
    searchbook = searchBook()
    page_no = request.json.get("page_no", "")
    page_size = request.json.get("page_size", "")
    foozytitle = request.json.get("foozytitle", None)
    reqtags = request.json.get("reqtags", None)
    id = request.json.get("id", None)
    isbn = request.json.get("isbn", None)
    author = request.json.get("author", None)
    lowest_price = request.json.get("lowest_price", None)
    highest_price = request.json.get("highest_price", None)
    lowest_pub_year = request.json.get("lowest_pub_year", None)
    highest_pub_year = request.json.get("highest_pub_year", None)
    store_id = request.json.get("store_id", None)
    publisher = request.json.get("publisher", None)
    translator = request.json.get("translator", None)
    binding = request.json.get("binding", None)
    order_by_method = request.json.get("order_by_method", None)
    having_stock = request.json.get("having_stock", None)
    code, message, res = searchbook.find_book(
        page_no=page_no,
        page_size=page_size,
        foozytitle=foozytitle,
        reqtags=reqtags,
        id=id,
        isbn=isbn,
        author=author,
        lowest_price=lowest_price,
        highest_price=highest_price,
        lowest_pub_year=lowest_pub_year,
        highest_pub_year=highest_pub_year,
        store_id=store_id,
        publisher=publisher,
        translator=translator,
        binding=binding,
        order_by_method=
        order_by_method,  # [stock_level, sales, pub_time, price] + [1,-1]  1 means increasingly and -1 means decreasingly
        having_stock=having_stock)
    return jsonify({"message": message, "book_info": res}), code


@bp_auth.route("/search_order_detail", methods=["POST"])
def search_order_detail():
    order_id = request.json.get("order_id")
    u = user.User()
    code, message, order_detail_list = u.search_order_detail(order_id)
    return jsonify({
        "message": message,
        "order_detail_list": order_detail_list
    }), code
