# Launch an Agave App from a Reactor

Because a Reactor has a working Agave client embedded in it, you can simply 
use AgavePy client's native method for job submission. The body of the
job submission is a JSON dict that maps exactly to the serialized format
in which we usually represent Agave job definitions.

```python
agaveclient.jobs.submit(body=job_dict)
```

Since you likely care about the ID of the job, you can do

```python
job_id = agaveclient.jobs.submit(body=job_dict)['id']
```

## Making a proper dict

From an Agave job JSON file::

```python
import json

with open('myfile.json', 'e') as f:
    job_dict = json.load(f)

```

## Generating a template

```shell
jobs-template -A APPID > job-template.json
```

## Serialzing in and out of YAML

It's a soft convention to use YAML in parameterizing Reactors. 
The [JSONtoYAML](https://www.json2yaml.com/) tool online is a good starting 
point to create a YAML serialization of your job definition. 

## Extending a template 

Leave slots empty in your YAML. Once you've read it into a dictionary, 
fill in slots dynamically using code in your Reactor. 