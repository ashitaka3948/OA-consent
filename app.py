from flask import Flask, request, send_file
from flask_cors import CORS
from PyPDF2 import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from io import BytesIO
import os

app = Flask(__name__)
CORS(app)

# Register Chinese font
pdfmetrics.registerFont(TTFont('MSung', 'static/fonts/MSung.ttf'))

# Dictionary mapping operations to their template files
TEMPLATES = {
    'phaco': {
        'english': 'templates/cataract_consent_en.pdf',
        'chinese': 'templates/cataract_consent_cn.pdf'
    },
    'vitrectomy': {
        'english': 'templates/vitrectomy_consent_en.pdf',
        'chinese': 'templates/vitrectomy_consent_cn.pdf'
    },
    'glaucoma': {
        'english': 'templates/glaucoma_consent_en.pdf',
        'chinese': 'templates/glaucoma_consent_cn.pdf'
    },
    'sfiol': {
        'english': 'templates/sfiol_consent_en.pdf',
        'chinese': 'templates/sfiol_consent_cn.pdf'
    },
    'injection': {
        'english': 'templates/injection_consent_en.pdf',
        'chinese': 'templates/injection_consent_cn.pdf'
    },
    'ot_checklist': {
        'template': 'templates/OT_Checklist.pdf'
    }
}

# Add this doctor name mapping at the top of the file
DOCTOR_NAMES = {
    'leslie_cheng': {
        'english': 'Cheng Ka Lok',
        'chinese': '鄭家樂'
    },
    'callie_ko': {
        'english': 'Ko Ka Li',
        'chinese': '高嘉莉'
    },
    'isabel_lai': {
        'english': 'Lai Sum Wai',
        'chinese': '黎心慧'
    },
    'douglas_lam': {
        'english': 'Lam King Tak',
        'chinese': '林敬德'
    },
    'winnie_lau': {
        'english': 'Lau Wai Ying',
        'chinese': '劉韋形'
    },
    'gary_lee': {
        'english': 'Lee Ka Yau',
        'chinese': '李嘉祐'
    },
    'alex_ng': {
        'english': 'Ng Lap Ki',
        'chinese': '伍立祺'
    },
    'patrick_tong': {
        'english': 'Tong Pak Chuen',
        'chinese': '唐柏泉'
    },
    'victor_woo': {
        'english': 'Woo Chi Pang',
        'chinese': '胡志鵬'
    },
    'nancy_yuen': {
        'english': 'Yuen Shi Yin',
        'chinese': '袁淑賢'
    },
    'andrew_fok': {
        'english': 'Andrew Fok',
        'chinese': '霍頌天'
    },
    'carol_yu': {
        'english': 'Carol Yu',
        'chinese': '余珊'
    },
    'charmaine_hon': {
        'english': 'Charmaine Hon',
        'chinese': '韓尚穎'
    },
    'cheung_sek_hong': {
        'english': 'Cheung Sek Hong',
        'chinese': '張錫康'
    },
    'jean_paul_yih': {
        'english': 'Jean Paul Yih',
        'chinese': '葉禮邦'
    },
    'donald_woo': {
        'english': 'Woo Chai Fong',
        'chinese': '賀澤烽'
    },
    'shiu_chi_yuen': {
        'english': 'Shiu Chi Yuen',
        'chinese': '邵志遠'
    }
}

# Update the coordinates to include three date fields
FIELD_COORDINATES = {
    'english': {
        'patient_name': (50, 701),
        'patient_id': (100, 650),
        'eye': (50, 688),
        'doctors': (160, 673),  # First doctors field
        'doctors2': (160, 500), # Second doctors field
        'operation_date': (200, 723),
        'operation_date2': (200, 500), # Second date field - adjust coordinates
        'operation_date3': (200, 300), # Third date field - adjust coordinates
    },
    'chinese': {
        'patient_name': (105, 723),
        'patient_id': (110, 283),
        'eye': (77, 708),
        'doctors': (375, 723),  # First doctors field
        'doctors2': (50, 118), # Second doctors field
        'operation_date': (400, 118),
        'operation_date2': (65, 267), # Second date field - adjust coordinates
        'operation_date3': (395, 255), # Third date field - adjust coordinates
    }
}

# Add field coordinates for OT Checklist
OT_CHECKLIST_COORDINATES = {
    'doctors': (115, 730),  # These coordinates seem to work
    'date': (420, 730),     # Try different coordinates for date
    'patient_name': (150, 704),  # These coordinates seem to work
    'patient_number': (200, 450),
    'hkid': (350, 677),
    'operation': (130, 650)
}

def format_hkid(hkid):
    """Helper function to format HKID consistently"""
    if not hkid or len(hkid.strip()) == 0:
        return "()"
    
    # Clean the input
    hkid = hkid.strip().upper()
    
    if len(hkid) >= 8:
        # For complete HKID (8 characters)
        main_part = hkid[:7]
        check_digit = hkid[7]
        return f"{main_part}({check_digit})"
    elif len(hkid) == 7:
        # For HKID without check digit
        return f"{hkid}()"
    else:
        # For partial HKID
        return f"{hkid}()"

def fill_pdf_template(template_path, form_data, language='english'):
    packet = BytesIO()
    can = canvas.Canvas(packet)
    
    # Set font based on language or if it's OT checklist
    if language == 'chinese' or 'OT_Checklist.pdf' in template_path:
        can.setFont('MSung', 12)
    else:
        can.setFont('Helvetica', 12)
    
    # Get template
    template = PdfReader(open(template_path, 'rb'))
    
    # Fill in the fields (only on first page)
    if 'OT_Checklist.pdf' in template_path:
        field_coordinates = OT_CHECKLIST_COORDINATES
    else:
        field_coordinates = FIELD_COORDINATES[language]

    for field, coords in field_coordinates.items():
        if field in form_data:
            # Special handling for HKID to ensure brackets are preserved
            if field == 'hkid' or field == 'patient_id':
                if language == 'chinese' or 'OT_Checklist.pdf' in template_path:
                    can.setFont('MSung', 12)
                else:
                    can.setFont('Helvetica', 12)
            
            can.drawString(coords[0], coords[1], str(form_data[field]))
    
    can.save()
    packet.seek(0)
    new_pdf = PdfReader(packet)
    
    output = PdfWriter()
    
    # Process all pages from the template
    for page_num in range(len(template.pages)):
        page = template.pages[page_num]
        # Only merge the form data with the first page
        if page_num == 0:
            page.merge_page(new_pdf.pages[0])
        output.add_page(page)
    
    output_buffer = BytesIO()
    output.write(output_buffer)
    output_buffer.seek(0)
    
    return output_buffer

@app.route('/')
def index():
    return app.send_static_file('index.html')

@app.route('/english', methods=['POST'])
def generate_english_consent():
    try:
        # Get operation value and validate
        operation = request.form.get('operation1', '')
        if not operation:
            return "No operation selected", 400
            
        # Check if template exists in dictionary
        if operation not in TEMPLATES or 'english' not in TEMPLATES[operation]:
            return f"Template not found for operation: {operation}", 404
            
        template_path = TEMPLATES[operation]['english']
        
        # Verify template file exists
        if not os.path.exists(template_path):
            return f"Template file does not exist: {template_path}", 404
        
        # Get doctor names in English and combine if necessary
        doctor1_id = request.form.get('doctor1')
        doctor2_id = request.form.get('doctor2')
        doctor1_name = DOCTOR_NAMES[doctor1_id]['english'] if doctor1_id else ''
        doctor2_name = DOCTOR_NAMES[doctor2_id]['english'] if doctor2_id else ''
        
        # Format doctors string for both fields
        if doctor2_name:
            doctors = f"{doctor1_name} and {doctor2_name}"
        else:
            doctors = f"          {doctor1_name}"
        
        # Format the date to DD/MM/YYYY only if date is provided
        operation_date = request.form.get('selectedDate')
        formatted_date = ''
        if operation_date:  # Only format if date exists
            date_parts = operation_date.split('-')
            formatted_date = f"{date_parts[2]}/{date_parts[1]}/{date_parts[0]}"
        
        # Get HKID and format it
        try:
            hkid = request.form.get('hkid', '').strip()
            formatted_hkid = format_hkid(hkid)
        except Exception as e:
            print(f"Error formatting HKID: {e}")
            formatted_hkid = "()"
        
        form_data = {
            'patient_name': request.form.get('patientName', ''),
            'patient_id': formatted_hkid,
            'eye': request.form.get('selectedEye', ''),
            'doctors': doctors,
            'doctors2': doctors,
            'operation_date': formatted_date,
            'operation_date2': formatted_date,
            'operation_date3': formatted_date,
        }
        
        pdf_buffer = fill_pdf_template(template_path, form_data, 'english')
        return send_file(
            pdf_buffer,
            mimetype='application/pdf',
            download_name=f'consent_{operation}_en.pdf'
        )
    except Exception as e:
        import traceback
        print(f"Error generating English consent: {e}")
        print(traceback.format_exc())
        return "Error generating consent form. Please check server logs.", 500

@app.route('/chinese', methods=['POST'])
def generate_chinese_consent():
    try:
        # Get operation value and validate
        operation = request.form.get('operation1', '')
        if not operation:
            return "No operation selected", 400
            
        # Check if template exists
        if operation not in TEMPLATES or 'chinese' not in TEMPLATES[operation]:
            return f"Template not found for operation: {operation}", 404
            
        template_path = TEMPLATES[operation]['chinese']
        
        # Verify template file exists
        if not os.path.exists(template_path):
            return f"Template file does not exist: {template_path}", 404
        
        # Get doctor names in Chinese and combine if necessary
        doctor1_id = request.form.get('doctor1')
        doctor2_id = request.form.get('doctor2')
        doctor1_name = DOCTOR_NAMES[doctor1_id]['chinese'] if doctor1_id else ''
        doctor2_name = DOCTOR_NAMES[doctor2_id]['chinese'] if doctor2_id else ''
        
        # Format doctors string for both fields
        if doctor2_name:
            doctors = f"{doctor1_name}及{doctor2_name}"
        else:
            doctors = f"          {doctor1_name}"
        
        # Format the date to DD/MM/YYYY only if date is provided
        operation_date = request.form.get('selectedDate')
        formatted_date = ''
        if operation_date:  # Only format if date exists
            date_parts = operation_date.split('-')
            formatted_date = f"{date_parts[2]}/{date_parts[1]}/{date_parts[0]}"
        
        # Translate eye selection to Chinese
        eye_selection = request.form.get('selectedEye')
        eye_in_chinese = {
            'right eye': '右',
            'left eye': '左',
            'both eyes': '雙'
        }.get(eye_selection, '')
        
        # Get HKID from form data and format it
        try:
            hkid = request.form.get('hkid', '').strip()
            formatted_hkid = format_hkid(hkid)
        except Exception as e:
            print(f"Error formatting HKID: {e}")
            formatted_hkid = "()"
        
        form_data = {
            'patient_name': request.form.get('patientName', ''),
            'patient_id': formatted_hkid,  # Use formatted HKID here
            'eye': eye_in_chinese,
            'doctors': doctors,
            'doctors2': doctors,
            'operation_date': formatted_date,
            'operation_date2': formatted_date,
            'operation_date3': formatted_date,
        }
        
        pdf_buffer = fill_pdf_template(template_path, form_data, 'chinese')
        return send_file(
            pdf_buffer,
            mimetype='application/pdf',
            download_name=f'consent_{operation}_cn.pdf'
        )
    except Exception as e:
        import traceback
        print(f"Error generating Chinese consent: {e}")
        print(traceback.format_exc())
        return "Error generating consent form. Please check server logs.", 500

@app.route('/ot_checklist', methods=['POST'])
def generate_ot_checklist():
    template_path = TEMPLATES['ot_checklist']['template']
    
    # Format doctors' names (Chinese + English)
    doctor1_id = request.form.get('doctor1')
    doctor2_id = request.form.get('doctor2')
    
    doctor1_name = ''
    if doctor1_id:
        doctor1_name = f"{DOCTOR_NAMES[doctor1_id]['chinese']} {DOCTOR_NAMES[doctor1_id]['english']}"
    
    doctor2_name = ''
    if doctor2_id:
        doctor2_name = f"{DOCTOR_NAMES[doctor2_id]['chinese']} {DOCTOR_NAMES[doctor2_id]['english']}"
    
    doctors = doctor1_name
    if doctor2_name:
        doctors = f"{doctor1_name}   {doctor2_name}"
    
    # Get operations
    operations = []
    for i in range(1, 4):  # Check all 3 operation fields
        op = request.form.get(f'operation{i}')
        if op:
            operations.append(op.capitalize())
    
    # Format operation string with eye selection
    eye_selection = request.form.get('selectedEye', '')
    operation_str = f"{eye_selection.capitalize()}   {' + '.join(operations)}"
    
    # Format date
    operation_date = request.form.get('selectedDate')
    formatted_date = ''
    if operation_date:
        date_parts = operation_date.split('-')
        formatted_date = f"{date_parts[2]}/{date_parts[1]}/{date_parts[0]}"
    
    # Get HKID from form data and format it
    hkid = request.form.get('hkid', '').strip()
    formatted_hkid = format_hkid(hkid)
    
    form_data = {
        'doctors': doctors,
        'date': formatted_date,
        'patient_name': request.form.get('patientName', ''),
        'hkid': formatted_hkid,
        'operation': operation_str
    }
    
    pdf_buffer = fill_pdf_template(template_path, form_data)
    return send_file(
        pdf_buffer,
        mimetype='application/pdf',
        download_name='ot_checklist.pdf'
    )

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)