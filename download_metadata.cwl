# Automate model checking workflow
class: CommandLineTool
cwlVersion: v1.0
id: download_metadata
label: Download Metadata TODO
$namespaces:
  sbg: 'https://www.sevenbridges.com/'

requirements: []
  # - class: InitialWorkDirRequirement
  #   listing:
  #     -$(inputs.workdir)

  # 'sbg:license': CeCiLL
  # 'sbg:toolAuthor': Florent Bonnier
baseCommand: ["hbp_cwl_input_downloader"]

inputs:
  hbp_token:
    type: string
    inputBinding:
        position: 1

  model_instance_id:
    type: string
    inputBinding:
        position: 2

  # workdir: 
  #   type: string
  #   inputBinding:
  #       position: 3
  #       prefix: 

  instruction: 
    type: string
    inputBinding:
      position: 3
      # prefix: --run
    # dirname: workdir
    # basename: 
    

outputs: 
    jsonfile:
        type: File