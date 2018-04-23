"""
Uses the plan referenced by a manifest to bootstrap an instance of FCS-ETL app
"""
import datetime
import json
import os
import sys
from time import sleep
from attrdict import AttrDict
from reactors.utils import Reactor, agaveutils, process

# import datetime
# import json
# import os
# import sys
# from attrdict import AttrDict
# import reactors as Reactor
# from agaveutils import *
# from agavedb import AgaveKeyValStore

PWD = os.getcwd()
AGAVE_APP_ALIAS = 'fcs_etl_app'


def on_success(self, successMessage):
    '''Custom success handler'''
    try:
        slackid = self.settings.linked_reactors.slackbot.id
        slackchan = self.settings.linked_reactors.slackbot.opts.get(
            'channel', 'notifications')
        slacktxt = ':star2: {}'.format(successMessage)
        slackmsg = {'text': slacktxt,
                    'channel': slackchan}
        self.send_message(slackid, slackmsg, ignoreErrors=True,
                          retryMaxAttempts=1)
    except Exception:
        pass
    self.logger.info("{}".format(successMessage))
    sys.exit(0)


def on_failure(self, failMessage, exceptionObject):
    '''Custom failure handler'''
    try:
        slackid = self.settings.linked_reactors.slackbot.id
        slackchan = self.settings.linked_reactors.slackbot.opts.channel
        slacktxt = ":bomb: {} : {}".format(failMessage, exceptionObject)
        slackmsg = {'text': slacktxt,
                    'channel': slackchan}
        self.send_message(slackid, slackmsg, ignoreErrors=True,
                          retryMaxAttempts=1)
    except Exception:
        pass
    self.logger.critical("{} : {}".format(failMessage, exceptionObject))
    sys.exit(1)


def sample_to_URI(plan,sample,base='http://hub.sd2e.org/user/nicholasroehner/rule_30',version='1'):

    for i in plan['initialState']:
        if i['Sample Id'] == sample:
            try:
                for c in i['Conditions']:
                    for k in c:
                        if k == 'IPTG_measure':
                            iptg = c[k]
                        if k == 'Larabinose_measure':
                            ara = c[k]
                        if k == 'aTc_measure':
                            atc = str(c[k]).replace('.','p')
                strains = []
                for s in i['Strains']:
                    strains.append(s['Strain Id'].split('#')[-1])

                if len(strains)==1:
                    strain_string = strains[0]
                else:
                    strain_string = 'pAN3928_pAN4036'

                return '{}/{}_system_{}_{}_{}/{}'.format(base,strain_string,ara,atc,iptg,version)

            except KeyError as e:
                print 'Could not find all metadata for ',sample,e
                return 'undefined'


def file_and_parent(filepath):
    '''Return a file and its parent directory'''
    return os.path.join(os.path.basename(os.path.dirname(filepath)), os.path.basename(filepath))


def extract_experimental_data(manifest, plan):
    experimental_data = {}
    samples = []
    for sample in [s for s in manifest['samples'] if s['collected']]:
        samples.extend([{'file': file_and_parent(f['file']),
                         'sample': sample_to_URI(plan, sample['sample'])} for f in sample['files'] if 'beadcontrol' not in sample['sample']])
    experimental_data['tasbe_experimental_data'] = {'samples': samples, 'rdf:about': manifest['rdf:about']}
    return experimental_data


def build_analysis_parameters():
    analysis_parameters = json.loads('''{
      "_comment1": "Information linking experiment FCS files to the appropriate cytometer channels, to be supplied by TA1/TA2",
      "tasbe_analysis_parameters": {
        "_comment1": "the rdf:about field is a URI that persistently identifies this analysis configuration",
        "rdf:about": "placeholder",

        "_comment2": "Compatible TASBE interface version, following Semantic Versioning (semver.org).  Note that underspecifying version allows use of backward compatible upgrades.",
        "tasbe_version": "https://github.com/SD2E/reactors-etl/releases/tag/2",

        "_comment3": "identifier linking to the color model for interpreting units.  Should typically be derived from the same process_control_data as is referenced in the experimental_data",
        "color_model": "placeholder",

        "_comment4": "identifier linking to the data collection to analyze",
        "experimental_data": "placeholder",

        "_comment5": "each replicate group collects a set of samples from the experimental collection under a label",
        "replicate_groups": [{
            "label": "",
            "samples": []
          }
        ],

        "TASBEConfig": {
            "flow": {
                "outputPointCloud": true,
                "pointCloudPath": "output"
            },
            "OutputSettings": {
                "StemName": "plots",
                "FixedInputAxis": false
            },
            "outputDirectory": "output"
        },
        "_comment6": "additional configuration parameters",
        "output": {
          "title": "placeholder",
          "plots": true,
          "plots_folder": "plots",
          "file": "./output/output.csv",
          "quicklook": true,
          "quicklook_folder": "./output/quicklook"
        },
        "channels": ["GFP"],
        "_comment7": "additional parameters controlling data processing and output",
        "additional_outputs": ["histogram", "point_clouds", "bayesdb_files"],
        "min_valid_count": 100,
        "pem_drop_threshold": 5,
        "bin_min": 6,
        "bin_max": 10,
        "bin_width": 0.1
      }
    }''')
    return analysis_parameters

def build_color_model(channels):
    color_model = json.loads('''{
      "_comment1": "Parameters controlling conversion of process controls into an ERF color model, plus debugging/graphical outputs, to be supplied by TA1/TA2",
      "tasbe_color_model_parameters": {
        "_comment1": "the rdf:about field is a URI that persistently identifies this run configuration",
        "rdf:about": "placeholder",

        "TASBEConfig": {
            "heatmapPlottype": "contour",
            "plots": {
                "plotPath": "plots"
            }
        },
        "_comment2": "Compatible TASBE interface version, following Semantic Versioning (semver.org).  Note that underspecifying version allows use of backward compatible upgrades.",
        "tasbe_version": "https://github.com/SD2E/reactors-etl/releases/tag/2",

        "_comment3": "identifier linking to the process control data set to be run",
        "process_control_data": "placeholder",

        "_comment4": "For each channel, the species and how to process and display it",
        "channel_parameters": [''' + ',\n'.join(['''{
            "_comment1": "name must match a channel from the cytometer configuration",
            "name": "''' + channels[c]['name'] + '''",
            "_comment2": "a persistent URI linking to the actual species being quantified",
            "species": "https://www.ncbi.nlm.nih.gov/protein/AMZ00011.1",
            "_comment3": "Nickname for the species for charts",
            "label": "GFP",
            "_comment4": "cutoff for analysis",
            "min": 2,
            "_comment5": "primary color for lines on certain plots",
            "chart_color": "y"
          }''' for c in range(len(channels))]) + '''    ],
        "_comment5": "Other processing parameters, to be exposed",
        "tasbe_config": {
          "gating": {
            "type": "auto",
            "k_components": 2
          },
          "autofluorescence": {
            "type": "placeholder"
          },
          "compensation": {
            "type": "placeholder"
          },
          "beads": {
            "type": "placeholder"
          }
        },

        "_comment6": "Cutoff for bead peak detection",
        "bead_min": 2,

        "_comment7": "Which channel is being used for unit calibration",
        "ERF_channel_name": "''' + channels[0]['name'] + '''",

        "_comment8": "additional parameters controlling data processing and output",
        "translation_plot": false,
        "noise_plot": false
      }
    }''') # Defaulting to first channel for ERF_channel_name; all channels' names will be "GFP"
    return color_model

def build_process_control_data(plan, channels, experimental_data, cytometer_configuration_file_URI, manifest):
    for state in plan['initialState']:
        for condition in state.get('Conditions', []):
            if 'bead_model' in condition:
                bead_model = condition['bead_model']
                bead_file_URI = state.get('Sample Id', 'UNKNOWN')
                bead_batch = condition.get('bead_batch', 'Lot AJ02') # This is a baby bumper for Q0
                break # Should only be one bead file, until we're handling multiple channels, at which point we'll need more data to know which is which

    for sample in [s for s in manifest['samples'] if s['collected']]:
        if sample['sample'] == bead_file_URI:
            #bead_file = sample['files'][0]['file']
            bead_file = file_and_parent(sample['files'][0]['file'])

    for state in plan['initialState']:
        for condition in state.get('Conditions', []):
            if 'Is_Blank' in condition and condition['Is_Blank']==True:
                blank_sample = state['Sample Id']
                blank_file = ''
                for sample in [s for s in manifest['samples'] if s['collected']]:
                    if sample['sample'] == blank_sample:
                        blank_file = file_and_parent(sample['files'][0]['file'])
                        break
                break # Should only be one blank/negative control file, until we're handling multiple channels, at which point we'll need more data to know which is which.

    positive_control_files = [''] * len(channels)

    #beads and blanks/negative control
    #channel names can come from cytometer config
    process_control_data = json.loads('''{
      "_comment1": "Information linking process control FCS files to the appropriate cytometer channels, to be supplied by TA3",
      "tasbe_process_control_data": {
        "_comment1": "the rdf:about field is a URI that persistently identifies this process control information set",
        "rdf:about": "placeholder",

        "_comment2": "Compatible TASBE interface version, following Semantic Versioning (semver.org).  Note that underspecifying version allows use of backward compatible upgrades.",
        "tasbe_version": "https://github.com/SD2E/reactors-etl/releases/tag/2",

        "_comment3": "identifier linking to the instrument and optical configuration used for collecting data",
        "cyometer_configuration": "''' + cytometer_configuration_file_URI + '''",

        "_comment4": "all files are URIs to the location of a file on the TA4 infrastructure",
        "bead_file": "''' + bead_file + '''",
        "_comment5": "name of the type of beads being used; must match an entry in the TASBE bead catalog https://github.com/TASBE/TASBEFlowAnalytics/blob/master/code/BeadCatalog.xlsx",
        "_comment6": "name of the batch of beads being used; must match an entry in the TASBE bead catalog https://github.com/TASBE/TASBEFlowAnalytics/blob/master/code/BeadCatalog.xlsx",
        "TASBEConfig": {
            "beads": {
                "beadModel": "''' + bead_model + '''",
                "beadBatch": "''' + bead_batch + '''"
            }
        },

        "_comment7": "the blank file should be wild-type or null transfection",
        "blank_file": "''' + blank_file + '''",

        "_comment8": "each channel should have a strong single positive control of the species it quantifies",
        "channels": [''' +
            ',\n'.join(['''      {
            "_comment1": "name must match a channel from the cytometer configuration",
            "name": "''' + channels[c]['name'] + '''",
            "_comment2": "FCS file for single positive control",
            "calibration_file": "''' + positive_control_files[c] + '''"
          }''' for c in range(len(channels))]) + '''
        ],

        "_comment9": "cross-file pairs are for converting to FITC units; only needed if a fluorescent protein is measured outside the FITC channel",
        "cross_file_pairs": []
      }
    }''') #Again, no support for multiple channels, so no cross-file pairs
    return process_control_data


def main():

    r = Reactor()
    m = AttrDict(r.context.message_dict)
    # Look up my own name
    actor_name = r.get_attr('name')
    # example:
    # 'bob' 'was unable to call' 'karen' (id: ABCDEX, exec: BCDEG)
    template = "{} {} {} (actor/exec {} {})"
    # override on_failure and on_success
    funcType = type(r.on_failure)
    r.on_failure = funcType(on_failure, r, Reactor)
    funcType = type(r.on_success)
    r.on_success = funcType(on_success, r, Reactor)

    r.logger.debug("message: {}".format(m))
    # Use JSONschema-based message validator
    # - In theory, this obviates some get() boilerplate
    if not r.validate_message(m):
        r.on_failure(template.format(
            actor_name, 'got an invalid message', m, r.uid, r.execid), None)

    ag = r.client  # Agave client
    # db = AgaveKeyValStore(ag)  # AgaveDB client
    context = r.context  # Actor context
    m = context.message_dict

    r.logger.debug("Message: {}".format(m))

    agave_uri = m.get('uri')
    (agave_storage_sys, agave_abs_dir, agave_filename) =\
        agaveutils.from_agave_uri(agave_uri)
    manifest_path = os.path.join('/', agave_abs_dir, agave_filename)

    r.logger.debug("fetching manifest {}".format(agave_uri))

    try:
        mani_file = agaveutils.agave_download_file(
            agaveClient=r.client,
            agaveAbsolutePath=manifest_path,
            systemId=agave_storage_sys,
            localFilename='manifest.json')

        if mani_file is None:
            raise Exception("no error was detected but file appears empty")

    except Exception as e:
        r.on_failure(template.format(
            actor_name, 'failed to download',
            manifest_path, r.uid, r.execid), e)

    # Load manifest so we can read the plan and config
    # - Use AttrDict so we can use dot.notation
    r.logger.debug("loading manifest into a dict and getting values")
    manifest_dict = {}
    try:
        with open('manifest.json') as json_data:
            manifest_dict = AttrDict(json.load(json_data))
            plan_uri = manifest_dict.plan
            instrument_config_uri = manifest_dict.instrument_configuration
    except Exception as e:
        r.on_failure(template.format(
            actor_name, 'was unable to properly parse the',
            'manifest file', r.uid, r.execid), e)

    r.logger.debug("fetching plan {}".format(plan_uri))
    plan_abs_path = None
    try:
        (plan_system, plan_dirpath, plan_filename) =\
            agaveutils.from_agave_uri(plan_uri)
        plan_abs_path = os.path.join(plan_dirpath, plan_filename)
        plan_file = agaveutils.agave_download_file(
            agaveClient=r.client,
            agaveAbsolutePath=plan_abs_path,
            systemId=plan_system,
            localFilename='plan.json')
    except Exception as e:
        r.on_failure(template.format(
            actor_name, 'failed to download',
            plan_abs_path, r.uid, r.execid), e)

    r.logger.debug("fetching instrument config {}".format(instrument_config_uri))
    try:
        (ic_system, ic_dirpath, ic_filename) = \
            agaveutils.from_agave_uri(instrument_config_uri)
        ic_abs_path = os.path.join(ic_dirpath, ic_filename)
        ic_file = agaveutils.agave_download_file(
            agaveClient=r.client,
            agaveAbsolutePath=ic_abs_path,
            systemId=ic_system,
            localFilename='cytometer_configuration.json')
    except Exception as e:
        r.on_failure(template.format(
            actor_name, 'failed to download',
            ic_abs_path, r.uid, r.execid), e)

    r.logger.debug("loading dict from instrument config file {}".format(ic_file))
    try:
        cytometer_configuration = json.load(open(ic_file, 'rb'))
    except Exception as e:
        r.on_failure(template.format(
            actor_name, 'could not load dict from JSON document',
            ic_file, r.uid, r.execid), e)

    r.logger.debug("loading tasbe_cytometer_configuration.channels")
    try:
        channels = cytometer_configuration['tasbe_cytometer_configuration']['channels']
    except Exception as e:
        r.on_failure(template.format(
            actor_name, 'was unable to load',
            'tasbe_cytometer_configuration.channels from settings',
            r.uid, r.execid), e)

    r.logger.debug("loading dict from plan JSON file {}".format(plan_file))
    try:
        plan = json.load(open(plan_file, 'rb'))
    except Exception as e:
        r.on_failure(template.format(
            actor_name, 'could not load dict from JSON document',
            plan_file, r.uid, r.execid), e)

    r.logger.debug("writing experimental data to local storage")
    experimental_data = extract_experimental_data(manifest_dict, plan)
    with open('experimental_data.json', 'wb') as outfile:
        json.dump(experimental_data, outfile, sort_keys=True,indent=4,separators=(',', ': '))

    r.logger.debug("writing intermediary JSON files to local storage")
    try:
        with open('process_control_data.json', 'wb') as outfile:
            json.dump(build_process_control_data(plan, channels, experimental_data, instrument_config_uri,manifest_dict), outfile, sort_keys=True,indent=4,separators=(',', ': '))
        with open('color_model_parameters.json', 'wb') as outfile:
            json.dump(build_color_model(channels), outfile, sort_keys=True,indent=4,separators=(',', ': '))
        with open('analysis_parameters.json', 'wb') as outfile:
            json.dump(build_analysis_parameters(), outfile, sort_keys=True,indent=4,separators=(',', ': '))
    except Exception as e:
        r.on_failure(template.format(
            actor_name, 'could not load write JSON file(s)',
            plan_file, r.uid, r.execid), e)

    # We will now upload the completed files to:
    # agave://data-sd2e-community/temp/flow_etl/REACTOR_NAME/PLAN_ID
    # - /temp/flow_etl/REACTOR_NAME is set by config.yml/destination.base_path
    #
    # Expectation: these files have been written to pwd() somwhere above
    datafiles = {'analysisParameters': 'analysis_parameters.json',
                 'colorModelParameters': 'color_model_parameters.json',
                 'cytometerConfiguration': 'cytometer_configuration.json',
                 'experimentalData': 'experimental_data.json',
                 'processControl': 'process_control_data.json'}

    # Figure out the plan_id from plan_uri
    # - Get the JSON file
    plan_uri_file = os.path.basename(plan_uri)
    # - Get JSON filename root
    plan_id = os.path.splitext(plan_uri_file)[0]
    # Default upload destination set in config.yml
    # - may want to add override but not essential now
    dest_dir = os.path.join(r.settings.destination.base_path, plan_id)
    dest_sys = r.settings.destination.system_id

    r.logger.debug("ensuring destination {} exists".format(
        agaveutils.to_agave_uri(dest_sys, dest_dir)))
    try:
        agaveutils.agave_mkdir(r.client, plan_id, dest_sys,
                               r.settings.destination.base_path)
    except Exception as e:
        r.on_failure(template.format(
            actor_name, 'could not access or create destination',
            dest_dir, r.uid, r.execid), e)

    job_def_inputs = {}
    for agaveparam, fname in datafiles.items():
        r.logger.info("uploading {} to {}".format(fname, dest_dir))
        fpath = os.path.join(PWD, fname)

        # rename the remote if it exists
        try:
            r.logger.debug("renaming remote {}".format(fname))
            remote_abs_path = os.path.join(dest_dir, fname)
            new_name = os.path.basename(remote_abs_path) + \
                '.' + str(int(datetime.datetime.now().strftime("%s")) * 1000)
            r.client.files.manage(systemId=dest_sys,
                                  body={'action': 'rename',
                                        'path': new_name},
                                  filePath=remote_abs_path)
        except Exception:
            r.logger.debug("{} does not exist or is inaccessible. ({})".format(
                remote_abs_path, 'ignoring error'))
            pass

        # upload the newly-generated file
        try:
            r.logger.debug("now uploading {}".format(fname))
            agaveutils.agave_upload_file(r.client, dest_dir, dest_sys, fpath)
        except Exception as e:
            prefix = '{} failed to upload {}'.format(actor_name, fname)
            r.on_failure(template.format(prefix, 'to', dest_dir,
                                         r.uid, r.execid), e)

        # Entries in this dict are needed to submit the FCS-ETL job later
        job_def_inputs[agaveparam] = agaveutils.to_agave_uri(
            dest_sys, os.path.join(dest_dir, fname))

    # Base inputPath off path of manifest
    # Cowboy coding - Take grandparent directory sans sanity checking!
    manifest_pathGrandparent = os.path.dirname(os.path.dirname(manifest_path))

    # Build the inputData path from settings (instead of hard-coding vals)
    #
    #   Our settings.job_params.data_subdir could be an array
    #   should there be a need to pull in other top-level dirs.
    #   In such a case inputPath would be constructed as a list
    #   of agave URIs. This is challenging to process in the
    #   job's runner script but possible and documented.

    inputDataPath = os.path.join(
        manifest_pathGrandparent, r.settings.job_params.data_subdir)
    job_def_inputs['inputData'] = agaveutils.to_agave_uri(
        agave_storage_sys, inputDataPath)

    # Submit a job request to the FCS-ETL app based on template + vars
    #
    # The job configuration is templated from settings.job_definition
    # name, inputs are empty. notifications are empty, too,
    # but we aren't implementing for the time being. Use the inputs
    # we built above from the uploaded list and path to the manifest
    # and synthesize a job name from app/actor/execution.
    #
    # By convention, slots we wish to template are left empty. Slots
    # we want to have a default value (that aren't defined by the app
    # itself) are included in the template, but can be over-ridden
    # programmatically with Python dict operations

    job_def = r.settings.job_definition
    app_record = r.settings.linked_reactors.get(AGAVE_APP_ALIAS, {})
    # this allows the appId to be set in the job_definition, but overridden
    # by configuration provided in settings.
    job_def_orig_appId = job_def.get('appId', None)
    job_def.appId = app_record.get('id', job_def_orig_appId)

    job_def.inputs = job_def_inputs
    job_def.name = "{}-{}".format(
        r.uid,
        r.execid)
    # set archivePath and archiveSystem based on manifest
    job_def.archiveSystem = agave_storage_sys
    job_def.archivePath = os.path.join(
        manifest_pathGrandparent, r.settings.job_params.output_subdir,
        job_def.appId, "{}-{}".format(
            r.uid, r.execid))

    # Expected outcome:
    #
    # An experimental data collection 'ABCDEF'
    # has (at present) directories of measurements and one or more
    # manifests (allowing for versioning). ETL apps can deposit results
    # under ABCDEF/processed/appid/<unique-directory-name>.
    r.logger.info('submitting FSC-ETL agave compute job')
    job_id = 'mockup'
    try:
        job_id = r.client.jobs.submit(body=job_def)['id']
        r.logger.info("compute job id is {}".format(job_id))
    except Exception as e:
        # Use a print here so we can more easily snag the job def
        # TODO - come back and take this out if we ever add a nonce to
        #        the callback notifications because that should not
        #        show up in the logs. One alternative would be to
        #        register a plaintext log formatter with redaction
        #        support, but that requires extending our logger module
        print(json.dumps(job_def, indent=4))
        r.on_failure(template.format(
            actor_name, 'failed when submitting an agave compute job for',
            job_def.appId, r.uid, r.execid), e)

    # Make a nice human-readable success message for the Slack log
    suffix = '{} and will deposit outputs in {}'.format(
        job_id, job_def.archivePath)
    r.on_success(template.format(actor_name, 'submitted job',
                                 suffix, r.uid, r.execid))


if __name__ == '__main__':
    main()
