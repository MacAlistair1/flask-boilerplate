from flask import Flask, flash, render_template, request, redirect, url_for
from flask_mail import Mail, Message
from celery import Celery
import logging
from flask_cors import CORS

app = Flask(__name__)
app.config.from_object("config")
app.secret_key = app.config['SECRET_KEY']


 # cors init
# cors = CORS(app)


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
        data['recipients'] = [request.form['email']]
        data['first_name'] = request.form['first_name']
        data['last_name'] = request.form['last_name']
        data['subject'] = "Ping!!"
        data['body'] = request.form['message']
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
        msg = Message(data['subject'],
                      recipients=data['recipients'])
        msg.body = data['body']
        data['action'] = url_for('index', _external=True)
        msg.html = render_template("mail/test.html", data=data)
        mail.send(msg)

if __name__ == '__main__':
    app.run(debug=True, port=5001)
