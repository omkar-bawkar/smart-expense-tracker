from flask import Flask, session, redirect, render_template
from routes.auth import auth
from routes.user import user
from routes.admin import admin

app = Flask(__name__)
app.secret_key = "secret123"

# ========================
# HOME ROUTE (THIS WAS MISSING)
# ========================
@app.route("/")
def home():
    return render_template("index.html")


# REGISTER ROUTES
app.register_blueprint(auth)
app.register_blueprint(user)
app.register_blueprint(admin)


# ========================
# LOGOUT
# ========================
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


if __name__ == "__main__":
    app.run(debug=True)