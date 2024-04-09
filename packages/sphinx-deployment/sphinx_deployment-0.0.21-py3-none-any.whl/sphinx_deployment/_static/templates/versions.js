var sphinx_deployment_current_version = `{{ sphinx_deployment_current_version }}`;
var sphinx_deployment_versions_file = new URL(
  window.location.href.slice(0, window.location.href.lastIndexOf("/")) +
    "/" +
    `{{ sphinx_deployment_versions_file }}`,
).toString();
