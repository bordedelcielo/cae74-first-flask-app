from app import db
from flask_login import UserMixin # Use only for the a USER model
from datetime import datetime as dt, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
from app import login
import secrets
from sqlalchemy import Table, Column, Integer, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
import uuid

Base = declarative_base

association_table = db.Table('association',
    db.Column('user_id', db.ForeignKey('user.id')),
    db.Column('pokemon_id', db.ForeignKey('pokemon.the_pokemon_id'))
)

followers = db.Table(
    'followers',
    db.Column('follower_id',db.Integer, db.ForeignKey('user.id')),
    db.Column('followed_id',db.Integer, db.ForeignKey('user.id'))
)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True, unique = True)
    first_name = db.Column(db.String(150))
    last_name = db.Column(db.String(150))
    email = db.Column(db.String(200), unique=True, index=True)
    password = db.Column(db.String(200))
    icon = db.Column(db.Integer)
    created_on = db.Column(db.DateTime, default=dt.utcnow)
    posts = db.relationship('Post', backref='author', lazy='dynamic')
    followed = db.relationship('User',
                    secondary = followers,
                    primaryjoin=(followers.c.follower_id == id),
                    secondaryjoin=(followers.c.followed_id == id),
                    backref=db.backref('followers',lazy='dynamic'),
                    lazy='dynamic'
                    )
    children = relationship("Pokemon",
                    secondary=association_table, 
                    backref="users"
                    )
                    
    token = db.Column(db.String, index=True, unique=True)
    token_exp = db.Column(db.DateTime)
    is_admin = db.Column(db.Boolean, default=False)

    ##################################################
    ############## Methods for Token auth ############
    ##################################################

    def get_token(self, exp=86400):
        current_time = dt.utcnow()
        # give the user their token if the token is not expired
        if self.token and self.token_exp > current_time + timedelta(seconds=60):
            return self.token
        # if not a token create a token and exp date
        self.token = secrets.token_urlsafe(32)
        self.token_exp = current_time + timedelta(seconds=exp)
        self.save()
        return self.token

    def revoke_token(self):
        self.token_exp = dt.utcnow() - timedelta(seconds=61)

    @staticmethod
    def check_token(token):
        u = User.query.filter_by(token=token).first()
        if not u or u.token_exp < dt.utcnow():
            return None
        return u

    #########################################
    ############# End Methods for tokens ####
    #########################################

    # We want to check if the user is following someone
    def is_following(self, user):
        return self.followed.filter(followers.c.followed_id == user.id).count() > 0

    # follow a user
    def follow(self, user):
        if not self.is_following(user):
            self.followed.append(user)
            db.session.commit()

    # unfollow a user
    def unfollow(self,user):
        if self.is_following(user):
            self.followed.remove(user)
            db.session.commit()

    # Catch a Pokemon


    # get all the posts from the users I am following
    def followed_posts(self):
        #get posts for all the users I'm following
        followed = Post.query.join(followers, (Post.user_id == followers.c.followed_id)).filter(followers.c.follower_id == self.id)
        #get all my own posts
        self_posts = Post.query.filter_by(user_id=self.id)

        #add those together and then I want to sort then my dates in descending order
        all_posts = followed.union(self_posts).order_by(Post.date_created.desc())
        return all_posts


    def from_dict(self, data):
        self.first_name = data['first_name']
        self.last_name = data['last_name']
        self.email = data["email"]
        self.icon = data['icon']
        self.password = self.hash_password(data['password'])

    #salts and hashes our password to make it hard to steal
    def hash_password(self, original_password):
        return generate_password_hash(original_password)

    # compares the user password to the password provided in the login form
    def check_hashed_password(self, login_password):
        return check_password_hash(self.password, login_password)

    # saves the user to the database
    def save(self):
        db.session.add(self) # add the user to the db session
        db.session.commit() #save everything in the session to the database
    
    def get_icon_url(self):
        return f'https://avatars.dicebear.com/api/bottts/{self.icon}.svg'

    def __repr__(self):
        return f'<User: {self.id} | {self.email}>'


@login.user_loader
def load_user(id):
    return User.query.get(int(id))
    
    # SELECT * FROM user WHERE id = ???

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text)
    date_created = db.Column(db.DateTime, default=dt.utcnow)
    date_updated = db.Column(db.DateTime, onupdate=dt.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    # saves the Post to the database
    def save(self):
        db.session.add(self) # add the Post to the db session
        db.session.commit() #save everything in the session to the database

    def edit(self, new_body):
        self.body=new_body
        self.save()
    
    def delete(self):
        db.session.delete(self)
        db.session.commit()
    
    def __repr__(self):
        return f'<id:{self.id} | Post: {self.body[:15]}>'

class Pokemon(db.Model):
    the_pokemon_id = db.Column(db.String, primary_key = True, unique = True)
    name = db.Column(db.String, primary_key=True)
    hp = db.Column(db.Integer)
    attack = db.Column(db.Integer)
    defense = db.Column(db.Integer)
    ability = db.Column(db.String)
    sprite = db.Column(db.String)
    date_added = db.Column(db.DateTime, default = dt.utcnow)
    added_by_user = db.Column(db.String)

    def __init__(self, name, hp, attack, defense, ability, sprite, id='', date_added='', added_by_user=''):
        self.the_pokemon_id = self.set_id()
        self.name = name
        self.hp = hp
        self.attack = attack
        self.defense = defense
        self.ability = ability
        self.sprite = sprite
        self.added_by_user = added_by_user

    def set_id(self):
        return str(uuid.uuid4())