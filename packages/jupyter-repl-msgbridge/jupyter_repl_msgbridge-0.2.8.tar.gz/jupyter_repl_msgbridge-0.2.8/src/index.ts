import {
  JupyterFrontEnd,
  JupyterFrontEndPlugin
} from '@jupyterlab/application';
import { INotebookTracker } from '@jupyterlab/notebook';
import { ICodeCellModel } from '@jupyterlab/cells';

const plugin: JupyterFrontEndPlugin<void> = {
  id: 'jupyter-repl-msgbridge:plugin',
  description: 'A JupyterLab extension that output to parent document',
  autoStart: true,
  requires: [INotebookTracker],
  activate: (app: JupyterFrontEnd, notebooks: INotebookTracker) => {
    console.log('JupyterLab extension jupyter-repl-msgbridge is activated!');

    notebooks.activeCellChanged.connect((sender, cell) => {
      if (cell && cell.model.type === 'code') {
        const codeCellModel = cell.model as ICodeCellModel;
        codeCellModel.outputs.changed.connect(() => {
          const output = codeCellModel.outputs.get(0);
          if (output) {
            window.parent.postMessage(output.toJSON(), '*');
          }
        });
      }
    });
  }
};

export default plugin;
