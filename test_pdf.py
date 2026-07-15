from app import app, export_registrations_pdf, db
import traceback
with app.app_context():
    # Mocking the request context because export_registrations_pdf uses request.args.get('view')
    with app.test_request_context('/admin/registrations/export-pdf'):
        try:
            export_registrations_pdf()
            print("Success")
        except Exception as e:
            traceback.print_exc()
