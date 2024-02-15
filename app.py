"""
This file contains the main flask application. It contains the routes for the website, and the functions that are called when a route is accessed.
"""

import os
from time import time
from flask import jsonify
import math
import zipfile
import pathlib
import builder
import webbrowser
import multiprocessing
from io import BytesIO
from flask import request
from datetime import datetime
from display import SimulationWindow
from werkzeug.utils import secure_filename
from flask import Flask, render_template, request, redirect, url_for, send_from_directory, send_file

#Flask app setup
app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(12).hex()

#Alert class for displaying alerts on the GUI
class alert:
    def __init__(self, message, type):
        self.type = type
        self.message = message

#Specify allowed file types for upload
ALLOWED_EXTENSIONS = set(['csv'])

def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

""" Routes """

""" Default Route """
@app.route('/')
def index():
    return render_template("index.html")

""" Custom Routes"""

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

#route to upload page
@app.route('/upload', methods=['GET', 'POST'])
def upload():

    # Clear output folder of any files from previous simulations.
    path = pathlib.Path('logs\output_batch')
    for root, dirs, files in os.walk(path):
        for file in files:
            os.remove((str(path) + '/'  + file))

    #Get current time to be displayed on download page.
    now = datetime.now()
    date_time =now.strftime("%m/%d/%Y, %H:%M:%S")


    #Set default alert message.
    alertDanger = alert("Running Simulation Failed", "Danger")
   
   # If user is submitting the upload form, check whether they are running a settings preset simulation or a custom simulation based on the button which was pressed.
    if request.method == 'POST':

        # User is electing to run a settings preset simulation.
        if 'settings-submit' in request.form:
            file = request.files['setting-preset']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                save_location = os.path.join('input', filename)
                file.save(save_location)

                sim = SimulationWindow()
           
                output_file = 0
                output_file = sim.settings_preset_simulation_button_handler(save_location)

                # print("output_file: ", output_file)
                if(output_file):
                    # print("output")
                    return redirect(url_for('download', concentration_status = 0, diffusion_status = 0 , date_time = date_time))
        
            return 'uploaded'
        
        # User is not electing to run a settings preset simulation. Thus, running a custom simulation with selected files/settings.
        elif 'preset-submit' in request.form:

            # Get pipe network and flows files from form
            pipes = request.files['pipe-network']
            flows = request.files['flow-preset']

            #Validating density input. Input must be a number between 0 and 1 inclusive. 
            try:
                density = request.values['density']

                # If no density is input, default to 120.
                if density == '':                
                    density = 120
                density = float(density)
                if density < 0 or density > 12000:
                    alertDanger.message = "Density must be between 1 and 12000"
                    raise Exception
            except:
                alertDanger.message = "Density must be a number between 1 and 12000"
                raise Exception
                
            # Validating granularity input. Input is a number in unit: seconds, which is converted to unit: minutes granularity for the simulation.
            granularity = request.values['custom-granularity']
            if granularity == '':
                granularity = 1
            else:
                granularity = float(granularity) 
                granularity /= 60
        
            # Check if diffusion is enabled (flexbox is checked). If so, set diffusion status to 1. Else, set to 0.
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
            
            # Validate that molecular diffusion coefficient input exists. If not, d_m will be set to default value.
            molecular_diffusion_coefficient = request.values['molecular-diffusion-coefficient']
            if any(char.isdigit() for char in molecular_diffusion_coefficient):
                pass
            else:
                molecular_diffusion_coefficient = 8.28 * math.pow(10, -4) 

            global decay_free_chlorine_status 
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
            
            # Attempts to build pipe network. If builder.build successfully returns a single value, an error will be shown to the user.
            try:
                message = builder.build(pipes_save_location)
                alertDanger.message = message
                raise Exception
            except:
                pass

            sim = SimulationWindow()

            # Catches and alerts users of errors in the simulation. These include errors involving output files being open,
            # errors involving the input files, and errors involving the simulation itself.
            try:
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
                
            except Exception as e:
                alertDanger.message = e

            with open('static/update-text.txt', 'w') as f:
                f.write('')

            #If simulation is successful, redirect to download page. If failed, show error message.
            if(output_file):
                print("Simulation Complete...")
                return redirect(url_for('download' ,  concentration_status = int(decay_free_chlorine_status), diffusion_status = diffusion_status, date_time = date_time))

            else:
                # alertDanger.message = "Simulation Failed. Do the files contain the correct data?"
                return render_template("upload.html", alert = alertDanger)
    
    
    return render_template("upload.html")


# Route to download page accessed by running a simulation from upload. If not redirected from the upload page, redirect to upload page.
# Therefore, it is not possible to search pipesim.com/download directly. It will just make you upload.
@app.route('/download')
def download():
    path = pathlib.Path('input')

    for root, dirs, files in os.walk(path):
        for file in files:
            if file != "README.txt":
                os.remove((str(path) + '/'  + file))
                
    try: 
        date_time = request.args['date_time']
        diffusion_status = request.args['diffusion_status']
        concentration_status = request.args['concentration_status']
    except:
        return redirect(url_for('upload'))

    return render_template('download.html', concentration_status = int(concentration_status), diffusion_status = diffusion_status, date_time = date_time)

# Download log files from the output folder. This is a zip file containing all the output files from the simulation.
@app.route('/download_log')
def download_log():
    
    path = pathlib.Path('logs\output_batch')
    memory_file = BytesIO()

    
    with zipfile.ZipFile(memory_file, 'w') as zf:
        zf.write('static/output/age_graph.png')
        zf.write('static/output/age_graph_large.png')
        zf.write('static/output/expelled_histogram.png')
        zf.write('static/output/flow_graph.png')
        zf.write('static/output/expelled.csv')
        if(decay_free_chlorine_status == 1):
            zf.write('static/output/concentration_graph.png')
        # zf.write('static/output/graph_scaled.png')


        # zf.write('static/output/modifier_histogram.png')

    # with zipfile.ZipFile(memory_file, 'w') as zf:
    #     for root, dirs, files in os.walk(path):
    #         for file in files:
    #             print(root, file)
    #             zf.write(os.path.join(root, file))
    memory_file.seek(0)
    
    return send_file(memory_file, as_attachment=True, download_name='logs.zip')

""" Error Routes """

#Page not found error(404)
@app.errorhandler(404)
def page_not_found_404(e):
    return render_template("404.html"), 404

#Internal server error(500)
@app.errorhandler(500)
def page_not_found_500(e):
    return render_template("500.html"), 500

if __name__ == '__main__':

    # multiprocessing.freeze_support() # Required for multiprocessing to work on Windows

    print("App Running...")

    # webbrowser.open("http://localhost:5000") # Open browser to localhost:5000
    app.run()