package edu.graitdm.ednajobcontroller.configuration;

/**
 * The <code>IConfigurationDefaults</code> interface contains the default configuration parameters
 * for the EdnaJobController. These defaults are loaded into {@link BaseConfiguration} with
 * {@link com.beust.jcommander.JCommander}. Defaults can be replaced with command line arguments.
 */
public interface IConfigurationDefaults {

    String KUBECTL_PROTOCOL = "http";   // Default protocol is with http, not https (TODO -- should this be changed)
    String KUBECTL_HOST = "127.0.0.1";  // Default address is localhost
    String KUBECTL_PORT = "8080";       // Default port is 8080 from kubectl proxy --port 8080
    String EDNA_NAMESPACE = "default";  // The default namespace.
    String DOCKER_HOST_UNIX = "unix:///var/run/docker.sock";    // The docker socket for Unix
    String DOCKER_HOST_WINDOWS = "tcp://localhost:2375";        // The docker socket for Windows (not yet tested, but should work according to docs)
    String EDNA_SOURCE_DIR = System.getProperty("user.dir");    // TODO (Abhijit) update to pypi
    String EDNA_APP_DIR = System.getProperty("user.dir");       // Default path to the app dir containing applications and jobs, in home
    String LOG_LEVEL = "INFO";          // Set log level to info (net yet tested, but does not seem to work right now)


}
