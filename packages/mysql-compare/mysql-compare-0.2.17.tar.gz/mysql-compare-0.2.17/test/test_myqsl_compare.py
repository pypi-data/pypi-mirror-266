import mysql_compare

if __name__ == "__main__":
    MysqlTableCompare(
        {"host": "192.168.161.2", "port": 3306, "user": "dtle_sync", "password": "dtle_sync"},
        {"host": "192.168.161.93", "port": 3306, "user": "dtle_sync", "password": "dtle_sync"},
        "merchant_center_vela_v1",
        "mc_products_to_tags",
        "merchant_center_vela_v1",
        "mc_products_to_tags",
    ).run()
