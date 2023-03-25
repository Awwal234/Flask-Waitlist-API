from flask_restx import Namespace, Resource, fields, Api
from flask_sqlalchemy import SQLAlchemy
from flask import request, Flask
from flask_mail import Mail, Message
from http import HTTPStatus
from flask_migrate import Migrate


def create_app():
    app = Flask(__name__)
    api = Api(app, title="A waitlist API")
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///uss.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = "lol234090124lo"
    app.config['MAIL_SERVER'] = 'sandbox.smtp.mailtrap.io'
    app.config['MAIL_PORT'] = 2525
    app.config['MAIL_USERNAME'] = '4f8ebb01149373'
    app.config['MAIL_PASSWORD'] = 'cd04ce84df12bb'
    app.config['MAIL_USE_TLS'] = True
    app.config['MAIL_USE_SSL'] = False
    db = SQLAlchemy()
    db.init_app(app)
    with app.app_context():
        db.create_all()
    Migrate(app, db)

    class Waitlistdb(db.Model):
        __tablename__ = 'waitlistdb'
        id = db.Column(db.Integer(), primary_key=True, autoincrement=True)
        email = db.Column(db.String(50), unique=True, nullable=False)

        def __repr__(self):
            return '<Waitlistdb %r>' % self.email

    # namespace
    mail_namespace = Namespace('mailing', description="add mail to database")

    mail_schema = mail_namespace.model('AddMail', {
        'id': fields.Integer(readOnly=True, description="id of user"),
        'email': fields.String(required=True, description="email of user")
    })

    # function to adding mail to waitlist database

    @mail_namespace.route('/add/waitlist')
    class add_mail(Resource):
        @mail_namespace.expect(mail_schema)
        @mail_namespace.marshal_with(mail_schema)
        def post(self):
            data = request.get_json()
            email = data.get('email')
            wait_list = Waitlistdb(email=email)

            db.session.add(wait_list)
            db.session.commit()
            if wait_list:
                apps = app
                mail = Mail(apps)

                msg = Message('Gloria from PayDay!',
                              sender='fabowalemuhawwal@gmail.com', recipients=['fabowalemuhawwal@gmail.com'])
                msg.body = "Hello {} thanks for joining our waitlist".format(
                    email)
                mail.send(msg)
            return wait_list, HTTPStatus.CREATED

    # end namespace
    api.add_namespace(mail_namespace, path="/api")

    return app
