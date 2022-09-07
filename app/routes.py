from datetime import datetime
from flask import render_template, flash, redirect, url_for, request
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.urls import url_parse
from app import app, db
from app.forms import LoginForm, RegistrationForm, EditProfileForm, ResetPasswordRequestForm, ResetPasswordForm, PeriodForm
#EmptyForm, PostForm, 
from app.models import User, Period
#Post
from app.email import send_password_reset_email


@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()

@app.route('/', methods=['GET', 'POST'])
@app.route('/index_pic', methods=['GET', 'POST'])
#@login_required
def index_pic():
        
    return render_template('index_pic.html', title='Home')
    # ,form=form,next_url=next_url, prev_url=prev_url)

@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
#@login_required
def index():
    page = request.args.get('page', 1, type=int)
    dates = Period.query.filter(Period.reserved_user.is_(None)).paginate(page, app.config['LINES_PER_PAGE'], False)
   
    return render_template('index.html', title='Home', lines=dates.items)
    # ,form=form,next_url=next_url, prev_url=prev_url)

@app.route('/explore', methods=['GET', 'POST'])
@login_required
def explore():
    page = request.args.get('page', 1, type=int)
    #dates = Period.query.paginate(page, app.config['LINES_PER_PAGE'], False) 
    dates = Period.query.filter(Period.reserved_user.is_(None)).paginate(page, app.config['LINES_PER_PAGE'], False)
    #next_url = url_for('home', page=dates.next_num) if dates.has_next else None 
    #prev_url = url_for('home', page=dates.prev_num) if dates.has_prev else None 
    return render_template('home.html', title='Home', lines=dates.items)
    #next_url=next_url, prev_url=prev_url) 

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('explore'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Benutzername oder Passwort falsch.')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('explore')
        return redirect(next_page)
    return render_template('login.html', title='Login', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data, 
                    name=form.name.data, lastname=form.lastname.data, 
                    address=form.address.data, phone=form.phone.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Registration erfolgreich abgeschlossen, vielen Dank!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Registrieren', form=form)


@app.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            send_password_reset_email(user)
        flash('Check your email for the instructions to reset your password')
        return redirect(url_for('login'))
    return render_template('reset_password_request.html',
                           title='Reset Password', form=form)


@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    user = User.verify_reset_password_token(token)
    if not user:
        return redirect(url_for('index'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash('Passwort wurde erfolgreich zurückgesetzt.')
        return redirect(url_for('login'))
    return render_template('reset_password.html', form=form)


@app.route('/user/<username>')
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    page = request.args.get('page', 1, type=int)
    #dates = Period.query.paginate(page, app.config['LINES_PER_PAGE'], False) 
    dates = Period.query.filter_by(reserved_user=user.id).paginate(page, app.config['LINES_PER_PAGE'], False)
    return render_template('user.html', title='User', user=user, lines=dates.items) 
    


@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm(current_user.username)
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.phone = form.phone.data
        #current_user.about_me = form.about_me.data
        db.session.commit()
        flash('Änderungen gespeichert.')
        return redirect(url_for('edit_profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.phone.data = current_user.phone
        #form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', title='Edit Profile',
                           form=form)


@app.route('/reserve/<period_id>')
@login_required
def reserve(period_id : str):
    period = Period.query.get(period_id) 
    period.reserved_user = current_user.id 
    db.session.add(period) 
    db.session.commit()
    flash('Reserviert vom {} bis {}'.format(period.begin.strftime('%d.%m.%Y'), period.end.strftime('%d.%m.%Y')))
    return redirect(url_for('user', username=current_user.username))

@app.route('/delete/<period_id>')
@login_required
def delete(period_id : str):
    period = Period.query.get(period_id)
    period.reserved_user = current_user.id
    if period is None:
        flash('Period not found.')
        return redirect(url_for('user', username=current_user.username))
    if period.reserved_user != current_user.id:
        flash('You cannot delete this period.')
        return redirect(url_for('user', username=current_user.username))
    db.session.delete(period)
    db.session.commit()
    flash('PERIODE GELÖSCHT')
    return redirect(url_for('admin', username=current_user.username))


@app.route('/delete_res/<period_id>')
@login_required
def delete_res(period_id : str):
    period = Period.query.get(period_id)
    period.reserved_user = current_user.id
    if period is None:
        flash('Period not found.')
        return redirect(url_for('user', username=current_user.username))
    if period.reserved_user != current_user.id:
        flash('You cannot cancel this period.')
        return redirect(url_for('user', username=current_user.username))
    period.reserved_user = None
    db.session.commit()
    flash('RESERVATION ANNULLIERT')
    return redirect(url_for('user', username=current_user.username))



@app.route('/admin', methods=['GET', 'POST']) 
@login_required
def admin(): 
    if current_user.id !=1:
        flash('Zutritt nur für Administrator')
        return redirect(url_for('logout'))
    form = PeriodForm()
    if form.validate_on_submit(): 
        period = Period(begin=form.begin.data, end=form.end.data) 
        db.session.add(period)
        db.session.commit()
        flash('Periode von {} bis {} erfasst!'. 
            format(period.begin.strftime('%d.%m.%Y'), 
            period.end.strftime('%d.%m.%Y')))
        return redirect(url_for('admin')) 
    page = request.args.get('page', 1, type=int)
    dates = Period.query.paginate(page, app.config['LINES_PER_PAGE'], False) 
    #dates = Period.query.paginate( page, app.config['LINES_PER_PAGE'], False) 
    next_url = url_for('admin', page=dates.next_num) \
        if dates.has_next else None
    prev_url = url_for('admin', page=dates.prev_num) \
        if dates.has_prev else None
    return render_template('admin.html', title='Admin', form=form, lines=dates.items, next_url=next_url, prev_url=prev_url)