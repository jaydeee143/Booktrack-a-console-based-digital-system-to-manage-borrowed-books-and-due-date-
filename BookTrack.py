from datetime import date, timedelta
import re

# BOOKTRACK - console system to manage borrowed books and due dates

students = {}
librarians = {"librarian": {"password": "1234", "name": "Main Librarian"}}
records = {}
next_record_id = 1
ACTIVE = ["Pending Approval", "Borrowed", "Pending Return"]

book_catalog = {
    "Information Technology": ["Python Programming", "Introduction to Computing", "Computer Networks",
                               "Database Management Systems", "Web Development Basics"],
    "Nursing": ["Fundamentals of Nursing", "Anatomy and Physiology", "Medical-Surgical Nursing",
                "Pharmacology", "Community Health Nursing"],
    "Business Accountancy": ["Financial Accounting", "Business Mathematics", "Principles of Management",
                             "Marketing Management", "Business Law"],
    "Architecture": ["Architectural Design", "Building Materials", "History of Architecture",
                     "Structural Design", "Architectural Drawing"],
    "Psychology": ["Introduction to Psychology", "Developmental Psychology", "Social Psychology",
                   "Abnormal Psychology", "Personality Psychology"],
    "Criminology": ["Introduction to Criminology", "Criminal Law", "Forensic Science",
                    "Crime Detection", "Criminal Investigation"],
    "Civil Engineering": ["Engineering Mathematics", "Structural Engineering", "Construction Materials",
                          "Surveying", "Fluid Mechanics"],
}

# Every book starts with 5 copies.
books = {
    f"B{n:03d}": {"title": t, "category": c, "total": 5, "available": 5}
    for n, (c, t) in enumerate(((c, t) for c, ts in book_catalog.items() for t in ts), start=1)
}


# ==================== GENERAL FUNCTIONS ====================

def pause():
    input("\nPress Enter to continue...")


def ask(label):
    return input(f"Enter {label} (0 to go back): ").strip()


def valid_student_id(student_id):
    return re.fullmatch(r"\d{2}-\d{4}-\d{6}", student_id) is not None


def calculate_due_date():
    due = date.today() + timedelta(days=30)
    # If the due date falls on Sunday, move it to Saturday.
    return due - timedelta(days=1) if due.weekday() == 6 else due


def due_text(record):
    due = record["due_date"]
    return due.strftime("%Y-%m-%d") if due else "Not assigned"


def show_book_inventory():
    print("\n" + "=" * 105)
    print("                              BOOK INVENTORY")
    print("=" * 105)
    print(f"| {'BOOK ID':<10} | {'BOOK TITLE':<35} | {'CATEGORY':<25} | {'AVAILABLE':<10} | {'TOTAL':<5} |")
    print("-" * 105)
    for bid, b in books.items():
        print(f"| {bid:<10} | {b['title']:<35} | {b['category']:<25} | {b['available']:<10} | {b['total']:<5} |")
    print("=" * 105)


def inventory_and_pause():
    show_book_inventory()
    pause()


def show_books_by_category():
    categories = list(book_catalog)
    while True:
        print("\n========== BOOK CATEGORIES ==========")
        for n, c in enumerate(categories, start=1):
            print(f"{n}. {c}")
        print("0. Back")
        choice = input("\nChoose a category: ").strip()

        if choice == "0":
            return
        if not choice.isdigit() or not 1 <= int(choice) <= len(categories):
            print("Invalid choice. Please try again.")
            continue

        category = categories[int(choice) - 1]
        print("\n" + "=" * 85)
        print(f"                  {category.upper()} BOOKS")
        print("=" * 85)
        print(f"| {'BOOK ID':<10} | {'BOOK TITLE':<40} | {'AVAILABLE':<10} | {'TOTAL':<5} |")
        print("-" * 85)
        for bid, b in books.items():
            if b["category"] == category:
                print(f"| {bid:<10} | {b['title']:<40} | {b['available']:<10} | {b['total']:<5} |")
        print("=" * 85)
        input("\nPress Enter to go back to Categories...")


def student_has_active_book(student_id, book_id):
    return any(r["student_id"] == student_id and r["book_id"] == book_id and r["status"] in ACTIVE
               for r in records.values())


def field_error(key, value):
    """Return an error message for an invalid student field, else None."""
    if not value:
        return "This field cannot be empty."
    if key == "student_id":
        if not valid_student_id(value):
            return "Invalid Student ID format.\nUse this format: XX-XXXX-XXXXXX"
        if value in students:
            return "This Student ID is already registered."
    if key == "contact" and (not value.isdigit() or len(value) < 10):
        return "Please enter a valid contact number."
    return None


STUDENT_FIELDS = [("Student ID", "student_id"), ("Full Name", "name"), ("Contact Number", "contact"),
                  ("Section", "section"), ("Password", "password")]


def save_student(v):
    students[v["student_id"]] = {
        "name": v["name"], "contact": v["contact"], "section": v["section"],
        "password": v["password"], "year": "First Year", "course": "BS Information Technology",
    }


# ==================== REGISTRATION & LOGIN ====================

def student_registration():
    print("\n========== STUDENT REGISTRATION ==========")
    values, pos = {}, 0
    while pos < len(STUDENT_FIELDS):
        label, key = STUDENT_FIELDS[pos]
        entered = ask(label)
        if entered == "0":
            if pos == 0:
                return
            pos -= 1
            continue
        error = field_error(key, entered)
        if error:
            print(error)
            continue
        values[key] = entered
        pos += 1

    save_student(values)
    print("\nRegistration successful!")
    print("You can now log in using your Student ID and password.")
    pause()


def login(title, label, accounts, is_student=False):
    kind = "Student" if is_student else "Librarian"
    while True:
        print(f"\n========== {title} ==========")
        uid = ask(label)
        if uid == "0":
            return None
        if is_student and not valid_student_id(uid):
            print("Invalid Student ID format.\nUse this format: XX-XXXX-XXXXXX")
            continue
        if uid not in accounts:
            print(f"{kind} account not found.")
            continue
        while True:
            password = ask("Password")
            if password == "0":
                break
            if password == accounts[uid]["password"]:
                print("\nLogin successful!")
                if is_student:
                    print(f"Welcome, {accounts[uid]['name']}!")
                return uid
            print("Incorrect password. Please try again.")


# ==================== STUDENT FUNCTIONS ====================

def borrow_book(student_id):
    global next_record_id
    while True:
        show_book_inventory()
        book_id = input("\nEnter Book ID to borrow (0 to go back): ").strip().upper()
        if book_id == "0":
            return
        if book_id not in books:
            print("Book ID not found.")
            continue
        book = books[book_id]
        if book["available"] <= 0:
            print("Sorry, this book is currently unavailable.")
            continue
        if student_has_active_book(student_id, book_id):
            print("You already have an active request or borrowing record for this book.")
            continue

        record_id = f"R{next_record_id:03d}"
        next_record_id += 1
        book["available"] -= 1  # Reserve one copy when the request is submitted.
        records[record_id] = {"student_id": student_id, "book_id": book_id,
                              "borrow_date": date.today(), "due_date": None,
                              "status": "Pending Approval"}

        print("\nBorrow request submitted successfully!")
        print(f"Record ID: {record_id}")
        print("Please wait for librarian approval.")
        pause()
        return


def view_student_records(student_id):
    print("\n========== MY BORROWING RECORDS ==========")
    print(f"{'RECORD ID':<12}{'BOOK TITLE':<32}{'STATUS':<20}{'DUE DATE'}")
    print("-" * 85)
    mine = [(rid, r) for rid, r in records.items() if r["student_id"] == student_id]
    for rid, r in mine:
        print(f"{rid:<12}{books[r['book_id']]['title']:<32}{r['status']:<20}{due_text(r)}")
    if not mine:
        print("You have no borrowing records.")
    pause()


def request_book_return(student_id):
    while True:
        print("\n========== REQUEST BOOK RETURN ==========")
        borrowed = [rid for rid, r in records.items()
                    if r["student_id"] == student_id and r["status"] == "Borrowed"]
        if not borrowed:
            print("You have no borrowed books available for return.")
            pause()
            return

        print(f"{'RECORD ID':<12}{'BOOK TITLE':<35}{'DUE DATE'}")
        print("-" * 70)
        for rid in borrowed:
            r = records[rid]
            print(f"{rid:<12}{books[r['book_id']]['title']:<35}{r['due_date']}")

        record_id = input("\nEnter Record ID (0 to go back): ").strip().upper()
        if record_id == "0":
            return
        if record_id not in borrowed:
            print("Invalid Record ID. Please try again.")
            continue

        records[record_id]["status"] = "Pending Return"
        print("\nReturn request submitted successfully!")
        print("Please wait for the librarian to process your request.")
        pause()
        return


# ==================== LIBRARIAN FUNCTIONS ====================

def view_all_students():
    print("\n========== REGISTERED STUDENTS ==========")
    if not students:
        print("No registered students.")
    else:
        print(f"{'STUDENT ID':<18}{'NAME':<25}{'CONTACT':<16}{'SECTION':<15}")
        print("-" * 75)
        for sid, s in students.items():
            print(f"{sid:<18}{s['name']:<25}{s['contact']:<16}{s['section']:<15}")
    pause()


def select_pending(title, status, empty_msg):
    """Show records with the given status and return the chosen Record ID (or None)."""
    while True:
        print(f"\n========== {title} ==========")
        pending = [rid for rid, r in records.items() if r["status"] == status]
        if not pending:
            print(empty_msg)
            pause()
            return None

        print(f"{'RECORD ID':<12}{'STUDENT NAME':<25}{'BOOK TITLE':<35}")
        print("-" * 80)
        for rid in pending:
            r = records[rid]
            print(f"{rid:<12}{students[r['student_id']]['name']:<25}{books[r['book_id']]['title']:<35}")

        record_id = input("\nEnter Record ID (0 to go back): ").strip().upper()
        if record_id == "0":
            return None
        if record_id in pending:
            return record_id
        print("Invalid Record ID. Please try again.")


def ask_action(options):
    """Show numbered actions; return the chosen number (0 = back)."""
    while True:
        print()
        for n, text in enumerate(options, start=1):
            print(f"{n}. {text}")
        print("0. Back to Record Selection")
        choice = input("Choose an action: ").strip()
        if choice == "0":
            return 0
        if choice.isdigit() and 1 <= int(choice) <= len(options):
            return int(choice)
        print("Invalid choice. Please try again.")


def approve_borrow_requests():
    while record_id := select_pending("PENDING BORROW REQUESTS", "Pending Approval",
                                      "No pending borrow requests."):
        choice = ask_action(["Approve Request", "Reject Request"])
        if choice == 0:
            continue
        record = records[record_id]
        if choice == 1:
            record.update(status="Borrowed", borrow_date=date.today(), due_date=calculate_due_date())
            print("\nBorrow request approved!")
            print(f"Due Date: {record['due_date']}")
        else:
            record["status"] = "Rejected"
            books[record["book_id"]]["available"] += 1  # Restore the reserved copy.
            print("\nBorrow request rejected.")
        pause()
        return


def process_return_requests():
    while record_id := select_pending("PENDING RETURN REQUESTS", "Pending Return",
                                      "No pending return requests."):
        if ask_action(["Confirm Return"]) == 0:
            continue
        record = records[record_id]
        record["status"] = "Returned"
        books[record["book_id"]]["available"] += 1  # Restore the returned copy.
        print("\nBook return confirmed successfully!")
        pause()
        return


def view_all_records():
    print("\n========== ALL BORROWING RECORDS ==========")
    if not records:
        print("No borrowing records.")
    else:
        print(f"{'RECORD ID':<12}{'STUDENT ID':<18}{'BOOK ID':<10}{'STATUS':<20}{'DUE DATE'}")
        print("-" * 85)
        for rid, r in records.items():
            print(f"{rid:<12}{r['student_id']:<18}{r['book_id']:<10}{r['status']:<20}{due_text(r)}")
    pause()


def view_overdue_books():
    print("\n========== OVERDUE BOOKS ==========")
    today = date.today()
    found = False
    for rid, r in records.items():
        if r["status"] == "Borrowed" and r["due_date"] is not None and r["due_date"] < today:
            found = True
            print("----------------------------------------")
            print(f"Record ID: {rid}")
            print(f"Student: {students[r['student_id']]['name']}")
            print(f"Book: {books[r['book_id']]['title']}")
            print(f"Due Date: {r['due_date']}")
    if not found:
        print("There are no overdue books.")
    pause()


def delete_record():
    while True:
        print("\n========== DELETE BORROWING RECORD ==========")
        if not records:
            print("No records available.")
            pause()
            return

        for rid, r in records.items():
            print(f"{rid} | {students[r['student_id']]['name']} | "
                  f"{books[r['book_id']]['title']} | {r['status']}")

        record_id = input("\nEnter Record ID to delete (0 to go back): ").strip().upper()
        if record_id == "0":
            return
        if record_id not in records:
            print("Record ID not found.")
            continue

        record = records.pop(record_id)
        # Restore a copy if the record still holds a reservation.
        if record["status"] in ACTIVE:
            books[record["book_id"]]["available"] += 1

        print("Record deleted successfully.")
        pause()
        return


def add_librarian():
    fields = [("new username", "Username"), ("password", "Password"), ("librarian name", "Name")]
    while True:
        print("\n========== ADD LIBRARIAN ==========")
        vals = []
        for label, name in fields:
            v = ask(label)
            if v == "0":
                return
            if not v:
                print(f"{name} cannot be empty.")
                break
            if name == "Username" and v in librarians:
                print("Username already exists.")
                break
            vals.append(v)
        else:
            librarians[vals[0]] = {"password": vals[1], "name": vals[2]}
            print("\nLibrarian account added successfully!")
            pause()
            return


def view_librarians():
    print("\n========== LIBRARIAN ACCOUNTS ==========")
    print(f"{'USERNAME':<20} {'NAME':<30}")
    print("-" * 55)
    for username, lib in librarians.items():
        print(f"{username:<20} {lib['name']:<30}")
    pause()


def add_student():
    while True:
        print("\n========== ADD STUDENT ACCOUNT ==========")
        values = {}
        for label, key in STUDENT_FIELDS:
            v = ask(label)
            if v == "0":
                return
            error = field_error(key, v)
            if error:
                print(error)
                break
            values[key] = v
        else:
            save_student(values)
            print("\nStudent account added successfully!")
            pause()
            return


# ==================== MENUS ====================

def run_menu(title, items, exit_label="Logout", exit_msg="Logging out...", welcome=None):
    """Generic menu loop. items = [(label, function), ...]; 0 exits."""
    actions = {str(n): fn for n, (_, fn) in enumerate(items, start=1)}
    while True:
        print("\n" + "=" * 40)
        print(title)
        print("=" * 40)
        if welcome:
            print(welcome)
            print("-" * 40)
        for n, (label, _) in enumerate(items, start=1):
            print(f"{n}. {label}")
        print(f"0. {exit_label}")
        print("-" * 40)

        choice = input("Enter your choice: ").strip()
        if choice == "0":
            print(exit_msg)
            return
        if choice in actions:
            actions[choice]()
        else:
            print("Invalid choice. Please try again.")


def student_menu(sid):
    run_menu("              STUDENT MENU", [
        ("View Books by Course", show_books_by_category),
        ("View Book Inventory", inventory_and_pause),
        ("Borrow a Book", lambda: borrow_book(sid)),
        ("View My Borrowing Records", lambda: view_student_records(sid)),
        ("Request Book Return", lambda: request_book_return(sid)),
    ], welcome=f"Welcome, {students[sid]['name']}!")


def librarian_menu(username):
    run_menu("             LIBRARIAN MENU", [
        ("View Book Inventory", inventory_and_pause),
        ("View Registered Students", view_all_students),
        ("View All Borrowing Records", view_all_records),
        ("Approve or Reject Borrow Requests", approve_borrow_requests),
        ("Process Book Return Requests", process_return_requests),
        ("View Overdue Books", view_overdue_books),
        ("Delete Borrowing Record", delete_record),
        ("Add Librarian Account", add_librarian),
        ("View Librarian Accounts", view_librarians),
        ("Add Student Account", add_student),
    ], welcome=f"Welcome, {librarians[username]['name']}!")


def student_flow():
    sid = login("STUDENT LOGIN", "Student ID", students, is_student=True)
    if sid:
        student_menu(sid)


def librarian_flow():
    username = login("LIBRARIAN LOGIN", "Username", librarians)
    if username:
        librarian_menu(username)


def main():
    run_menu("               BOOKTRACK", [
        ("Student Registration", student_registration),
        ("Student Login", student_flow),
        ("Librarian Login", librarian_flow),
    ], exit_label="Exit Program",
        exit_msg="\nThank you for using BookTrack!\nProgram closed.")


if __name__ == "__main__":
    main()