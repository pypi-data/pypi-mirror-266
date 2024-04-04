const pluginIds = {
  ExamplePlugin: '@amzn/sagemaker-jupyterlab-extensions:example',
  HideShutDownPlugin: '@amzn/sagemaker-jupyterlab-extensions:hideshutdown',
  SessionManagementPlugin: '@amzn/sagemaker-jupyterlab-extensions:sessionmanagement',
  ResourceUsagePlugin: '@amzn/sagemaker-jupyterlab-extensions:resourceusage',
  GitClonePlugin: '@amzn/sagemaker-jupyterlab-extensions:gitclone',
  PerformanceMeteringPlugin: '@amzn/sagemaker-jupyterlab-extensions:performance-metering',
  SpaceMenuPlugin: '@amzn/sagemaker-jupyterlab-extensions:spacemenu',
};

const JUPYTER_COMMAND_IDS = {
  mainMenu: {
    fileMenu: {
      shutdown: 'filemenu:shutdown',
    },
  },
  createTerminal: 'terminal:create-new',
  openDocManager: 'docmanager:open',
  goToPath: 'filebrowser:go-to-path',
};

const RESOURCE_PLUGIN_ID = '@amzn/sagemaker-jupyterlab-extensions:resourceusage:resource-usage-widget';
const SPACE_MENU_PLUGIN_ID = '@amzn/sagemaker-jupyterlab-extensions:spacemenu:space-menu-widget';

const i18nStrings = {};

const COOKIE_NAMES = {
  USER_PROFILE_NAME: 'studioUserProfileName',
};

export { pluginIds, i18nStrings, JUPYTER_COMMAND_IDS, RESOURCE_PLUGIN_ID, COOKIE_NAMES, SPACE_MENU_PLUGIN_ID };
