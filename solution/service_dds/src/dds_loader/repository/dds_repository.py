import uuid
from datetime import datetime
from typing import Dict, List

from lib.pg import PgConnect


def generate_uuid(*args) -> uuid.UUID:
    return uuid.uuid5(
        uuid.NAMESPACE_OID,
        "_".join(map(str, args))
    )

class DdsRepository:
    def __init__(self, db: PgConnect) -> None:
        self._db = db

    def insert_order(self, msg: Dict) -> None:
        payload = msg["payload"]

        user = payload["user"]
        restaurant = payload["restaurant"]
        products = payload["products"]
        
        order_dt = datetime.strptime(payload["date"], "%Y-%m-%d %H:%M:%S")
        load_dt = datetime.utcnow()
        load_src = "stg-service-orders"

        with self._db.connection() as conn:
            
            # ХАБЫ
            h_user_pk = generate_uuid(str(user["id"]))
            conn.execute(
                """
                INSERT INTO dds.h_user(
                    h_user_pk,
                    user_id,
                    load_dt,
                    load_src
                )
                VALUES (%s,%s,%s,%s)
                ON CONFLICT DO NOTHING
                """,
                (
                    h_user_pk,
                    user["id"],
                    load_dt,
                    load_src
                )
            )
        
            h_restaurant_pk = generate_uuid(str(restaurant["id"]))
            conn.execute(
                """
                INSERT INTO dds.h_restaurant(
                    h_restaurant_pk,
                    restaurant_id,
                    load_dt,
                    load_src
                )
                VALUES (%s,%s,%s,%s)
                ON CONFLICT DO NOTHING
                """,
                (
                    h_restaurant_pk,
                    restaurant["id"],
                    load_dt,
                    load_src
                )
            )

            h_order_pk = generate_uuid(str(payload["id"]))
            conn.execute(
                """
                INSERT INTO dds.h_order(
                    h_order_pk,
                    order_id,
                    order_dt,
                    load_dt,
                    load_src
                )
                VALUES (%s,%s,%s,%s,%s)
                ON CONFLICT DO NOTHING
                """,
                (
                    h_order_pk,
                    payload["id"],
                    order_dt,
                    load_dt,
                    load_src
                )
            )

            for product in products:
                h_product_pk = generate_uuid(str(product["id"]))
                conn.execute(
                    """
                    INSERT INTO dds.h_product(
                        h_product_pk,
                        product_id,
                        load_dt,
                        load_src
                    )
                    VALUES (%s,%s,%s,%s)
                    ON CONFLICT DO NOTHING
                    """,
                    (
                        h_product_pk,
                        product["id"],
                        load_dt,
                        load_src
                    )
                )
            
            unique_categories = {p["category"] for p in products}
            for category in unique_categories:
                h_category_pk = generate_uuid(category)
                conn.execute(
                    """
                    INSERT INTO dds.h_category(
                        h_category_pk,
                        category_name,
                        load_dt,
                        load_src
                    )
                    VALUES (%s,%s,%s,%s)
                    ON CONFLICT DO NOTHING
                    """,
                    (
                        h_category_pk,
                        category,
                        load_dt,
                        load_src
                    )
                )

            # ЛИНКИ
            conn.execute(
                """
                INSERT INTO dds.l_order_user(
                    hk_order_user_pk,
                    h_order_pk,
                    h_user_pk,
                    load_dt,
                    load_src
                )
                VALUES (%s,%s,%s,%s,%s)
                ON CONFLICT DO NOTHING
                """,
                (
                    generate_uuid(h_order_pk, h_user_pk),
                    h_order_pk,
                    h_user_pk,
                    load_dt,
                    load_src
                )
            )

            for product in products:          
                h_product_pk = generate_uuid(str(product["id"]))
                conn.execute(
                """
                INSERT INTO dds.l_order_product(
                    hk_order_product_pk,
                    h_order_pk,
                    h_product_pk,
                    load_dt,
                    load_src
                )
                VALUES (%s,%s,%s,%s,%s)
                ON CONFLICT DO NOTHING
                """,
                (
                    generate_uuid(h_order_pk, h_product_pk),
                    h_order_pk,
                    h_product_pk,
                    load_dt,
                    load_src
                )
            )

            if isinstance(products, dict):
                products = list(products.values())

            for product in products:

                if not isinstance(product, dict):
                    continue
                h_product_pk = generate_uuid(str(product.get("id")))

                category = product.get("category")
                if not category:
                    continue  # или можно пропустить связь

                h_category_pk = generate_uuid(category)

                conn.execute(
                    """
                    INSERT INTO dds.l_product_category(
                        hk_product_category_pk,
                        h_product_pk,
                        h_category_pk,
                        load_dt,
                        load_src
                    )
                    VALUES (%s,%s,%s,%s,%s)
                    ON CONFLICT DO NOTHING
                    """,
                    (
                        generate_uuid(h_product_pk, h_category_pk),
                        h_product_pk,
                        h_category_pk,
                        load_dt,
                        load_src
                    )
                )
           
            for product in products:
                h_product_pk = generate_uuid(str(product["id"]))
                conn.execute(
                """
                INSERT INTO dds.l_product_restaurant(
                    hk_product_restaurant_pk,
                    h_product_pk,
                    h_restaurant_pk,
                    load_dt,
                    load_src
                )
                VALUES (%s,%s,%s,%s,%s)
                ON CONFLICT DO NOTHING
                """,
                (
                    generate_uuid(h_product_pk, h_restaurant_pk),
                    h_product_pk,
                    h_restaurant_pk,
                    load_dt,
                    load_src
                )
            )

            # САТТЕЛИТЫ
            conn.execute(
                """
                INSERT INTO dds.s_user_names(
                    h_user_pk,
                    username,
                    userlogin,
                    load_dt,
                    load_src,
                    hk_user_names_hashdiff
                )
                VALUES (%s,%s,%s,%s,%s,%s)
                ON CONFLICT DO NOTHING

                """,
                (
                    h_user_pk,
                    user["name"],
                    user["login"],
                    load_dt,
                    load_src,
                    generate_uuid(
                        str(user["id"]),
                        str(user["name"]),
                        str(user["login"])
                    )
                )
            )

            for product in products:
                h_product_pk = generate_uuid(str(product["id"]))
                conn.execute(
                    """
                    INSERT INTO dds.s_product_names(
                        h_product_pk,
                        name,
                        load_dt,
                        load_src,
                        hk_product_names_hashdiff
                    )
                    VALUES (%s,%s,%s,%s,%s)
                    ON CONFLICT DO NOTHING

                    """,
                    (
                        h_product_pk,
                        product["name"],
                        load_dt,
                        load_src,
                        generate_uuid(str(product["id"]), str(product["name"]))
                    )
                )

            conn.execute(
                """
                INSERT INTO dds.s_restaurant_names(
                    h_restaurant_pk,
                    name,
                    load_dt,
                    load_src,
                    hk_restaurant_names_hashdiff
                )
                VALUES (%s,%s,%s,%s,%s)
                ON CONFLICT DO NOTHING

                """,
                (
                    h_restaurant_pk,
                    restaurant["name"],
                    load_dt,
                    load_src,
                    generate_uuid(str(restaurant["id"]), str(restaurant["name"]))
                )
            )

            conn.execute(
                """
                INSERT INTO dds.s_order_cost(
                    h_order_pk,
                    cost,
                    payment,
                    load_dt,
                    load_src,
                    hk_order_cost_hashdiff
                )
                VALUES (%s,%s,%s,%s,%s,%s)
                ON CONFLICT DO NOTHING

                """,
                (
                    h_order_pk,
                    payload["cost"],
                    payload["payment"],
                    load_dt,
                    load_src,
                    generate_uuid(str(payload["cost"]), str(payload["payment"]))
                )
            )

            conn.execute(
                """
                INSERT INTO dds.s_order_status(
                    h_order_pk,
                    status,
                    load_dt,
                    load_src,
                    hk_order_status_hashdiff
                )
                VALUES (%s,%s,%s,%s,%s)
                ON CONFLICT DO NOTHING

                """,
                (
                    h_order_pk,
                    payload["status"],
                    load_dt,
                    load_src,
                    generate_uuid(str(payload["id"]), str(payload["status"]))
                )
            )
