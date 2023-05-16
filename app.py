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
import webbrowser
import builder


# pylint: disable=C0103
app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(12).hex()

#Create a form class (file)
class SettingsForm(FlaskForm):
    photo = FileField(validators=[FileRequired()])

#Default route
@app.route('/')
def index():
    return render_template("index.html")

class alert:
    def __init__(self, message, type):
        self.type = type
        self.message = message
#Custom routes

#route to documentation page
@app.route('/documentation', methods = ['GET', 'POST'])
def documentation():
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

    #Get current time
    now = datetime.now()
    date_time =now.strftime("%m/%d/%Y, %H:%M:%S")

    form = SettingsForm()
    alertDanger = alert("Running Simulation Failed", "Danger")
   
    if request.method == 'POST':

        if 'settings-submit' in request.form:
            file = request.files['setting-preset']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
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
        
        # User is not electing to run a settings preset simulation. 
        # Thus, running a custom simulation with selected files/settings.
        elif 'preset-submit' in request.form:
            try:
                # Get pipe network and flows files from form
                pipes = request.files['pipe-network']
                flows = request.files['flow-preset']

                #Validating density input. Input must be a number between 0 and 1 inclusive.
                try:
                    density = request.values['density']
                    density = float(density)
                    if density < 0 or density > 1:
                        alertDanger.message = "Density must be between 0 and 1"
                        raise Exception
                except:
                    alertDanger.message = "Density must be a number between 0 and 1"
                    raise Exception
                    
                
                # Validate that granularity option is selected. If none is selected, default to minutes.
                # In case of no selection, error will be shown to the user.
                try:
                    req_radio = request.values['inlineRadioOptions']
                except:
                    alertDanger.message = "Granularity option not selected."
                    raise Exception
                    

                if req_radio == 'option1':
                    granularity = 'Seconds'
                elif req_radio == 'option2':
                    granularity = 'Minutes'
                elif req_radio == 'option3':
                    granularity = 'Hours'
                else:
                    granularity = 'Minutes'

                
                # Check if diffusion is enabled (flexbox is checked). If so, set diffusion status to 1. Else, set to 0.
                # If diffusion is not enabled (flexbox not checked), molecular diffusion coefficient (d_m) will be set to default value.
                # Otherwise, validate that molecular diffusion coefficient is a number. If not, d_m will be set to default value.
                if('flex-check' in request.values):
                    diffusion_status = 1                    
                else:
                    diffusion_status = 0
                
                molecular_diffusion_coefficient = request.values['molecular-diffusion-coefficient']
                if any(char.isdigit() for char in molecular_diffusion_coefficient):
                    pass
                else:
                    molecular_diffusion_coefficient =  9.3 * math.pow(10, -5) 

                # Attempt to save pipe network and flows files to input folder. If unsuccessful (most likely due to incorrect file type),
                # an error will be shown to the user.    
                try:
                    if pipes and allowed_file(pipes.filename) and flows and allowed_file(flows.filename):
                        pipes_filename = secure_filename(pipes.filename)
                        pipes_save_location = os.path.join('input', pipes_filename)
                        pipes.save(pipes_save_location)

                        flows_filename = secure_filename(flows.filename)
                        flows_save_location = os.path.join('input', flows_filename)
                        flows.save(flows_save_location)
                except:
                    alertDanger.message = "Pipe Network File Could Not Uploaded. Is file type CSV?"
                    raise Exception
                
                # Attempts to build pipe network. 
                # If builder.build successfully returns a single value, an error will be shown to the user.
                try:
                    message = builder.build(pipes_save_location)
                    alertDanger.message = message
                    raise Exception
                except:
                    pass

                sim = simulation_window()

                # Catches and alerts users of errors in the simulation. These include errors involving output files being open,
                # errors involving the input files, and errors involving the simulation itself.
                try:
                    output_file = 0
                    output_file = sim.preset_simulation_button_handler(pipes_save_location, flows_save_location, density, diffusion_status, molecular_diffusion_coefficient, granularity)
                except Exception as e:
                    alertDanger.message = e
                    raise Exception
            except:
                # alertDanger.message = e
                return render_template("upload.html", form=form, alert = alertDanger)
            
            #If simulation is successful, redirect to download page. If failed, show error message.
            if(output_file):
                return render_template("download.html", files=os.listdir('output'), date_time = date_time)
            else:
                alertDanger.message = "Simulation Failed. Do the files contain the correct data?"
                return render_template("upload.html", form=form, alert = alertDanger)
            
    return render_template("upload.html", form=form)

#Route to download page accessed by running a simulation from upload.
@app.route('/download')
def download():

    date_time = "Latest Simulation"

    #pass current time, and list of files in output folder to download page. Load download page.
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
    # webbrowser.open('http://localhost:8080/', new=2)
    app.run(debug=False, port=server_port, host='0.0.0.0')
