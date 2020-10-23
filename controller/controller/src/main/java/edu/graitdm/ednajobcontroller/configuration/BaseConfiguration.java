package edu.graitdm.ednajobcontroller.configuration;


import com.beust.jcommander.Parameter;
import lombok.Getter;
import lombok.Setter;

import java.util.ArrayList;
import java.util.List;

import static edu.graitdm.ednajobcontroller.configuration.IConfigurationDefaults.EDNA_JOB_PATHS;
import static edu.graitdm.ednajobcontroller.configuration.IConfigurationDefaults.EDNA_NAMESPACE;
import static edu.graitdm.ednajobcontroller.configuration.IConfigurationDefaults.KUBECTL_HOST;
import static edu.graitdm.ednajobcontroller.configuration.IConfigurationDefaults.KUBECTL_PORT;
import static edu.graitdm.ednajobcontroller.configuration.IConfigurationDefaults.KUBECTL_PROTOCOL;

public class BaseConfiguration {
    @Parameter
    private List<String> parameters = new ArrayList<>();

    @Parameter(names = "--kubectl-protocol", description = "Access protocol for kubectl proxy. Either `http` or `https`")
    @Getter @Setter private String kubectlProtocol;

    @Parameter(names = "--kubectl-host", description = "The kubectl proxy host. Default is `127.0.0.1`.")
    @Getter @Setter private String kubectlHost;

    @Parameter(names = "--kubectl-port", description = "The kubectl proxy port. Default is `8080`.")
    @Getter @Setter private String kubectlPort;

    @Parameter(names = "--edna-job-path", description = "Location for edna application and job executables.")
    @Getter @Setter private String ednaJobPaths;

    @Parameter(names = "--edna-namespace", description = "Location for edna application and job executables.")
    @Getter @Setter private String ednaNamespace;

    private String kubectlURL;

    public BaseConfiguration(){
        kubectlProtocol = KUBECTL_PROTOCOL;
        kubectlHost = KUBECTL_HOST;
        kubectlPort = KUBECTL_PORT;
        ednaJobPaths = EDNA_JOB_PATHS;
        ednaNamespace = EDNA_NAMESPACE;
        buildURL();
    }

    public String getKubectlURL(){
        buildURL();
        return kubectlURL;
    }
    private void buildURL(){
        kubectlURL = getKubectlProtocol() + "://" + getKubectlHost() + ":" + getKubectlPort();
    }

}
