import functools
from flask import Blueprint, flash, g, redirect, render_template
from flask import request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.exceptions import abort

from flaskr.db import get_db
from flaskr.auth import login_required

bp = Blueprint('blog', __name__)

@bp.route('/')
def index():
    db = get_db()
    print(db)
    posts = db.execute(
        "SELECT p.id, title, body, created, author_id, username"
        " FROM post p JOIN user u ON p.author_id = u.id"
        " ORDER BY created desc"
    ).fetchall()

    return render_template('blog/index.html', posts=posts)


def get_post(id, check_author=True):
    post = (
        get_db()
        .execute(
            'SELECT p.id, title, body, created, author_id, username'
            ' FROM post p JOIN user u ON p.author_id=u.id'
            ' WHERE p.id = ?', (id,),
        )
        .fetchone()
    )

    if post is None:
        abort(404, "Post id {0} doesn't exist.".format(id))
    
    if check_author and post['author_id'] != g.user['id']:
        abort(403)
    
    return post


@bp.route('/create', methods=['POST', 'GET'])
@login_required
def create():
    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        # image = request.files(['image'])
        error = None

        if not title:
            error = 'Title is required.'
            
        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'INSERT INTO post (title, body, author_id)'
                'VALUES (?, ?, ?)', (title, body, g.user['id'])
            )

            db.commit()
            return redirect(url_for('blog.index'))

    return render_template('blog/create.html')


@bp.route('/<int:id>/update', methods=['POST', 'GET'])
@login_required
def update(id):
    post = get_post(id)

    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        # image = request.form['image']
        error = None

        if not title:
            error = 'Title is required.'
        
        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'UPDATE post SET title = ?, body = ? WHERE id = ?', (title, body, id)
            )

            db.commit()
            return redirect(url_for('blog.index'))


    return render_template('blog/update.html', post=post)


@bp.route('/<int:id>/view')
def viewmore(id):
    post = get_post(id)

    db = get_db()
    posts = db.execute(
        'SELECT p.id, title, body, created, author_id, username'
        ' FROM post p JOIN user u ON p.author_id = u.id'
        ' ORDER BY created DESC'
    ).fetchall()

    return render_template('blog/viewmore.html', post=post, posts=posts)


@bp.route('/<int:id>/delete', methods=['POST',])
@login_required
def delete(id):
    get_post(id)
    db = get_db()
    db.execute(
        'DELETE FROM post WHERE id = ?',(id,)
    )

    db.commit()
    
    return redirect(url_for('blog.index'))