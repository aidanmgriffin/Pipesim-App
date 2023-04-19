"""
A sample Hello World server.
"""
import os
from flask import Flask, render_template, request, redirect, url_for, send_from_directory, send_file
from display import simulation_window
from datetime import datetime
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired
from werkzeug.utils import secure_filename
from datetime import datetime
import sys
import math
from io import BytesIO
import zipfile
import pathlib


# pylint: disable=C0103
app = Flask(__name__)
app.config['SECRET_KEY'] = "pipesimunlock"

#Get current time
now = datetime.now()
date_time =now.strftime("%d/%m/%Y, %H:%M:%S")

#Create a form class (file)
class SettingsForm(FlaskForm):
    photo = FileField(validators=[FileRequired()])

#Default route
@app.route('/')
def index():
    return render_template("index.html")

#Custom routes

#route to documentation page
@app.route('/documentation', methods = ['GET', 'POST'])
def documentation():
    name = None
    # form = NamerForm()

    # if form.validate_on_submit():
    #     name = form.name.data
    #     form.name.data = ''

    return render_template("documentation.html")

#route to learn more page
@app.route('/learn_more')
def learn_more():
    return render_template("learn_more.html")

ALLOWED_EXTENSIONS = set(['csv'])

def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

#Upload files
@app.route('/upload', methods=['GET', 'POST'])
def upload():
    form = SettingsForm()
   
    if request.method == 'POST':

        if 'settings-submit' in request.form:
            file = request.files['setting-preset']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                print("filename: ", filename)
                save_location = os.path.join('input', filename)
                file.save(save_location)

                sim = simulation_window()
           
                output_file = 0
                output_file = sim.settings_preset_simulation_button_handler(save_location)
                #output_file = process_csv(save_location)
                #return send_from_directory('output', output_file)

                if(output_file):
                    return redirect(url_for('download'))
        
            return 'uploaded'
        elif 'preset-submit' in request.form:

            pipes = request.files['pipe-network']
            flows = request.files['flow-preset']
            print("request.values", request.values)
            # print(request.values['asymptotic-diffusion-coefficient'])

            # asymptotic_diffusion_coefficient = request.values['asymptotic-diffusion-coefficient']
            density = request.values['density']
            req_radio = request.values['inlineRadioOptions']

            asymptotic_diffusion_coefficient = request.values['asymptotic-diffusion-coefficient']
            if any(char.isdigit() for char in asymptotic_diffusion_coefficient):
                pass
            else:
                asymptotic_diffusion_coefficient =  9.3 * math.pow(10, -5)
                
            
            if req_radio == 'option1':
                granularity = 'Seconds'
            elif req_radio == 'option2':
                granularity = 'Minutes'
            elif req_radio == 'option3':
                granularity = 'Hours'
            else:
                granularity = 'Minutes'

            if pipes and allowed_file(pipes.filename) and flows and allowed_file(flows.filename):
                pipes_filename = secure_filename(pipes.filename)
                pipes_save_location = os.path.join('input', pipes_filename)
                pipes.save(pipes_save_location)

                flows_filename = secure_filename(flows.filename)
                flows_save_location = os.path.join('input', flows_filename)
                flows.save(flows_save_location)

            # print("request vals ", request.values, file = sys.stderr)
            if('flex-check' in request.values):
                diffusion_status = 1                    
            else:
                diffusion_status = 0

            sim = simulation_window()

            print("run: ", pipes_save_location, flows_save_location, density, diffusion_status, asymptotic_diffusion_coefficient, granularity)

            output_file = 0
            output_file = sim.preset_simulation_button_handler(pipes_save_location, flows_save_location, density, diffusion_status, asymptotic_diffusion_coefficient, granularity)

            if(output_file):
                print("output", file = sys.stderr)
                return render_template("download.html", files=os.listdir('output'), date_time = date_time)
                # return redirect(url_for('download'))
            print("no output", file = sys.stderr)
            # return asymptotic_diffusion_coefficient
            return render_template("upload.html", form=form)

        #return redirect(url_for('download'))
    return render_template("upload.html", form=form)

@app.route('/download')
def download():
    return render_template('download.html', files=os.listdir('logs'), date_time = date_time)
    
    # path = pathlib.Path('logs\output_batch')
    # memory_file = BytesIO()

    # with zipfile.ZipFile(memory_file, 'w') as zf:
    #     for root, dirs, files in os.walk(path):
    #         for file in files:
    #             zf.write(os.path.join(root, file))
    # memory_file.seek(0)
    
    # return send_file(memory_file, as_attachment=True, download_name='logs.zip')

@app.route('/download_log')
def download_log():
    
    path = pathlib.Path('logs\output_batch')
    memory_file = BytesIO()

    with zipfile.ZipFile(memory_file, 'w') as zf:
        for root, dirs, files in os.walk(path):
            for file in files:
                zf.write(os.path.join(root, file))
    memory_file.seek(0)
    
    return send_file(memory_file, as_attachment=True, download_name='logs.zip')
    # return send_file(age_path, as_attachment=True)
    # send_file(expelled_ages_path, as_attachment=True)
    # send_file(expelled_path, as_attachment=True)
    # send_file(contents_path, as_attachment=True)
    # return render_template("download.html", files=os.listdir('logs'), date_time = date_time)
    # return render_template('download.html', files=os.listdir('logs'), date_time = date_time)

# @app.route('/download/<filename>', methods = ['GET', 'POST'])
# def download_log():
#     path = 'downloadfile.txt'
#     return send_file(path, as_attachment=True)

#Error routes

#Page not found error(404)
@app.errorhandler(404)
def page_not_found_404(e):
    return render_template("404.html"), 404

#Internal server error(500)
@app.errorhandler(500)
def page_not_found_500(e):
    return render_template("500.html"), 500

if __name__ == '__main__':
    server_port = os.environ.get('PORT', '8080')
    app.run(debug=False, port=server_port, host='0.0.0.0')
