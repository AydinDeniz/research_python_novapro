from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_restful import Api, Resource
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///jobs.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
api = Api(app)

scheduler = BackgroundScheduler()
scheduler.start()

# Models
class Job(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    cron_expression = db.Column(db.String(100), nullable=False)
    last_run = db.Column(db.DateTime, nullable=True)

class JobLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    job_id = db.Column(db.Integer, db.ForeignKey('job.id'), nullable=False)
    job = db.relationship('Job', backref=db.backref('logs', lazy=True))
    timestamp = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    message = db.Column(db.String(200), nullable=False)

db.create_all()

# Job function to be scheduled
def job_function(job_id):
    job = Job.query.get(job_id)
    if job:
        job.last_run = datetime.datetime.utcnow()
        db.session.commit()
        log = JobLog(job_id=job_id, message="Job executed")
        db.session.add(log)
        db.session.commit()

# Resources
class JobResource(Resource):
    def post(self):
        data = request.json
        name = data.get('name')
        cron_expression = data.get('cron_expression')
        
        job = Job(name=name, cron_expression=cron_expression)
        db.session.add(job)
        db.session.commit()
        
        trigger = CronTrigger.from_crontab(cron_expression)
        scheduler.add_job(job_function, trigger, args=[job.id], id=str(job.id))
        
        return {'id': job.id, 'name': job.name, 'cron_expression': job.cron_expression}, 201

class JobHistoryResource(Resource):
    def get(self, job_id):
        job = Job.query.get(job_id)
        if job:
            logs = JobLog.query.filter_by(job_id=job_id).all()
            log_history = [{'timestamp': log.timestamp.isoformat(), 'message': log.message} for log in logs]
            return {'job_id': job_id, 'logs': log_history}, 200
        else:
            return {'error': 'Job not found'}, 404

api.add_resource(JobResource, '/jobs')
api.add_resource(JobHistoryResource, '/jobs/<int:job_id>/history')

if __name__ == '__main__':
    app.run(debug=True)