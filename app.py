import os
from datetime import datetime
from functools import wraps

from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    session,
    flash,
    jsonify
)

from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash


# --------------------------------------------------
# APP CONFIGURATION
# --------------------------------------------------

app = Flask(__name__)

app.secret_key = os.environ.get(
    "SECRET_KEY",
    "church_secret_key_2026"
)

database_url = os.environ.get("DATABASE_URL")

if database_url:

    if database_url.startswith("postgres://"):
        database_url = database_url.replace(
            "postgres://",
            "postgresql://",
            1
        )

    app.config["SQLALCHEMY_DATABASE_URI"] = database_url

else:

    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///church.db"

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)


# --------------------------------------------------
# DATABASE MODELS
# --------------------------------------------------

class User(db.Model):
    __tablename__ = "church_users"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    name = db.Column(
        db.String(100),
        nullable=False
    )

    email = db.Column(
        db.String(120),
        unique=True,
        nullable=False
    )

    password = db.Column(
        db.String(255),
        nullable=False
    )

    role = db.Column(
        db.String(50),
        default="Member"
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

class Event(db.Model):

    __tablename__ = "events"

    id = db.Column(db.Integer, primary_key=True)

    title = db.Column(db.String(150), nullable=False)

    date = db.Column(db.String(50))

    description = db.Column(db.Text)


class Sermon(db.Model):

    __tablename__ = "sermons"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    title = db.Column(
        db.String(150),
        nullable=False
    )

    pastor = db.Column(
        db.String(100)
    )

    date = db.Column(
        db.String(50)
    )


class Discussion(db.Model):

    __tablename__ = "discussion"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    title = db.Column(
        db.String(200),
        nullable=False
    )

    content = db.Column(
        db.Text,
        nullable=False
    )

    category = db.Column(
        db.String(100),
        default="General"
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("church_users.id"),
        nullable=False
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    author = db.relationship(
        "User",
        backref="discussions"
    )

    replies = db.relationship(
        "Reply",
        backref="discussion",
        lazy=True,
        cascade="all, delete-orphan"
    )

    likes = db.relationship(
        "DiscussionLike",
        backref="discussion",
        lazy=True,
        cascade="all, delete-orphan"
    )


class Reply(db.Model):

    __tablename__ = "reply"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    discussion_id = db.Column(
        db.Integer,
        db.ForeignKey("discussion.id"),
        nullable=False
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("church_users.id"),
        nullable=False
    )

    message = db.Column(
        db.Text,
        nullable=False
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    author = db.relationship("User")


class DiscussionLike(db.Model):

    __tablename__ = "discussion_like"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    discussion_id = db.Column(
        db.Integer,
        db.ForeignKey("discussion.id"),
        nullable=False
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("church_users.id"),
        nullable=False
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )


class ChurchSettings(db.Model):

    __tablename__ = "church_settings"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    church_name = db.Column(db.String(200))
    church_motto = db.Column(db.String(255))
    vicar = db.Column(db.String(150))
    established = db.Column(db.String(20))

    address = db.Column(db.Text)
    description = db.Column(db.Text)

    phone = db.Column(db.String(50))
    alt_phone = db.Column(db.String(50))
    email = db.Column(db.String(150))
    website = db.Column(db.String(200))

    office_hours = db.Column(db.String(200))
    postal_address = db.Column(db.String(100))
    county = db.Column(db.String(100))
    location = db.Column(db.String(150))
    google_maps = db.Column(db.Text)

    theme = db.Column(db.String(50))
    language = db.Column(db.String(50))

    welcome_message = db.Column(db.Text)

    show_sermons = db.Column(db.String(20))
    show_events = db.Column(db.String(20))
    prayer_requests = db.Column(db.String(20))
    visitor_registration = db.Column(db.String(20))

    email_notifications = db.Column(db.String(20))
    prayer_notifications = db.Column(db.String(20))
    event_notifications = db.Column(db.String(20))
    newsletter_notifications = db.Column(db.String(20))
    system_alerts = db.Column(db.String(20))
    backup_reminder = db.Column(db.String(50))

    session_timeout = db.Column(db.String(50))
    two_factor = db.Column(db.String(20))
    auto_backup = db.Column(db.String(20))

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )


class ContactMessage(db.Model):

    __tablename__ = "contact_messages"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    name = db.Column(db.String(100))
    email = db.Column(db.String(120))
    message = db.Column(db.Text)


class Gallery(db.Model):

    __tablename__ = "gallery"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    title = db.Column(db.String(150))
    image = db.Column(db.String(300))


class PrayerRequest(db.Model):

    __tablename__ = "prayer_requests"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    full_name = db.Column(
        db.String(150),
        nullable=False
    )

    email = db.Column(db.String(150))
    phone = db.Column(db.String(30))
    category = db.Column(db.String(100))

    prayer = db.Column(
        db.Text,
        nullable=False
    )

    confidential = db.Column(
        db.Boolean,
        default=False
    )

    date = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )


class Wedding(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    bride_name = db.Column(db.String(150), nullable=False)
    groom_name = db.Column(db.String(150), nullable=False)
    phone = db.Column(db.String(30), nullable=False)
    email = db.Column(db.String(120))
    wedding_date = db.Column(db.String(30))
    guests = db.Column(db.Integer)
    message = db.Column(db.Text)
    status = db.Column(db.String(30), default="Booked")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Baptism(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(150), nullable=False)
    phone = db.Column(db.String(30), nullable=False)
    email = db.Column(db.String(120))
    dob = db.Column(db.String(30))
    message = db.Column(db.Text)
    status = db.Column(db.String(30), default="Pending")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Notification(db.Model):

    __tablename__ = "notifications"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    title = db.Column(
        db.String(200),
        nullable=False
    )

    message = db.Column(
        db.Text,
        nullable=False
    )

    category = db.Column(
        db.String(100),
        default="General"
    )

    is_read = db.Column(
        db.Boolean,
        default=False
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )


class Activity(db.Model):

    __tablename__ = "activities"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    title = db.Column(
        db.String(150)
    )

    description = db.Column(
        db.Text
    )


# --------------------------------------------------
# CREATE TABLES
# --------------------------------------------------

with app.app_context():
    db.create_all()


# --------------------------------------------------
# LOGIN DECORATOR
# --------------------------------------------------

def login_required(func):

    @wraps(func)
    def wrapper(*args, **kwargs):

        if "user_id" not in session:

            flash(
                "Please login first.",
                "warning"
            )

            return redirect(
                url_for("login")
            )

        return func(*args, **kwargs)

    return wrapper


# ==========================================================
# HOME PAGE
# ==========================================================

@app.route("/")
def home():
    return render_template("index.html")


# ==========================================================
# REGISTER
# ==========================================================

@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        if not name or not email or not password:
            flash("Please fill in all required fields.", "danger")
            return redirect(url_for("register"))

        existing_user = User.query.filter_by(email=email).first()

        if existing_user:
            flash("An account with this email already exists.", "warning")
            return redirect(url_for("register"))

        hashed_password = generate_password_hash(password)

        new_user = User(
            name=name,
            email=email,
            password=hashed_password,
            role="Member"
        )

        try:
            db.session.add(new_user)
            db.session.commit()

            flash(
                "Registration successful! Please login.",
                "success"
            )

            return redirect(url_for("login"))

        except Exception as e:
            db.session.rollback()
            print(e)

            flash(
                "Registration failed. Please try again.",
                "danger"
            )

            return redirect(url_for("register"))

    return render_template("register.html")


# ==========================================================
# LOGIN
# ==========================================================




# ==========================================================
# WEBSITE SETTINGS
# ==========================================================

@app.route("/settings", methods=["GET", "POST"])
@login_required
def settings():

    settings = ChurchSettings.query.first()


    if request.method == "POST":


        if not settings:

            settings = ChurchSettings()

            db.session.add(settings)



        settings.church_name = request.form.get("church_name")

        settings.church_motto = request.form.get("church_motto")

        settings.vicar = request.form.get("vicar")

        settings.established = request.form.get("established")


        settings.address = request.form.get("address")

        settings.description = request.form.get("description")


        settings.phone = request.form.get("phone")

        settings.alt_phone = request.form.get("alt_phone")

        settings.email = request.form.get("email")

        settings.website = request.form.get("website")


        settings.office_hours = request.form.get("office_hours")

        settings.postal_address = request.form.get("postal_address")

        settings.county = request.form.get("county")

        settings.location = request.form.get("location")

        settings.google_maps = request.form.get("google_maps")


        settings.theme = request.form.get("theme")

        settings.language = request.form.get("language")

        settings.welcome_message = request.form.get("welcome_message")


        settings.show_sermons = request.form.get("show_sermons")

        settings.show_events = request.form.get("show_events")

        settings.prayer_requests = request.form.get("prayer_requests")

        settings.visitor_registration = request.form.get("visitor_registration")


        settings.email_notifications = request.form.get("email_notifications")

        settings.prayer_notifications = request.form.get("prayer_notifications")

        settings.event_notifications = request.form.get("event_notifications")

        settings.newsletter_notifications = request.form.get("newsletter_notifications")

        settings.system_alerts = request.form.get("system_alerts")

        settings.backup_reminder = request.form.get("backup_reminder")


        settings.session_timeout = request.form.get("session_timeout")

        settings.two_factor = request.form.get("two_factor")

        settings.auto_backup = request.form.get("auto_backup")



        try:

            db.session.commit()


            flash(
                "Website settings updated successfully.",
                "success"
            )


        except Exception as e:

            db.session.rollback()

            print(e)


            flash(
                "Unable to save settings.",
                "danger"
            )



        return redirect(
            url_for("settings")
        )



    return render_template(
        "settings.html",
        settings=settings
    )


# ==========================================================
# CHURCH MEMBERS
# ==========================================================

@app.route("/church-users")
@login_required
def church_users():

    users = User.query.order_by(
        User.created_at.desc()
    ).all()

    return render_template(
        "church_users.html",
        users=users
    )

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, password):

            session.clear()

            session["user_id"] = user.id
            session["user_name"] = user.name
            session["user_role"] = user.role

            flash(
                f"Welcome {user.name}!",
                "success"
            )

            return redirect(url_for("dashboard"))

        flash(
            "Invalid email or password.",
            "danger"
        )

    return render_template("login.html")


# ==========================================================
# LOGOUT
# ==========================================================

@app.route("/logout")
def logout():

    session.clear()

    flash(
        "You have logged out successfully.",
        "success"
    )

    return redirect(url_for("login"))


# ==========================================================
# DASHBOARD
# ==========================================================

@app.route("/dashboard")
@login_required
def dashboard():

    current_user = User.query.get(session["user_id"])

    users = User.query.all()

    prayers = PrayerRequest.query.order_by(
        PrayerRequest.id.desc()
    ).limit(5).all()

    events = Event.query.order_by(
        Event.id.desc()
    ).limit(5).all()

    sermons = Sermon.query.order_by(
        Sermon.id.desc()
    ).limit(5).all()

    notifications = Notification.query.order_by(
        Notification.created_at.desc()
    ).limit(5).all()

    return render_template(
        "dashboard.html",
        user=current_user,
        users=users,
        prayers=prayers,
        events=events,
        sermons=sermons,
        notifications=notifications
    )


# ==========================================================
# REPORTS PAGE
# ==========================================================

@app.route("/reports")
@login_required
def reports():

    total_users = User.query.count()

    total_prayers = PrayerRequest.query.count()

    total_events = Event.query.count()

    total_sermons = Sermon.query.count()

    total_discussions = Discussion.query.count()

    return render_template(
        "reports.html",
        total_users=total_users,
        total_prayers=total_prayers,
        total_events=total_events,
        total_sermons=total_sermons,
        total_discussions=total_discussions
    )



# ==========================================================
# NOTIFICATIONS PAGE
# ==========================================================

@app.route("/notifications")
@login_required
def notifications():

    notifications = Notification.query.order_by(
        Notification.created_at.desc()
    ).all()

    return render_template(
        "notifications.html",
        notifications=notifications
    )

# ==========================================================
# PROFILE
# ==========================================================

@app.route("/profile")
@login_required
def profile():

    user = User.query.get_or_404(session["user_id"])

    return render_template(
        "profile.html",
        user=user
    )


# ==========================================================
# UPDATE PROFILE
# ==========================================================

@app.route("/update-profile", methods=["POST"])
@login_required
def update_profile():

    user = User.query.get_or_404(session["user_id"])

    name = request.form.get("name", "").strip()
    email = request.form.get("email", "").strip().lower()

    if not name or not email:

        flash(
            "Name and email are required.",
            "danger"
        )

        return redirect(url_for("profile"))

    existing = User.query.filter(
        User.email == email,
        User.id != user.id
    ).first()

    if existing:

        flash(
            "Email already belongs to another account.",
            "warning"
        )

        return redirect(url_for("profile"))

    user.name = name
    user.email = email

    try:

        db.session.commit()

        session["user_name"] = user.name

        flash(
            "Profile updated successfully.",
            "success"
        )

    except Exception as e:

        db.session.rollback()

        print(e)

        flash(
            "Failed to update profile.",
            "danger"
        )

    return redirect(url_for("profile"))


# ==========================================================
# ABOUT PAGE
# ==========================================================

@app.route("/about")
def about():
    return render_template("about.html")


# ==========================================================
# PRAYER REQUEST
# ==========================================================

@app.route("/prayer-request", methods=["GET", "POST"])
def prayer_request():

    if request.method == "POST":

        prayer = PrayerRequest(
            full_name=request.form.get("full_name"),
            email=request.form.get("email"),
            phone=request.form.get("phone"),
            category=request.form.get("category"),
            prayer=request.form.get("prayer"),
            confidential="confidential" in request.form
        )

        try:

            db.session.add(prayer)
            db.session.commit()

            flash(
                "Your prayer request has been received. Our prayer team will stand with you in prayer.",
                "success"
            )

        except Exception as e:

            db.session.rollback()
            print(e)

            flash(
                "Unable to submit prayer request.",
                "danger"
            )

        return redirect(url_for("prayer_request"))

    return render_template("prayer_request.html")


# ==========================================================
# EVENTS / MINISTRIES PAGE
# ==========================================================

# ==========================================================
# EVENTS PAGE
# ==========================================================

@app.route("/events")
def events():

    events = Event.query.order_by(Event.id.desc()).all()

    baptisms = Baptism.query.order_by(Baptism.created_at.desc()).all()

    weddings = Wedding.query.order_by(Wedding.created_at.desc()).all()

    return render_template(
        "events.html",
        events=events,
        baptisms=baptisms,
        weddings=weddings
    )


# ==========================================================
# HOLY BAPTISM REGISTRATION
# ==========================================================

@app.route("/baptism-registration", methods=["POST"])
def baptism_registration():

    baptism = Baptism(
        full_name=request.form["full_name"],
        phone=request.form["phone"],
        email=request.form.get("email"),
        dob=request.form["dob"],
        message=request.form.get("message")
    )

    db.session.add(baptism)
    db.session.commit()

    flash("Baptism registration submitted successfully.", "success")

    return redirect(url_for("events"))


# ==========================================================
# CHRISTIAN WEDDING BOOKING
# ==========================================================

@app.route("/wedding-registration", methods=["POST"])
def wedding_registration():

    wedding = Wedding(
        bride_name=request.form["bride_name"],
        groom_name=request.form["groom_name"],
        phone=request.form["phone"],
        email=request.form.get("email"),
        wedding_date=request.form["wedding_date"],
        guests=request.form.get("guests") or None,
        message=request.form.get("message")
    )

    db.session.add(wedding)
    db.session.commit()

    flash("Wedding booking submitted successfully.", "success")

    return redirect(url_for("events"))


# ==========================================================
# VIEW BAPTISM
# ==========================================================

@app.route("/view-baptism/<int:baptism_id>")
def view_baptism(baptism_id):

    baptism = Baptism.query.get_or_404(baptism_id)

    return render_template(
        "view_baptism.html",
        baptism=baptism
    )


# ==========================================================
# DELETE BAPTISM
# ==========================================================

@app.route("/delete-baptism/<int:baptism_id>")
def delete_baptism(baptism_id):

    baptism = Baptism.query.get_or_404(baptism_id)

    db.session.delete(baptism)
    db.session.commit()

    flash("Baptism registration deleted successfully.", "success")

    return redirect(url_for("events"))


# ==========================================================
# VIEW WEDDING
# ==========================================================

@app.route("/view-wedding/<int:wedding_id>")
def view_wedding(wedding_id):

    wedding = Wedding.query.get_or_404(wedding_id)

    return render_template(
        "view_wedding.html",
        wedding=wedding
    )


# ==========================================================
# DELETE WEDDING
# ==========================================================

@app.route("/delete-wedding/<int:wedding_id>")
def delete_wedding(wedding_id):

    wedding = Wedding.query.get_or_404(wedding_id)

    db.session.delete(wedding)
    db.session.commit()

    flash("Wedding booking deleted successfully.", "success")

    return redirect(url_for("events"))

# ==========================================================
# CHURCH ACTIVITIES
# ==========================================================

@app.route("/activities")
@login_required
def activities():

    activities = Activity.query.order_by(
        Activity.id.desc()
    ).all()

    return render_template(
        "activities.html",
        activities=activities
    )




# ==========================================================
# SERMONS
# ==========================================================

@app.route("/sermons")
def sermons():

    sermons = Sermon.query.order_by(
        Sermon.id.desc()
    ).all()

    return render_template(
        "sermons.html",
        sermons=sermons
    )


# ==========================================================
# ADD SERMON
# ==========================================================

@app.route("/add-sermon", methods=["POST"])
@login_required
def add_sermon():

    sermon = Sermon(
        title=request.form.get("title"),
        pastor=request.form.get("pastor"),
        date=request.form.get("date")
    )

    try:

        db.session.add(sermon)
        db.session.commit()

        flash(
            "Sermon added successfully.",
            "success"
        )

    except Exception as e:

        db.session.rollback()
        print(e)

        flash(
            "Unable to add sermon.",
            "danger"
        )

    return redirect(url_for("sermons"))


# ==========================================================
# GALLERY
# ==========================================================

@app.route("/gallery")
def gallery():

    images = Gallery.query.order_by(
        Gallery.id.desc()
    ).all()

    return render_template(
        "gallery.html",
        images=images
    )


# ==========================================================
# ADD GALLERY IMAGE
# ==========================================================

@app.route("/add-gallery", methods=["POST"])
@login_required
def add_gallery():

    gallery = Gallery(
        title=request.form.get("title"),
        image=request.form.get("image")
    )

    try:

        db.session.add(gallery)
        db.session.commit()

        flash(
            "Image uploaded successfully.",
            "success"
        )

    except Exception as e:

        db.session.rollback()
        print(e)

        flash(
            "Unable to upload image.",
            "danger"
        )

    return redirect(url_for("gallery"))

# ==========================================================
# SPORTS ACTIVITIES
# ==========================================================

@app.route("/sports")
def sports():
    return render_template("sports_activities.html")


# ==========================================================
# BOOKS
# ==========================================================

@app.route("/books")
def books():
    return render_template("books.html")


# ==========================================================
# EXPLORE
# ==========================================================

@app.route("/explore")
def explore():
    return render_template("explore.html")


# ==========================================================
# CHURCH LEADERSHIP
# ==========================================================

@app.route("/leadership")
def leadership():
    return render_template("leadership.html")


# ==========================================================
# LIVE STREAMING
# ==========================================================

@app.route("/live")
def live():
    return render_template("live.html")


# ==========================================================
# SUPPORT PAGE
# ==========================================================

@app.route("/support")
def support():
    return render_template("support.html")


# ==========================================================
# CONTACT US
# ==========================================================

@app.route("/contact", methods=["GET", "POST"])
def contact():

    if request.method == "POST":

        message = ContactMessage(
            name=request.form.get("name"),
            email=request.form.get("email"),
            message=request.form.get("message")
        )

        try:

            db.session.add(message)
            db.session.commit()

            flash(
                "Thank you for contacting ACK St. Paul's Parish Mafisini. We have received your message.",
                "success"
            )

        except Exception as e:

            db.session.rollback()
            print(e)

            flash(
                "Unable to send your message.",
                "danger"
            )

        return redirect(url_for("contact"))

    messages = ContactMessage.query.order_by(
        ContactMessage.id.desc()
    ).all()

    return render_template(
        "contact.html",
        messages=messages
    )


# ==========================================================
# DISCUSSION FORUM
# ==========================================================

@app.route("/discussions")
@login_required
def discussions():

    discussions = Discussion.query.order_by(
        Discussion.created_at.desc()
    ).all()

    return render_template(
        "discussions.html",
        discussions=discussions
    )


# ==========================================================
# CREATE DISCUSSION
# ==========================================================

@app.route("/create-discussion", methods=["POST"])
@login_required
def create_discussion():

    title = request.form.get("title")
    category = request.form.get("category")
    content = request.form.get("content")

    if not title or not content:

        flash(
            "Please complete all required fields.",
            "warning"
        )

        return redirect(url_for("discussions"))

    discussion = Discussion(
        title=title,
        category=category,
        content=content,
        user_id=session["user_id"]
    )

    try:

        db.session.add(discussion)
        db.session.commit()

        flash(
            "Discussion posted successfully.",
            "success"
        )

    except Exception as e:

        db.session.rollback()
        print(e)

        flash(
            "Unable to post discussion.",
            "danger"
        )

    return redirect(url_for("discussions"))

# ==========================================================
# REPLY TO DISCUSSION
# ==========================================================

@app.route("/reply/<int:discussion_id>", methods=["POST"])
@login_required
def reply(discussion_id):

    discussion = Discussion.query.get_or_404(discussion_id)

    message = request.form.get("reply")

    if not message:

        flash(
            "Reply cannot be empty.",
            "warning"
        )

        return redirect(url_for("discussions"))

    new_reply = Reply(
        discussion_id=discussion.id,
        user_id=session["user_id"],
        message=message
    )

    try:

        db.session.add(new_reply)
        db.session.commit()

        flash(
            "Reply posted successfully.",
            "success"
        )

    except Exception as e:

        db.session.rollback()
        print(e)

        flash(
            "Unable to post reply.",
            "danger"
        )

    return redirect(url_for("discussions"))

# ==========================================================
# LIKE DISCUSSION
# ==========================================================

@app.route("/like-discussion/<int:discussion_id>", methods=["POST"])
@login_required
def like_discussion(discussion_id):

    existing = DiscussionLike.query.filter_by(
        discussion_id=discussion_id,
        user_id=session["user_id"]
    ).first()

    if existing:

        db.session.delete(existing)
        flash("Like removed.", "info")

    else:

        like = DiscussionLike(
            discussion_id=discussion_id,
            user_id=session["user_id"]
        )

        db.session.add(like)
        flash("Discussion liked.", "success")

    db.session.commit()

    return redirect(url_for("discussions"))


# ==========================================================
# DELETE DISCUSSION
# ==========================================================

@app.route("/delete-discussion/<int:id>")
@login_required
def delete_discussion(id):

    discussion = Discussion.query.get_or_404(id)

    if discussion.user_id != session["user_id"] and not session.get("admin"):

        flash(
            "You are not allowed to delete this discussion.",
            "danger"
        )

        return redirect(url_for("discussions"))

    db.session.delete(discussion)
    db.session.commit()

    flash(
        "Discussion deleted successfully.",
        "success"
    )

    return redirect(url_for("discussions"))


# ==========================================================
# ADMIN LOGIN
# ==========================================================

# ==========================================================
# ADMIN LOGIN REQUIRED DECORATOR
# ==========================================================

def admin_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):

        if not session.get("admin"):

            flash(
                "Please login as administrator.",
                "warning"
            )

            return redirect(url_for("admin_login"))

        return func(*args, **kwargs)

    return wrapper


# ==========================================================
# ADMIN LOGIN
# ==========================================================

@app.route("/admin-login", methods=["GET", "POST"])
def admin_login():

    # Already logged in
    if session.get("admin"):
        return redirect(url_for("admin_dashboard"))

    if request.method == "POST":

        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "").strip()

        admin_email = os.environ.get(
            "ADMIN_EMAIL",
            "admin@ackmafisini.org"
        ).lower()

        admin_password = os.environ.get(
            "ADMIN_PASSWORD",
            "admin123"
        )

        if email == admin_email and password == admin_password:

            session.clear()

            session["admin"] = True
            session["admin_name"] = "Church Administrator"
            session["admin_email"] = admin_email

            flash(
                "Welcome Administrator.",
                "success"
            )

            return redirect(url_for("admin_dashboard"))

        flash(
            "Invalid administrator email or password.",
            "danger"
        )

    return render_template("admin-login.html")


# ==========================================================
# ADMIN DASHBOARD
# ==========================================================

@app.route("/admin-dashboard")
@admin_required
def admin_dashboard():

    total_users = User.query.count()

    total_prayers = PrayerRequest.query.count()

    total_events = Event.query.count()

    total_sermons = Sermon.query.count()

    total_gallery = Gallery.query.count()

    total_discussions = Discussion.query.count()

    total_notifications = Notification.query.count()

    total_activities = Activity.query.count()

    recent_users = User.query.order_by(
        User.id.desc()
    ).limit(5).all()

    recent_prayers = PrayerRequest.query.order_by(
        PrayerRequest.id.desc()
    ).limit(5).all()

    recent_events = Event.query.order_by(
        Event.id.desc()
    ).limit(5).all()

    recent_sermons = Sermon.query.order_by(
        Sermon.id.desc()
    ).limit(5).all()

    recent_notifications = Notification.query.order_by(
        Notification.created_at.desc()
    ).limit(5).all()

    return render_template(

        "admin-dashboard.html",

        admin_name=session.get("admin_name"),

        admin_email=session.get("admin_email"),

        total_users=total_users,

        total_prayers=total_prayers,

        total_events=total_events,

        total_sermons=total_sermons,

        total_gallery=total_gallery,

        total_discussions=total_discussions,

        total_notifications=total_notifications,

        total_activities=total_activities,

        users=recent_users,

        prayers=recent_prayers,

        events=recent_events,

        sermons=recent_sermons,

        notifications=recent_notifications

    )


# ==========================================================
# ADMIN PROFILE
# ==========================================================

@app.route("/admin-profile")
@login_required
def admin_profile():

    if not session.get("admin"):

        flash(
            "Administrator access required.",
            "danger"
        )

        return redirect(url_for("dashboard"))

    return render_template(

        "admin-profile.html",

        admin_name=session.get("admin_name"),

        admin_email=session.get("admin_email")

    )


# ==========================================================
# ADMIN LOGOUT
# ==========================================================

@app.route("/admin-logout")
@login_required
def admin_logout():

    session.clear()

    flash(
        "Administrator logged out successfully.",
        "success"
    )

    return redirect(url_for("admin_login"))


@app.route("/notification-count")
@login_required
def notification_count():

    count = Notification.query.filter_by(
        is_read=False
    ).count()

    return jsonify({
        "count": count
    })


@app.route("/latest-notifications")
@login_required
def latest_notifications():

    notifications = Notification.query.order_by(
        Notification.created_at.desc()
    ).limit(5).all()

    data = []

    for notification in notifications:

        data.append({

            "id": notification.id,

            "title": notification.title,

            "message": notification.message,

            "category": notification.category,

            "created_at": notification.created_at.strftime(
                "%d %b %Y %I:%M %p"
            )

        })

    return jsonify(data)


@app.route("/mark-notification-read/<int:id>")
@login_required
def mark_notification_read(id):

    notification = Notification.query.get_or_404(id)

    notification.is_read = True

    db.session.commit()

    flash(
        "Notification marked as read.",
        "success"
    )

    return redirect(
        url_for("notifications")
    )


@app.route("/popup-notifications")
@login_required
def popup_notifications():

    notifications = Notification.query.filter_by(
        is_read=False
    ).order_by(
        Notification.created_at.desc()
    ).limit(3).all()

    results = []

    for notification in notifications:

        results.append({

            "id": notification.id,

            "title": notification.title,

            "message": notification.message,

            "category": notification.category

        })

    return jsonify(results)


@app.route("/send-alert", methods=["POST"])
@login_required
def send_alert():

    if not session.get("admin"):

        return jsonify({
            "success": False,
            "message": "Unauthorized"
        }), 403

    title = request.form.get("title")
    message = request.form.get("message")
    category = request.form.get("category", "General")

    notification = Notification(
        title=title,
        message=message,
        category=category
    )

    db.session.add(notification)
    db.session.commit()

    return jsonify({
        "success": True,
        "message": "Notification sent successfully."
    })


@app.errorhandler(404)
def page_not_found(error):

    return (
        "404 - Page Not Found",
        404
    )


@app.errorhandler(500)
def internal_server_error(error):

    db.session.rollback()

    return (
        "500 - Internal Server Error",
        500
    )


@app.route("/health")
def health():

    return jsonify({

        "status": "running",

        "application": "ACK St. Paul's Parish Mafisini",

        "database": "connected"

    })
    


if __name__ == "__main__":

    port = int(
        os.environ.get(
            "PORT",
            5000
        )
    )

    app.run(
        host="0.0.0.0",
        port=port,
        debug=False
    )
