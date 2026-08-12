# Australian Imaging Service Pipelines - Community

Community contributed pipelines for the Australian Imaging Service.

Pipelines defined in this repository will be automatically built and deployed
to the Australian Imaging Service (after security screening) so they are
available to be run using the AIS' integrated container service.

## Tutorial

Please see the tutorial to learn how to contribute your own pipeline to the service

A static version of the tutorial can be found [here](https://nbviewer.org/github/Australian-Imaging-Service/pipelines-community/blob/main/tutorial/ais-pipelines-tutorial.ipynb). Note that you will need to clone repository and
run your own version if you execute the cells. Instructions on how to set this up are
included in the static version of the tutorial.

## Documentation and repository guides

- [Repository analysis](doc/repository_analysis.md) explains the committed
  package, specification, test, CI, and documentation layout.
- [ProtocolQC](doc/protocol-qc/README.md) documents the UNSW pipeline,
  its configuration, and its current production limitations.
- [VS Code setup](README_VSCode.md) covers the Mamba environment, workspace
  verification, and safe Codex session startup.
- Package-specific documentation is located at
  [Sydney Imaging](src/au.edu.sydney.sydneyimaging/README.md) and
  [UNSW RINSW](src/au.edu.unsw.rinsw/README.md).
