from be.conf import *

error_code = {
    401: "authorization fail.",
    511: "non exist user id {}",
    512: "exist user id {}",
    513: "non exist store id {}",
    514: "exist store id {}",
    515: "non exist book id {}",
    516: "exist book id {}",
    517: "stock level low, book id {}",
    518: "invalid order id {}",
    519: "not sufficient funds, order id {}",
    520: "non exist order id {}",
    521: "non processing order id {}",
    522: "order condition not exists {}",
    523: "unmatched user id {}, order_id {}",
    524: "book {} out of stock",
    525: "not enough fund id{}",
    526: "unfished buyer orders",
    527: "unfished seller orders",
    532: "unmatched order {} and store {}",
    529: "unmatched order {} and user {}",
    531: "unmatched store {} and user {}",
    541: "order {} amount exceeds limit ({}})",
    542: "order {} book types exceed limit ({})",
    543: "add amount exceeds limit ({})",
    544: "store {} book types exceed limit ({})"
}

def error_order_amount_ex(order_id):
    return 541, error_code[541].format(order_id,Order_amount_limit)

def error_order_book_type_ex(order_id):
    return 542, error_code[542].format(order_id,Order_book_type_limit)

def error_add_amount_ex():
    return 543, error_code[543].format(Add_amount_limit)

def error_store_book_type_ex(store_id):
    return 544, error_code[544].format(store_id,Store_book_type_limit)



def error_unfished_buyer_orders():
    return 526, error_code[526]


def error_unfished_seller_orders():
    return 527, error_code[527]


def error_non_exist_user_id(user_id):
    return 511, error_code[511].format(user_id)


def error_exist_user_id(user_id):
    return 512, error_code[512].format(user_id)


def error_non_exist_store_id(store_id):
    return 513, error_code[513].format(store_id)


def error_exist_store_id(store_id):
    return 514, error_code[514].format(store_id)


def error_non_exist_book_id(book_id):
    return 515, error_code[515].format(book_id)


def error_exist_book_id(book_id):
    return 516, error_code[516].format(book_id)


def error_stock_level_low(book_id):
    return 517, error_code[517].format(book_id)


def error_invalid_order_id(order_id):
    return 518, error_code[518].format(order_id)


def error_not_sufficient_funds(order_id):
    return 519, error_code[519].format(order_id)


def error_authorization_fail():
    return 401, error_code[401]


def error_and_message(code, message):
    return code, message


def error_non_exist_order_id(order_id):
    return 520, error_code[520].format(order_id)


def error_non_prossessing_order_id(order_id):
    return 521, error_code[521].format(order_id)


def error_illegal_order_condition(order_condition):
    return 522, error_code[522].format(order_condition)


def error_order_user_id(order_id, user_id):
    return 523, error_code[523].format(order_id, user_id)


def error_out_of_stock(book_id):
    return 524, error_code[524].format(book_id)


def error_non_enough_fund(user_id):
    return 525, error_code[525].format(user_id)


def unmatched_order_store(order_id, store_id):
    return 532, error_code[532].format(order_id, store_id)


def unmatched_order_user(order_id, user_id):
    return 529, error_code[529].format(order_id, user_id)


def unmatched_seller_store(seller_id, store_id):
    return 531, error_code[531].format(seller_id, store_id)
