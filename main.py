from flask import Flask, render_template, redirect, url_for, request,flash, get_flashed_messages
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column,relationship
from sqlalchemy import Integer, String, Float,DATE ,ForeignKey,or_
from forms import LoginForm ,SignUpForm ,AddForm
from flask_login import login_user ,login_required  ,logout_user,UserMixin,LoginManager,current_user
from werkzeug.security import generate_password_hash, check_password_hash


import datetime

app = Flask(__name__)
login_manager = LoginManager()
app.secret_key = 'very_secret_key'
app.config['SQLALCHEMY_DATABASE_URI']= 'sqlite:///vault.db'
login_manager.init_app(app)
login_manager.login_view = "login"
class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)
db.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    return db.get_or_404(User,int(user_id))
#creating the data_base tables

class User(db.Model,UserMixin):
    __tablename__ = 'users'
    id : Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50))
    email: Mapped[str] = mapped_column(String(300))
    password: Mapped[str] = mapped_column(String(300))
    bookmarks = relationship('Bookmarks', back_populates='bookmark_owner')

class Bookmarks(db.Model):
    __tablename__ = 'bookmarks'
    id : Mapped[int] = mapped_column(primary_key=True)
    title : Mapped[int]  = mapped_column(String(100))
    url : Mapped[str] = mapped_column()
    bookmark_owner_id =mapped_column(db.ForeignKey('users.id'))
    tags : Mapped[str] = mapped_column()
    bookmark_owner  = relationship('User',back_populates='bookmarks')

with app.app_context():
    db.create_all()


@app.route('/',methods=['GET','POST'])
def home():
    user = current_user
    bookmarks = []
    query = request.args.get('q')
    if user.is_authenticated :
        if query :
            bookmarks = db.session.execute(db.select(Bookmarks).where(Bookmarks.bookmark_owner_id == user.id,or_(Bookmarks.tags.ilike(f"%{query}%"),Bookmarks.title.ilike(f"%{query}%")))).scalars().all()

        else:
            bookmarks = user.bookmarks
    return render_template('index.html',bookmarks=bookmarks,current_user=current_user,user = current_user)
@app.route('/login',methods=['GET','POST'])
def login():
    form = LoginForm()
    if request.method == 'POST' and form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        user = db.session.execute(db.select(User).where(User.email == email)).scalar()
        if user :
            if check_password_hash(user.password,password):
                login_user(user)
                return redirect(url_for('home'))
            else :
                flash('WRONG PASSWORD','warning')
        else :
            flash('Email does not exist ,Register instead','warning')
            return redirect(url_for('signup'))

    return render_template('login.html',form=form ,user=current_user)

@app.route('/sign-up',methods=['GET','POST'])
def signup():
    form = SignUpForm()
    if request.method == 'POST' and form.validate_on_submit():
        name = form.name.data
        email = form.email.data
        user = db.session.execute(db.select(User).where(User.email == email)).scalar()
        if user:
            flash('Email already registered login instead','warning')
            return redirect(url_for('login'))
        hashed_password = generate_password_hash(form.password.data,'scrypt',salt_length=8)
        new_user = User(name=name,email=email,password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        login_user(new_user)
        return redirect(url_for('home'))

    return render_template('signup.html',form=form,user=current_user)
#
@app.route('/add/bookmarks',methods=['GET','POST'])
@login_required
def add():
    form = AddForm()
    user = current_user
    if request.method == 'POST' and form.validate_on_submit():

        title_entered_by_user = form.title.data
        url_entered_by_user = form.url.data
        tags = form.tags.data
        note_to_add = Bookmarks(title=title_entered_by_user,url= url_entered_by_user,tags=tags,bookmark_owner = user)
        db.session.add(note_to_add)
        db.session.commit()
        flash("Note CREATED successfully!", "success")
        return redirect(url_for('home'))
    return render_template('add.html', form =form,user = current_user)
#
@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route('/delete/notes/<int:id>')
@login_required
def delete(id):
    bookmark_to_delete = db.get_or_404(Bookmarks,id)
    db.session.delete(bookmark_to_delete)
    db.session.commit()
    return redirect(url_for('home'))
#
@app.route('/update/notes/<int:id>',methods=['GET','POST'])
@login_required
def update(id):
    form2 = AddForm()
    if request.method == 'POST' and form2.validate_on_submit():
        bookmark_to_update = db.get_or_404(Bookmarks,id)
        bookmark_to_update.title = form2.title.data
        bookmark_to_update.url= form2.url.data
        db.session.commit()
        flash("Note UPDATED successfully!", "info")
        return redirect(url_for('home'))
    if request.method == 'GET' :
        bookmark_to_update = db.get_or_404(Bookmarks, id)
        form2.title.data = bookmark_to_update.title
        form2.url.data = bookmark_to_update.url
        form2.tags.data = bookmark_to_update.tags
    return render_template('update.html',form = form2,id=id,user = current_user)


if __name__ =='__main__':
    app.run(debug=True)

