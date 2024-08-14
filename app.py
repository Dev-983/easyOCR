from flask import Flask, request, render_template, redirect, url_for, flash
import os
import requests
from pypdf import PdfReader
import easyocr
from pdf2image import convert_from_path


app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Necessary for flashing messages

# Ensure the 'pdf' directory exists
if not os.path.exists('pdf'):
    os.makedirs('pdf')

@app.route('/url', methods=['GET'])
def url():
    if request.method == 'GET':
        pdf_url = request.args.get('url')  # Use request.args.get() to retrieve query parameters
        if pdf_url:
            response = requests.get(pdf_url)
            response.raise_for_status()  # Raise exception if the request failed

            # Extract the file name from the URL
            pdf_name = pdf_url.split("/")[-1]

            # Save the PDF to the 'pdf' folder
            pdf_path = os.path.join('pdf', pdf_name)
            with open(pdf_path, 'wb') as pdf_file:
                pdf_file.write(response.content)

            easyocr.Reader(['en'])
            reader = easyocr.Reader(['en'])
            images = convert_from_path(pdf_path)
            pdftext=''
            pdfimage= []
            output_dir = "pdfimage"
            os.makedirs(output_dir, exist_ok=True)
            for i, image in enumerate(images):
              image_path = os.path.join(output_dir, f'page_{i + 1}.png')
              image.save(image_path, 'PNG')
              pdfimage.append(image_path)


              for img in pdfimage:
                result = reader.readtext(img)
                for  text in result:
                pdftext+=text[1]

            # reader = PdfReader(pdf_path)
            # pdf_content = ''
            # for page in reader.pages:
            #     pdf_content += page.extract_text() 
            delete_all_pdfImages()
            return pdftext
        else:
            return "No URL provided", 400  # Return a message if no URL is provided


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        pdf_url = request.form['pdf_url']
        
        if pdf_url:
            try:
                # Send GET request to fetch the PDF
                response = requests.get(pdf_url)
                response.raise_for_status()  # Raise exception if the request failed

                # Extract the file name from the URL
                pdf_name = pdf_url.split("/")[-1]

                # Save the PDF to the 'pdf' folder
                pdf_path = os.path.join('pdf', pdf_name)
                with open(pdf_path, 'wb') as pdf_file:
                    pdf_file.write(response.content)

                reader = PdfReader(pdf_path)
                pdf_content = ''
                for page in reader.pages:
                    pdf_content += page.extract_text()    
                #return pdf_content
                delete_all_pdfs()
                flash(f"PDF downloaded successfully and saved as\n {pdf_content}", "success")
            except requests.exceptions.RequestException as e:
                flash(f"Failed to download PDF: {e}", "danger")
        else:
            flash("Please enter a valid URL", "warning")
        
        return redirect(url_for('index'))

    return render_template('index.html')

def delete_all_pdfImages():
    folder_path = 'pdfimage'
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        try:
            if os.path.isfile(file_path):
                os.remove(file_path)
        except Exception as e:
            print(f"Error deleting file {file_path}: {e}")


def delete_all_pdfs():
    folder_path = 'pdf'
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        try:
            if os.path.isfile(file_path):
                os.remove(file_path)
        except Exception as e:
            print(f"Error deleting file {file_path}: {e}")

if __name__ == '__main__':
    app.run(debug=True)
