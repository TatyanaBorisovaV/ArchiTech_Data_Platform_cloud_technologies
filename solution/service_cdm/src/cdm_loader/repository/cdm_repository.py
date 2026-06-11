from uuid import UUID

from lib.pg import PgConnect


class CdmRepository:

    def __init__(self, pg: PgConnect):
        self._db = pg

    def increment_user_product_counter(
        self,
        user_id: UUID,
        product_id: UUID,
        product_name: str,
        cnt: int
    ) -> None:


        with self._db.connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO cdm.user_product_counters
                    (
                        user_id,
                        product_id,
                        product_name,
                        order_cnt
                    )
                    VALUES (%s, %s, %s, %s)

                    ON CONFLICT (user_id, product_id)
                    DO UPDATE
                    SET order_cnt =
                        cdm.user_product_counters.order_cnt
                        + EXCLUDED.order_cnt
                    """,
                    (
                        user_id,
                        product_id,
                        product_name,
                        cnt
                    )
                )

    def increment_user_category_counter(
        self,
        user_id: UUID,
        category_id: UUID,
        category_name: str,
        cnt: int
    ) -> None:

        with self._db.connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO cdm.user_category_counters
                    (
                        user_id,
                        category_id,
                        category_name,
                        order_cnt
                    )
                    VALUES (%s, %s, %s, %s)

                    ON CONFLICT (user_id, category_id)
                    DO UPDATE
                    SET order_cnt =
                        cdm.user_category_counters.order_cnt
                        + EXCLUDED.order_cnt
                    """,
                    (
                        user_id,
                        category_id,
                        category_name,
                        cnt
                    )
                )
