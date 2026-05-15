from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify, send_file, make_response
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_mail import Mail, Message
from models import db, Admin, Registration, Donation, EventSchedule
from config import Config
from datetime import datetime
import os, openpyxl

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)
mail = Mail(app)

login_manager = LoginManager(app)
login_manager.login_view = 'admin_login'
login_manager.login_message = 'Please login to access admin panel.'

@login_manager.user_loader
def load_user(user_id):
    return Admin.query.get(int(user_id))

# ─── SEED DATABASE ────────────────────────────────────────────────────────────
def seed_data():
    # Create admin
    if not Admin.query.first():
        admin = Admin(
            lesson_no='00000',
            name='YSS Admin',
            email=app.config['ADMIN_EMAIL'],
            mobile='9494457607'
        )
        admin.set_password(app.config['ADMIN_PASSWORD'])
        db.session.add(admin)

    # Seed schedule
    if not EventSchedule.query.first():
        schedule_data = [
            # Day 1 – 24 June 2026
            (1,'Day 1 – 24 June 2026','05:00 AM','06:00 AM','Morning Meditation','meditation',1),
            (1,'Day 1 – 24 June 2026','06:00 AM','07:00 AM','Energisation Exercises','other',2),
            (1,'Day 1 – 24 June 2026','07:00 AM','08:00 AM','Breakfast','food',3),
            (1,'Day 1 – 24 June 2026','08:30 AM','10:00 AM','Spiritual Talk – Kriya Yoga Introduction','talk',4),
            (1,'Day 1 – 24 June 2026','10:00 AM','11:00 AM','Group Meditation Session','meditation',5),
            (1,'Day 1 – 24 June 2026','11:00 AM','01:00 PM','Devotional Bhajans & Kirtan','bhajan',6),
            (1,'Day 1 – 24 June 2026','01:00 PM','02:00 PM','Lunch','food',7),
            (1,'Day 1 – 24 June 2026','02:00 PM','03:00 PM','Rest / Personal Sadhana','other',8),
            (1,'Day 1 – 24 June 2026','03:00 PM','05:00 PM','Volunteer Service (Seva)','volunteer',9),
            (1,'Day 1 – 24 June 2026','05:00 PM','06:30 PM','Evening Meditation','meditation',10),
            (1,'Day 1 – 24 June 2026','06:30 PM','07:30 PM','Satsanga & Discourse','talk',11),
            (1,'Day 1 – 24 June 2026','07:30 PM','08:30 PM','Dinner','food',12),
            (1,'Day 1 – 24 June 2026','08:30 PM','09:30 PM','Night Bhajans & Aarti','bhajan',13),
            # Day 2 – 25 June 2026
            (2,'Day 2 – 25 June 2026','04:30 AM','05:30 AM','Brahma Muhurta Meditation','meditation',1),
            (2,'Day 2 – 25 June 2026','05:30 AM','06:30 AM','Energisation Exercises','other',2),
            (2,'Day 2 – 25 June 2026','07:00 AM','08:00 AM','Breakfast','food',3),
            (2,'Day 2 – 25 June 2026','08:30 AM','10:30 AM','Deep Meditation Workshop','meditation',4),
            (2,'Day 2 – 25 June 2026','10:30 AM','12:00 PM','Spiritual Talk – Path of Devotion','talk',5),
            (2,'Day 2 – 25 June 2026','12:00 PM','01:00 PM','Bhajans & Group Prayer','bhajan',6),
            (2,'Day 2 – 25 June 2026','01:00 PM','02:00 PM','Lunch','food',7),
            (2,'Day 2 – 25 June 2026','02:00 PM','04:00 PM','Volunteer Service & Ashram Upkeep','volunteer',8),
            (2,'Day 2 – 25 June 2026','04:00 PM','05:00 PM','Question & Answer Session','talk',9),
            (2,'Day 2 – 25 June 2026','05:00 PM','06:30 PM','Evening Meditation & Chanting','meditation',10),
            (2,'Day 2 – 25 June 2026','06:30 PM','07:30 PM','Satsanga – Divine Teachings','talk',11),
            (2,'Day 2 – 25 June 2026','07:30 PM','08:30 PM','Dinner','food',12),
            (2,'Day 2 – 25 June 2026','08:30 PM','10:00 PM','Candlelight Bhajans & Meditation','bhajan',13),
            # Day 3 – 26 June 2026
            (3,'Day 3 – 26 June 2026','05:00 AM','07:00 AM','Long Meditation Session','meditation',1),
            (3,'Day 3 – 26 June 2026','07:00 AM','08:00 AM','Breakfast','food',2),
            (3,'Day 3 – 26 June 2026','08:30 AM','10:00 AM','Kriya Yoga Techniques Class','talk',3),
            (3,'Day 3 – 26 June 2026','10:00 AM','11:30 AM','Group Healing Meditation','meditation',4),
            (3,'Day 3 – 26 June 2026','11:30 AM','01:00 PM','Final Bhajans & Devotional Songs','bhajan',5),
            (3,'Day 3 – 26 June 2026','01:00 PM','02:00 PM','Lunch & Prasad Distribution','food',6),
            (3,'Day 3 – 26 June 2026','02:00 PM','03:30 PM','Closing Ceremony & Blessings','talk',7),
            (3,'Day 3 – 26 June 2026','03:30 PM','04:30 PM','Volunteer Wrap-up & Farewell','volunteer',8),
        ]
        for s in schedule_data:
            item = EventSchedule(
                day_number=s[0], day_label=s[1], start_time=s[2],
                end_time=s[3], activity=s[4], category=s[5], sort_order=s[6]
            )
            db.session.add(item)
    db.session.commit()

# ─── EXCEL HELPERS ────────────────────────────────────────────────────────────
def update_registrations_excel():
    path = os.path.join(app.config['EXPORTS_DIR'], 'registrations.xlsx')
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = 'Registrations'
    headers = ['S.No','Reg ID','Lesson No','Full Name','Gender','Age','Place','WhatsApp',
               'Kriyaban','Accommodation','Volunteer','Arrival','Departure',
               'Payment Mode','Payment Status','Reg Status','Date']
    ws.append(headers)
    regs = Registration.query.order_by(Registration.id).all()
    for i, r in enumerate(regs, 1):
        ws.append([i, r.reg_id, r.lesson_no, r.full_name, r.gender, r.age, r.place,
                   r.whatsapp, 'Yes' if r.is_kriyaban else 'No',
                   'Yes' if r.accommodation else 'No', 'Yes' if r.volunteer else 'No',
                   r.arrival_date, r.departure_date, r.payment_mode,
                   r.payment_status, r.reg_status,
                   r.created_at.strftime('%d-%m-%Y') if r.created_at else ''])
    wb.save(path)

def update_donations_excel():
    path = os.path.join(app.config['EXPORTS_DIR'], 'donations.xlsx')
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = 'Donations'
    headers = ['S.No','Donation ID','Lesson No','Name','Age','Place','WhatsApp',
               'Amount (₹)','Payment Mode','Payment Status','Date']
    ws.append(headers)
    dons = Donation.query.order_by(Donation.id).all()
    for i, d in enumerate(dons, 1):
        ws.append([i, d.donation_id, d.lesson_no, d.name, d.age, d.place,
                   d.whatsapp, d.amount, d.payment_mode, d.payment_status,
                   d.created_at.strftime('%d-%m-%Y') if d.created_at else ''])
    wb.save(path)

def send_registration_email(reg):
    try:
        msg = Message(
            subject='Registration Confirmed – YSS 3-Day Spiritual Program, Anantapur',
            recipients=[app.config['MAIL_USERNAME']],
            html=render_template('email_reg.html', reg=reg, config=app.config)
        )
        mail.send(msg)
    except Exception as e:
        app.logger.warning(f'Email send failed: {e}')

# ─── PUBLIC ROUTES ────────────────────────────────────────────────────────────
@app.route('/')
def index():
    return render_template('index.html', config=app.config)

@app.route('/about')
def about():
    return render_template('about.html', config=app.config)

@app.route('/schedule')
def schedule():
    days = {}
    schedules = EventSchedule.query.order_by(EventSchedule.day_number, EventSchedule.sort_order).all()
    for s in schedules:
        days.setdefault(s.day_number, {'label': s.day_label, 'items': []})['items'].append(s)
    return render_template('schedule.html', days=days, config=app.config)

@app.route('/faq')
def faq():
    return render_template('faq.html', config=app.config)

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        flash('Your message has been sent. We will get back to you soon!', 'success')
        return redirect(url_for('contact'))
    return render_template('contact.html', config=app.config)

# ─── REGISTRATION ─────────────────────────────────────────────────────────────
@app.route('/registration', methods=['GET', 'POST'])
def registration():
    if request.method == 'POST':
        errors = []
        lesson_no = request.form.get('lesson_no', '').strip()
        full_name = request.form.get('full_name', '').strip()
        gender = request.form.get('gender', '').strip()
        age = request.form.get('age', '').strip()
        place = request.form.get('place', '').strip()
        whatsapp = request.form.get('whatsapp', '').strip()
        is_kriyaban = request.form.get('is_kriyaban') == 'yes'
        accommodation = request.form.get('accommodation') == 'yes'
        volunteer = request.form.get('volunteer') == 'yes'
        arrival_date = request.form.get('arrival_date', '').strip()
        departure_date = request.form.get('departure_date', '').strip()
        payment_mode = request.form.get('payment_mode', '').strip()

        if not lesson_no: errors.append('Lesson Number is required.')
        if not full_name: errors.append('Full Name is required.')
        if not gender: errors.append('Gender is required.')
        if not age or not age.isdigit(): errors.append('Valid Age is required.')
        if not place: errors.append('Place is required.')
        if not whatsapp or len(whatsapp) < 10: errors.append('Valid WhatsApp number is required.')
        if not arrival_date: errors.append('Date of Arrival is required.')
        if not departure_date: errors.append('Date of Departure is required.')
        if not payment_mode: errors.append('Payment Mode is required.')

        if errors:
            for e in errors:
                flash(e, 'error')
            return render_template('registration.html', config=app.config, form=request.form)

        reg = Registration(
            lesson_no=lesson_no, full_name=full_name, gender=gender,
            age=int(age), place=place, whatsapp=whatsapp,
            is_kriyaban=is_kriyaban, accommodation=accommodation,
            volunteer=volunteer, arrival_date=arrival_date,
            departure_date=departure_date, payment_mode=payment_mode
        )
        db.session.add(reg)
        db.session.commit()
        update_registrations_excel()
        send_registration_email(reg)
        return redirect(url_for('reg_success', reg_id=reg.reg_id))

    return render_template('registration.html', config=app.config, form={})

@app.route('/registration/success/<reg_id>')
def reg_success(reg_id):
    reg = Registration.query.filter_by(reg_id=reg_id).first_or_404()
    return render_template('reg_success.html', reg=reg, config=app.config)

# ─── DONATION ─────────────────────────────────────────────────────────────────
@app.route('/donation', methods=['GET', 'POST'])
def donation():
    if request.method == 'POST':
        errors = []
        lesson_no = request.form.get('lesson_no', '').strip()
        name = request.form.get('name', '').strip()
        age = request.form.get('age', '').strip()
        place = request.form.get('place', '').strip()
        whatsapp = request.form.get('whatsapp', '').strip()
        amount = request.form.get('amount', '').strip()
        payment_mode = request.form.get('payment_mode', '').strip()

        if not lesson_no: errors.append('Lesson Number is required.')
        if not name: errors.append('Name is required.')
        if not age or not age.isdigit(): errors.append('Valid Age is required.')
        if not place: errors.append('Place is required.')
        if not whatsapp or len(whatsapp) < 10: errors.append('Valid WhatsApp number is required.')
        if not amount: errors.append('Donation Amount is required.')
        try:
            float(amount)
        except:
            errors.append('Valid Amount is required.')
        if not payment_mode: errors.append('Payment Mode is required.')

        if errors:
            for e in errors:
                flash(e, 'error')
            return render_template('donation.html', config=app.config, form=request.form)

        don = Donation(
            lesson_no=lesson_no, name=name, age=int(age), place=place,
            whatsapp=whatsapp, amount=float(amount), payment_mode=payment_mode
        )
        db.session.add(don)
        db.session.commit()
        update_donations_excel()
        return redirect(url_for('donation_success', don_id=don.donation_id))

    return render_template('donation.html', config=app.config, form={})

@app.route('/donation/success/<don_id>')
def donation_success(don_id):
    don = Donation.query.filter_by(donation_id=don_id).first_or_404()
    return render_template('donation_success.html', don=don, config=app.config)

# ─── ADMIN AUTH ───────────────────────────────────────────────────────────────
@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if current_user.is_authenticated:
        return redirect(url_for('admin_dashboard'))
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '').strip()
        admin = Admin.query.filter_by(email=email).first()
        if admin and admin.check_password(password):
            login_user(admin)
            return redirect(url_for('admin_dashboard'))
        flash('Invalid email or password.', 'error')
    return render_template('admin/login.html', config=app.config)

@app.route('/admin/logout')
@login_required
def admin_logout():
    logout_user()
    flash('Logged out successfully.', 'success')
    return redirect(url_for('admin_login'))

# ─── ADMIN DASHBOARD ──────────────────────────────────────────────────────────
@app.route('/admin/dashboard')
@login_required
def admin_dashboard():
    total_regs = Registration.query.count()
    total_dons = Donation.query.count()
    total_amount = db.session.query(db.func.sum(Donation.amount)).scalar() or 0
    recent_regs = Registration.query.order_by(Registration.created_at.desc()).limit(5).all()
    return render_template('admin/dashboard.html',
        total_regs=total_regs, total_dons=total_dons,
        total_amount=total_amount, recent_regs=recent_regs, config=app.config)

# ─── ADMIN REGISTRATIONS ──────────────────────────────────────────────────────
@app.route('/admin/registrations')
@login_required
def admin_registrations():
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '')
    pay_status = request.args.get('pay_status', '')
    reg_status = request.args.get('reg_status', '')
    q = Registration.query
    if search:
        q = q.filter(db.or_(Registration.full_name.ilike(f'%{search}%'),
                             Registration.whatsapp.ilike(f'%{search}%'),
                             Registration.reg_id.ilike(f'%{search}%')))
    if pay_status:
        q = q.filter_by(payment_status=pay_status)
    if reg_status:
        q = q.filter_by(reg_status=reg_status)
    pagination = q.order_by(Registration.id.desc()).paginate(page=page, per_page=10)
    return render_template('admin/registrations.html', pagination=pagination,
                           search=search, pay_status=pay_status, reg_status=reg_status, config=app.config)

@app.route('/admin/registrations/export')
@login_required
def export_registrations():
    update_registrations_excel()
    path = os.path.join(app.config['EXPORTS_DIR'], 'registrations.xlsx')
    return send_file(path, as_attachment=True, download_name='registrations.xlsx')

@app.route('/api/registrations/<int:rid>', methods=['PUT', 'DELETE'])
@login_required
def api_registration(rid):
    reg = Registration.query.get_or_404(rid)
    if request.method == 'DELETE':
        db.session.delete(reg)
        db.session.commit()
        update_registrations_excel()
        return jsonify({'success': True})
    data = request.json
    reg.payment_status = data.get('payment_status', reg.payment_status)
    reg.reg_status = data.get('reg_status', reg.reg_status)
    db.session.commit()
    update_registrations_excel()
    return jsonify({'success': True})

# ─── ADMIN DONATIONS ──────────────────────────────────────────────────────────
@app.route('/admin/donations')
@login_required
def admin_donations():
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '')
    pay_status = request.args.get('pay_status', '')
    q = Donation.query
    if search:
        q = q.filter(db.or_(Donation.name.ilike(f'%{search}%'),
                             Donation.whatsapp.ilike(f'%{search}%'),
                             Donation.donation_id.ilike(f'%{search}%')))
    if pay_status:
        q = q.filter_by(payment_status=pay_status)
    pagination = q.order_by(Donation.id.desc()).paginate(page=page, per_page=10)
    return render_template('admin/donations.html', pagination=pagination,
                           search=search, pay_status=pay_status, config=app.config)

@app.route('/admin/donations/export')
@login_required
def export_donations():
    update_donations_excel()
    path = os.path.join(app.config['EXPORTS_DIR'], 'donations.xlsx')
    return send_file(path, as_attachment=True, download_name='donations.xlsx')

@app.route('/api/donations/<int:did>', methods=['PUT', 'DELETE'])
@login_required
def api_donation(did):
    don = Donation.query.get_or_404(did)
    if request.method == 'DELETE':
        db.session.delete(don)
        db.session.commit()
        update_donations_excel()
        return jsonify({'success': True})
    data = request.json
    don.payment_status = data.get('payment_status', don.payment_status)
    db.session.commit()
    update_donations_excel()
    return jsonify({'success': True})

# ─── ADMIN ID CARDS ───────────────────────────────────────────────────────────
@app.route('/admin/id-cards')
@login_required
def admin_id_cards():
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '')
    reg_status = request.args.get('reg_status', '')
    q = Registration.query
    if search:
        q = q.filter(db.or_(Registration.full_name.ilike(f'%{search}%'),
                             Registration.whatsapp.ilike(f'%{search}%')))
    if reg_status:
        q = q.filter_by(reg_status=reg_status)
    pagination = q.order_by(Registration.id).paginate(page=page, per_page=6)
    return render_template('admin/id_cards.html', pagination=pagination,
                           search=search, reg_status=reg_status, config=app.config)

# ─── ADMIN SCHEDULE MGMT ─────────────────────────────────────────────────────
@app.route('/admin/schedule', methods=['GET', 'POST'])
@login_required
def admin_schedule():
    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'add':
            item = EventSchedule(
                day_number=int(request.form.get('day_number')),
                day_label=request.form.get('day_label'),
                start_time=request.form.get('start_time'),
                end_time=request.form.get('end_time'),
                activity=request.form.get('activity'),
                category=request.form.get('category'),
                sort_order=int(request.form.get('sort_order', 99))
            )
            db.session.add(item)
            db.session.commit()
            flash('Schedule item added.', 'success')
        elif action == 'delete':
            item = EventSchedule.query.get(int(request.form.get('item_id')))
            if item:
                db.session.delete(item)
                db.session.commit()
            flash('Schedule item deleted.', 'success')
        elif action == 'edit':
            item = EventSchedule.query.get(int(request.form.get('item_id')))
            if item:
                item.day_number = int(request.form.get('day_number'))
                item.day_label = request.form.get('day_label')
                item.start_time = request.form.get('start_time')
                item.end_time = request.form.get('end_time')
                item.activity = request.form.get('activity')
                item.category = request.form.get('category')
                item.sort_order = int(request.form.get('sort_order', 99))
                db.session.commit()
            flash('Schedule item updated.', 'success')
        return redirect(url_for('admin_schedule'))

    schedules = EventSchedule.query.order_by(EventSchedule.day_number, EventSchedule.sort_order).all()
    return render_template('admin/schedule_mgmt.html', schedules=schedules, config=app.config)

# ─── ERROR HANDLERS ───────────────────────────────────────────────────────────
@app.errorhandler(404)
def not_found(e):
    return render_template('errors/404.html', config=app.config), 404

@app.errorhandler(500)
def server_error(e):
    return render_template('errors/500.html', config=app.config), 500

# ─── MAIN ─────────────────────────────────────────────────────────────────────
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        seed_data()
    app.run(debug=True, port=5000)
