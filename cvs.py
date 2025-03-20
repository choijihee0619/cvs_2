from mysql.connector import MySQLConnection, Error
from configparser import ConfigParser

# ========================= MySQL 연결 및 설정 =========================
def read_config(filename='app.ini', section='mysql'):    
    """ app.ini 파일에서 데이터베이스 연결 정보를 읽어오는 함수 """
    config = ConfigParser()
    config.read(filename)
    data = {}
    if config.has_section(section):
        items = config.items(section)
        for item in items:
            data[item[0]] = item[1]
    else:
        raise Exception(f'{section} section not found in the {filename} file')
    return data

def connect():
    """ MySQL 데이터베이스 연결 """
    try:
        print('Connecting to MySQL database...')
        config = read_config()
        conn = MySQLConnection(**config)
        return conn
    except Error as error:
        print(error)
        return None

# ========================= 1️ 발주 및 영수증 조회 =========================
def place_order(conn):
    """ 스토어에서 상품을 발주 (스토어 ID, 상품 ID, 수량 입력) """
    store_id = int(input("스토어 ID 입력 >>> "))
    product_id = int(input("상품 ID 입력 >>> "))
    quantity = int(input("주문 수량 입력 >>> "))

    query = "INSERT INTO order_details (order_id, product_id, quantity) VALUES (%s, %s, %s)"
    args = (store_id, product_id, quantity)

    with conn.cursor() as cursor:
        cursor.execute(query, args)
    conn.commit()

    print("발주가 완료되었습니다!")

from datetime import datetime

def get_order_receipt(conn):
    """ 주문 상세 영수증 조회 (가게 검색 → 공급업체 검색 & 선택 → 주문 목록 출력 → 상세 조회) """

    #   가게 이름 검색 (LIKE 검색)
    store_keyword = input("검색할 가게명을 입력하세요 (예: 'GS' 입력 시 GS25 검색) >>> ").strip()

    query = "SELECT store_id, name FROM store WHERE name LIKE %s"
    param = (f"%{store_keyword}%",)
    with conn.cursor() as cursor:
        cursor.execute(query, param)
        stores = cursor.fetchall()

    if not stores:
        print("검색된 가게가 없습니다.")
        return

    print("\n=== 검색된 가맹점 목록 ===")
    for store in stores:
        print(f"ID: {store[0]}, 매장명: {store[1]}")

    store_id = int(input("스토어 ID를 선택하세요 >>> "))

    #   공급업체 이름 검색 (LIKE 검색)
    supplier_keyword = input("검색할 공급업체명을 입력하세요 (예: '농심' 입력 시 농심 검색) >>> ").strip()

    query = "SELECT supplier_id, name FROM supplier WHERE name LIKE %s"
    param = (f"%{supplier_keyword}%",)
    with conn.cursor() as cursor:
        cursor.execute(query, param)
        suppliers = cursor.fetchall()

    if not suppliers:
        print(" 검색된 공급업체가 없습니다.")
        return

    print("\n=== 검색된 공급업체 목록 ===")
    supplier_dict = {}
    for idx, supplier in enumerate(suppliers, start=1):
        print(f"{idx}. ID: {supplier[0]}, 공급업체명: {supplier[1]}")
        supplier_dict[idx] = supplier[0]  # 공급업체 선택을 위해 딕셔너리 저장

    while True:
        try:
            supplier_choice = int(input("선택할 공급업체 번호를 입력하세요 >>> "))
            if supplier_choice in supplier_dict:
                supplier_id = supplier_dict[supplier_choice]
                break
            else:
                print(" 잘못된 입력입니다. 다시 선택하세요.")
        except ValueError:
            print(" 숫자로 입력하세요.")

    #   선택한 가게 & 공급업체 관련 주문 목록 출력
    query = """
        SELECT 
            o.order_id, 
            o.order_date, 
            o.status
        FROM order_table o
        WHERE o.store_id = %s AND o.supplier_id = %s
        ORDER BY o.order_date DESC
    """

    with conn.cursor() as cursor:
        cursor.execute(query, (store_id, supplier_id))
        orders = cursor.fetchall()

    if not orders:
        print(" 해당 가게가 해당 공급업체에서 발주한 주문이 없습니다.")
        return

    print("\n=== 주문 목록 ===")
    order_dict = {}
    for idx, order in enumerate(orders, start=1):
        print(f"{idx}. 주문 ID: {order[0]}, 주문일자: {order[1]}, 상태: {order[2]}")
        order_dict[idx] = order[0]  # 주문 선택을 위해 딕셔너리 저장

    while True:
        try:
            order_choice = int(input("상세 조회할 주문 번호를 입력하세요 >>> "))
            if order_choice in order_dict:
                order_id = order_dict[order_choice]
                break
            else:
                print(" 잘못된 입력입니다. 다시 선택하세요.")
        except ValueError:
            print(" 숫자로 입력하세요.")

    #  선택한 주문 ID에 대한 상세 영수증 출력
    query = """
        SELECT 
            o.order_id,
            o.order_date, 
            s.name AS store_name,
            sp.name AS supplier_name,
            GROUP_CONCAT(p.name SEPARATOR ', ') AS product_names,  -- 상품명을 한 줄로 출력
            SUM(od.quantity) AS total_quantity
        FROM order_table o
        JOIN order_details od ON o.order_id = od.order_id
        JOIN product p ON od.product_id = p.product_id
        JOIN store s ON o.store_id = s.store_id
        JOIN supplier sp ON o.supplier_id = sp.supplier_id
        WHERE o.order_id = %s
        GROUP BY o.order_id, o.order_date, s.name, sp.name
    """

    with conn.cursor() as cursor:
        cursor.execute(query, (order_id,))
        row = cursor.fetchone()

    if row:
        print("\n=== 주문 상세 영수증 ===")
        print(f"주문 ID: {row[0]}")
        print(f"주문일자: {row[1]}")
        print(f"가게: {row[2]}")
        print(f"공급업체: {row[3]}")
        print(f"상품명: {row[4]}")
        print(f"총 수량: {row[5]}")
        print("-" * 50)  # 가독성을 위한 구분선
    else:
        print("해당 주문의 상세 정보를 찾을 수 없습니다.")

# ========================= 2️ 가맹점별 재고 조회 및 업데이트 =========================
def get_store_inventory(conn):
    """ 가게 이름으로 검색 후 선택하여 해당 가게의 재고 목록 출력 """

    # 가게 이름 검색 (LIKE 검색)
    store_keyword = input("검색할 가게명을 입력하세요 (예: 'GS' 입력 시 GS25 검색) >>> ").strip()

    query = "SELECT store_id, name FROM store WHERE name LIKE %s"
    param = (f"%{store_keyword}%",)
    with conn.cursor() as cursor:
        cursor.execute(query, param)
        stores = cursor.fetchall()

    if not stores:
        print("검색된 가게가 없습니다.")
        return

    print("\n=== 검색된 가맹점 목록 ===")
    for store in stores:
        print(f"ID: {store[0]}, 매장명: {store[1]}")

    store_id = int(input("스토어 ID를 선택하세요 >>> "))

    # 선택한 가게의 재고 목록 출력
    query = """
        SELECT 
            p.name AS product_name,
            p.category,
            s.quantity,
            s.last_updated
        FROM stock s
        JOIN product p ON s.product_id = p.product_id
        WHERE s.store_id = %s
        ORDER BY p.name ASC
    """

    with conn.cursor() as cursor:
        cursor.execute(query, (store_id,))
        stocks = cursor.fetchall()

    if not stocks:
        print("해당 가게의 재고가 없습니다.")
        return

    print("\n=== 현재 재고 현황 ===")
    print(f"선택한 가게 ID: {store_id}")
    print("-------------------------------------------------")
    print("상품명 | 카테고리 | 수량 | 마지막 업데이트")
    print("-------------------------------------------------")
    for stock in stocks:
        print(f"{stock[0]} | {stock[1]} | {stock[2]} | {stock[3]}")
    print("-------------------------------------------------")


def update_stock_on_delivery(conn):
    """ 주문 상태가 Delivered로 변경되면 재고 자동 추가 """
    query = """
        UPDATE stock st
        JOIN order_details od ON st.product_id = od.product_id
        JOIN order_table o ON od.order_id = o.order_id
        SET st.quantity = st.quantity + od.quantity
        WHERE o.status = 'Delivered'
    """

    with conn.cursor() as cursor:
        cursor.execute(query)
    conn.commit()
    
    print("재고가 업데이트되었습니다!")

# ========================= 3️ 거래 및 영수증 조회 =========================
def process_transaction(conn):
    """ 고객이 상품을 구매하면 거래(판매) 등록 (스토어, 직원, 상품 LIKE 검색 & 결제 방식 선택 포함) """
    try:
        # 1️ **스토어 검색 & 선택 (LIKE 검색)**
        store_keyword = input("검색할 스토어명을 입력하세요 >>> ")
        query = "SELECT store_id, name FROM store WHERE name LIKE %s"
        param = (f"%{store_keyword}%",)
        with conn.cursor() as cursor:
            cursor.execute(query, param)
            stores = cursor.fetchall()

        if not stores:
            print(" 검색된 스토어가 없습니다.")
            return

        print("\n=== 검색된 가맹점 목록 ===")
        for store in stores:
            print(f"ID: {store[0]}, 매장명: {store[1]}")

        store_id = int(input("스토어 ID를 선택하세요 >>> "))

        # 2️ **직원 검색 & 선택 (LIKE 검색)**
        employee_keyword = input("검색할 직원 이름을 입력하세요 >>> ")
        query = "SELECT employee_id, name FROM employee WHERE store_id = %s AND name LIKE %s"
        param = (store_id, f"%{employee_keyword}%")
        with conn.cursor() as cursor:
            cursor.execute(query, param)
            employees = cursor.fetchall()

        if not employees:
            print(" 해당 매장에 검색된 직원이 없습니다.")
            return

        print("\n=== 검색된 직원 목록 ===")
        for emp in employees:
            print(f"ID: {emp[0]}, 이름: {emp[1]}")

        employee_id = int(input("직원 ID를 선택하세요 >>> "))

        # 3️ **상품 검색 & 선택 (LIKE 검색)**
        product_keyword = input("검색할 상품명을 입력하세요 >>> ")
        query = "SELECT product_id, name, price FROM product WHERE name LIKE %s"
        param = (f"%{product_keyword}%",)
        with conn.cursor() as cursor:
            cursor.execute(query, param)
            products = cursor.fetchall()

        if not products:
            print(" 검색된 상품이 없습니다.")
            return

        print("\n=== 검색된 상품 목록 ===")
        for product in products:
            print(f"ID: {product[0]}, 상품명: {product[1]}, 가격: {product[2]}원")

        product_id = int(input("상품 ID를 선택하세요 >>> "))
        quantity = int(input("구매 수량 입력 >>> "))

        #  **현재 재고 확인**
        query = "SELECT quantity FROM stock WHERE store_id = %s AND product_id = %s"
        with conn.cursor() as cursor:
            cursor.execute(query, (store_id, product_id))
            stock_data = cursor.fetchone()

        if not stock_data:
            print(" 해당 상품이 이 매장에 등록되지 않았습니다.")
            return

        current_stock = stock_data[0]

        if current_stock < quantity:
            print(f" 재고 부족! 현재 재고: {current_stock}개, 요청 수량: {quantity}개")
            return

        # 4️ **결제 방식 선택**
        print('''
--------------------- 결제 방식 선택 ---------------------
1. 현금 (Cash)
2. 카드 (Card)
3. 모바일 결제 (Mobile Payment)
-------------------------------------------------------
        ''')
        payment_choice = input("결제 방식을 선택하세요 (1~3) >>> ").strip()

        if payment_choice == "1":
            payment_method = "Cash"
        elif payment_choice == "2":
            payment_method = "Card"
        elif payment_choice == "3":
            payment_method = "Mobile Payment"
        else:
            print(" 잘못된 입력입니다. 기본값(카드)으로 설정합니다.")
            payment_method = "Card"

        #  거래 추가 (결제 방식 반영)
        with conn.cursor() as cursor:
            query = "INSERT INTO transaction (store_id, employee_id, transaction_date, payment_method) VALUES (%s, %s, NOW(), %s)"
            args = (store_id, employee_id, payment_method)
            cursor.execute(query, args)
            transaction_id = cursor.lastrowid  # 새로 삽입된 거래의 ID 가져오기

            #  거래 상세 추가
            query = "INSERT INTO transaction_details (transaction_id, product_id, quantity) VALUES (%s, %s, %s)"
            args = (transaction_id, product_id, quantity)
            cursor.execute(query, args)

            #  재고 감소 (판매된 수량만큼 stock 감소)
            query = "UPDATE stock SET quantity = quantity - %s WHERE store_id = %s AND product_id = %s"
            args = (quantity, store_id, product_id)
            cursor.execute(query, args)

        conn.commit()  # 모든 변경사항을 DB에 반영
        print(f" 거래가 성공적으로 완료되었습니다! (거래 ID: {transaction_id})")
        print(f" 재고 감소 완료! {product_keyword} 남은 재고: {current_stock - quantity}개")

    except Error as error:
        conn.rollback()  #  오류 발생 시 롤백
        print(f" 거래 처리 중 오류 발생: {error}")


def get_transaction_receipt(conn):
    """ 거래 상세 영수증 조회 (가게 검색 → 직원 검색 & 선택 → 직원이 처리한 거래 목록 → 거래 상세 조회) """

    # 5
    # 가게 이름 검색 (LIKE 검색)
    store_keyword = input("검색할 가게명을 입력하세요 (예: 'GS' 입력 시 GS25 검색) >>> ").strip()

    query = "SELECT store_id, name FROM store WHERE name LIKE %s"
    param = (f"%{store_keyword}%",)
    with conn.cursor() as cursor:
        cursor.execute(query, param)
        stores = cursor.fetchall()

    if not stores:
        print("검색된 가게가 없습니다.")
        return

    print("\n=== 검색된 가맹점 목록 ===")
    for store in stores:
        print(f"ID: {store[0]}, 매장명: {store[1]}")

    store_id = int(input("스토어 ID를 선택하세요 >>> "))

    # 직원 이름 검색 (LIKE 검색)
    employee_keyword = input("검색할 직원 이름을 입력하세요 (예: '철수' 입력 시 김철수 검색) >>> ").strip()

    query = "SELECT employee_id, name FROM employee WHERE store_id = %s AND name LIKE %s"
    param = (store_id, f"%{employee_keyword}%")
    with conn.cursor() as cursor:
        cursor.execute(query, param)
        employees = cursor.fetchall()

    if not employees:
        print("해당 매장에서 검색된 직원이 없습니다.")
        return

    print("\n=== 검색된 직원 목록 ===")
    employee_dict = {}
    for idx, emp in enumerate(employees, start=1):
        print(f"{idx}. ID: {emp[0]}, 이름: {emp[1]}")
        employee_dict[idx] = emp[0]  # 직원 선택을 위해 딕셔너리 저장

    while True:
        try:
            employee_choice = int(input("선택할 직원 번호를 입력하세요 >>> "))
            if employee_choice in employee_dict:
                employee_id = employee_dict[employee_choice]
                break
            else:
                print("잘못된 입력입니다. 다시 선택하세요.")
        except ValueError:
            print("숫자로 입력하세요.")

    # 해당 직원이 담당한 거래 목록 출력 (거래 ID - 거래일자 - 총 금액)
    query = """
        SELECT 
            t.transaction_id, 
            t.transaction_date, 
            SUM(td.quantity * p.price) AS total_price
        FROM transaction t
        JOIN transaction_details td ON t.transaction_id = td.transaction_id
        JOIN product p ON td.product_id = p.product_id
        WHERE t.employee_id = %s
        GROUP BY t.transaction_id, t.transaction_date
        ORDER BY t.transaction_date DESC
    """

    with conn.cursor() as cursor:
        cursor.execute(query, (employee_id,))
        transactions = cursor.fetchall()

    if not transactions:
        print("해당 직원이 처리한 거래가 없습니다.")
        return

    print("\n=== 해당 직원이 처리한 거래 목록 ===")
    transaction_dict = {}
    for idx, trans in enumerate(transactions, start=1):
        print(f"{idx}. 거래 ID: {trans[0]}, 거래일자: {trans[1]}, 총 결제 금액: {trans[2]} 원")
        transaction_dict[idx] = trans[0]  # 거래 선택을 위해 딕셔너리 저장

    while True:
        try:
            transaction_choice = int(input("상세 조회할 거래 번호를 입력하세요 >>> "))
            if transaction_choice in transaction_dict:
                transaction_id = transaction_dict[transaction_choice]
                break
            else:
                print("잘못된 입력입니다. 다시 선택하세요.")
        except ValueError:
            print("숫자로 입력하세요.")

    # 선택한 거래 ID에 대한 상세 영수증 출력
    query = """
        SELECT 
            t.transaction_id,
            t.transaction_date, 
            s.name AS store_name,
            e.name AS employee_name,
            GROUP_CONCAT(p.name SEPARATOR ', ') AS product_names,  -- 상품명을 한 줄로 출력
            SUM(td.quantity) AS total_quantity, 
            SUM(td.quantity * p.price) AS total_price
        FROM transaction t
        JOIN transaction_details td ON t.transaction_id = td.transaction_id
        JOIN product p ON td.product_id = p.product_id
        JOIN store s ON t.store_id = s.store_id
        JOIN employee e ON t.employee_id = e.employee_id
        WHERE t.transaction_id = %s
        GROUP BY t.transaction_id, t.transaction_date, s.name, e.name
    """

    with conn.cursor() as cursor:
        cursor.execute(query, (transaction_id,))
        row = cursor.fetchone()

    if row:
        print("\n=== 거래 상세 영수증 ===")
        print(f"거래 ID: {row[0]}")
        print(f"거래일자: {row[1]}")
        print(f"가게: {row[2]}")
        print(f"직원: {row[3]}")
        print(f"상품명: {row[4]}")
        print(f"총 수량: {row[5]}")
        print(f"총 결제 금액: {row[6]} 원")
        print("-" * 50)  # 가독성을 위한 구분선
    else:
        print("해당 거래의 상세 정보를 찾을 수 없습니다.")


# ========================= 4️⃣ 직원 관리 =========================
def get_top_employees(conn):
    """ 가장 판매를 많이 한 직원 조회 (이달의 판매왕) """
    query = """
        SELECT e.employee_id, e.name, SUM(td.quantity * p.price) AS total_sales
        FROM employee e
        JOIN transaction t ON e.employee_id = t.employee_id
        JOIN transaction_details td ON t.transaction_id = td.transaction_id
        JOIN product p ON td.product_id = p.product_id
        GROUP BY e.employee_id
        ORDER BY total_sales DESC
    """

    with conn.cursor() as cursor:
        cursor.execute(query)
        rows = cursor.fetchall()

    print("\n=== 이달의 판매왕 ===")
    for row in rows:
        print(row)

# ========================= 실행 코드 =========================
if __name__ == '__main__':
    conn = connect()

    while True:
        display = '''
-------------------------------------------------------------
1. 발주, 2. 주문 영수증 조회, 3. 재고 조회, 4. 재고 업데이트 (Delivered)
5. 거래 등록, 6. 거래 영수증 조회, 7. 이달의 판매왕 조회, 8. 종료
-------------------------------------------------------------
메뉴를 선택하세요 >>> '''
        
        choice = input(display).strip()

        if choice == "1":
            place_order(conn)
        elif choice == "2":
            get_order_receipt(conn)
        elif choice == "3":
            get_store_inventory(conn)
        elif choice == "4":
            update_stock_on_delivery(conn)
        elif choice == "5":
            process_transaction(conn)
        elif choice == "6":
            get_transaction_receipt(conn)
        elif choice == "7":
            get_top_employees(conn)
        elif choice == "8":
            print("프로그램을 종료합니다.")
            conn.close()
            break
