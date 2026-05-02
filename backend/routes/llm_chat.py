from flask import Blueprint, request, jsonify
import os
from openai import OpenAI
from models import db, User, StudentProfile, CompanyProfile, PlacementDrive, Application
from datetime import datetime
import typing

llm_chat_bp = Blueprint('llm_chat', __name__)

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"


def get_database_context():
    try:
        total_students = User.query.filter_by(role='student').count()
        total_companies = User.query.filter_by(role='company').count()
        branches = db.session.query(StudentProfile.branch, db.func.count(StudentProfile.id))\
            .group_by(StudentProfile.branch).all()
        branch_summary = ", ".join([f"{b}: {c}" for b, c in branches])

        avg_cgpa = db.session.query(db.func.avg(StudentProfile.cgpa)).scalar()
        avg_cgpa = round(avg_cgpa, 2) if avg_cgpa else "N/A"
        approved_companies = CompanyProfile.query.filter_by(approval_status='approved').count()
        pending_companies = CompanyProfile.query.filter_by(approval_status='pending').count()
        approved_company_names = db.session.query(CompanyProfile.company_name)\
            .filter_by(approval_status='approved').all()
        company_names = ", ".join([c[0] for c in approved_company_names]) or "None"
        total_drives = PlacementDrive.query.count()
        active_drives = PlacementDrive.query.filter_by(status='approved')\
            .filter(PlacementDrive.application_deadline >= datetime.now()).count()
        closed_drives = PlacementDrive.query.filter(
            PlacementDrive.application_deadline < datetime.now()
        ).count()
        active_drive_list = db.session.query(
            PlacementDrive.job_title,
            PlacementDrive.package_info,
            PlacementDrive.min_cgpa,
            PlacementDrive.application_deadline,
            CompanyProfile.company_name
        ).join(CompanyProfile, PlacementDrive.company_id == CompanyProfile.id)\
         .filter(PlacementDrive.status == 'approved')\
         .filter(PlacementDrive.application_deadline >= datetime.now()).all()

        drives_detail = "\n".join([
            f"  - {d.company_name} | {d.job_title} | Package: {d.package_info or 'N/A'} | Min CGPA: {d.min_cgpa} | Deadline: {d.application_deadline.strftime('%d %b %Y')}"
            for d in active_drive_list
        ]) or "  No active drives currently."
        total_applications = Application.query.count()
        selected_count = Application.query.filter_by(status='selected').count()
        rejected_count = Application.query.filter_by(status='rejected').count()
        pending_apps = Application.query.filter_by(status='applied').count()

        return f"""
You are an assistant for a college placement portal. Answer only based on the data below.
If asked something not in this data, say you don't have that information.

=== PLACEMENT PORTAL SUMMARY ===

STUDENTS:
- Total registered students: {total_students}
- Average CGPA: {avg_cgpa}
- Branch-wise count: {branch_summary or 'N/A'}

COMPANIES:
- Total registered companies: {total_companies}
- Approved companies: {approved_companies}
- Pending approval: {pending_companies}
- Approved company names: {company_names}

PLACEMENT DRIVES:
- Total drives: {total_drives}
- Active/open drives: {active_drives}
- Closed drives: {closed_drives}
- Active drive details:
{drives_detail}

APPLICATIONS:
- Total applications submitted: {total_applications}
- Selected: {selected_count}
- Rejected: {rejected_count}
- Pending/under review: {pending_apps}
"""
    except Exception as e:
        print("DB context error:", e)
        return "Database context unavailable."


@llm_chat_bp.route('/api/llm_chat', methods=['POST'])
def llm_chat():
    data = request.get_json()
    user_message = data.get('message', '')

    if not user_message:
        return jsonify({'error': 'No message provided'}), 400

    try:
        db_context = get_database_context()

        if not OPENROUTER_API_KEY:
            return jsonify({'error': 'OPENROUTER_API_KEY not set on server'}), 500

        # Try using the installed OpenAI client first. Some deployments have
        # mismatched SDKs that reject certain kwargs (e.g. `proxies`). If the
        # client call fails with a TypeError/AttributeError, fall back to a
        # plain HTTP request to the OpenRouter endpoint.
        try:
            client = OpenAI(api_key=OPENROUTER_API_KEY, base_url=OPENROUTER_BASE_URL)
            response = client.chat.completions.create(
                model="openai/gpt-4o-mini",
                messages=[
                    {"role": "system", "content": db_context},
                    {"role": "user", "content": user_message}
                ],
                max_tokens=300,
                temperature=0.5
            )
            # safe access
            bot_reply = None
            if hasattr(response, 'choices') and len(response.choices) > 0:
                choice = response.choices[0]
                # some SDKs return different shapes; try multiple fallbacks
                bot_reply = getattr(choice, 'message', None) or (choice.get('message') if isinstance(choice, dict) else None)
                if isinstance(bot_reply, dict):
                    bot_reply = bot_reply.get('content')
                elif hasattr(bot_reply, 'content'):
                    bot_reply = bot_reply.content
            if not bot_reply:
                # last-resort try indexing into dict-like response
                resp_json = getattr(response, 'to_dict', None)
                if callable(resp_json):
                    resp_json = response.to_dict()
                bot_reply = (resp_json or {}).get('choices', [{}])[0].get('message', {}).get('content', '')

            return jsonify({'reply': bot_reply})
        except (TypeError, AttributeError) as sdk_err:
            # fallback to requests POST when SDK signature is incompatible
            try:
                import requests
                headers = {
                    "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                    "Content-Type": "application/json"
                }
                payload = {
                    "model": "openai/gpt-4o-mini",
                    "messages": [
                        {"role": "system", "content": db_context},
                        {"role": "user", "content": user_message}
                    ],
                    "max_tokens": 300,
                    "temperature": 0.5
                }
                r = requests.post(f"{OPENROUTER_BASE_URL}/chat/completions", json=payload, headers=headers, timeout=30)
                r.raise_for_status()
                data = r.json()
                bot_reply = data.get('choices', [{}])[0].get('message', {}).get('content', '')
                return jsonify({'reply': bot_reply})
            except Exception as http_err:
                print("HTTP fallback error:", http_err)
                return jsonify({'error': str(sdk_err)}), 500
    except Exception as e:
        print("OpenRouter API error:", e)
        return jsonify({'error': str(e)}), 500
