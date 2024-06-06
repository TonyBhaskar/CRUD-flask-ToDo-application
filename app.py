from flask import Flask, render_template, session, redirect, request, url_for, flash
import secrets
import mysql.connector

app = Flask(__name__)
app.secret_key = secrets.token_hex(32)

db = mysql.connector.connect(
    host = 'localhost',
    user = 'root',
    password = 'password', #replace with your password
    database = 'database'  #replace with your database name
)
cursor = db.cursor()

@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/login', methods = ['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        cursor.execute('SELECT * FROM users WHERE email = %s AND password = %s', (email, password))

        user = cursor.fetchone()

        if user:
            session['name'] = user[1]
            session['email'] = email
            return redirect(url_for('landing'))
        else:
            # return "Invalid email or password <a href='/register'>Register</a>"
            flash('Invalid email or password. Please try again.', 'error')
            return redirect(url_for('login'))

    return render_template('login.html')


def fetch_todos(email):
    try:
        cursor.fetchall()
        cursor.execute('SELECT * FROM todos WHERE email = %s', (email,))
        todos = cursor.fetchall()
        cursor.fetchall()  # Consume remaining results
        print("Fetched Todos:", todos)
        return todos
    except mysql.connector.Error as err:
        print(f"Error fetching todos: {err}")
        return []
    
def fetch_users(email):
    try:
        cursor.fetchall()
        cursor.execute('SELECT * FROM users WHERE email = %s', (email,))
        users = cursor.fetchone()
        cursor.fetchall()  # Consume remaining results
        print("Fetched user:", users)
        return users
    except mysql.connector.Error as err:
        print(f"Error fetching user: {err}")
        return []

@app.route('/register', methods = ['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']

        #check if email already exists in the database
        user_existed = fetch_users(email=email)

        if user_existed:
            flash('Email already exists. Please choose a different email.', 'error')
            return redirect(url_for('register'))
        

        #else if user not existed
        cursor.execute('INSERT INTO users (name, email, password) VALUES (%s, %s, %s)', (name, email, password))
        db.commit()
        session['name'] = name
        session['email'] = email
        return redirect(url_for('landing'))
    return render_template('register.html')





# @app.route('/landing')
# def landing():
#     if 'email' in session:
#         # Fetch user's todos and pass them to the template
#         # Assuming you have a function to fetch todos for the user
#         todos = fetch_todos(session['email'])
#         return render_template('landing.html', user_name=session['name'], todos=todos)
#     else:
#         return redirect(url_for('login'))
    



@app.route('/landing', methods=['GET', 'POST'])
def landing():
    if 'email' in session:
        if request.method == 'POST':
            new_todo = request.form.get('new_todo')
            if new_todo:
                try:
                    cursor.execute('INSERT INTO todos (email, todo) VALUES (%s, %s)', (session['email'], new_todo))
                    db.commit()
                    flash('Todo added successfully', 'success')
                except mysql.connector.Error as err:
                    flash(f"Failed to add todo: {err}", 'error')
            else:
                flash('Todo cannot be empty', 'error')
        todos = fetch_todos(session['email'])
        return render_template('landing.html', user_name=session['name'], todos=todos)
    else:
        return redirect(url_for('login'))

# @app.route('/delete_todo', methods=['POST'])
# def delete_todo():
#     if 'email' in session:
#         todo_id = request.form.get('todo_id')
#         try:
#             cursor.execute('DELETE FROM todos WHERE id = %s', (todo_id,))
#             db.commit()
#             flash('Todo deleted successfully', 'success')
#         except mysql.connector.Error as err:
#             flash(f"Failed to delete todo: {err}", 'error')
#     return redirect(url_for('landing'))



# @app.route('/update_todo', methods=['POST'])
# def update_todo():
#     if 'email' in session:
#         todo_id = request.form.get('todo_id')
#         updated_todo = request.form.get('updated_todo')
#         try:
#             cursor.execute('UPDATE todos SET todo = %s WHERE id = %s', (updated_todo, todo_id))
#             db.commit()
#             flash('Todo updated successfully', 'success')
#         except mysql.connector.Error as err:
#             flash(f"Failed to update todo: {err}", 'error')
#     return redirect(url_for('landing'))

def delete_query(id):
    try:
        cursor.execute('DELETE FROM todos WHERE id = %s', (id,))
        db.commit()
    except mysql.connector.Error as err:
        print(f'We got {err}')


@app.route('/delete/<int:id>')
def delete(id):
    try:
        deleted = delete_query(id)
        return redirect(url_for('landing'))
    except:
        return 'There was a problem while deleting todo'

@app.route('/update/<int:id>')
def update(id):
    try:
        cursor.execute('SELECT * FROM todos WHERE id = %s', (id,))
        todo = cursor.fetchone()
        return render_template('update.html', todo=todo)
    except mysql.connector.Error as err:
        return 'There was a problem while fetching todo details'

@app.route('/update/<int:id>', methods=['POST'])
def update_submit(id):
    try:
        new_todo = request.form['new_todo']
        cursor.execute('UPDATE todos SET todo = %s WHERE id = %s', (new_todo, id))
        db.commit()
        return redirect(url_for('landing'))
    except mysql.connector.Error as err:
        return 'There was a problem while updating todo'

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out', 'info')
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)