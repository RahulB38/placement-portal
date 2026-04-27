import csv
import io

from app import app as flask_app
from celery_app import celery_app
from models import Application, StudentProfile


@celery_app.task(name="tasks.export_tasks.export_applications_csv")
def export_applications_csv(student_id):
    with flask_app.app_context():
        student = StudentProfile.query.get(student_id)
        if not student:
            return {"error": "Student not found"}

        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["Student ID", "Roll Number", "Company", "Job Title", "Status", "Applied On"])

        for app in Application.query.filter_by(student_id=student_id):
            drive = app.placement_drive
            company = drive.company if drive else None
            writer.writerow([
                student.id,
                student.roll_number,
                company.company_name if company else "N/A",
                drive.job_title if drive else "N/A",
                app.status,
                app.application_date.strftime("%Y-%m-%d") if app.application_date else ""
            ])

        return {
            "csv": output.getvalue(),
            "filename": f"applications_{student.roll_number}.csv"
        }