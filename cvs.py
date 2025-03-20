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

# ========================= 1️⃣ 발주 및 영수증 조회 =========================
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

def get_order_receipt(conn):
    """ 주문 상세 영수증 조회 """
    order_id = int(input("조회할 주문 ID 입력 >>> "))

    query = """
        SELECT o.order_id, s.name AS store_name, p.name AS product_name, od.quantity, o.status, sup.name AS supplier_name
        FROM order_table o
        JOIN order_details od ON o.order_id = od.order_id
        JOIN product p ON od.product_id = p.product_id
        JOIN supplier sup ON p.supplier_id = sup.supplier_id
        JOIN store s ON o.store_id = s.store_id
        WHERE o.order_id = %s
    """

    with conn.cursor() as cursor:
        cursor.execute(query, (order_id,))
        rows = cursor.fetchall()

    print("\n=== 주문 상세 영수증 ===")
    for row in rows:
        print(row)

# ========================= 2️⃣ 가맹점별 재고 조회 및 업데이트 =========================
def get_store_inventory(conn):
    """ 가맹점별 재고 현황 조회 (항상 최신 데이터 반영) """
    store_id = int(input("재고를 조회할 스토어 ID를 입력하세요 >>> "))

    query = """
        SELECT s.name AS store_name, p.name AS product_name, p.category, st.quantity
        FROM stock st
        JOIN store s ON st.store_id = s.store_id
        JOIN product p ON st.product_id = p.product_id
        WHERE s.store_id = %s
    """

    with conn.cursor() as cursor:
        cursor.execute(query, (store_id,))
        rows = cursor.fetchall()

    print("\n=== 가맹점별 재고 현황 ===")
    for row in rows:
        print(row)

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

# ========================= 3️⃣ 거래 및 영수증 조회 =========================
def process_transaction(conn):
    """ 고객이 상품을 구매하면 거래(판매) 등록 (스토어, 직원, 상품 LIKE 검색 & 결제 방식 선택 포함) """
    try:
        # 1️⃣ **스토어 검색 & 선택 (LIKE 검색)**
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

        # 2️⃣ **직원 검색 & 선택 (LIKE 검색)**
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

        # 3️⃣ **상품 검색 & 선택 (LIKE 검색)**
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

        # 4️⃣ **결제 방식 선택**
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

        # ✅  거래 추가 (결제 방식 반영)
        with conn.cursor() as cursor:
            query = "INSERT INTO transaction (store_id, employee_id, transaction_date, payment_method) VALUES (%s, %s, NOW(), %s)"
            args = (store_id, employee_id, payment_method)
            cursor.execute(query, args)
            transaction_id = cursor.lastrowid  # 새로 삽입된 거래의 ID 가져오기

            # ✅  거래 상세 추가
            query = "INSERT INTO transaction_details (transaction_id, product_id, quantity) VALUES (%s, %s, %s)"
            args = (transaction_id, product_id, quantity)
            cursor.execute(query, args)

            # ✅  재고 감소 (판매된 수량만큼 stock 감소)
            query = "UPDATE stock SET quantity = quantity - %s WHERE store_id = %s AND product_id = %s"
            args = (quantity, store_id, product_id)
            cursor.execute(query, args)

        conn.commit()  # 모든 변경사항을 DB에 반영
        print(f"✅ 거래가 성공적으로 완료되었습니다! (거래 ID: {transaction_id})")
        print(f" 재고 감소 완료! {product_keyword} 남은 재고: {current_stock - quantity}개")

    except Error as error:
        conn.rollback()  #  오류 발생 시 롤백
        print(f" 거래 처리 중 오류 발생: {error}")



def get_transaction_receipt(conn):
    """ 거래 상세 영수증 조회 (연, 월, 일 따로 입력 & 자동 변환) """

    # ✅  연, 월, 일을 개별적으로 입력받음
    year = input("조회할 연도를 입력하세요 (예: 2024) >>> ").strip()
    month = input("조회할 월을 입력하세요 (예: 7) >>> ").strip()
    day = input("조회할 일을 입력하세요 (예: 3) >>> ").strip()

    # ✅  월/일이 한 자리 숫자인 경우 앞에 '0'을 추가
    month = month.zfill(2)  # 예: '7' → '07'
    day = day.zfill(2)      # 예: '3' → '03'

    # ✅  YYYY-MM-DD 형식으로 변환
    transaction_date = f"{year}-{month}-{day}"
    print(f"\n📅 검색할 거래 날짜: {transaction_date}")

    query = """
        SELECT 
            t.transaction_id,
            t.transaction_date, 
            s.name AS store_name,
            e.name AS employee_name,
            GROUP_CONCAT(p.name SEPARATOR ', ') AS product_names,  --  상품명을 한 줄로 출력
            SUM(td.quantity) AS total_quantity, 
            SUM(td.quantity * p.price) AS total_price
        FROM transaction t
        JOIN transaction_details td ON t.transaction_id = td.transaction_id
        JOIN product p ON td.product_id = p.product_id
        JOIN store s ON t.store_id = s.store_id
        JOIN employee e ON t.employee_id = e.employee_id
        WHERE DATE(t.transaction_date) = %s
        GROUP BY t.transaction_id, t.transaction_date, s.name, e.name
        ORDER BY t.transaction_date DESC
    """

    with conn.cursor() as cursor:
        cursor.execute(query, (transaction_date,))
        rows = cursor.fetchall()

    if rows:
        print("\n=== 거래 상세 영수증 ===")
        for row in rows:
            print(f"거래 ID: {row[0]}")
            print(f"거래일자: {row[1]}")
            print(f"가게: {row[2]}")
            print(f"직원: {row[3]}")
            print(f"상품명: {row[4]}")
            print(f"총 수량: {row[5]}")
            print(f"총 결제 금액: {row[6]} 원")
            print("-" * 50)  # 가독성을 위한 구분선
    else:
        print("해당 날짜에 거래가 없습니다.")



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
