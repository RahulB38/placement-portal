from datetime import datetime, timedelta
from flask_mail import Message
from app import app as flask_app
from celery_app import celery_app
from extensions import mail
from models import PlacementDrive, StudentProfile, User, Application, db


@celery_app.task(name="tasks.email_tasks.send_daily_reminders")
def send_daily_reminders():
    with flask_app.app_context():
        now = datetime.utcnow()
        cutoff = now + timedelta(days=1)

        upcoming = PlacementDrive.query.filter(
            PlacementDrive.status == "approved",
            PlacementDrive.application_deadline.between(now, cutoff)
        ).all()

        sent = 0
        for drive in upcoming:
            already_applied = {a.student_id for a in drive.applications}
            students = [s for s in StudentProfile.query.all() if s.id not in already_applied]

            for student in students:
                if not student.user or not student.user.email:
                    continue

                msg = Message(
                    subject=f"Action Required: {drive.job_title} — Application Closes Tomorrow",
                    recipients=[student.user.email]
                )
                msg.body = (
                    f"Dear {student.name},\n\n"
                    f"This is a reminder that the application deadline for "
                    f"{drive.job_title} at {drive.company.company_name} is tomorrow.\n\n"
                    "Please visit the FirstPlace Portal and submit your application "
                    "before the deadline. Students who do not apply will not be "
                    "considered eligible for this Placement Drive.\n\n"
                    "Regards,\nFirstPlace Team"
                )
                mail.send(msg)
                sent += 1

        return {"drives": len(upcoming), "sent": sent}


@celery_app.task(name="tasks.email_tasks.send_monthly_report")
def send_monthly_report():
    with flask_app.app_context():
        admin = User.query.filter_by(role="admin").first()
        if not admin or not admin.email:
            return {"error": "No admin found"}

        since = datetime.utcnow() - timedelta(days=30)
        month = datetime.utcnow().strftime('%B %Y')

        drives = PlacementDrive.query.filter(PlacementDrive.created_at >= since).count()
        apps = Application.query.filter(Application.application_date >= since).count()
        selected = Application.query.filter(
            Application.application_date >= since,
            Application.status == "selected"
        ).count()
        placed = db.session.query(Application.student_id).filter(
            Application.status == "selected",
            Application.updated_at >= since
        ).distinct().count()

        rows = [
            ("Drives Conducted", drives),
            ("Total Applications", apps),
            ("Students Selected", selected),
            ("Unique Students Placed", placed),
        ]
        table_rows = "".join(f"<tr><td>{k}</td><td>{v}</td></tr>" for k, v in rows)

        html = f"""<html><body style="font-family:Arial;padding:20px">
            <h2>FirstPlace — Monthly Activity Report</h2>
            <p>Period: {month}</p>
            <table border="1" cellpadding="10">
                <tr><th>Metric</th><th>Count</th></tr>
                {table_rows}
            </table>
            <p>FirstPlace Campus Portal</p>
        </body></html>"""

        msg = Message(
            subject="Monthly Placement Activity Report",
            recipients=[admin.email]
        )
        msg.html = html
        mail.send(msg)

        return {"sent": True}