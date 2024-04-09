**Multi-Agent Accelerator for Data Science: Batch AutoML (MAADSBML)

*Revolutionizing Data Science with Artificial Intelligence*

**Overview**

*MAADSBML combines Artificial Intelligence, Docker, Machine Learning.  It automates the machine learning process, and finds the BEST algorithm for your data.  It also
produces a very detailed PDF report.  MAADSBML is integrated with Docker Container.
 
This library allows users to harness the power of agent-based computing using hundreds of advanced linear and non-linear algorithms. 

**Compatibility**
    - Python 3.8 or greater
    - Minimal Python skills needed

**Copyright**
   - Author: Sebastian Maurice, PhD

**Installation**
   - At the command prompt write:
     **pip install maadsbml**
     - This assumes you have [Downloaded Python](https://www.python.org/downloads/) and installed it on your computer.  
	 - You will also need to pull the MAADSBML Docker container:  **maadsdocker/maads-batch-automl-otics**

**Syntax**
  - There are literally two lines of code you need to write to train your data and make predictions:

**Main functions:**
   - **hypertraining**
     Executes hundreds of agents, running hundreds of advanced algorithms and completes in minutes.  A master agent then chooses the BEST algorithm that best  models your data.
   - **hyperpredictions**
     After training, make high quality predictions - takes less than half a second (about ~100 milliseconds). Users can also generate predictions using **non-python code** 
	 such as JAVA.  	 
   - **algodescription**
     Get detailed information on the optimal algorithm found during hypertraining
   - **abort**
     Abort the training process.
   - **rundemo**
     To run canned demo of the system to see how it works.
	 
**First import the Python library.**

**import maadsbml**

1. **maadsbml.hypertraining(host,port,filename,dependentvariable,removeoutliers=0,hasseasonality=0,summer='6,7,8',winter='11,12,1,2',shoulder='3,4,5,9,10',
       trainingpercentage=70,shuffle=0,deepanalysis=0,username='admin',timeout=1200,company='otics',password='123',email='support@otics.ca',usereverseproxy=0,
       microserviceid='',maadstoken='123',mode=0)**

**Parameters:**	

*host* : string, required

- This is the IP address of the running Docker container - it is usually http://localhost

*port* : int, required

- This is the TRAINING PORT in the container. The default is port==5595

*filename* : string, required
 
 - This is the raw data file in csv format - Note this file is stored on your host machine - the DOCKER container needs to be mapped to this volume using -v

*dependentvariable* : string, required

- This is the dependent variable in your csv file.

*removeoutliers* : int, optional, 1 or 0

- If 1, then outliers will be removed from your data.  If 0, no outliers are removed.

*hasseasonality* : int, optional, 1 or 0
      
- If 1, then your data will be modeled for seasonality: Winter, Summer, Shoulder. If 0, then your data will 
  not be modeled for seasonality.  If modeling for seasonality, ensure you have enough data points that 
  covers the seasons, usually 1 year of data.
       
*summer* : string, optional
       
- Definition for summer months.  This can be changed.

*winter* : string, optional
       
- Definition for winter months.  This can be changed.

*shoulder* : string, optional
       
- Definition for shoulder months.  This can be changed.

*trainingpercentage* : int, optional, Default=70
       
- This is the split percentage between Training and Test data sets.   It is defaulted to 70 (70% for training, 30% test).

*shuffle* : number, 0 or 1, optional

- Indicates whether to shuffle the training dataset or not, default=0.

*deepanalysis* : int, optional

- This will force MAADSBML to perform deeper analysis on your data.  This could take 30-40 minutes.  Set to 1 for deepanalysis, 0 for no deep analysis.

*username* : string, optional
 
 - This identifies a user.  You may want to change this if multiple users are running the same file.

*company* : string, optional
 
 - This identifies your company. You may want to change this for the Report.

*timeout* : int, optional

- You can increase this if you receive a timeout error before the training is taking too long. The setting is in seconds.

*password* : string, optional 

 - leave as is

*email* : string, optional 

 - leave as is
 
*usereverseproxy* : int, optional

- leave as is
 
*microserviceid* : string, optional

- leave as is if not using a pass through service.

*mode* : int, optional

- leave as is

*maadstoken* : string, optional

- leave as is

**Returns:** string JSON buffer, with the algorithm key (PKEY) and other details:
        
- PKEY: : This is the key to the BEST algorithm and must be used when making predictions.
			
**2. maadsbml.hyperpredictions(pkey,theinputdata,host,port,username,algoname='',seasonname='',usereverseproxy=0,microserviceid='',password='123',company='otics',
       email='support@otics.ca',maadstoken='123')**

**Parameters:**	

*pkey* : string, required

- This is the PKEY you received from the hypertraining function.

*theinputdata* : string, required

- These are the Xs for your model: For example if my model had 3 Xs then inputdata='5/21/2010,-14.3,-32.0,-12.0', with the first entry as Date: Date 
must be in the format: MM/DD/YYYY

*host* : string, required

- This is the IP address of the running Docker container - it is usually http://localhost

*port* : int, required

- This is the PREDICTION PORT in the container. The default is port==5495 (or 5595)

*username* : string, required

- The username you used in the hypertraining functions. Default is admin.

*algoname* : string, optional

- Enter the name of the algorithm to use, this can be retrieved from the hypertraining function.  If this is empty, the BEST algorithm will be used by default.

*seasonname* : string, optional

- Enter the season to use (winter,summer,shoulder), this can be retrieved from the hypertraining function.  If this is empty, the default season is used.

*usereverseproxy* : int, optional

- leave as is

*microserviceid* : int, optional

- leave as is

*password* : string, optional

- leave as is

*company* : string, optional

- change for reporting.

*email* : string, optional

- leave as is

*maadstoken* : string, optional

- leave as is
	 
**Returns:** string buffer containing the prediction, and other details.
        

**3. maadsbml.abort(host,port=10000)**

**Parameters:**	

*host* : string, required

- This is the IP address of the Docker container: http://localhost
     
*port* : string, optional
      
- Port is fixed at 10000

**Returns:** Abort will shutdown and re-start your system.
        
  
**4. maadsbml.rundemo(host,port,demotype=1,timeout=1200,usereverseproxy=0,microserviceid='')**

**Parameters:**	

*host* : string, required

- This is the IP address of the Docker container: http://localhost
     
*port* : string, required
      
- This is the TRAININGPORT, it is usually 5595.

*demotype* : int, required

- If demotype is 1, then a regression models is run; if demotype is 0 then a classification model is run.

*timeout* : int, optional

- The connection timeout between Python and the container, in seconds

*usereverseproxy* : int, optional

- leave as is 

*microserviceid* : string, optional

- leave as is
        
**Returns:** null
        
 
**5. maadsbml.algodescription(host,port,pkey,timeout=300,usereverseproxy=0,microserviceid='')**

**Parameters:**	

*host* : string, required

- This is the IP address of the Docker container: http://localhost
     
*port* : string, required
      
- This is the TRAININGPORT, it is usually 5595.

*pkey* : string, required

- This is the PKEY from hypertraining.

*timeout* : int, optional

- The connection timeout between Python and the container, in seconds

*usereverseproxy* : int, optional

- leave as is 

*microserviceid* : string, optional

- leave as is
        
**Returns:** null
        
 

       