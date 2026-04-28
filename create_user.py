from database import init_db, create_user

init_db()

create_user("admin", "admin123", "admin")

print("Admin user created!")
