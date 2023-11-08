"""
A sample Hello World server.
"""
import os
from flask import Flask, render_template, request, redirect, url_for, send_from_directory, send_file
from display import simulation_window
from datetime import datetime
# from selenium import webdriver
# import webbrowser
# from flask_wtf import FlaskForm
# from flask_wtf.file import FileField, FileRequired
from werkzeug.utils import secure_filename
from datetime import datetime
# import sys
import math
from io import BytesIO
import zipfile
import pathlib
import builder
import multiprocessing
import webbrowser
# import webview
# import multiprocessing
# import cairo


# pylint: disable=C0103
# template_folder = os.path.join(os.getcwd(), 'templates')
app = Flask(__name__)#, template_folder=template_folder)
app.config['SECRET_KEY'] = os.urandom(12).hex()

#Create a form class (file)
# class SettingsForm(FlaskForm):
#     photo = FileField(validators=[FileRequired()])

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

#route to expiremental html5 canvas
@app.route('/canvas')
def canvas():
    return render_template("canvas.html")

ALLOWED_EXTENSIONS = set(['csv'])

def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

#Upload files

#route to upload page
@app.route('/upload_page')
def upload_page():
    return render_template("upload_page.html")

@app.route('/upload', methods=['GET', 'POST'])
def upload():

    path = pathlib.Path('logs\output_batch')

    for root, dirs, files in os.walk(path):
        for file in files:
            os.remove((str(path) + '/'  + file))
                # os.remove(path + file)

    #Get current time
    now = datetime.now()
    date_time =now.strftime("%m/%d/%Y, %H:%M:%S")

    # form = SettingsForm()
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
                    return redirect(url_for('download', diffusion_status = output_file[1] , date_time = date_time))
        
            return 'uploaded'
        
        # User is not electing to run a settings preset simulation. 
        # Thus, running a custom simulation with selected files/settings.
        elif 'preset-submit' in request.form:
            # try:
            # Get pipe network and flows files from form
            pipes = request.files['pipe-network']
            flows = request.files['flow-preset']

            #Validating density input. Input must be a number between 0 and 1 inclusive. 
            try:
                density = request.values['density']
                # If no density is input, default to 0.5.
                if density == '':                
                    density = 0.5
                density = float(density)
                if density < 0 or density > 1:
                    alertDanger.message = "Density must be between 0 and 1"
                    raise Exception
            except:
                alertDanger.message = "Density must be a number between 0 and 1"
                raise Exception
                
            
            granularity = request.values['custom-granularity']
            if granularity == '':
                granularity = 1
            else:
                granularity = float(granularity) 
                granularity /= 60
                print("granularity: ", granularity)
        
            
            # Check if diffusion is enabled (flexbox is checked). If so, set diffusion status to 1. Else, set to 0.
            # If diffusion is not enabled (flexbox not checked), molecular diffusion coefficient (d_m) will be set to default value.
            # Otherwise, validate that molecular diffusion coefficient is a number. If not, d_m will be set to default value.
            if('flex-check' in request.values):
                diffusion_status = 1                    
            else:
                diffusion_status = 0
            
            if('flexCheckStagnant' in request.values):
                stagnant_diffusion_status = 1                    
            else:
                stagnant_diffusion_status = 0
            
            if('flexCheckAdvective' in request.values):
                advective_diffusion_status = 1                    
            else:
                advective_diffusion_status = 0
            
            
            molecular_diffusion_coefficient = request.values['molecular-diffusion-coefficient']
            if any(char.isdigit() for char in molecular_diffusion_coefficient):
                pass
            else:
                molecular_diffusion_coefficient = 8.28 * math.pow(10, -4) #9.3 * math.pow(10, -5) 

            # Check if Free chlorine / monochloramine decay are enabled. Will affect whether the update function in particles.py will call the decay subroutines.
            if('flexCheckFreeChlorineDecay' in request.values):
                decay_free_chlorine_status = 1
                starting_particles_free_chlorine_concentration = request.values['starting-particles-concentration-free-chlorine']
                injected_particles_free_chlorine_concentration = request.values['injected-particles-concentration-free-chlorine']
            else:
                decay_free_chlorine_status = 0
                starting_particles_free_chlorine_concentration = 1.0
                injected_particles_free_chlorine_concentration = 1.0
            
            if starting_particles_free_chlorine_concentration == '':
                starting_particles_free_chlorine_concentration = 1.0
            if injected_particles_free_chlorine_concentration == '':
                injected_particles_free_chlorine_concentration = 1.0

            decay_monochloramine_dict = {}

            if('flexCheckMonochloramineDecay' in request.values):
                decay_monochloramine_status = 1
            else:
                decay_monochloramine_status = 0

            if('starting-particles-concentration-hypochlorous' in request.values):
                starting_particles_hypochlorous_concentration = request.values['starting-particles-concentration-hypochlorous']
                injected_particles_hypochlorous_concentration = request.values['injected-particles-concentration-hypochlorous']
            else:
                starting_particles_hypochlorous_concentration = 1.0
                injected_particles_hypochlorous_concentration = 1.0

            if starting_particles_hypochlorous_concentration == '':
                starting_particles_hypochlorous_concentration = 1.0
            if injected_particles_hypochlorous_concentration == '':
                injected_particles_hypochlorous_concentration = 1.0
            
            decay_monochloramine_dict['starting-particles-concentration-hypochlorous'] = starting_particles_hypochlorous_concentration
            decay_monochloramine_dict['injected-particles-concentration-hypochlorous'] = injected_particles_hypochlorous_concentration
            
            if('starting-particles-concentration-ammonia' in request.values):
                starting_particles_ammonia_concentration = request.values['starting-particles-concentration-ammonia']
                injected_particles_ammonia_concentration = request.values['injected-particles-concentration-ammonia']
            else:
                starting_particles_ammonia_concentration = 1.0
                injected_particles_ammonia_concentration = 1.0
            
            if starting_particles_ammonia_concentration == '':
                starting_particles_ammonia_concentration = 1.0
            if injected_particles_ammonia_concentration == '':
                injected_particles_ammonia_concentration = 1.0

            decay_monochloramine_dict['starting-particles-concentration-ammonia'] = starting_particles_ammonia_concentration
            decay_monochloramine_dict['injected-particles-concentration-ammonia'] = injected_particles_ammonia_concentration

            if('starting-particles-concentration-monochloramine' in request.values):
                starting_particles_monochloramine_concentration = request.values['starting-particles-concentration-monochloramine']
                injected_particles_monochloramine_concentration = request.values['injected-particles-concentration-monochloramine']
            else:
                starting_particles_monochloramine_concentration = 1.0
                injected_particles_monochloramine_concentration = 1.0

            if starting_particles_monochloramine_concentration == '':
                starting_particles_monochloramine_concentration = 1.0
            if injected_particles_monochloramine_concentration == '':
                injected_particles_monochloramine_concentration = 1.0

            decay_monochloramine_dict['starting-particles-concentration-monochloramine'] = starting_particles_monochloramine_concentration
            decay_monochloramine_dict['injected-particles-concentration-monochloramine'] = injected_particles_monochloramine_concentration
            
            if('starting-particles-concentration-dichloramine' in request.values):
                starting_particles_dichloramine_concentration = request.values['starting-particles-concentration-dichloramine']
                injected_particles_dichloramine_concentration = request.values['injected-particles-concentration-dichloramine']
            else:
                starting_particles_dichloramine_concentration = 1.0
                injected_particles_dichloramine_concentration = 1.0

            if starting_particles_dichloramine_concentration == '':
                starting_particles_dichloramine_concentration = 1.0
            if injected_particles_dichloramine_concentration == '':
                injected_particles_dichloramine_concentration = 1.0
            
            decay_monochloramine_dict['starting-particles-concentration-dichloramine'] = starting_particles_dichloramine_concentration
            decay_monochloramine_dict['injected-particles-concentration-dichloramine'] = injected_particles_dichloramine_concentration

            if('starting-particles-concentration-iodine' in request.values):
                starting_particles_iodine_concentration = request.values['starting-particles-concentration-iodine']
                injected_particles_iodine_concentration = request.values['injected-particles-concentration-iodine']
            else:
                starting_particles_iodine_concentration = 1.0
                injected_particles_iodine_concentration = 1.0
            
            if starting_particles_iodine_concentration == '':
                starting_particles_iodine_concentration = 1.0
            if injected_particles_iodine_concentration == '':
                injected_particles_iodine_concentration = 1.0
            
            decay_monochloramine_dict['starting-particles-concentration-iodine'] = starting_particles_iodine_concentration
            decay_monochloramine_dict['injected-particles-concentration-iodine'] = injected_particles_iodine_concentration

            if('starting-particles-concentration-docb' in request.values):
                starting_particles_docb_concentration = request.values['starting-particles-concentration-docb']
                injected_particles_docb_concentration = request.values['injected-particles-concentration-docb']
            else:
                starting_particles_docb_concentration = 1.0
                injected_particles_docb_concentration = 1.0
            
            if starting_particles_docb_concentration == '':
                starting_particles_docb_concentration = 1.0
            if injected_particles_docb_concentration == '':
                injected_particles_docb_concentration = 1.0

            decay_monochloramine_dict['starting-particles-concentration-docb'] = starting_particles_docb_concentration
            decay_monochloramine_dict['injected-particles-concentration-docb'] = injected_particles_docb_concentration

            if('starting-particles-concentration-docbox' in request.values):
                starting_particles_docbox_concentration = request.values['starting-particles-concentration-docbox']
                injected_particles_docbox_concentration = request.values['injected-particles-concentration-docbox']
            else:
                starting_particles_docbox_concentration = 1.0
                injected_particles_docbox_concentration = 1.0

            if starting_particles_docbox_concentration == '':
                starting_particles_docbox_concentration = 1.0
            if injected_particles_docbox_concentration == '':
                injected_particles_docbox_concentration = 1.0

            decay_monochloramine_dict['starting-particles-concentration-docbox'] = starting_particles_docbox_concentration
            decay_monochloramine_dict['injected-particles-concentration-docbox'] = injected_particles_docbox_concentration

            if('starting-particles-concentration-docw' in request.values):
                starting_particles_docw_concentration = request.values['starting-particles-concentration-docw']
                injected_particles_docw_concentration = request.values['injected-particles-concentration-docw']
            else:
                starting_particles_docw_concentration = 1.0
                injected_particles_docw_concentration = 1.0

            if starting_particles_docw_concentration == '':
                starting_particles_docw_concentration = 1.0
            if injected_particles_docw_concentration == '':
                injected_particles_docw_concentration = 1.0
            
            decay_monochloramine_dict['starting-particles-concentration-docw'] = starting_particles_docw_concentration
            decay_monochloramine_dict['injected-particles-concentration-docw'] = injected_particles_docw_concentration

            if('starting-particles-concentration-docwox' in request.values):
                starting_particles_docwox_concentration = request.values['starting-particles-concentration-docwox']
                injected_particles_docwox_concentration = request.values['injected-particles-concentration-docwox']
            else:
                starting_particles_docwox_concentration = 1.0
                injected_particles_docwox_concentration = 1.0

            if starting_particles_docwox_concentration == '':
                starting_particles_docwox_concentration = 1.0
            if injected_particles_docwox_concentration == '':
                injected_particles_docwox_concentration = 1.0
            
            decay_monochloramine_dict['starting-particles-concentration-docwox'] = starting_particles_docwox_concentration
            decay_monochloramine_dict['injected-particles-concentration-docwox'] = injected_particles_docwox_concentration

            if('starting-particles-concentration-chlorine' in request.values):
                starting_particles_chlorine_concentration = request.values['starting-particles-concentration-chlorine']
                injected_particles_chlorine_concentration = request.values['injected-particles-concentration-chlorine']
            else:
                starting_particles_chlorine_concentration = 1.0
                injected_particles_chlorine_concentration = 1.0

            if starting_particles_chlorine_concentration == '':
                starting_particles_chlorine_concentration = 1.0
            if injected_particles_chlorine_concentration == '':
                injected_particles_chlorine_concentration = 1.0
            
            decay_monochloramine_dict['starting-particles-concentration-chlorine'] = starting_particles_chlorine_concentration
            decay_monochloramine_dict['injected-particles-concentration-chlorine'] = injected_particles_chlorine_concentration

            if('flexCheckGroupByTimestep' in request.values):
                groupby_status = 1
                timestep_group_size = request.values['timestep-group-size']
            else:
                groupby_status = 0
                timestep_group_size = 1.0

            if timestep_group_size == '':
                timestep_group_size = 1.0

            print("gb: ", groupby_status)

            # Attempt to save pipe network and flows files to input folder. If unsuccessful (most likely due to incorrect file type),
            # an error will be shown to the user.
            try:
                if pipes and allowed_file(pipes.filename) and flows and allowed_file(flows.filename):
                    pipes_filename = secure_filename(pipes.filename)
                    pipes_save_location = os.path.join("input", pipes_filename)
                    pipes.save(pipes_save_location)
                    flows_filename = secure_filename(flows.filename)
                    flows_save_location = os.path.join("input", flows_filename)
                    flows.save(flows_save_location)
            except Exception as e:
                alertDanger.message = "Pipe Network File Could Not Uploaded. Is file type CSV?" + e
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
                print("running simulation...")
                output_file = 0
                output_file = sim.preset_simulation_button_handler(
                    pipes_save_location,
                    flows_save_location,
                    density, diffusion_status, 
                    stagnant_diffusion_status, 
                    advective_diffusion_status, 
                    molecular_diffusion_coefficient, 
                    granularity, 
                    decay_free_chlorine_status, 
                    decay_monochloramine_status, 
                    starting_particles_free_chlorine_concentration,
                    injected_particles_free_chlorine_concentration,
                    decay_monochloramine_dict,
                    groupby_status,
                    timestep_group_size)
                print("done running simulation...")
                
            except Exception as e:
                print("01ALERT", e)
                alertDanger.message = e
            # print(e)
                # raise Exception
            # print("APP ALERT ERROR: ", alertDanger.message)
            #If simulation is successful, redirect to download page. If failed, show error message.
            print( "output_file: ", output_file)
            if(output_file):
                print("Simulation Complete...")
                return redirect(url_for('download' , diffusion_status = diffusion_status, date_time = date_time))

            else:
                # alertDanger.message = "Simulation Failed. Do the files contain the correct data?"
                return render_template("upload.html", alert = alertDanger)
            
    return render_template("upload.html")

#Route to download page accessed by running a simulation from upload. If not redirected from the upload page, redirect to upload page.
#  Therefore, it is not possible to search pipesim.com/download directly. It will just make you upload.
@app.route('/download')
def download():
    path = pathlib.Path('input')


    for root, dirs, files in os.walk(path):
        for file in files:
            os.remove((str(path) + '/'  + file))

    try: 
        date_time = request.args['date_time']
        diffusion_status = request.args['diffusion_status']
    except:
        return redirect(url_for('upload'))

    return render_template('download.html', diffusion_status = diffusion_status, date_time = date_time)

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
    multiprocessing.freeze_support()
    print("App Running...")

    webbrowser.open("http://localhost:5000")
    app.run()