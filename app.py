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
    }
}

# Add this doctor name mapping at the top of the file
DOCTOR_NAMES = {
    'leslie_cheng': {
        'english': 'Leslie Cheng',
        'chinese': '鄭志釗'
    },
    'cheung_sek_hong': {
        'english': 'Cheung Sek Hong',
        'chinese': '張錫康'
    },
    'andrew_fok': {
        'english': 'Andrew Fok',
        'chinese': '霍經昌'
    },
    'charmaine_hon': {
        'english': 'Charmaine Hon',
        'chinese': '韓慶璋'
    },
    'callie_ko': {
        'english': 'Callie Ko',
        'chinese': '高天藍'
    },
    'isabel_lai': {
        'english': 'Isabel Lai',
        'chinese': '黎珮瑤'
    },
    'douglas_lam': {
        'english': 'Douglas Lam',
        'chinese': '林偉聰'
    },
    'winnie_lau': {
        'english': 'Winnie Lau',
        'chinese': '劉芷欣'
    },
    'gary_lee': {
        'english': 'Gary Lee',
        'chinese': '李傑'
    },
    'alex_ng': {
        'english': 'Alex Ng',
        'chinese': '吳國強'
    },
    'shiu_chi_yuen': {
        'english': 'Shiu Chi Yuen',
        'chinese': '邵志源'
    },
    'patrick_tong': {
        'english': 'Patrick Tong',
        'chinese': '唐俊業'
    },
    'donald_woo': {
        'english': 'Donald Woo',
        'chinese': '胡子傑'
    },
    'victor_woo': {
        'english': 'Victor Woo',
        'chinese': '胡釗明'
    },
    'jean_paul_yih': {
        'english': 'Jean Paul Yih',
        'chinese': '葉霖'
    },
    'nancy_yuen': {
        'english': 'Nancy Yuen',
        'chinese': '袁淑欣'
    },
    'carol_yu': {
        'english': 'Carol Yu',
        'chinese': '余詠欣'
    }
}

def fill_pdf_template(template_path, form_data, language='english'):
    packet = BytesIO()
    can = canvas.Canvas(packet)
    
    # Set font based on language
    if language == 'chinese':
        can.setFont('MSung', 12)  # Use Chinese font for Chinese consent
    else:
        can.setFont('Helvetica', 12)  # Use default font for English
    
    # Get template dimensions
    template = PdfReader(open(template_path, 'rb'))
    page = template.pages[0]
    
    # Define coordinates for each field in the template
    # These would need to be adjusted based on your actual templates
    field_coordinates = {
        'patient_name': (50, 701),  # x, y coordinates
        'patient_id': (100, 650),
        'eye': (50, 688),
        'doctor1': (160, 673),
        'doctor2': (100, 500),
        'operation_date': (50, 715),  # Add this line with appropriate coordinates
        # Add more fields and their coordinates as needed
    }
    
    # Fill in the fields
    for field, coords in field_coordinates.items():
        if field in form_data:
            can.drawString(coords[0], coords[1], str(form_data[field]))
    
    can.save()
    
    # Move to the beginning of the buffer
    packet.seek(0)
    new_pdf = PdfReader(packet)
    
    # Merge with template
    output = PdfWriter()
    page = template.pages[0]
    page.merge_page(new_pdf.pages[0])
    output.add_page(page)
    
    # Save to a temporary buffer
    output_buffer = BytesIO()
    output.write(output_buffer)
    output_buffer.seek(0)
    
    return output_buffer

@app.route('/')
def index():
    return app.send_static_file('index.html')

@app.route('/english', methods=['POST'])
def generate_english_consent():
    operation = request.form.get('operation1')
    template_path = TEMPLATES[operation]['english']
    
    # Get doctor names in English
    doctor1_id = request.form.get('doctor1')
    doctor2_id = request.form.get('doctor2')
    doctor1_name = DOCTOR_NAMES[doctor1_id]['english'] if doctor1_id else ''
    doctor2_name = DOCTOR_NAMES[doctor2_id]['english'] if doctor2_id else ''
    
    form_data = {
        'patient_name': request.form.get('patientName'),
        'patient_id': request.form.get('patientId'),
        'eye': request.form.get('selectedEye'),
        'doctor1': doctor1_name,
        'doctor2': doctor2_name,
        'operation_date': request.form.get('selectedDate'),
    }
    
    pdf_buffer = fill_pdf_template(template_path, form_data, 'english')
    return send_file(
        pdf_buffer,
        mimetype='application/pdf',
        download_name=f'consent_{operation}_en.pdf'
    )

@app.route('/chinese', methods=['POST'])
def generate_chinese_consent():
    operation = request.form.get('operation1')
    template_path = TEMPLATES[operation]['chinese']
    
    # Get doctor names in Chinese
    doctor1_id = request.form.get('doctor1')
    doctor2_id = request.form.get('doctor2')
    doctor1_name = DOCTOR_NAMES[doctor1_id]['chinese'] if doctor1_id else ''
    doctor2_name = DOCTOR_NAMES[doctor2_id]['chinese'] if doctor2_id else ''
    
    form_data = {
        'patient_name': request.form.get('patientName'),
        'patient_id': request.form.get('patientId'),
        'eye': request.form.get('selectedEye'),
        'doctor1': doctor1_name,
        'doctor2': doctor2_name,
        'operation_date': request.form.get('selectedDate'),
    }
    
    pdf_buffer = fill_pdf_template(template_path, form_data, 'chinese')
    return send_file(
        pdf_buffer,
        mimetype='application/pdf',
        download_name=f'consent_{operation}_cn.pdf'
    )

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)