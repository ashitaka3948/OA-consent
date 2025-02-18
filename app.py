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
        'english': 'CHENG LESLIE KA-LOK',
        'chinese': '鄭家樂'
    },
    'cheung_sek_hong': {
        'english': 'CHEUNG SEK HONG',
        'chinese': '張錫康'
    },
    'andrew_fok': {
        'english': 'FOK CHUNG TIN ANDREW',
        'chinese': '霍頌天'
    },
    'charmaine_hon': {
        'english': 'HON CHARMAINE',
        'chinese': '韓尚穎'
    },
    'callie_ko': {
        'english': 'KO KA LI CALLIE',
        'chinese': '高嘉莉'
    },
    'isabel_lai': {
        'english': 'LAI SUM WAI ISABEL',
        'chinese': '黎心慧'
    },
    'douglas_lam': {
        'english': 'LAM KING TAK DOUGLAS',
        'chinese': '林敬德'
    },
    'winnie_lau': {
        'english': 'LAU WAI YING WINNIE',
        'chinese': '劉韋形'
    },
    'gary_lee': {
        'english': 'LEE KA YAU',
        'chinese': '李嘉祐'
    },
    'alex_ng': {
        'english': 'NG LAP KI',
        'chinese': '伍立祺'
    },
    'shiu_chi_yuen': {
        'english': 'SHIU CHI YUEN',
        'chinese': '邵志遠'
    },
    'patrick_tong': {
        'english': 'TONG PAK CHUEN',
        'chinese': '唐柏泉'
    },
    'donald_woo': {
        'english': 'WOO CHAI FONG DONALD',
        'chinese': '賀澤烽'
    },
    'victor_woo': {
        'english': 'WOO CHI PANG CLEOPHAS',
        'chinese': '胡志鵬'
    },
    'jean_paul_yih': {
        'english': 'YIH JEAN-PAUL LAI BONG',
        'chinese': '葉禮邦'
    },
    'nancy_yuen': {
        'english': 'YUEN SHI YIN',
        'chinese': '袁淑賢'
    },
    'carol_yu': {
        'english': 'YU SHAN CAROL',
        'chinese': '余珊'
    }
}

# Update the coordinates for operation_date in both languages
FIELD_COORDINATES = {
    'english': {
        'patient_name': (50, 701),
        'patient_id': (100, 650),
        'eye': (50, 688),
        'doctor1': (160, 673),
        'doctor2': (100, 500),
        'operation_date': (200, 723),  # Adjusted coordinates for operation date
    },
    'chinese': {
        'patient_name': (72, 723),
        'patient_id': (200, 650),
        'eye': (150, 688),
        'doctor1': (400, 723),
        'doctor2': (200, 500),
        'operation_date': (400, 118),  # Adjusted coordinates for operation date
    }
}

def fill_pdf_template(template_path, form_data, language='english'):
    packet = BytesIO()
    can = canvas.Canvas(packet)
    
    # Set font based on language
    if language == 'chinese':
        can.setFont('MSung', 12)
    else:
        can.setFont('Helvetica', 12)
    
    # Get template
    template = PdfReader(open(template_path, 'rb'))
    
    # Fill in the fields (only on first page)
    field_coordinates = FIELD_COORDINATES[language]
    for field, coords in field_coordinates.items():
        if field in form_data:
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
    operation = request.form.get('operation1')
    template_path = TEMPLATES[operation]['english']
    
    # Get doctor names in English
    doctor1_id = request.form.get('doctor1')
    doctor2_id = request.form.get('doctor2')
    doctor1_name = DOCTOR_NAMES[doctor1_id]['english'] if doctor1_id else ''
    doctor2_name = DOCTOR_NAMES[doctor2_id]['english'] if doctor2_id else ''
    
    # Format the date to DD/MM/YYYY
    operation_date = request.form.get('selectedDate')  # Comes in as YYYY-MM-DD
    date_parts = operation_date.split('-')
    formatted_date = f"{date_parts[2]}/{date_parts[1]}/{date_parts[0]}"  # Convert to DD/MM/YYYY
    
    form_data = {
        'patient_name': request.form.get('patientName'),
        'patient_id': request.form.get('patientId'),
        'eye': request.form.get('selectedEye'),
        'doctor1': doctor1_name,
        'doctor2': doctor2_name,
        'operation_date': formatted_date,
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
    
    # Format the date to DD/MM/YYYY
    operation_date = request.form.get('selectedDate')  # Comes in as YYYY-MM-DD
    date_parts = operation_date.split('-')
    formatted_date = f"{date_parts[2]}/{date_parts[1]}/{date_parts[0]}"  # Convert to DD/MM/YYYY
    
    form_data = {
        'patient_name': request.form.get('patientName'),
        'patient_id': request.form.get('patientId'),
        'eye': request.form.get('selectedEye'),
        'doctor1': doctor1_name,
        'doctor2': doctor2_name,
        'operation_date': formatted_date,
    }
    
    pdf_buffer = fill_pdf_template(template_path, form_data, 'chinese')
    return send_file(
        pdf_buffer,
        mimetype='application/pdf',
        download_name=f'consent_{operation}_cn.pdf'
    )

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)