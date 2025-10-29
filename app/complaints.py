# app/complaints.py
from flask import (
    Blueprint, render_template, request, redirect,
    url_for, flash, jsonify, send_file, Response
)
from .models import Complaint, ComplaintType, Area, User
from . import db
from flask_login import login_required, current_user
from sqlalchemy import func
import os, re, csv, io, base64
from datetime import datetime

bp = Blueprint('complaints', __name__)

# ---------------------------
# CSV Path Setup
# ---------------------------
LOCAL_DATA_DIR = r"D:\Project\complaint-analyzer\data"
os.makedirs(LOCAL_DATA_DIR, exist_ok=True)
COMPLAINTS_CSV_PATH = os.path.join(LOCAL_DATA_DIR, "complaints.csv")


# ---------------------------
# Helper: Save All Complaints to CSV
# ---------------------------
def save_all_complaints_to_csv():
    complaints = Complaint.query.order_by(Complaint.id).all()
    fieldnames = ["id", "user_id", "username", "email", "phone", "type", "area", "status", "text"]
    with open(COMPLAINTS_CSV_PATH, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for c in complaints:
            writer.writerow({
                "id": c.id,
                "user_id": c.user_id,
                "username": getattr(c.user, "username", ""),
                "email": getattr(c.user, "email", ""),
                "phone": getattr(c.user, "phone", ""),
                "type": getattr(c.complaint_type, "name", ""),
                "area": getattr(c.area, "name", ""),
                "status": c.status,
                "text": c.text
            })


# ---------------------------
# Submit Complaint (User Only)
# ---------------------------
@bp.route('/submit', methods=['GET', 'POST'])
@login_required
def submit():
    if getattr(current_user, 'role', '') == "admin":
        flash("Admins cannot submit complaints.", "error")
        return redirect(url_for('complaints.dashboard'))

    types = ComplaintType.query.order_by(ComplaintType.name).all()
    areas = Area.query.order_by(Area.name).all()

    if request.method == 'POST':
        text = request.form.get('description', '').strip()
        type_name = request.form.get('complaint_type_input', '').strip()
        area_name = request.form.get('area_input', '').strip()

        if not type_name or not area_name:
            flash('Please enter both type and area.', 'error')
            return redirect(url_for('complaints.submit'))

        if not re.match(r'^[A-Za-z\s]+$', type_name):
            flash('Complaint type must contain only letters.', 'error')
            return redirect(url_for('complaints.submit'))

        complaint_type = ComplaintType.query.filter_by(name=type_name).first()
        if not complaint_type:
            complaint_type = ComplaintType(name=type_name)
            db.session.add(complaint_type)
            db.session.commit()

        area = Area.query.filter_by(name=area_name).first()
        if not area:
            area = Area(name=area_name)
            db.session.add(area)
            db.session.commit()

        complaint = Complaint(
            user_id=current_user.id,
            complaint_type_id=complaint_type.id,
            area_id=area.id,
            text=text,
            status='pending'
        )
        db.session.add(complaint)
        db.session.commit()

        save_all_complaints_to_csv()
        flash('Complaint submitted successfully!', 'success')
        return redirect(url_for('complaints.submit'))

    complaints = Complaint.query.filter_by(user_id=current_user.id).order_by(Complaint.id.desc()).all()
    return render_template('submit.html', types=types, areas=areas, complaints=complaints)


# ---------------------------
# Dashboard (Admin & User)
# ---------------------------
@bp.route('/dashboard')
@login_required
def dashboard():
    is_admin = getattr(current_user, 'role', '') == "admin"
    complaints = Complaint.query.order_by(Complaint.id.desc()).all() if is_admin else \
        Complaint.query.filter_by(user_id=current_user.id).order_by(Complaint.id.desc()).all()

    # Chart data
    type_data = db.session.query(ComplaintType.name, func.count(Complaint.id)) \
        .join(Complaint, Complaint.complaint_type_id == ComplaintType.id) \
        .group_by(ComplaintType.name).all()

    area_data = db.session.query(Area.name, func.count(Complaint.id)) \
        .join(Complaint, Complaint.area_id == Area.id) \
        .group_by(Area.name).all()

    status_data = db.session.query(Complaint.status, func.count(Complaint.id)) \
        .group_by(Complaint.status).all()

    type_data = [[t[0], int(t[1])] for t in type_data]
    area_data = [[a[0], int(a[1])] for a in area_data]
    status_data = [[s[0], int(s[1])] for s in status_data]

    total_complaints = Complaint.query.count()
    pending_count = Complaint.query.filter_by(status='pending').count()
    resolved_count = Complaint.query.filter_by(status='resolved').count()

    complaints_json = [{
        "id": c.id,
        "username": getattr(c.user, "username", ""),
        "email": getattr(c.user, "email", ""),
        "phone": getattr(c.user, "phone", ""),
        "type": getattr(c.complaint_type, "name", ""),
        "area": getattr(c.area, "name", ""),
        "status": c.status,
        "text": c.text
    } for c in complaints]

    return render_template(
        'dashboard.html',
        complaints=complaints,
        type_data=type_data,
        area_data=area_data,
        status_data=status_data,
        total_complaints=total_complaints,
        pending_count=pending_count,
        resolved_count=resolved_count,
        complaints_json=complaints_json,
        is_admin=is_admin
    )


# ---------------------------
# Dashboard Auto-refresh API
# ---------------------------
@bp.route('/dashboard_data')
@login_required
def dashboard_data():
    is_admin = getattr(current_user, 'role', '') == "admin"
    complaints_qs = Complaint.query.order_by(Complaint.id.desc()).all() if is_admin else \
        Complaint.query.filter_by(user_id=current_user.id).order_by(Complaint.id.desc()).all()

    type_data = db.session.query(ComplaintType.name, func.count(Complaint.id)) \
        .join(Complaint, Complaint.complaint_type_id == ComplaintType.id) \
        .group_by(ComplaintType.name).all()

    area_data = db.session.query(Area.name, func.count(Complaint.id)) \
        .join(Complaint, Complaint.area_id == Area.id) \
        .group_by(Area.name).all()

    status_data = db.session.query(Complaint.status, func.count(Complaint.id)) \
        .group_by(Complaint.status).all()

    type_data = [[t[0], int(t[1])] for t in type_data]
    area_data = [[a[0], int(a[1])] for a in area_data]
    status_data = [[s[0], int(s[1])] for s in status_data]

    complaints_json = [{
        "id": c.id,
        "username": getattr(c.user, "username", ""),
        "email": getattr(c.user, "email", ""),
        "phone": getattr(c.user, "phone", ""),
        "type": getattr(c.complaint_type, "name", ""),
        "area": getattr(c.area, "name", ""),
        "status": c.status,
        "text": c.text
    } for c in complaints_qs]

    return jsonify({
        "type_data": type_data,
        "area_data": area_data,
        "status_data": status_data,
        "complaints": complaints_json
    })


# ---------------------------
# Download PDF (Charts + Table)
# ---------------------------
@bp.route('/download_report', methods=['POST'])
@login_required
def download_report():
    data = request.get_json() or {}
    chart_images = data.get('chart_images', {})

    try:
        from reportlab.lib.pagesizes import letter, landscape
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table
        from reportlab.lib.styles import getSampleStyleSheet
        from reportlab.lib import utils
    except Exception:
        return jsonify({"success": False, "error": "Please install reportlab"}), 501

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=landscape(letter))
    styles = getSampleStyleSheet()
    flow = [
        Paragraph("Complaint Report", styles['Heading1']),
        Paragraph(f"Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", styles['Normal']),
        Spacer(1, 12)
    ]

    # Add chart images
    for key, img_data in chart_images.items():
        if not img_data:
            continue
        try:
            img_bytes = base64.b64decode(img_data.split(",")[1])
            img_io = io.BytesIO(img_bytes)
            img = utils.ImageReader(img_io)
            iw, ih = img.getSize()
            max_w = 350
            scale = min(1.0, max_w / iw)
            flow.append(Image(img_io, width=iw * scale, height=ih * scale))
            flow.append(Spacer(1, 8))
        except Exception:
            continue

    # Add complaint table
    flow.append(Spacer(1, 12))
    flow.append(Paragraph("Complaints Table", styles['Heading2']))

    rows = Complaint.query.order_by(Complaint.id.desc()).all() if getattr(current_user, 'role', '') == "admin" else \
        Complaint.query.filter_by(user_id=current_user.id).order_by(Complaint.id.desc()).all()

    table_data = [["ID", "User", "Email", "Phone", "Type", "Area", "Status", "Text"]]
    for c in rows:
        table_data.append([
            str(c.id),
            getattr(c.user, "username", ""),
            getattr(c.user, "email", ""),
            getattr(c.user, "phone", ""),
            getattr(c.complaint_type, "name", ""),
            getattr(c.area, "name", ""),
            c.status,
            (c.text[:90] + "...") if c.text and len(c.text) > 90 else c.text or ""
        ])
    flow.append(Table(table_data, repeatRows=1))
    doc.build(flow)

    buffer.seek(0)
    return send_file(buffer, as_attachment=True, download_name="complaint_report.pdf", mimetype="application/pdf")


# ---------------------------
# Export Excel (Admin only)
# ---------------------------
@bp.route('/export_excel')
@login_required
def export_excel():
    is_admin = getattr(current_user, 'role', '') == "admin"
    if not is_admin:
        flash("Access denied: Only admins can export Excel reports.", "error")
        return redirect(url_for('complaints.dashboard'))

    qs = Complaint.query.order_by(Complaint.id).all()
    rows = [{
        "id": c.id,
        "username": getattr(c.user, "username", ""),
        "email": getattr(c.user, "email", ""),
        "phone": getattr(c.user, "phone", ""),
        "type": getattr(c.complaint_type, "name", ""),
        "area": getattr(c.area, "name", ""),
        "status": c.status,
        "text": c.text
    } for c in qs]

    try:
        import openpyxl
        from openpyxl.workbook import Workbook
        wb = Workbook()
        ws = wb.active
        ws.append(list(rows[0].keys()))
        for r in rows:
            ws.append(list(r.values()))
        bio = io.BytesIO()
        wb.save(bio)
        bio.seek(0)
        return send_file(
            bio,
            as_attachment=True,
            download_name="complaints.xlsx",
            mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    except Exception:
        si = io.StringIO()
        writer = csv.DictWriter(si, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)
        return Response(
            si.getvalue(),
            mimetype="text/csv",
            headers={"Content-Disposition": "attachment;filename=complaints.csv"}
        )


# ---------------------------
# Delete Complaint (User only, Pending)
# ---------------------------
@bp.route('/delete/<int:complaint_id>', methods=['POST'])
@login_required
def delete_complaint(complaint_id):
    complaint = Complaint.query.get_or_404(complaint_id)

    if getattr(current_user, 'role', '') == "admin":
        flash("Admins cannot delete complaints.", "error")
        return redirect(url_for('complaints.dashboard'))

    if complaint.user_id != current_user.id:
        flash("Unauthorized: Not your complaint.", "error")
        return redirect(url_for('complaints.dashboard'))

    if complaint.status != 'pending':
        flash("You can only delete complaints with status 'pending'.", "error")
        return redirect(url_for('complaints.dashboard'))

    db.session.delete(complaint)
    db.session.commit()
    save_all_complaints_to_csv()
    flash("Complaint deleted successfully!", "success")
    return redirect(url_for('complaints.dashboard'))


# ---------------------------
# ✅ Bulk Update Status (Admin only)
# ---------------------------
@bp.route('/update_status_bulk', methods=['POST'])
@login_required
def update_status_bulk():
    if getattr(current_user, 'role', '') != "admin":
        return jsonify({"success": False, "message": "Unauthorized"}), 403

    data = request.get_json() or {}
    updates = data.get("updates", [])

    if not updates:
        return jsonify({"success": False, "message": "No updates received"}), 400

    for upd in updates:
        cid = upd.get("id")
        status = upd.get("status")
        if not cid or not status:
            continue
        complaint = Complaint.query.get(cid)
        if complaint:
            complaint.status = status

    db.session.commit()
    save_all_complaints_to_csv()

    flash("✅ Status Updated Successfully!", "success")
    return jsonify({"success": True})
