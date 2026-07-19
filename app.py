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


from werkzeug.security import (
    generate_password_hash,
    check_password_hash
)




app = Flask(__name__)



# Secret key from Render environment

app.secret_key = os.environ.get(
    "SECRET_KEY",
    "church_secret_key_2026"
)



database_url = os.environ.get(
    "DATABASE_URL"
)



if database_url:


    # Render PostgreSQL compatibility fix

    if database_url.startswith("postgres://"):

        database_url = database_url.replace(
            "postgres://",
            "postgresql://",
            1
        )


    app.config["SQLALCHEMY_DATABASE_URI"] = database_url



else:


    # Local development database

    app.config["SQLALCHEMY_DATABASE_URI"] = (
        "sqlite:///church.db"
    )



app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False



db = SQLAlchemy(app)



class User(db.Model):

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
        db.String(200),
        nullable=False
    )


    role = db.Column(
        db.String(50),
        default="Member"
    )






class Event(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )


    title = db.Column(
        db.String(150),
        nullable=False
    )


    date = db.Column(
        db.String(50)
    )


    description = db.Column(
        db.Text
    )





class Sermon(db.Model):

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
        db.ForeignKey("user.id"),
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









# =========================
# REPLY MODEL
# =========================


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
        db.ForeignKey("user.id"),
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


    author = db.relationship(
        "User"
    )








# =========================
# DISCUSSION LIKE MODEL
# =========================


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
        db.ForeignKey("user.id"),
        nullable=False
    )


    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )








# =========================
# CONTACT MODEL
# =========================


class ContactMessage(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )


    name = db.Column(
        db.String(100)
    )


    email = db.Column(
        db.String(120)
    )


    message = db.Column(
        db.Text
    )








# =========================
# GALLERY MODEL
# =========================


class Gallery(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )


    title = db.Column(
        db.String(150)
    )


    image = db.Column(
        db.String(300)
    )








# =========================
# PRAYER REQUEST MODEL
# =========================


class PrayerRequest(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )


    full_name = db.Column(
        db.String(150),
        nullable=False
    )


    email = db.Column(
        db.String(150)
    )


    phone = db.Column(
        db.String(30)
    )


    category = db.Column(
        db.String(100)
    )


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





class Notification(db.Model):

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





with app.app_context():

    db.create_all()







def login_required(function):


    @wraps(function)

    def wrapper(*args, **kwargs):


        if "user_id" not in session:


            flash(
                "Please login first",
                "warning"
            )


            return redirect(
                url_for("login")
            )



        return function(
            *args,
            **kwargs
        )


    return wrapper





@app.route("/")
def home():

    return render_template(
        "index.html"
    )




@app.route(
    "/register",
    methods=["GET","POST"]
)

def register():


    if request.method == "POST":


        name = request.form["name"]


        email = request.form["email"]


        password = request.form["password"]




        existing_user = User.query.filter_by(
            email=email
        ).first()



        if existing_user:


            flash(
                "Email already registered",
                "danger"
            )


            return redirect(
                url_for("register")
            )





        user = User(

            name=name,

            email=email,

            password=generate_password_hash(
                password
            )

        )



        db.session.add(user)

        db.session.commit()



        flash(
            "Registration successful. Login now.",
            "success"
        )



        return redirect(
            url_for("login")
        )



    return render_template(
        "register.html"
    )






@app.route(
    "/login",
    methods=["GET","POST"]
)

def login():


    if request.method == "POST":



        email = request.form["email"]


        password = request.form["password"]





        user = User.query.filter_by(
            email=email
        ).first()





        if user and check_password_hash(
            user.password,
            password
        ):



            session["user_id"] = user.id


            session["user_name"] = user.name



            return redirect(
                url_for("dashboard")
            )





        flash(
            "Invalid login details",
            "danger"
        )




    return render_template(
        "login.html"
    )






@app.route("/logout")

def logout():


    session.clear()



    flash(
        "Logged out successfully",
        "success"
    )



    return redirect(
        url_for("login")
    )







@app.route("/dashboard")

@login_required

def dashboard():



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





    user = User.query.get(
        session["user_id"]
    )




    return render_template(

        "dashboard.html",

        users=users,

        prayers=prayers,

        events=events,

        sermons=sermons,

        user=user

    )



@app.route("/profile")

@login_required

def profile():


    user = User.query.get(
        session["user_id"]
    )



    return render_template(
        "profile.html",
        user=user
    )



@app.route(
    "/update-profile",
    methods=["POST"]
)

@login_required

def update_profile():



    user = User.query.get(
        session["user_id"]
    )



    user.name = request.form["name"]


    user.email = request.form["email"]



    db.session.commit()



    session["user_name"] = user.name




    flash(
        "Profile updated successfully",
        "success"
    )



    return redirect(
        url_for("profile")
    )





@app.route("/about")

@login_required

def about():

    return render_template(
        "about.html"
    )




@app.route(
    "/prayer-request",
    methods=["GET","POST"]
)

def prayer_request():


    if request.method == "POST":



        prayer = PrayerRequest(

            full_name=request.form["full_name"],

            email=request.form.get("email"),

            phone=request.form.get("phone"),

            category=request.form.get("category"),

            prayer=request.form["prayer"],

            confidential=
            "confidential" in request.form

        )



        db.session.add(prayer)

        db.session.commit()



        flash(
            "Prayer request submitted successfully.",
            "success"
        )



        return redirect(
            url_for("prayer_request")
        )



    return render_template(
        "prayer_request.html"
    )



@app.route('/events')
def events():
    return render_template("events.html")

@app.route("/sermons")

@login_required

def sermons():


    sermons = Sermon.query.order_by(
        Sermon.id.desc()
    ).all()



    return render_template(
        "sermons.html",
        sermons=sermons
    )




@app.route(
    "/add-sermon",
    methods=["POST"]
)

@login_required

def add_sermon():


    sermon = Sermon(


        title=request.form["title"],


        pastor=request.form["pastor"],


        date=request.form["date"]

    )



    db.session.add(sermon)

    db.session.commit()



    flash(
        "Sermon added successfully",
        "success"
    )



    return redirect(
        url_for("sermons")
    )




@app.route("/gallery")

@login_required

def gallery():


    images = Gallery.query.all()



    return render_template(
        "gallery.html",
        images=images
    )








@app.route(
    "/add-gallery",
    methods=["POST"]
)

@login_required

def add_gallery():


    gallery = Gallery(

        title=request.form["title"],

        image=request.form["image"]

    )



    db.session.add(gallery)

    db.session.commit()



    flash(
        "Image added successfully",
        "success"
    )



    return redirect(
        url_for("gallery")
    )





@app.route("/sports")

@login_required

def sports():


    return render_template(
        "sports_activities.html"
    )



@app.route("/books")

@login_required

def books():


    return render_template(
        "books.html"
    )





@app.route("/explore")

@login_required

def explore():


    return render_template(
        "explore.html"
    )



@app.route("/leadership")

@login_required

def leadership():


    return render_template(
        "leadership.html"
    )






@app.route("/live")

@login_required

def live():


    return render_template(
        "live.html"
    )



@app.route("/support")

def support():


    return render_template(
        "support.html"
    )





@app.route(
    "/contact",
    methods=["GET","POST"]
)

@login_required

def contact():



    if request.method == "POST":


        message = ContactMessage(


            name=request.form["name"],


            email=request.form["email"],


            message=request.form["message"]

        )



        db.session.add(message)

        db.session.commit()



        flash(
            "Message sent successfully",
            "success"
        )



        return redirect(
            url_for("contact")
        )





    messages = ContactMessage.query.all()



    return render_template(

        "contact.html",

        messages=messages

    )



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




@app.route(
    "/create-discussion",
    methods=["POST"]
)

@login_required

def create_discussion():


    title = request.form.get(
        "title"
    )


    category = request.form.get(
        "category",
        "General"
    )


    content = request.form.get(
        "content"
    )



    if not title or not content:


        flash(
            "Please fill all required fields",
            "danger"
        )


        return redirect(
            url_for("discussions")
        )





    discussion = Discussion(


        title=title,


        category=category,


        content=content,


        user_id=session["user_id"],


        created_at=datetime.utcnow()

    )



    db.session.add(
        discussion
    )


    db.session.commit()



    flash(

        "Discussion posted successfully",

        "success"

    )



    return redirect(

        url_for("discussions")

    )






@app.route(

    "/reply/<int:discussion_id>",

    methods=["POST"]

)

@login_required

def reply(discussion_id):


    discussion = Discussion.query.get_or_404(

        discussion_id

    )



    message = request.form.get(

        "reply"

    )



    if not message:


        flash(

            "Reply cannot be empty",

            "danger"

        )


        return redirect(

            url_for("discussions")

        )





    new_reply = Reply(


        discussion_id=discussion.id,


        user_id=session["user_id"],


        message=message,


        created_at=datetime.utcnow()

    )



    db.session.add(

        new_reply

    )


    db.session.commit()



    flash(

        "Reply posted successfully",

        "success"

    )



    return redirect(

        url_for("discussions")

    )




@app.route(

    "/like-discussion/<int:discussion_id>",

    methods=["POST"]

)

@login_required

def like_discussion(discussion_id):


    discussion = Discussion.query.get_or_404(

        discussion_id

    )



    existing = DiscussionLike.query.filter_by(

        discussion_id=discussion.id,

        user_id=session["user_id"]

    ).first()





    if existing:


        db.session.delete(existing)


        flash(

            "Like removed",

            "info"

        )


    else:


        like = DiscussionLike(

            discussion_id=discussion.id,

            user_id=session["user_id"]

        )


        db.session.add(

            like

        )


        flash(

            "Discussion liked",

            "success"

        )




    db.session.commit()



    return redirect(

        url_for("discussions")

    )




@app.route(

    "/delete-discussion/<int:id>"

)

@login_required

def delete_discussion(id):


    discussion = Discussion.query.get_or_404(

        id

    )



    if discussion.user_id != session["user_id"] and not session.get("admin"):


        flash(

            "You cannot delete this discussion",

            "danger"

        )


        return redirect(

            url_for("discussions")

        )





    db.session.delete(

        discussion

    )


    db.session.commit()



    flash(

        "Discussion deleted",

        "success"

    )



    return redirect(

        url_for("discussions")

    )



@app.route(

    "/delete-reply/<int:id>"

)

@login_required

def delete_reply(id):


    reply = Reply.query.get_or_404(

        id

    )



    if reply.user_id != session["user_id"] and not session.get("admin"):


        flash(

            "You cannot delete this reply",

            "danger"

        )


        return redirect(

            url_for("discussions")

        )





    db.session.delete(

        reply

    )


    db.session.commit()



    flash(

        "Reply deleted",

        "success"

    )



    return redirect(

        url_for("discussions")

    )




@app.route("/notifications")

@login_required

def notifications():


    notifications = Notification.query.order_by(

        Notification.created_at.desc()

    ).all()



    unread = Notification.query.filter_by(

        is_read=False

    ).count()




    return render_template(

        "notifications.html",

        notifications=notifications,

        unread=unread

    )



@app.route(

    "/add-notification",

    methods=["GET","POST"]

)

@login_required

def add_notification():


    if not session.get("admin"):


        flash(

            "Administrator access required",

            "danger"

        )


        return redirect(

            url_for("dashboard")

        )




    if request.method=="POST":



        notification = Notification(


            title=request.form["title"],


            message=request.form["message"],


            category=request.form["category"]

        )



        db.session.add(

            notification

        )


        db.session.commit()



        flash(

            "Notification added",

            "success"

        )



        return redirect(

            url_for("notifications")

        )




    return render_template(

        "add_notification.html"

    )


@app.route(
    "/admin-login",
    methods=["GET","POST"]
)

def admin_login():


    if request.method == "POST":


        email = request.form["email"]


        password = request.form["password"]




        # Render environment variables

        admin_email = os.environ.get(
            "ADMIN_EMAIL",
            "admin@ackmafisini.com"
        )


        admin_password = os.environ.get(
            "ADMIN_PASSWORD",
            "admin123"
        )





        if email == admin_email and password == admin_password:



            session["admin"] = True


            session["admin_name"] = "Church Administrator"


            session["admin_email"] = email




            flash(

                "Admin login successful",

                "success"

            )



            return redirect(

                url_for("admin_dashboard")

            )





        else:


            flash(

                "Invalid admin credentials",

                "danger"

            )




    return render_template(

        "admin-login.html"

    )




@app.route("/admin-dashboard")

@login_required

def admin_dashboard():


    if not session.get("admin"):


        flash(

            "Administrator access required",

            "danger"

        )


        return redirect(

            url_for("dashboard")

        )





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





    total_users = User.query.count()


    total_prayers = PrayerRequest.query.count()


    total_events = Event.query.count()


    total_sermons = Sermon.query.count()


    total_notifications = Notification.query.count()




    return render_template(


        "admin-dashboard.html",



        users=users,

        prayers=prayers,

        events=events,

        sermons=sermons,

        notifications=notifications,



        total_users=total_users,


        total_prayers=total_prayers,


        total_events=total_events,


        total_sermons=total_sermons,


        total_notifications=total_notifications,



        admin_name=session.get(

            "admin_name"

        ),



        admin_email=session.get(

            "admin_email"

        )


    )



@app.route("/admin-logout")

def admin_logout():


    session.pop(

        "admin",

        None

    )


    session.pop(

        "admin_name",

        None

    )


    session.pop(

        "admin_email",

        None

    )



    flash(

        "Admin logged out successfully",

        "success"

    )


    return redirect(

        url_for("admin_login")

    )
    



@app.route("/users")

@login_required

def users():


    if not session.get("admin"):


        flash(

            "Administrator access required",

            "danger"

        )


        return redirect(

            url_for("dashboard")

        )



    users = User.query.all()



    return render_template(

        "users.html",

        users=users

    )




@app.route(

    "/delete-user/<int:id>"

)

@login_required

def delete_user(id):


    if not session.get("admin"):


        flash(

            "Administrator access required",

            "danger"

        )


        return redirect(

            url_for("dashboard")

        )





    user = User.query.get_or_404(

        id

    )



    db.session.delete(

        user

    )


    db.session.commit()



    flash(

        "User deleted successfully",

        "success"

    )



    return redirect(

        url_for("users")

    )




@app.route("/activities")

@login_required

def activities():


    activities = Activity.query.all()



    return render_template(

        "activities.html",

        activities=activities

    )




@app.route(

    "/add-activity",

    methods=["POST"]

)

@login_required

def add_activity():


    activity = Activity(


        title=request.form["title"],


        description=request.form["description"]

    )



    db.session.add(

        activity

    )


    db.session.commit()



    flash(

        "Activity added successfully",

        "success"

    )



    return redirect(

        url_for("activities")

    )



@app.route("/reports")

@login_required

def reports():


    if not session.get("admin"):


        flash(

            "Administrator access required",

            "danger"

        )


        return redirect(

            url_for("dashboard")

        )





    total_users = User.query.count()


    total_prayers = PrayerRequest.query.count()


    total_events = Event.query.count()


    total_sermons = Sermon.query.count()


    total_gallery = Gallery.query.count()



    users = User.query.all()


    prayers = PrayerRequest.query.all()


    events = Event.query.all()


    sermons = Sermon.query.all()





    return render_template(

        "reports.html",


        total_users=total_users,


        total_prayers=total_prayers,


        total_events=total_events,


        total_sermons=total_sermons,


        total_gallery=total_gallery,



        users=users,


        prayers=prayers,


        events=events,


        sermons=sermons

    )




@app.route("/settings")

@login_required

def settings():


    return render_template(

        "settings.html"

    )


@app.route(

    "/delete-notification/<int:id>"

)

@login_required

def delete_notification(id):


    if not session.get("admin"):


        flash(

            "Administrator access required",

            "danger"

        )


        return redirect(

            url_for("notifications")

        )



    notification = Notification.query.get_or_404(

        id

    )


    db.session.delete(

        notification

    )


    db.session.commit()



    flash(

        "Notification deleted",

        "success"

    )


    return redirect(

        url_for("notifications")

    )




@app.errorhandler(404)

def page_not_found(error):


    return render_template(

        "404.html"

    ),404
    
    

@app.route("/health")

def health():

    return jsonify({

        "status": "running",

        "message":
        "ACK St. Paul's Parish Mafisini system is online"

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

        port=port

    )    
        
