import {
  JupyterFrontEnd,
  JupyterFrontEndPlugin
} from '@jupyterlab/application';

const risemdf: JupyterFrontEndPlugin<void> = {
  id: '@jans-code/jupyterlab_rise_metadata_form:risemdf',
  autoStart: true,
  activate: (app: JupyterFrontEnd) => {
    console.log('Jupyterlab rise metadata-form activated');
  }
};

export default [risemdf];
