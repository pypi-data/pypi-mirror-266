from mlflow import log_metrics, log_params, log_artifacts, log_image, set_experiment, set_tracking_uri, log_artifact, set_tags, start_run
from mlflow.pytorch import log_model as log_mlflow_model
import cv2 as cv
import os
import sys
import imp
import datetime
import glob

def write_param(param_dict={"learning_rate": "0.001", "total_epochs": "10"}):
    """
    This method stores the string type parameters which ideally remain same for each epoch like- Total Epochs, Learning Rate
    Args:
        param_dict (dict): a dictionary with key-value pair for parameters which remains constant for each epoch.
    """
    log_params(param_dict)


def write_metric(metric_dict={"train_loss": None, "valid_loss": None, "test_loss": None}, step = 0):
    """
    This method is used to store metrics into the MLFLOW Server for each run.
    Args: 
         metric_dict (dict): a dictionary with various key-pair for an epoch (i.e. step) which we want to store
         step (int): current epoch for the metric to be stored
    """
    log_metrics(metric_dict, step)


def write_image(numpy_array, image_name="image.jpg"):
    """
    This method can be used to store numpy_data of images read with opencv directly into the MLFLOW Server.
    Args:
         numpy_array (numpy arr): numpy array of an image
         image_name (str): Name with which we want to save this numpy_array as an image in the MLFLOW Server
    """
    numpy_shape = numpy_array.shape
    if len(numpy_shape) == 3:
        numpy_array = cv.cvtColor(numpy_array, cv.COLOR_BGR2RGB) # mlflow reads channels in reverse order of opencv
    log_image(numpy_array, image_name)


def write_text(filename, filedata):
    """
    This method will store the textual information directly in the MLFLOW Server and save it with the name specified in variable filename
    Args:
        filename (str): Name with which we want to save the textual data in the MLFLOW Server
        filedata (str): Textual data which we want to save in the mlflow server.
    """
    if not os.path.exists("additional_info"):
        os.makedirs("additional_info")
    with open("additional_info/"+filename, "w") as f:
        f.write(filedata)
    log_artifacts("additional_info")


def write_files(filename, filepath="weights"):
    """
    This method will save the file specified in the filename variable, to the MLFLOW Server within the directory specified in filepath.
    Args:
        filename (str): Name of the file to be saved in the mlflow server.
        filepath (str): Directory within MLFLOW Server where we want to save the file.
    """
    log_artifact(filename, filepath)


def write_directory(send_directory, mlflow_dir_path="artifacts"):
    """
    This method takes all the data present inside the send_directory folder and send it to the Mlflow server in the folder "artifacts"
    Args:
        send_directory (str): data present inside this directory is send it to the Mlflow server
        mlflow_dir_path (str): directory in Mlflow server where the data will get stored
    """
    for filename in glob.glob(send_directory):
        write_files(filename, mlflow_dir_path)


def init_run(user_name, project_name, experiment_name, runName, mlflow_server_uri = "http://127.0.0.1:5555"):
    """
    This method will establish connection with the MLFLOW Server, create the Project, And auto-add informations like
    experiment name, username, terminal command used to run the file, and start recording the terminal output.
    Args:
        user_name (str): Name of the programmer running the code.
        project_name (str): Name of the project.
        experiment_name (str): Name of the experiment performing within the project.
        runName (str): any other specific detail about the experiment.
        mlflow_server_uri (str): URI of the MLFLOW Server.
    """
    terminal_command = " ".join(sys.argv)
    runName = runName + " " + str(datetime.datetime.now())
    set_tracking_uri(mlflow_server_uri)
    set_experiment(project_name)
    start_run(run_name = runName)
    set_tags({"experiment_name": experiment_name, "user_name": user_name, "terminal_run": "python3 "+ terminal_command})
    record_terminal_logs()
    

def record_terminal_logs(log_filename="log.txt"):
    """
    This method start recording the terminal outputs in the log.txt file, and also prints the output to the terminal.
    Args:
        log_filename (str): filename in which the logs will be written
    """
    sys.stdout = Logger(log_filename)


def write_terminal_logs(log_filename, log_directory = "log"):
    """
    This method sends the stored terminal logs (saved in log.txt) to the mlflow-server and store it within the log/ directory.
    Args:
        log_filename (str): Filename which stores the terminal logs
        log_directory (str): Drectory in which the log_filname will be stored inside the MLFLOW Server
    """
    write_files(log_filename, log_directory)
    os.system("rm "+log_filename)


def log_model(model_architecture, model_run_path="models"):
    """
    This method is used to log model architecture to the MLFLOW Server, later which can be used for Model Registry
    Args:
        model_architecture (tensor): DL model architecture
        model_run_path (str): Path in MLFLOW Server where this architecture will be saved within the run_id folder
    """
    log_mlflow_model(model_architecture, model_run_path)    


def end_run(log_filename="log.txt"):
    """ 
    This method stores the log.txt file containing the terminal logs for the experiment into the MLFLOW Server.
    Args:
        log_filename (str): Filename which stores the terminal logs
    """
    sys.stdout.file.close()
    imp.reload(sys)
    write_terminal_logs(log_filename)


class Logger:
    def __init__(self, filename):
        self.console = sys.stdout
        self.file = open(filename, 'w')
 
    def write(self, message):
        self.console.write(message)
        self.file.write(message)
 
    def flush(self):
        self.console.flush()
        try:
          self.file.flush()
        except:
          pass
