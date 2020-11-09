package edu.graitdm.ednajobcontroller.configuration;

import com.beust.jcommander.Parameter;
import lombok.Getter;
import lombok.Setter;

import java.util.ArrayList;
import java.util.List;

import static edu.graitdm.ednajobcontroller.configuration.IConfigurationDefaults.EDNA_NAMESPACE;
import static edu.graitdm.ednajobcontroller.configuration.IConfigurationDefaults.KUBECTL_HOST;
import static edu.graitdm.ednajobcontroller.configuration.IConfigurationDefaults.KUBECTL_PORT;
import static edu.graitdm.ednajobcontroller.configuration.IConfigurationDefaults.KUBECTL_PROTOCOL;
import static edu.graitdm.ednajobcontroller.configuration.IConfigurationDefaults.DOCKER_HOST_UNIX;
import static edu.graitdm.ednajobcontroller.configuration.IConfigurationDefaults.DOCKER_HOST_WINDOWS;
import static edu.graitdm.ednajobcontroller.configuration.IConfigurationDefaults.EDNA_APP_DIR;
import static edu.graitdm.ednajobcontroller.configuration.IConfigurationDefaults.EDNA_SOURCE_DIR;
import static edu.graitdm.ednajobcontroller.configuration.IConfigurationDefaults.LOG_LEVEL;

/**
 * The BaseConfiguration contains the default configuration options for the EdnaJobController.
 * Configuration options can be passed with command line args.
 */
public class BaseConfiguration {

    @Parameter
    private List<String> parameters = new ArrayList<>();

    @Parameter(names = "--kubectl-protocol", description = "Access protocol for kubectl proxy. Either `http` or `https`")
    @Getter @Setter private String kubectlProtocol;

    @Parameter(names = "--kubectl-host", description = "The kubectl proxy host. Default is `127.0.0.1`.")
    @Getter @Setter private String kubectlHost;

    @Parameter(names = "--kubectl-port", description = "The kubectl proxy port. Default is `8080`.")
    @Getter @Setter private String kubectlPort;

    @Parameter(names = "--edna-namespace", description = "Location for edna application and job executables.")
    @Getter @Setter private String ednaNamespace;

    @Parameter(names = "--docker-host", description = "URL for the docker daemon host")
    @Getter @Setter private String dockerHost;

    @Parameter(names = "--edna-source-dir", description = "Path to edna source directory. Defaults to current directory")
    @Getter @Setter private String ednaSourcedir;

    @Parameter(names = "--edna-app-dir", description = "Path to edna app directory. Defaults to current directory")
    @Getter @Setter private String ednaAppdir;

    @Parameter(names = "--log-level", description = "Log level: ALL, DEBUG, ERROR, FATAL, INFO, OFF")
    @Getter @Setter private String logLevel;

    private String kubectlURL;

    /**
     * Constructor for {@link BaseConfiguration}.
     *
     * Builds the kubectl URL using {@link #kubectlHost}, {@link #kubectlPort}
     * and {@link #kubectlProtocol}. Also sets the {@link #dockerHost} based on whether system is Windows or Unix.
     * Unix is supported as anything other than Windows, so this should be fixed (TODO).
     */
    public BaseConfiguration(){
        kubectlProtocol = KUBECTL_PROTOCOL;
        kubectlHost = KUBECTL_HOST;
        kubectlPort = KUBECTL_PORT;
        ednaNamespace = EDNA_NAMESPACE;
        if (System.getProperty("os.name").toLowerCase().indexOf("win") >= 0){
            dockerHost = DOCKER_HOST_WINDOWS;
        }
        else{
            dockerHost = DOCKER_HOST_UNIX;
        }
        ednaSourcedir = EDNA_SOURCE_DIR;
        ednaAppdir = EDNA_APP_DIR;
        logLevel = LOG_LEVEL;
        buildURL();
    }

    /**
     * Returns the {@link #kubectlURL}.
     *
     * The {@link #kubectlURL} is built with {@link #buildURL()}
     *
     * @return The {@link #kubectlURL} after setting it.
     */
    public String getKubectlURL(){
        buildURL();
        return kubectlURL;
    }

    /**
     * Builds the {@link #kubectlURL}
     *
     * The URL is build by combining the {@link #kubectlProtocol}, {@link #kubectlHost}, and {@link #kubectlPort}.
     */
    private void buildURL(){
        kubectlURL = getKubectlProtocol() + "://" + getKubectlHost() + ":" + getKubectlPort();
    }

}
