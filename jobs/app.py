from flask import Flask, flash, render_template, request, redirect, url_for
from flask_mail import Mail, Message
from celery import Celery
import logging

app = Flask(__name__)
app.config.from_object("config")
app.secret_key = app.config['SECRET_KEY']

# set up Flask-Mail Integration
mail = Mail(app)

# Set up celery client
client = Celery(app.name, broker=app.config['CELERY_BROKER_URL'])
client.conf.update(app.config)

# For Logging on Debug Mode
logging.basicConfig(filename='jobs.log', level=logging.DEBUG,
                    format=f'%(asctime)s %(levelname)s %(name)s %(threadName)s : %(message)s')


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'GET':
        return render_template('index.html')

    elif request.method == 'POST':
        data = {}
        data['email'] = request.form['email']
        data['first_name'] = request.form['first_name']
        data['last_name'] = request.form['last_name']
        data['message'] = request.form['message']
        duration = int(request.form['duration'])
        duration_unit = request.form['duration_unit']

        if duration_unit == 'minutes':
            duration *= 60
        elif duration_unit == 'hours':
            duration *= 3600
        elif duration_unit == 'days':
            duration *= 86400

        send_mail.apply_async(args=[data], countdown=duration)
        flash(
            f"Email will be sent to {data['email']} in {request.form['duration']} {duration_unit}")

        return redirect(url_for('index'))


@app.post('/send-mail')
def send_my_mail():
    data = request.get_json()

    duration = 1

    send_mail.apply_async(args=[data], countdown=duration)

    return "Message will be sent.", 200


# Add this decorator to our send_mail function
@client.task
def send_mail(data):
    """ Function to send emails.
    """
    with app.app_context():
        msg = Message("Ping!",
                      sender="admin.ping",
                      recipients=[data['email']])
        msg.body = data['message']
        mail.send(msg)


if __name__ == '__main__':
    app.run(debug=True, port=5001)
