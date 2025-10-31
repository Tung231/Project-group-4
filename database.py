# ==========================================
# File: database.py
# PHIÊN BẢN DỮ LIỆU DEMO NÂNG CAO
# ==========================================
import sqlite3, hashlib, pandas as pd, datetime as dt
from pathlib import Path
import random

DB_PATH = "expense.db"
ENABLE_DEMO = True

# ---------- DB Connection & Execution (Không đổi) ----------
def get_conn():
    c = sqlite3.connect(DB_PATH, check_same_thread=False)
    c.row_factory = sqlite3.Row
    return c

def get_df(query, params=()):
    conn = get_conn()
    df = pd.read_sql_query(query, conn, params=params)
    conn.close()
    return df

def execute_query(query, params=()):
    conn = get_conn()
    conn.execute(query, params)
    conn.commit()
    conn.close()

def fetch_one(query, params=()):
    conn = get_conn()
    result = conn.execute(query, params).fetchone()
    conn.close()
    return result

def execute_script(conn, script):
    conn.executescript(script)
    conn.commit()

# ---------- Password Hashing (Không đổi) ----------
def hash_password(password):
    return hashlib.sha256(password.encode("utf-8")).hexdigest()

# ---------- DB Initialization (Không đổi) ----------
INIT_SQL = """
PRAGMA foreign_keys = ON;
CREATE TABLE IF NOT EXISTS users(id INTEGER PRIMARY KEY AUTOINCREMENT, email TEXT UNIQUE NOT NULL, password_hash TEXT NOT NULL, created_at TEXT NOT NULL, display_name TEXT, onboarded INTEGER NOT NULL DEFAULT 0);
CREATE TABLE IF NOT EXISTS accounts(id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER NOT NULL, name TEXT NOT NULL, type TEXT NOT NULL, currency TEXT NOT NULL DEFAULT 'VND', opening_balance REAL NOT NULL DEFAULT 0, created_at TEXT NOT NULL, FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE);
CREATE TABLE IF NOT EXISTS categories(id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER NOT NULL, name TEXT NOT NULL, type TEXT NOT NULL, parent_id INTEGER, FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE);
CREATE TABLE IF NOT EXISTS transactions(id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER NOT NULL, account_id INTEGER NOT NULL, type TEXT NOT NULL, category_id INTEGER, amount REAL NOT NULL, currency TEXT NOT NULL DEFAULT 'VND', fx_rate REAL, merchant_id INTEGER, notes TEXT, tags TEXT, occurred_at TEXT NOT NULL, created_at TEXT NOT NULL, FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE, FOREIGN KEY(account_id) REFERENCES accounts(id) ON DELETE CASCADE, FOREIGN KEY(category_id) REFERENCES categories(id) ON DELETE SET NULL);
CREATE TABLE IF NOT EXISTS budgets(id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER NOT NULL, category_id INTEGER NOT NULL, amount REAL NOT NULL, start_date TEXT NOT NULL, end_date TEXT NOT NULL, FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE);
"""

# ===============================================================
# === HÀM SEED DEMO ĐÃ ĐƯỢC NÂNG CẤP (FIX #1, #2, #3, #4, #5) ===
# ===============================================================
def seed_demo_user_once(conn):
    """
    Tạo dữ liệu demo nâng cao:
    - Fix #1: Tạo danh mục cha/con (VD: Ăn uống -> Ăn trưa).
    - Fix #2: Gán giao dịch cho cả danh mục con.
    - Fix #3: Thêm giao dịch CỐ ĐỊNH cho tháng này để đảm bảo:
        - 1 budget VƯỢT (VD: Ăn uống > 100%).
        - 1 budget SÁT (VD: Cà phê ~ 90%).
        - 1 budget AN TOÀN (VD: Giải trí < 50%).
    - Fix #5: Thêm giao dịch KHÔNG CÓ danh mục.
    """
    
    # --- 1. Tạo user DEMO (nếu chưa có) ---
    if not conn.execute("SELECT 1 FROM users WHERE email='demo@expense.local'").fetchone():
        now = dt.datetime.now().isoformat()
        conn.execute("INSERT INTO users(email,password_hash,created_at,display_name,onboarded) VALUES(?,?,?,?,1)", ("demo@expense.local", hash_password("demo1234"), now, "Tài khoản DEMO"))
        conn.commit()
    uid = conn.execute("SELECT id FROM users WHERE email='demo@expense.local'").fetchone()["id"]
    now = dt.datetime.now().isoformat()

    # --- 2. Tạo Accounts (nếu chưa có) ---
    if not conn.execute("SELECT 1 FROM accounts WHERE user_id=?", (uid,)).fetchone():
        conn.execute("INSERT INTO accounts(user_id,name,type,currency,opening_balance,created_at) VALUES(?,?,?,?,?,?)", (uid, "Tiền mặt", "cash", "VND", 2_000_000, now))
        conn.execute("INSERT INTO accounts(user_id,name,type,currency,opening_balance,created_at) VALUES(?,?,?,?,?,?)", (uid, "Tài khoản ngân hàng", "bank", "VND", 8_000_000, now))
        conn.commit()

    # --- 3. Tạo Categories (Cha/Con) (nếu chưa có) ---
    if not conn.execute("SELECT 1 FROM categories WHERE user_id=?", (uid,)).fetchone():
        # Định nghĩa cấu trúc
        parent_cats_expense = ["Ăn uống", "Giải trí", "Đi lại", "Tiền học", "Mua sắm", "Cà phê"]
        parent_cats_income = ["Lương", "Thưởng", "Bán đồ cũ"]
        child_cats = {
            "Ăn uống": ["Ăn sáng", "Ăn trưa", "Ăn tối", "Tạp hoá"],
            "Giải trí": ["Xem phim", "Nghe nhạc", "Du lịch"],
            "Đi lại": ["Xăng xe", "Gửi xe", "Bảo dưỡng"],
            "Mua sắm": ["Quần áo", "Đồ gia dụng", "Mỹ phẩm"]
        }
        
        # Thêm các danh mục cha
        for name in parent_cats_expense:
            conn.execute("INSERT INTO categories(user_id,name,type) VALUES(?,?,?)",(uid,name,'expense'))
        for name in parent_cats_income:
            conn.execute("INSERT INTO categories(user_id,name,type) VALUES(?,?,?)",(uid,name,'income'))
        conn.commit()
        
        # Lấy ID của cha
        parents_map = {r["name"]: r["id"] for r in conn.execute("SELECT id, name FROM categories WHERE user_id=? AND parent_id IS NULL", (uid,)).fetchall()}
        
        # Thêm các danh mục con
        for parent_name, children in child_cats.items():
            parent_id = parents_map.get(parent_name)
            if parent_id:
                for child_name in children:
                    conn.execute("INSERT INTO categories(user_id,name,type,parent_id) VALUES(?,?,?,?)",(uid,child_name,'expense',parent_id))
        conn.commit()

    # --- 4. Tạo Transactions (Chỉ tạo 1 lần nếu chưa có) ---
    if not conn.execute("SELECT 1 FROM transactions WHERE user_id=?", (uid,)).fetchone():
        # Lấy ID tài khoản
        acc_ids = [r["id"] for r in conn.execute("SELECT id FROM accounts WHERE user_id=?", (uid,)).fetchall()]
        acc_cash_id = conn.execute("SELECT id FROM accounts WHERE user_id=? AND type='cash'", (uid,)).fetchone()["id"]
        acc_bank_id = conn.execute("SELECT id FROM accounts WHERE user_id=? AND type='bank'", (uid,)).fetchone()["id"]
        
        # Lấy ID TẤT CẢ danh mục (bao gồm cả con)
        exp_ids = [r["id"] for r in conn.execute("SELECT id FROM categories WHERE user_id=? AND type='expense'", (uid,)).fetchall()]
        inc_ids = [r["id"] for r in conn.execute("SELECT id FROM categories WHERE user_id=? AND type='income'", (uid,)).fetchall()]
        
        rng = random.Random(20231031)

        # Hàm tạo dữ liệu ngẫu nhiên (cho lịch sử)
        def add_month_data(y, m):
            month_mid = dt.date(y, m, 15)
            # Thu nhập
            for _ in range(rng.randint(3, 5)):
                cat = rng.choice(inc_ids); amt = rng.choice([rng.randint(6_000_000, 18_000_000), rng.randint(500_000, 2_000_000)]); day_off = rng.randint(-10, 10); hh, mm = rng.randint(8, 21), rng.randint(0, 59); occurred = dt.datetime.combine(month_mid + dt.timedelta(days=day_off), dt.time(hh, mm)).strftime("%Y-%m-%d %H:%M")
                conn.execute("INSERT INTO transactions(user_id,account_id,type,category_id,amount,currency,occurred_at,created_at) VALUES(?,?,?,?,?,?,?,?)", (uid, rng.choice(acc_ids), "income", cat, amt, "VND", occurred, now))
            # Chi tiêu
            for _ in range(rng.randint(14, 22)):
                cat = rng.choice(exp_ids); amt = rng.choice([rng.randint(80_000, 350_000), rng.randint(300_000, 1_200_000), rng.randint(1_500_000, 6_000_000)]); day_off = rng.randint(-13, 13); hh, mm = rng.randint(8, 22), rng.randint(0, 59); occurred = dt.datetime.combine(month_mid + dt.timedelta(days=day_off), dt.time(hh, mm)).strftime("%Y-%m-%d %H:%M")
                conn.execute("INSERT INTO transactions(user_id,account_id,type,category_id,amount,currency,occurred_at,created_at) VALUES(?,?,?,?,?,?,?,?)", (uid, rng.choice(acc_ids), "expense", cat, amt, "VND", occurred, now))

        # Seed dữ liệu lịch sử (VD: 2024, 2025)
        for y in (2024,): # Chỉ seed 1 năm cho nhanh
             for m in range(1, 12+1): add_month_data(y, m)
        today_hist = dt.date.today()
        for m in range(1, today_hist.month): # Chỉ seed các tháng TRƯỚC tháng này
             add_month_data(today_hist.year, m)
        conn.commit()

        # --- 4b. TẠO DỮ LIỆU CỐ ĐỊNH CHO THÁNG NÀY (ĐỂ TEST BUDGET) ---
        today = dt.date.today()
        now_iso = dt.datetime.now().isoformat()
        
        # Lấy ID danh mục con/cha cần thiết
        cat_an_trua_id = conn.execute("SELECT id FROM categories WHERE user_id=? AND name='Ăn trưa'", (uid,)).fetchone()["id"]
        cat_ca_phe_id = conn.execute("SELECT id FROM categories WHERE user_id=? AND name='Cà phê'", (uid,)).fetchone()["id"]
        cat_xem_phim_id = conn.execute("SELECT id FROM categories WHERE user_id=? AND name='Xem phim'", (uid,)).fetchone()["id"]

        # Kịch bản 1: VƯỢT HẠN MỨC "Ăn uống" (Hạn mức 4.5M)
        # Ta sẽ thêm 5M vào "Ăn trưa" (con của Ăn uống) để test gộp nhóm
        t1 = (today - dt.timedelta(days=1)).strftime("%Y-%m-%d 12:30")
        t2 = (today - dt.timedelta(days=3)).strftime("%Y-%m-%d 12:00")
        conn.execute("INSERT INTO transactions(user_id,account_id,type,category_id,amount,currency,occurred_at,created_at,notes) VALUES(?,?,?,?,?,?,?,?,?)", (uid, acc_bank_id, 'expense', cat_an_trua_id, 3000000, 'VND', t1, now_iso, "Liên hoan công ty"))
        conn.execute("INSERT INTO transactions(user_id,account_id,type,category_id,amount,currency,occurred_at,created_at,notes) VALUES(?,?,?,?,?,?,?,?,?)", (uid, acc_bank_id, 'expense', cat_an_trua_id, 2000000, 'VND', t2, now_iso, "Ăn nhà hàng"))

        # Kịch bản 2: SÁT HẠN MỨC "Cà phê" (Hạn mức 1.2M)
        # Ta sẽ thêm 1.1M
        t3 = (today - dt.timedelta(days=2)).strftime("%Y-%m-%d 08:30")
        t4 = (today - dt.timedelta(days=4)).strftime("%Y-%m-%d 09:00")
        conn.execute("INSERT INTO transactions(user_id,account_id,type,category_id,amount,currency,occurred_at,created_at,notes) VALUES(?,?,?,?,?,?,?,?,?)", (uid, acc_cash_id, 'expense', cat_ca_phe_id, 600000, 'VND', t3, now_iso, "Mua 10 ly cho team"))
        conn.execute("INSERT INTO transactions(user_id,account_id,type,category_id,amount,currency,occurred_at,created_at,notes) VALUES(?,?,?,?,?,?,?,?,?)", (uid, acc_cash_id, 'expense', cat_ca_phe_id, 500000, 'VND', t4, now_iso, "Cà phê cuối tuần"))

        # Kịch bản 3: AN TOÀN HẠN MỨC "Giải trí" (Hạn mức 2.5M)
        # Ta thêm 150k vào "Xem phim" (con của Giải trí)
        t5 = (today - dt.timedelta(days=5)).strftime("%Y-%m-%d 20:00")
        conn.execute("INSERT INTO transactions(user_id,account_id,type,category_id,amount,currency,occurred_at,created_at,notes) VALUES(?,?,?,?,?,?,?,?,?)", (uid, acc_cash_id, 'expense', cat_xem_phim_id, 150000, 'VND', t5, now_iso, "Vé xem phim"))

        # Kịch bản 4: GIAO DỊCH KHÔNG CÓ DANH MỤC
        t6 = (today - dt.timedelta(days=1)).strftime("%Y-%m-%d 18:00")
        t7 = (today - dt.timedelta(days=2)).strftime("%Y-%m-%d 10:00")
        conn.execute("INSERT INTO transactions(user_id,account_id,type,category_id,amount,currency,occurred_at,created_at,notes) VALUES(?,?,?,?,?,?,?,?,?)", (uid, acc_cash_id, 'expense', None, 50000, 'VND', t6, now_iso, "Rơi tiền"))
        conn.execute("INSERT INTO transactions(user_id,account_id,type,category_id,amount,currency,occurred_at,created_at,notes) VALUES(?,?,?,?,?,?,?,?,?)", (uid, acc_bank_id, 'income', None, 250000, 'VND', t7, now_iso, "Bạn trả nợ (không rõ)"))
        
        conn.commit()


    # --- 5. Tạo Budgets (Luôn kiểm tra và thêm nếu thiếu) ---
    # Lấy ID các danh mục cha
    cats_map = {r["name"]: r["id"] for r in conn.execute(
        "SELECT id,name FROM categories WHERE user_id=? AND type='expense' AND parent_id IS NULL", (uid,)
    ).fetchall()}
    
    # Hạn mức cho các danh mục cha
    budget_templates = {"Ăn uống": 4_500_000, "Cà phê": 1_200_000, "Giải trí": 2_500_000, "Tiền học": 6_000_000}
    
    # Tạo budget cho 12 tháng gần nhất (bao gồm tháng này)
    anchor = dt.date.today().replace(day=1)
    for i in range(12):
        first = (anchor - dt.timedelta(days=30*i)).replace(day=1)
        next_month = (first.replace(day=28) + dt.timedelta(days=4)).replace(day=1)
        last = next_month - dt.timedelta(days=1)
        for name, amt in budget_templates.items():
            cid = cats_map.get(name)
            if not cid: continue
            
            # Kiểm tra xem budget cho tháng này đã tồn tại chưa
            exists = conn.execute("""SELECT 1 FROM budgets 
                                     WHERE user_id=? AND category_id=? AND start_date=? AND end_date=?""",
                                  (uid, int(cid), str(first), str(last))).fetchone()
            if not exists:
                conn.execute("""INSERT INTO budgets(user_id,category_id,amount,start_date,end_date)
                              VALUES(?,?,?,?,?)""",
                           (uid, int(cid), float(amt), str(first), str(last)))
    conn.commit()

# --- Hàm Init_db (Không đổi) ---
def init_db():
    Path(DB_PATH).touch(exist_ok=True)
    conn = get_conn()
    execute_script(conn, INIT_SQL)
    if ENABLE_DEMO:
        seed_demo_user_once(conn)
    conn.close()

# ---------- Data Access Functions (Toàn bộ phần dưới không đổi) ----------

# USERS
def create_user(email, password):
    conn = get_conn()
    try:
        conn.execute("INSERT INTO users(email,password_hash,created_at,onboarded) VALUES(?,?,?,0)", (email.lower(), hash_password(password), dt.datetime.now().isoformat()))
        conn.commit()
        uid = conn.execute("SELECT id FROM users WHERE email=?", (email.lower(),)).fetchone()["id"]
        now = dt.datetime.now().isoformat()
        conn.execute("INSERT INTO accounts(user_id,name,type,currency,opening_balance,created_at) VALUES(?,?,?,?,?,?)", (uid, "Tiền mặt", "cash", "VND", 0, now))
        conn.execute("INSERT INTO accounts(user_id,name,type,currency,opening_balance,created_at) VALUES(?,?,?,?,?,?)", (uid, "Tài khoản ngân hàng", "bank", "VND", 0, now))
        conn.commit()
        is_success, message = True, "Tạo tài khoản thành công!"
    except sqlite3.IntegrityError:
        is_success, message = False, "Email đã tồn tại."
    finally:
        conn.close()
    return is_success, message

def login_user(email, password):
    user_row = fetch_one("SELECT id, password_hash FROM users WHERE email=?", (email.lower(),))
    if user_row and user_row["password_hash"] == hash_password(password):
        return user_row["id"]
    return None

def get_user(user_id): return fetch_one("SELECT * FROM users WHERE id=?", (user_id,))
def set_user_profile(user_id, name): execute_query("UPDATE users SET display_name=? WHERE id=?", (name.strip(), user_id))
def finish_onboarding(user_id): execute_query("UPDATE users SET onboarded=1 WHERE id=?", (user_id,))

# TRANSACTIONS
def get_transactions(user_id, start_date=None, end_date=None):
    query = """SELECT t.id, t.occurred_at, t.type, t.amount, t.currency,
             a.name AS account, c.name AS category, t.notes, t.tags, t.merchant_id AS merchant
           FROM transactions t JOIN accounts a ON a.id=t.account_id
           LEFT JOIN categories c ON c.id=t.category_id
           WHERE t.user_id=?"""
    params=[user_id]
    if start_date: query+=" AND date(t.occurred_at)>=date(?)"; params.append(str(start_date))
    if end_date: query+=" AND date(t.occurred_at)<=date(?)"; params.append(str(end_date))
    query += " ORDER BY t.occurred_at DESC, t.id DESC"
    return get_df(query, tuple(params))

def add_transaction(user_id, account_id, trans_type, cat_id, amount, notes, occurred_dt):
    execute_query("INSERT INTO transactions(user_id,account_id,type,category_id,amount,currency,occurred_at,created_at) VALUES(?,?,?,?,?,?,?,?)",
            (user_id, account_id, trans_type, cat_id, amount, "VND", occurred_dt, dt.datetime.now().isoformat()))

def delete_transaction(user_id, transaction_id: int):
    execute_query("DELETE FROM transactions WHERE user_id=? AND id=?", (user_id, int(transaction_id)))

def query_expense_aggregation(user_id, start_date, end_date, mode):
    if mode=="day": 
        group_by="date(occurred_at)"
        label="Ngày"
        xtype="O" # Giữ "O" (Ordinal)
    # Bỏ "week"
    elif mode=="month": 
        group_by="strftime('%Y-%m', occurred_at)"
        label="Tháng"
        xtype="O"
    else: # "year"
        group_by="strftime('%Y', occurred_at)"
        label="Năm"
        xtype="O"

    query = f"""
        SELECT {group_by} AS label,
               SUM(CASE WHEN type='expense' THEN amount ELSE 0 END) AS Chi_tieu
        FROM transactions
        WHERE user_id=? AND date(occurred_at) BETWEEN date(?) AND date(?)
        GROUP BY {group_by} ORDER BY {group_by}
    """
    df = get_df(query, (user_id, str(start_date), str(end_date)))
    if df.empty: df = pd.DataFrame(columns=[label,"Chi_tieu"])
    df = df.rename(columns={"label": label})
    return df, label, xtype

# ACCOUNTS
def get_accounts(user_id): return get_df("SELECT * FROM accounts WHERE user_id=?", (user_id,))

def add_account(user_id, name, account_type, balance):
    execute_query("INSERT INTO accounts(user_id,name,type,opening_balance,created_at) VALUES(?,?,?,?,?)",
            (user_id, name.strip(), account_type, balance, dt.datetime.now().isoformat()))

def get_accounts_with_balance(user_id: int) -> pd.DataFrame:
    query = """
    SELECT a.id, a.name, a.type, a.currency, a.opening_balance,
           a.opening_balance
           + COALESCE((SELECT SUM(t.amount) FROM transactions t WHERE t.user_id=a.user_id AND t.account_id=a.id AND t.type='income'), 0)
           - COALESCE((SELECT SUM(t.amount) FROM transactions t WHERE t.user_id=a.user_id AND t.account_id=a.id AND t.type='expense'), 0)
           AS balance
    FROM accounts a WHERE a.user_id = ? ORDER BY a.id
    """
    return get_df(query, (user_id,))

# CATEGORIES
def get_categories(user_id, category_type=None):
    query="SELECT * FROM categories WHERE user_id=?"; params=[user_id]
    if category_type: query+=" AND type=?"; params.append(category_type)
    query+=" ORDER BY name"; return get_df(query, tuple(params))

def add_category(user_id, name, category_type, parent_id=None):
    execute_query("INSERT INTO categories(user_id,name,type,parent_id) VALUES(?,?,?,?)",(user_id, name.strip(), category_type, parent_id))

def delete_category(user_id, category_id: int):
    execute_query("DELETE FROM budgets WHERE user_id=? AND category_id=?", (user_id, int(category_id)))
    execute_query("UPDATE transactions SET category_id=NULL WHERE user_id=? AND category_id=?", (user_id, int(category_id)))
    execute_query("UPDATE categories SET parent_id=NULL WHERE user_id=? AND parent_id=?", (user_id, int(category_id)))
    execute_query("DELETE FROM categories WHERE user_id=? AND id=?", (user_id, int(category_id)))

def get_all_expense_categories(user_id: int) -> pd.DataFrame:
    return get_df("SELECT id, name, parent_id FROM categories WHERE user_id=? AND type='expense'", (user_id,))

def get_descendant_ids(user_id: int, root_id: int, categories_df: pd.DataFrame) -> list[int]:
    if categories_df is None or categories_df.empty: return [int(root_id)]
    
    by_parent: dict[int|None, list[int]] = {}
    for _, row in categories_df.iterrows():
        pid = int(row["parent_id"]) if pd.notna(row["parent_id"]) else None
        by_parent.setdefault(pid, []).append(int(row["id"]))
        
    stack, seen, result = [int(root_id)], set(), []
    while stack:
        current_id = stack.pop()
        if current_id in seen: continue
        seen.add(current_id); result.append(current_id)
        for child_id in by_parent.get(current_id, []): stack.append(child_id)
    return result

# BUDGETS
def delete_budget(user_id, budget_id: int):
    execute_query("DELETE FROM budgets WHERE user_id=? AND id=?", (user_id, int(budget_id)))

def get_budget_progress_df(user_id, start_date, end_date):
    budgets_df = get_df("""
        SELECT b.id, b.category_id, c.name AS category, b.amount, b.start_date, b.end_date
        FROM budgets b JOIN categories c ON c.id = b.category_id
        WHERE b.user_id=? AND date(b.end_date) >= date(?) AND date(b.start_date) <= date(?)
        ORDER BY b.start_date DESC
    """, (user_id, str(start_date), str(end_date)))
    if budgets_df.empty: return budgets_df
    
    all_categories_df, result_rows = get_all_expense_categories(user_id), []
    for _, row in budgets_df.iterrows():
        period_start = max(pd.to_datetime(str(row["start_date"])).date(), start_date)
        period_end = min(pd.to_datetime(str(row["end_date"])).date(), end_date)
        
        category_ids = get_descendant_ids(user_id, int(row["category_id"]), all_categories_df)
        placeholders = ",".join(["?"] * len(category_ids)); params = [user_id] + category_ids + [str(period_start), str(period_end)]
        
        spent_row = fetch_one(f"""
            SELECT COALESCE(SUM(amount),0) AS s FROM transactions 
            WHERE user_id=? AND type='expense' AND category_id IN ({placeholders})
            AND date(occurred_at) BETWEEN date(?) AND date(?)
        """, tuple(params))
        
        used = float(spent_row["s"] or 0.0); limit = float(row["amount"] or 0.0)
        percent = 0.0 if limit <= 0 else (100.0 * used / limit)
        result_rows.append({"Danh mục": row["category"], "Đã dùng": used, "Hạn mức": limit, "%": percent})
        
    return pd.DataFrame(result_rows)

def get_all_budgets_with_progress(user_id: int) -> pd.DataFrame:
    budgets_df = get_df("""
        SELECT b.id, b.category_id, c.name AS category, b.amount, b.start_date, b.end_date
        FROM budgets b JOIN categories c ON c.id = b.category_id
        WHERE b.user_id = ? ORDER BY b.start_date DESC
    """, (user_id,))
    if budgets_df.empty: return budgets_df
    
    all_categories_df, result_rows = get_all_expense_categories(user_id), []
    for _, row in budgets_df.iterrows():
        start, end = pd.to_datetime(str(row["start_date"])).date(), pd.to_datetime(str(row["end_date"])).date()
        
        category_ids = get_descendant_ids(user_id, int(row["category_id"]), all_categories_df)
        placeholders = ",".join(["?"] * len(category_ids)); params = [user_id] + category_ids + [str(start), str(end)]
        
        spent_row = fetch_one(f"""
            SELECT COALESCE(SUM(amount),0) AS s FROM transactions
            WHERE user_id=? AND type='expense' AND category_id IN ({placeholders})
            AND date(occurred_at) BETWEEN date(?) AND date(?)
        """, tuple(params))
        
        used = float(spent_row["s"] or 0.0); limit = float(row["amount"] or 0.0)
        percent = 0.0 if limit <= 0 else (100.0 * used / limit)
        result_rows.append({"id": row["id"], "Danh mục": row["category"], "Từ ngày": str(start), "Đến ngày": str(end), "Đã dùng": used, "Hạn mức": limit, "%": percent})
        
    result_df = pd.DataFrame(result_rows)
    return result_df.sort_values("%", ascending=False, kind="mergesort")